"""
Sistema de caché para optimizar rendimiento
"""

from typing import Any, Optional, Callable
import hashlib
import pickle
import time
from pathlib import Path
import logging
from functools import wraps

logger = logging.getLogger(__name__)


class CacheManager:
    """
    Gestor de caché para embeddings y resultados de LLM
    """
    
    def __init__(self, cache_dir: Optional[Path] = None, ttl: int = 3600):
        """
        Inicializa el gestor de caché
        
        Args:
            cache_dir: Directorio para caché persistente
            ttl: Time-to-live en segundos
        """
        self.cache_dir = cache_dir
        self.ttl = ttl
        self.memory_cache = {}
        
        if cache_dir:
            cache_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Caché persistente habilitada en: {cache_dir}")
    
    def _generate_key(self, *args, **kwargs) -> str:
        """
        Genera una clave única basada en argumentos
        
        Args:
            *args: Argumentos posicionales
            **kwargs: Argumentos con nombre
            
        Returns:
            Clave hash única
        """
        # Crear string representativo
        key_parts = [str(arg) for arg in args]
        key_parts.extend([f"{k}={v}" for k, v in sorted(kwargs.items())])
        key_string = "|".join(key_parts)
        
        # Generar hash
        return hashlib.sha256(key_string.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """
        Obtiene valor de caché
        
        Args:
            key: Clave de caché
            
        Returns:
            Valor cacheado o None
        """
        # Intentar caché en memoria primero
        if key in self.memory_cache:
            value, timestamp = self.memory_cache[key]
            if time.time() - timestamp < self.ttl:
                logger.debug(f"Cache hit (memory): {key[:16]}...")
                return value
            else:
                # Expiró, eliminar
                del self.memory_cache[key]
        
        # Intentar caché persistente
        if self.cache_dir:
            cache_file = self.cache_dir / f"{key}.pkl"
            if cache_file.exists():
                try:
                    with open(cache_file, 'rb') as f:
                        value, timestamp = pickle.load(f)
                    
                    if time.time() - timestamp < self.ttl:
                        logger.debug(f"Cache hit (disk): {key[:16]}...")
                        # Cargar a memoria para acceso rápido
                        self.memory_cache[key] = (value, timestamp)
                        return value
                    else:
                        # Expiró, eliminar
                        cache_file.unlink()
                except Exception as e:
                    logger.warning(f"Error leyendo caché: {e}")
        
        logger.debug(f"Cache miss: {key[:16]}...")
        return None
    
    def set(self, key: str, value: Any):
        """
        Guarda valor en caché
        
        Args:
            key: Clave de caché
            value: Valor a cachear
        """
        timestamp = time.time()
        
        # Guardar en memoria
        self.memory_cache[key] = (value, timestamp)
        
        # Guardar en disco si está habilitado
        if self.cache_dir:
            cache_file = self.cache_dir / f"{key}.pkl"
            try:
                with open(cache_file, 'wb') as f:
                    pickle.dump((value, timestamp), f)
                logger.debug(f"Cached to disk: {key[:16]}...")
            except Exception as e:
                logger.warning(f"Error guardando caché: {e}")
    
    def clear(self):
        """
        Limpia toda la caché
        """
        self.memory_cache.clear()
        
        if self.cache_dir and self.cache_dir.exists():
            for cache_file in self.cache_dir.glob("*.pkl"):
                try:
                    cache_file.unlink()
                except Exception as e:
                    logger.warning(f"Error eliminando caché: {e}")
        
        logger.info("Caché limpiada")
    
    def get_stats(self) -> dict:
        """
        Obtiene estadísticas de caché
        
        Returns:
            Diccionario con estadísticas
        """
        stats = {
            'memory_items': len(self.memory_cache),
            'disk_items': 0
        }
        
        if self.cache_dir and self.cache_dir.exists():
            stats['disk_items'] = len(list(self.cache_dir.glob("*.pkl")))
        
        return stats


def cached(cache_manager: CacheManager):
    """
    Decorador para cachear resultados de funciones
    
    Args:
        cache_manager: Instancia de CacheManager
        
    Returns:
        Decorador
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generar clave de caché
            key = cache_manager._generate_key(func.__name__, *args, **kwargs)
            
            # Intentar obtener de caché
            cached_result = cache_manager.get(key)
            if cached_result is not None:
                return cached_result
            
            # Ejecutar función
            result = func(*args, **kwargs)
            
            # Guardar en caché
            cache_manager.set(key, result)
            
            return result
        
        return wrapper
    return decorator


class EmbeddingCache:
    """
    Caché especializada para embeddings
    """
    
    def __init__(self, cache_dir: Path):
        """
        Inicializa caché de embeddings
        
        Args:
            cache_dir: Directorio para caché
        """
        self.cache_manager = CacheManager(cache_dir, ttl=86400)  # 24 horas
    
    def get_embedding(self, text: str) -> Optional[Any]:
        """
        Obtiene embedding cacheado
        
        Args:
            text: Texto del embedding
            
        Returns:
            Embedding o None
        """
        key = self.cache_manager._generate_key("embedding", text)
        return self.cache_manager.get(key)
    
    def set_embedding(self, text: str, embedding: Any):
        """
        Guarda embedding en caché
        
        Args:
            text: Texto del embedding
            embedding: Embedding a guardar
        """
        key = self.cache_manager._generate_key("embedding", text)
        self.cache_manager.set(key, embedding)
    
    def get_batch_embeddings(self, texts: list) -> Optional[list]:
        """
        Obtiene embeddings de un batch
        
        Args:
            texts: Lista de textos
            
        Returns:
            Lista de embeddings o None
        """
        # Intentar obtener todos los embeddings del caché
        embeddings = []
        for text in texts:
            emb = self.get_embedding(text)
            if emb is None:
                return None  # Si falta uno, recalcular todos
            embeddings.append(emb)
        
        return embeddings
    
    def set_batch_embeddings(self, texts: list, embeddings: list):
        """
        Guarda embeddings de un batch
        
        Args:
            texts: Lista de textos
            embeddings: Lista de embeddings
        """
        for text, embedding in zip(texts, embeddings):
            self.set_embedding(text, embedding)
