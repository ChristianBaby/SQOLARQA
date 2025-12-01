"""
Configuración mejorada del sistema ScholarQA
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional
import logging

# Cargar variables de entorno
load_dotenv()

logger = logging.getLogger(__name__)


class Config:
    """Configuración centralizada y validada de la aplicación"""
    
    # Directorios base
    BASE_DIR = Path(__file__).parent.parent.parent
    DATA_DIR = BASE_DIR / "data"
    MODELS_DIR = BASE_DIR / "models"
    LOGS_DIR = BASE_DIR / "logs"
    CACHE_DIR = DATA_DIR / "cache"
    
    # Modelos
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    LLM_MODEL = os.getenv("LLM_MODEL", "models/downloaded/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf")
    
    # ChromaDB
    CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "data/vector_store")
    COLLECTION_NAME = os.getenv("COLLECTION_NAME", "academic_papers")
    CHROMA_BATCH_SIZE = int(os.getenv("CHROMA_BATCH_SIZE", 100))
    
    # Flask
    FLASK_HOST = os.getenv("FLASK_HOST", "0.0.0.0")
    FLASK_PORT = int(os.getenv("FLASK_PORT", 5000))
    FLASK_DEBUG = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", 100))  # MB
    
    # Procesamiento de texto
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 1000))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 200))
    MAX_CHUNKS_PER_QUERY = int(os.getenv("MAX_CHUNKS_PER_QUERY", 5))
    USE_SEMANTIC_CHUNKING = os.getenv("USE_SEMANTIC_CHUNKING", "True").lower() == "true"
    
    # LLM Settings
    MAX_TOKENS = int(os.getenv("MAX_TOKENS", 512))
    TEMPERATURE = float(os.getenv("TEMPERATURE", 0.7))
    TOP_P = float(os.getenv("TOP_P", 0.95))
    N_CTX = int(os.getenv("N_CTX", 2048))
    N_GPU_LAYERS = int(os.getenv("N_GPU_LAYERS", 0))
    
    # Embeddings Settings
    EMBEDDING_BATCH_SIZE = int(os.getenv("EMBEDDING_BATCH_SIZE", 32))
    NORMALIZE_EMBEDDINGS = os.getenv("NORMALIZE_EMBEDDINGS", "True").lower() == "true"
    
    # Cache Settings
    ENABLE_CACHE = os.getenv("ENABLE_CACHE", "True").lower() == "true"
    CACHE_TTL = int(os.getenv("CACHE_TTL", 3600))  # segundos
    
    # Performance
    MAX_WORKERS = int(os.getenv("MAX_WORKERS", 4))
    USE_GPU = os.getenv("USE_GPU", "False").lower() == "true"
    
    # Sistema
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_TO_FILE = os.getenv("LOG_TO_FILE", "True").lower() == "true"
    LOG_FILE = os.getenv("LOG_FILE", "logs/scholarqa.log")
    
    @classmethod
    def get_upload_folder(cls) -> Path:
        """Retorna la carpeta de uploads"""
        folder = cls.DATA_DIR / "uploads"
        folder.mkdir(parents=True, exist_ok=True)
        return folder
    
    @classmethod
    def get_pdfs_folder(cls) -> Path:
        """Retorna la carpeta de PDFs"""
        folder = cls.DATA_DIR / "pdfs"
        folder.mkdir(parents=True, exist_ok=True)
        return folder
    
    @classmethod
    def get_vector_store_path(cls) -> Path:
        """Retorna la ruta del vector store"""
        path = cls.BASE_DIR / cls.CHROMA_PERSIST_DIR
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    @classmethod
    def get_llm_model_path(cls) -> Path:
        """Retorna la ruta completa del modelo LLM"""
        if cls.LLM_MODEL.startswith("models/"):
            return cls.BASE_DIR / cls.LLM_MODEL
        return Path(cls.LLM_MODEL)
    
    @classmethod
    def get_cache_dir(cls) -> Path:
        """Retorna el directorio de caché"""
        cls.CACHE_DIR.mkdir(parents=True, exist_ok=True)
        return cls.CACHE_DIR
    
    @classmethod
    def get_logs_dir(cls) -> Path:
        """Retorna el directorio de logs"""
        cls.LOGS_DIR.mkdir(parents=True, exist_ok=True)
        return cls.LOGS_DIR
    
    @classmethod
    def validate(cls) -> dict:
        """
        Valida la configuración
        
        Returns:
            Diccionario con resultados de validación
        """
        issues = []
        warnings = []
        
        # Validar directorios
        try:
            cls.BASE_DIR.mkdir(parents=True, exist_ok=True)
            cls.DATA_DIR.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            issues.append(f"No se pueden crear directorios base: {e}")
        
        # Validar configuración de chunks
        if cls.CHUNK_OVERLAP >= cls.CHUNK_SIZE:
            issues.append("CHUNK_OVERLAP debe ser menor que CHUNK_SIZE")
        
        if cls.CHUNK_SIZE < 100:
            warnings.append("CHUNK_SIZE muy pequeño (<100)")
        
        # Validar modelo LLM
        llm_path = cls.get_llm_model_path()
        if not llm_path.exists():
            warnings.append(f"Modelo LLM no encontrado: {llm_path}")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings
        }
    
    @classmethod
    def print_config(cls):
        """Imprime la configuración actual"""
        print("=" * 60)
        print("CONFIGURACIÓN DE SCHOLARQA")
        print("=" * 60)
        print(f"Base Directory: {cls.BASE_DIR}")
        print(f"Embedding Model: {cls.EMBEDDING_MODEL}")
        print(f"LLM Model: {cls.LLM_MODEL}")
        print(f"Chunk Size: {cls.CHUNK_SIZE}")
        print(f"Chunk Overlap: {cls.CHUNK_OVERLAP}")
        print(f"Max Chunks per Query: {cls.MAX_CHUNKS_PER_QUERY}")
        print(f"Cache Enabled: {cls.ENABLE_CACHE}")
        print(f"GPU Enabled: {cls.USE_GPU}")
        print(f"Log Level: {cls.LOG_LEVEL}")
        print("=" * 60)
