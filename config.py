"""
Configuration management for RAG Query Rewrite POC
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Literal


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # OpenAI Configuration
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4-turbo-preview", env="OPENAI_MODEL")
    openai_embedding_model: str = Field(
        default="text-embedding-3-small", 
        env="OPENAI_EMBEDDING_MODEL"
    )
    
    # Vector Store Configuration
    vector_store_type: Literal["chroma", "faiss"] = Field(
        default="chroma", 
        env="VECTOR_STORE_TYPE"
    )
    vector_store_path: str = Field(
        default="./data/vector_store", 
        env="VECTOR_STORE_PATH"
    )
    chunk_size: int = Field(default=1000, env="CHUNK_SIZE")
    chunk_overlap: int = Field(default=200, env="CHUNK_OVERLAP")
    
    # Query Rewrite Configuration
    enable_query_rewrite: bool = Field(default=True, env="ENABLE_QUERY_REWRITE")
    rewrite_strategy: Literal["expansion", "decomposition", "refinement", "hybrid"] = Field(
        default="hybrid", 
        env="REWRITE_STRATEGY"
    )
    max_rewrite_attempts: int = Field(default=3, env="MAX_REWRITE_ATTEMPTS")
    
    # RAG Configuration
    top_k_results: int = Field(default=5, env="TOP_K_RESULTS")
    temperature: float = Field(default=0.7, env="TEMPERATURE")
    max_tokens: int = Field(default=1000, env="MAX_TOKENS")
    
    # API Configuration
    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=8000, env="API_PORT")
    api_reload: bool = Field(default=True, env="API_RELOAD")
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()
