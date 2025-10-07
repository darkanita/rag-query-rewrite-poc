"""
RAG Pipeline Module
Integrates query rewriting, document retrieval, and answer generation
"""
from typing import List, Dict, Any, Optional
from loguru import logger
from openai import OpenAI

from config import settings
from query_rewriter import QueryRewriter, create_rewriter
from vector_store import VectorStore, create_vector_store
from document_processor import DocumentProcessor


class RAGPipeline:
    """
    Complete RAG pipeline with query rewriting capabilities
    """
    
    def __init__(
        self,
        enable_rewrite: Optional[bool] = None,
        rewrite_strategy: Optional[str] = None,
        max_queries: int = 3,
        vector_store: Optional[VectorStore] = None,
        query_rewriter: Optional[QueryRewriter] = None
    ):
        """
        Initialize RAG pipeline
        
        Args:
            enable_rewrite: Whether to enable query rewriting
            rewrite_strategy: Strategy for query rewriting
            max_queries: Maximum number of query variations (default: 3)
            vector_store: Pre-initialized vector store (creates new if not provided)
            query_rewriter: Pre-initialized query rewriter (creates new if not provided)
        """
        self.enable_rewrite = enable_rewrite if enable_rewrite is not None else settings.enable_query_rewrite
        self.max_queries = max_queries
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
        
        # Initialize components
        self.vector_store = vector_store or create_vector_store()
        if self.enable_rewrite:
            if query_rewriter:
                self.query_rewriter = query_rewriter
            else:
                self.query_rewriter = create_rewriter(rewrite_strategy, max_queries)
        else:
            self.query_rewriter = None
        self.document_processor = DocumentProcessor()
        
        logger.info(
            f"RAGPipeline initialized: rewrite_enabled={self.enable_rewrite}, "
            f"model={self.model}"
        )
    
    def ingest_documents(
        self,
        source: str,
        source_type: str = "file"
    ) -> Dict[str, Any]:
        """
        Ingest documents into the vector store
        
        Args:
            source: Path to file/directory or raw text
            source_type: Type of source (file, directory, text)
        
        Returns:
            Ingestion statistics
        """
        logger.info(f"Ingesting documents from {source_type}: {source}")
        
        try:
            if source_type == "file":
                chunks = self.document_processor.load_document(source)
            elif source_type == "directory":
                chunks = self.document_processor.load_directory(source)
            elif source_type == "text":
                chunks = self.document_processor.load_text(source)
            else:
                raise ValueError(f"Unknown source type: {source_type}")
            
            # Add to vector store
            self.vector_store.add_documents(chunks)
            
            stats = {
                "success": True,
                "source": source,
                "source_type": source_type,
                "chunks_added": len(chunks)
            }
            
            logger.info(f"Ingestion complete: {len(chunks)} chunks added")
            return stats
            
        except Exception as e:
            logger.error(f"Error during ingestion: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def query(
        self,
        question: str,
        top_k: Optional[int] = None,
        context: Optional[Dict[str, Any]] = None,
        return_sources: bool = True
    ) -> Dict[str, Any]:
        """
        Query the RAG system
        
        Args:
            question: User question
            top_k: Number of documents to retrieve
            context: Optional context for query rewriting
            return_sources: Whether to include source documents in response
        
        Returns:
            Dictionary with answer and metadata
        """
        logger.info(f"Processing query: '{question}'")
        
        try:
            # Step 1: Query rewriting (if enabled)
            queries_to_search = [question]
            rewrite_info = None
            
            if self.enable_rewrite and self.query_rewriter:
                logger.info("Applying query rewriting")
                rewrite_result = self.query_rewriter.rewrite(question, context)
                queries_to_search = rewrite_result["rewritten"]
                rewrite_info = {
                    "strategy": rewrite_result["strategy"],
                    "num_queries": len(queries_to_search),
                    "queries": queries_to_search
                }
                logger.info(f"Query rewritten into {len(queries_to_search)} variations")
            
            # Step 2: Retrieve relevant documents
            logger.info("Retrieving relevant documents")
            
            if len(queries_to_search) > 1:
                # Multi-query retrieval
                retrieved_docs = self.vector_store.search_multiple(
                    queries_to_search,
                    top_k=top_k,
                    deduplicate=True
                )
            else:
                # Single query retrieval
                retrieved_docs = self.vector_store.search(
                    queries_to_search[0],
                    top_k=top_k
                )
            
            if not retrieved_docs:
                logger.warning("No relevant documents found")
                return {
                    "answer": "I couldn't find relevant information to answer your question.",
                    "sources": [],
                    "metadata": {
                        "query_rewrite": rewrite_info,
                        "documents_retrieved": 0
                    }
                }
            
            logger.info(f"Retrieved {len(retrieved_docs)} documents")
            
            # Step 3: Generate answer using retrieved context
            logger.info("Generating answer")
            answer = self._generate_answer(question, retrieved_docs)
            
            # Prepare response
            response = {
                "answer": answer,
                "metadata": {
                    "query_rewrite": rewrite_info,
                    "documents_retrieved": len(retrieved_docs),
                    "model": self.model
                }
            }
            
            if return_sources:
                response["sources"] = [
                    {
                        "content": doc["content"],
                        "metadata": doc["metadata"],
                        "relevance_score": doc["score"]
                    }
                    for doc in retrieved_docs[:top_k or settings.top_k_results]
                ]
            
            logger.info("Query processing complete")
            return response
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return {
                "answer": f"An error occurred: {str(e)}",
                "error": str(e)
            }
    
    def _generate_answer(
        self,
        question: str,
        documents: List[Dict[str, Any]]
    ) -> str:
        """
        Generate answer using retrieved documents
        
        Args:
            question: User question
            documents: Retrieved documents with content and metadata
        
        Returns:
            Generated answer
        """
        # Build context from retrieved documents
        context_parts = []
        for i, doc in enumerate(documents, 1):
            source = doc["metadata"].get("source", "Unknown")
            context_parts.append(f"[Document {i}] (Source: {source})\n{doc['content']}")
        
        context = "\n\n".join(context_parts)
        
        # Create prompt
        system_prompt = """You are a helpful AI assistant that answers questions based on the provided context.
Your task is to:
1. Carefully read and understand the context documents
2. Answer the user's question accurately using information from the context
3. If the context doesn't contain enough information, say so clearly
4. Cite the relevant document numbers when providing information
5. Be concise but comprehensive in your answer"""
        
        user_prompt = f"""Context Documents:
{context}

Question: {question}

Please provide a detailed answer based on the context documents above. Cite the document numbers when referencing specific information."""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=settings.temperature,
                max_tokens=settings.max_tokens
            )
            
            answer = response.choices[0].message.content.strip()
            return answer
            
        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            raise
    
    def batch_query(
        self,
        questions: List[str],
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Process multiple queries in batch
        
        Args:
            questions: List of questions
            **kwargs: Additional arguments passed to query()
        
        Returns:
            List of query results
        """
        logger.info(f"Processing batch of {len(questions)} queries")
        return [self.query(q, **kwargs) for q in questions]
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get pipeline statistics
        
        Returns:
            Dictionary with pipeline stats
        """
        return {
            "rewrite_enabled": self.enable_rewrite,
            "rewrite_strategy": self.query_rewriter.strategy.value if self.query_rewriter else None,
            "vector_store": self.vector_store.get_stats(),
            "model": self.model,
            "embedding_model": settings.openai_embedding_model
        }


def create_pipeline(
    enable_rewrite: Optional[bool] = None,
    rewrite_strategy: Optional[str] = None,
    max_queries: int = 3
) -> RAGPipeline:
    """
    Factory function to create a RAGPipeline instance
    
    Args:
        enable_rewrite: Optional override for query rewriting
        rewrite_strategy: Optional strategy override
        max_queries: Maximum number of query variations (default: 3)
    
    Returns:
        RAGPipeline instance
    """
    return RAGPipeline(
        enable_rewrite=enable_rewrite,
        rewrite_strategy=rewrite_strategy,
        max_queries=max_queries
    )
