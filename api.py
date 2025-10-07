"""
FastAPI Application for RAG Query Rewrite POC
"""
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import tempfile
import os
from pathlib import Path
from loguru import logger

from config import settings
from rag_pipeline import RAGPipeline, create_pipeline
from loguru import logger

# Configure logger
logger.add("logs/api.log", rotation="500 MB", level=settings.log_level)

# Initialize FastAPI app
app = FastAPI(
    title="RAG Query Rewrite API",
    description="A Proof of Concept API for RAG with intelligent query rewriting",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global RAG pipeline instance
pipeline: Optional[RAGPipeline] = None


# Request/Response Models
class QueryRequest(BaseModel):
    """Request model for querying the RAG system"""
    question: str = Field(..., description="The question to ask")
    top_k: Optional[int] = Field(None, description="Number of documents to retrieve")
    max_queries: Optional[int] = Field(3, description="Maximum number of query variations to generate")
    enable_rewrite: Optional[bool] = Field(None, description="Override query rewriting setting")
    return_sources: bool = Field(True, description="Include source documents in response")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context for query rewriting")


class QueryResponse(BaseModel):
    """Response model for query results"""
    answer: str
    sources: Optional[List[Dict[str, Any]]] = None
    metadata: Dict[str, Any]


class IngestRequest(BaseModel):
    """Request model for ingesting text documents"""
    text: str = Field(..., description="Text content to ingest")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadata for the document")


class IngestResponse(BaseModel):
    """Response model for document ingestion"""
    success: bool
    chunks_added: Optional[int] = None
    message: str


class StatsResponse(BaseModel):
    """Response model for system statistics"""
    pipeline: Dict[str, Any]


# API Endpoints
@app.on_event("startup")
async def startup_event():
    """Initialize the RAG pipeline on startup"""
    global pipeline
    logger.info("Starting up RAG Query Rewrite API")
    pipeline = create_pipeline()
    logger.info("Pipeline initialized successfully")


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "RAG Query Rewrite API",
        "version": "1.0.0",
        "description": "A POC implementation of RAG with intelligent query rewriting",
        "endpoints": {
            "POST /query": "Query the RAG system",
            "POST /ingest/text": "Ingest text documents",
            "POST /ingest/file": "Ingest file documents",
            "GET /stats": "Get system statistics",
            "GET /health": "Health check"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    if pipeline is None:
        raise HTTPException(status_code=503, detail="Pipeline not initialized")
    
    return {
        "status": "healthy",
        "rewrite_enabled": pipeline.enable_rewrite,
        "model": pipeline.model
    }


@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """
    Query the RAG system with optional query rewriting
    
    Args:
        request: Query request with question and parameters
    
    Returns:
        Query response with answer and sources
    """
    if pipeline is None:
        raise HTTPException(status_code=503, detail="Pipeline not initialized")
    
    try:
        logger.info(f"Received query: {request.question}")
        
        # Override rewrite setting if provided
        original_rewrite_setting = pipeline.enable_rewrite
        original_max_queries = pipeline.max_queries if hasattr(pipeline, 'max_queries') else 3
        
        if request.enable_rewrite is not None:
            pipeline.enable_rewrite = request.enable_rewrite
        
        if request.max_queries is not None and pipeline.query_rewriter:
            pipeline.query_rewriter.max_queries = request.max_queries
        
        # Process query
        result = pipeline.query(
            question=request.question,
            top_k=request.top_k,
            context=request.context,
            return_sources=request.return_sources
        )
        
        # Restore original settings
        pipeline.enable_rewrite = original_rewrite_setting
        if pipeline.query_rewriter:
            pipeline.query_rewriter.max_queries = original_max_queries
        
        return QueryResponse(**result)
        
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ingest/text", response_model=IngestResponse)
async def ingest_text(request: IngestRequest):
    """
    Ingest raw text into the RAG system
    
    Args:
        request: Text content and optional metadata
    
    Returns:
        Ingestion statistics
    """
    if pipeline is None:
        raise HTTPException(status_code=503, detail="Pipeline not initialized")
    
    try:
        logger.info(f"Ingesting text document ({len(request.text)} characters)")
        
        # Process text with metadata
        chunks = pipeline.document_processor.load_text(
            request.text,
            metadata=request.metadata
        )
        
        # Add to vector store
        pipeline.vector_store.add_documents(chunks)
        
        return IngestResponse(
            success=True,
            chunks_added=len(chunks),
            message=f"Successfully ingested {len(chunks)} chunks"
        )
        
    except Exception as e:
        logger.error(f"Error ingesting text: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ingest/file", response_model=IngestResponse)
async def ingest_file(file: UploadFile = File(...)):
    """
    Ingest a file document into the RAG system
    
    Supports: PDF, TXT, DOCX, Markdown
    
    Args:
        file: Uploaded file
    
    Returns:
        Ingestion statistics
    """
    if pipeline is None:
        raise HTTPException(status_code=503, detail="Pipeline not initialized")
    
    # Validate file extension
    supported_extensions = {".pdf", ".txt", ".docx", ".doc", ".md", ".markdown"}
    file_extension = Path(file.filename).suffix.lower()
    
    if file_extension not in supported_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Supported: {', '.join(supported_extensions)}"
        )
    
    try:
        logger.info(f"Ingesting file: {file.filename}")
        
        # Save uploaded file to temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        try:
            # Process the file
            result = pipeline.ingest_documents(
                source=tmp_file_path,
                source_type="file"
            )
            
            if result["success"]:
                return IngestResponse(
                    success=True,
                    chunks_added=result["chunks_added"],
                    message=f"Successfully ingested {file.filename}: {result['chunks_added']} chunks"
                )
            else:
                raise HTTPException(status_code=500, detail=result.get("error", "Unknown error"))
        
        finally:
            # Clean up temporary file
            os.unlink(tmp_file_path)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error ingesting file: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats", response_model=StatsResponse)
async def get_stats():
    """
    Get system statistics
    
    Returns:
        Pipeline and vector store statistics
    """
    if pipeline is None:
        raise HTTPException(status_code=503, detail="Pipeline not initialized")
    
    try:
        stats = pipeline.get_stats()
        return StatsResponse(pipeline=stats)
        
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/rewrite")
async def rewrite_query(question: str):
    """
    Test query rewriting without performing retrieval
    
    Args:
        question: Query to rewrite
    
    Returns:
        Rewritten query variations
    """
    if pipeline is None or pipeline.query_rewriter is None:
        raise HTTPException(status_code=503, detail="Query rewriter not available")
    
    try:
        result = pipeline.query_rewriter.rewrite(question)
        return result
        
    except Exception as e:
        logger.error(f"Error rewriting query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "api:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload,
        log_level=settings.log_level.lower()
    )
