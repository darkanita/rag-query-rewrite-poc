"""
Unit Tests for RAG Query Rewrite POC
"""
import pytest
from unittest.mock import Mock, patch
from pathlib import Path

from query_rewriter import QueryRewriter, RewriteStrategy
from document_processor import DocumentProcessor
from vector_store import VectorStore
from rag_pipeline import RAGPipeline


class TestQueryRewriter:
    """Tests for QueryRewriter"""
    
    def test_rewriter_initialization(self):
        """Test query rewriter initialization"""
        with patch('query_rewriter.OpenAI'):
            rewriter = QueryRewriter(strategy="expansion")
            assert rewriter.strategy == RewriteStrategy.EXPANSION
    
    def test_rewrite_expansion(self):
        """Test query expansion strategy"""
        with patch('query_rewriter.OpenAI') as mock_openai:
            # Mock API response
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = "query 1\nquery 2\nquery 3"
            mock_openai.return_value.chat.completions.create.return_value = mock_response
            
            rewriter = QueryRewriter(strategy="expansion")
            result = rewriter.rewrite("test query")
            
            assert result["strategy"] == "expansion"
            assert "rewritten" in result
            assert len(result["rewritten"]) > 1


class TestDocumentProcessor:
    """Tests for DocumentProcessor"""
    
    def test_processor_initialization(self):
        """Test document processor initialization"""
        processor = DocumentProcessor(chunk_size=500, chunk_overlap=50)
        assert processor.chunk_size == 500
        assert processor.chunk_overlap == 50
    
    def test_load_text(self):
        """Test text processing"""
        processor = DocumentProcessor()
        text = "This is a test document. " * 100
        chunks = processor.load_text(text)
        
        assert len(chunks) > 0
        assert all("content" in chunk for chunk in chunks)
        assert all("metadata" in chunk for chunk in chunks)
    
    def test_preprocess_text(self):
        """Test text preprocessing"""
        processor = DocumentProcessor()
        text = "  Multiple   spaces   here  "
        cleaned = processor.preprocess_text(text)
        assert cleaned == "Multiple spaces here"


class TestVectorStore:
    """Tests for VectorStore"""
    
    @patch('vector_store.OpenAIEmbeddings')
    @patch('vector_store.Chroma')
    def test_vector_store_initialization(self, mock_chroma, mock_embeddings):
        """Test vector store initialization"""
        store = VectorStore(store_type="chroma")
        assert store.store_type == "chroma"
    
    @patch('vector_store.OpenAIEmbeddings')
    @patch('vector_store.Chroma')
    def test_add_documents(self, mock_chroma, mock_embeddings):
        """Test adding documents to vector store"""
        store = VectorStore(store_type="chroma")
        chunks = [
            {"content": "Test content 1", "metadata": {"source": "test"}},
            {"content": "Test content 2", "metadata": {"source": "test"}}
        ]
        
        # Should not raise an exception
        store.add_documents(chunks)


class TestRAGPipeline:
    """Tests for RAGPipeline"""
    
    @patch('rag_pipeline.OpenAI')
    @patch('rag_pipeline.create_vector_store')
    @patch('rag_pipeline.create_rewriter')
    def test_pipeline_initialization(self, mock_rewriter, mock_store, mock_openai):
        """Test RAG pipeline initialization"""
        pipeline = RAGPipeline(enable_rewrite=True)
        assert pipeline.enable_rewrite is True
    
    @patch('rag_pipeline.OpenAI')
    @patch('rag_pipeline.create_vector_store')
    @patch('rag_pipeline.create_rewriter')
    def test_pipeline_without_rewrite(self, mock_rewriter, mock_store, mock_openai):
        """Test RAG pipeline with rewriting disabled"""
        pipeline = RAGPipeline(enable_rewrite=False)
        assert pipeline.query_rewriter is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
