"""
Vector Store Module
Manages document embeddings and similarity search
"""
from typing import List, Dict, Any, Optional, Literal
from pathlib import Path
import json
from loguru import logger
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.schema import Document
from config import settings

# Try to import FAISS, but make it optional for Python 3.13+
try:
    from langchain_community.vectorstores import FAISS
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    logger.warning("FAISS not available. Only ChromaDB will be supported.")


class VectorStore:
    """
    Manages document embeddings and vector similarity search
    """
    
    def __init__(
        self,
        store_type: Optional[str] = None,
        store_path: Optional[str] = None,
        embedding_model: Optional[str] = None
    ):
        """
        Initialize vector store
        
        Args:
            store_type: Type of vector store (chroma or faiss)
            store_path: Path to persist the vector store
            embedding_model: OpenAI embedding model to use
        """
        self.store_type = store_type or settings.vector_store_type
        
        # Check if FAISS is requested but not available
        if self.store_type == "faiss" and not FAISS_AVAILABLE:
            logger.warning(
                "FAISS is not available (requires Python < 3.13). "
                "Falling back to ChromaDB."
            )
            self.store_type = "chroma"
        
        self.store_path = Path(store_path or settings.vector_store_path)
        self.embedding_model = embedding_model or settings.openai_embedding_model
        
        # Initialize embeddings
        self.embeddings = OpenAIEmbeddings(
            model=self.embedding_model,
            openai_api_key=settings.openai_api_key
        )
        
        self.vector_store = None
        self._initialize_store()
        
        logger.info(
            f"VectorStore initialized: type={self.store_type}, "
            f"path={self.store_path}, model={self.embedding_model}"
        )
    
    def _initialize_store(self):
        """Initialize or load existing vector store"""
        self.store_path.mkdir(parents=True, exist_ok=True)
        
        if self.store_type == "chroma":
            # Check if store exists
            if (self.store_path / "chroma.sqlite3").exists():
                logger.info("Loading existing Chroma vector store")
                self.vector_store = Chroma(
                    persist_directory=str(self.store_path),
                    embedding_function=self.embeddings
                )
            else:
                logger.info("Initializing new Chroma vector store")
                self.vector_store = None  # Will be created on first add
        
        elif self.store_type == "faiss":
            if not FAISS_AVAILABLE:
                raise RuntimeError(
                    "FAISS is not available. Please use ChromaDB or install Python < 3.13"
                )
            index_path = self.store_path / "index.faiss"
            if index_path.exists():
                logger.info("Loading existing FAISS vector store")
                self.vector_store = FAISS.load_local(
                    str(self.store_path),
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
            else:
                logger.info("FAISS store will be created on first add")
                self.vector_store = None
    
    def add_documents(self, chunks: List[Dict[str, Any]]) -> None:
        """
        Add document chunks to the vector store
        
        Args:
            chunks: List of document chunks with content and metadata
        """
        if not chunks:
            logger.warning("No chunks to add")
            return
        
        logger.info(f"Adding {len(chunks)} chunks to vector store")
        
        # Convert to LangChain Document format
        documents = [
            Document(
                page_content=chunk["content"],
                metadata=chunk.get("metadata", {})
            )
            for chunk in chunks
        ]
        
        try:
            if self.store_type == "chroma":
                if self.vector_store is None:
                    # Create new store
                    self.vector_store = Chroma.from_documents(
                        documents=documents,
                        embedding=self.embeddings,
                        persist_directory=str(self.store_path)
                    )
                else:
                    # Add to existing store
                    self.vector_store.add_documents(documents)
                
                # Persist changes
                self.vector_store.persist()
                logger.info("Chroma vector store persisted")
            
            elif self.store_type == "faiss":
                if not FAISS_AVAILABLE:
                    raise RuntimeError(
                        "FAISS is not available. Please use ChromaDB or install Python < 3.13"
                    )
                if self.vector_store is None:
                    # Create new store
                    self.vector_store = FAISS.from_documents(
                        documents=documents,
                        embedding=self.embeddings
                    )
                else:
                    # Add to existing store
                    self.vector_store.add_documents(documents)
                
                # Save to disk
                self.vector_store.save_local(str(self.store_path))
                logger.info("FAISS vector store saved")
            
            logger.info(f"Successfully added {len(chunks)} chunks")
            
        except Exception as e:
            logger.error(f"Error adding documents to vector store: {e}")
            raise
    
    def search(
        self,
        query: str,
        top_k: Optional[int] = None,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents
        
        Args:
            query: Search query
            top_k: Number of results to return (uses config default if not provided)
            filter_metadata: Optional metadata filters
        
        Returns:
            List of similar documents with scores
        """
        if self.vector_store is None:
            logger.warning("Vector store is empty")
            return []
        
        top_k = top_k or settings.top_k_results
        
        logger.info(f"Searching for: '{query}' (top_k={top_k})")
        
        try:
            # Perform similarity search with scores
            results = self.vector_store.similarity_search_with_score(
                query=query,
                k=top_k,
                filter=filter_metadata
            )
            
            # Format results
            formatted_results = []
            for doc, score in results:
                formatted_results.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "score": float(score)
                })
            
            logger.info(f"Found {len(formatted_results)} results")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching vector store: {e}")
            raise
    
    def search_multiple(
        self,
        queries: List[str],
        top_k: Optional[int] = None,
        deduplicate: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Search using multiple queries and combine results
        
        Args:
            queries: List of search queries
            top_k: Number of results per query
            deduplicate: Whether to remove duplicate results
        
        Returns:
            Combined list of results
        """
        logger.info(f"Performing multi-query search with {len(queries)} queries")
        
        all_results = []
        seen_contents = set()
        
        for query in queries:
            results = self.search(query, top_k)
            
            for result in results:
                content = result["content"]
                
                if deduplicate:
                    if content not in seen_contents:
                        all_results.append(result)
                        seen_contents.add(content)
                else:
                    all_results.append(result)
        
        # Sort by score
        all_results.sort(key=lambda x: x["score"], reverse=True)
        
        logger.info(f"Multi-query search returned {len(all_results)} unique results")
        return all_results
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the vector store
        
        Returns:
            Dictionary with store statistics
        """
        if self.vector_store is None:
            return {
                "initialized": False,
                "document_count": 0
            }
        
        try:
            if self.store_type == "chroma":
                collection = self.vector_store._collection
                count = collection.count()
            elif self.store_type == "faiss":
                count = self.vector_store.index.ntotal
            else:
                count = 0
            
            return {
                "initialized": True,
                "store_type": self.store_type,
                "document_count": count,
                "embedding_model": self.embedding_model,
                "store_path": str(self.store_path)
            }
        except Exception as e:
            logger.error(f"Error getting store stats: {e}")
            return {"error": str(e)}
    
    def clear(self) -> None:
        """Clear all documents from the vector store"""
        logger.warning("Clearing vector store")
        
        if self.store_type == "chroma" and self.vector_store:
            self.vector_store.delete_collection()
        
        # Reinitialize
        self._initialize_store()
        logger.info("Vector store cleared")


def create_vector_store(
    store_type: Optional[str] = None,
    store_path: Optional[str] = None
) -> VectorStore:
    """
    Factory function to create a VectorStore instance
    
    Args:
        store_type: Optional type override
        store_path: Optional path override
    
    Returns:
        VectorStore instance
    """
    return VectorStore(store_type=store_type, store_path=store_path)
