"""
Document Processor Module
Handles document loading, chunking, and preprocessing
"""
from typing import List, Dict, Any, Optional
from pathlib import Path
import re
from loguru import logger

# Document loaders
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    Docx2txtLoader
)

# Try to import UnstructuredMarkdownLoader, but make it optional
try:
    from langchain_community.document_loaders import UnstructuredMarkdownLoader
    MARKDOWN_LOADER_AVAILABLE = True
except ImportError:
    MARKDOWN_LOADER_AVAILABLE = False
    logger.warning("UnstructuredMarkdownLoader not available. Markdown files will be loaded as plain text.")

from config import settings


class DocumentProcessor:
    """
    Processes documents for ingestion into the vector store
    """
    
    def __init__(
        self, 
        chunk_size: Optional[int] = None,
        chunk_overlap: Optional[int] = None
    ):
        """
        Initialize document processor
        
        Args:
            chunk_size: Size of text chunks (uses config default if not provided)
            chunk_overlap: Overlap between chunks (uses config default if not provided)
        """
        self.chunk_size = chunk_size or settings.chunk_size
        self.chunk_overlap = chunk_overlap or settings.chunk_overlap
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
        logger.info(
            f"DocumentProcessor initialized: chunk_size={self.chunk_size}, "
            f"chunk_overlap={self.chunk_overlap}"
        )
    
    def load_document(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Load a document from file
        
        Args:
            file_path: Path to the document file
        
        Returns:
            List of document chunks with metadata
        """
        file_path_obj = Path(file_path)
        
        if not file_path_obj.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        logger.info(f"Loading document: {file_path}")
        
        # Select appropriate loader based on file extension
        suffix = file_path_obj.suffix.lower()
        
        try:
            if suffix == ".pdf":
                loader = PyPDFLoader(file_path)
            elif suffix == ".txt":
                loader = TextLoader(file_path, encoding="utf-8")
            elif suffix in [".docx", ".doc"]:
                loader = Docx2txtLoader(file_path)
            elif suffix in [".md", ".markdown"]:
                if MARKDOWN_LOADER_AVAILABLE:
                    loader = UnstructuredMarkdownLoader(file_path)
                else:
                    # Fallback to text loader for markdown
                    logger.info("Using TextLoader for markdown file (unstructured not available)")
                    loader = TextLoader(file_path, encoding="utf-8")
            else:
                # Default to text loader
                logger.warning(f"Unknown file type {suffix}, using TextLoader")
                loader = TextLoader(file_path, encoding="utf-8")
            
            # Load documents
            documents = loader.load()
            logger.info(f"Loaded {len(documents)} page(s) from {file_path}")
            
            # Split into chunks
            chunks = self.text_splitter.split_documents(documents)
            
            # Convert to dict format with metadata
            processed_chunks = []
            for i, chunk in enumerate(chunks):
                processed_chunks.append({
                    "content": chunk.page_content,
                    "metadata": {
                        **chunk.metadata,
                        "source": file_path,
                        "chunk_id": i,
                        "chunk_size": len(chunk.page_content)
                    }
                })
            
            logger.info(f"Processed into {len(processed_chunks)} chunks")
            return processed_chunks
            
        except Exception as e:
            logger.error(f"Error loading document {file_path}: {e}")
            raise
    
    def load_directory(self, directory_path: str, file_pattern: str = "**/*") -> List[Dict[str, Any]]:
        """
        Load all documents from a directory
        
        Args:
            directory_path: Path to the directory
            file_pattern: Glob pattern for files to load (default: all files)
        
        Returns:
            List of all document chunks from the directory
        """
        directory = Path(directory_path)
        
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory_path}")
        
        logger.info(f"Loading documents from directory: {directory_path}")
        
        # Supported file extensions
        supported_extensions = {".pdf", ".txt", ".docx", ".doc", ".md", ".markdown"}
        
        all_chunks = []
        files = list(directory.glob(file_pattern))
        
        for file_path in files:
            if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
                try:
                    chunks = self.load_document(str(file_path))
                    all_chunks.extend(chunks)
                except Exception as e:
                    logger.error(f"Failed to process {file_path}: {e}")
                    continue
        
        logger.info(f"Loaded {len(all_chunks)} total chunks from {len(files)} files")
        return all_chunks
    
    def load_text(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Process raw text into chunks
        
        Args:
            text: Raw text content
            metadata: Optional metadata to attach to chunks
        
        Returns:
            List of text chunks with metadata
        """
        logger.info(f"Processing raw text ({len(text)} characters)")
        
        # Split text into chunks
        chunks = self.text_splitter.split_text(text)
        
        # Create chunk dictionaries
        processed_chunks = []
        for i, chunk in enumerate(chunks):
            chunk_metadata = {
                "source": "raw_text",
                "chunk_id": i,
                "chunk_size": len(chunk)
            }
            
            if metadata:
                chunk_metadata.update(metadata)
            
            processed_chunks.append({
                "content": chunk,
                "metadata": chunk_metadata
            })
        
        logger.info(f"Processed into {len(processed_chunks)} chunks")
        return processed_chunks
    
    def preprocess_text(self, text: str) -> str:
        """
        Clean and preprocess text
        
        Args:
            text: Raw text
        
        Returns:
            Cleaned text
        """
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters (optional, depends on use case)
        # text = re.sub(r'[^\w\s.,!?-]', '', text)
        
        return text.strip()
