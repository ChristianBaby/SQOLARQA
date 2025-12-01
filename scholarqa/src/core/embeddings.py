"""
Motor de embeddings optimizado usando Sentence Transformers
"""

from sentence_transformers import SentenceTransformer
from typing import List, Optional, Union
import logging
import numpy as np
from pathlib import Path
import torch

logger = logging.getLogger(__name__)


class EmbeddingEngine:
    """Genera embeddings de texto usando modelos locales con optimizaciones"""
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
                 device: Optional[str] = None,
                 batch_size: int = 32,
                 normalize_embeddings: bool = True):
        """
        Inicializa el motor de embeddings
        
        Args:
            model_name: Nombre del modelo de Sentence Transformers
            device: Dispositivo ('cuda', 'cpu', o None para auto-detección)
            batch_size: Tamaño de batch para procesamiento
            normalize_embeddings: Normalizar embeddings a norma unitaria
        """
        logger.info(f"Cargando modelo de embeddings: {model_name}")
        
        # Auto-detectar dispositivo si no se especifica
        if device is None:
            device = 'cuda' if torch.cuda.is_available() else 'cpu'
        
        self.device = device
        self.batch_size = batch_size
        self.normalize_embeddings = normalize_embeddings
        
        # Cargar modelo
        self.model = SentenceTransformer(model_name, device=device)
        self.dimension = self.model.get_sentence_embedding_dimension()
        self.model_name = model_name
        
        logger.info(f"Modelo cargado en '{device}' (dimensión: {self.dimension})")
        
        # Estadísticas
        self._total_encoded = 0
    
    def encode(self, texts: List[str], 
               batch_size: Optional[int] = None,
               show_progress: bool = False,
               convert_to_numpy: bool = True) -> Union[np.ndarray, torch.Tensor]:
        """
        Genera embeddings para una lista de textos con optimizaciones
        
        Args:
            texts: Lista de textos
            batch_size: Tamaño de batch (usa default si es None)
            show_progress: Mostrar barra de progreso
            convert_to_numpy: Convertir resultado a numpy array
            
        Returns:
            Array numpy o tensor con los embeddings
        """
        if not texts:
            return np.array([]) if convert_to_numpy else torch.tensor([])
        
        batch_size = batch_size or self.batch_size
        
        logger.debug(f"Generando embeddings para {len(texts)} textos (batch_size={batch_size})")
        
        try:
            embeddings = self.model.encode(
                texts,
                batch_size=batch_size,
                show_progress_bar=show_progress,
                convert_to_numpy=convert_to_numpy,
                normalize_embeddings=self.normalize_embeddings
            )
            
            self._total_encoded += len(texts)
            
            return embeddings
            
        except Exception as e:
            logger.error(f"Error generando embeddings: {e}", exc_info=True)
            raise
    
    def encode_single(self, text: str, convert_to_numpy: bool = True) -> Union[np.ndarray, torch.Tensor]:
        """
        Genera embedding para un solo texto
        
        Args:
            text: Texto individual
            convert_to_numpy: Convertir resultado a numpy array
            
        Returns:
            Array numpy o tensor con el embedding
        """
        return self.encode([text], convert_to_numpy=convert_to_numpy)[0]
    
    def encode_batch_streaming(self, texts: List[str], 
                               chunk_size: int = 100) -> np.ndarray:
        """
        Genera embeddings en streaming para listas muy grandes
        
        Args:
            texts: Lista de textos
            chunk_size: Tamaño de cada chunk a procesar
            
        Returns:
            Array numpy con todos los embeddings
        """
        if not texts:
            return np.array([])
        
        logger.info(f"Generando embeddings en streaming para {len(texts)} textos")
        
        all_embeddings = []
        
        for i in range(0, len(texts), chunk_size):
            chunk = texts[i:i + chunk_size]
            chunk_embeddings = self.encode(chunk, show_progress=False)
            all_embeddings.append(chunk_embeddings)
            
            logger.debug(f"Procesado chunk {i//chunk_size + 1}/{(len(texts)-1)//chunk_size + 1}")
        
        return np.vstack(all_embeddings)
    
    def similarity(self, text1: str, text2: str) -> float:
        """
        Calcula similitud coseno entre dos textos
        
        Args:
            text1: Primer texto
            text2: Segundo texto
            
        Returns:
            Similitud coseno (0 a 1)
        """
        emb1 = self.encode_single(text1)
        emb2 = self.encode_single(text2)
        
        # Similitud coseno
        similarity = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
        
        return float(similarity)
    
    def find_most_similar(self, query: str, candidates: List[str], 
                         top_k: int = 5) -> List[tuple]:
        """
        Encuentra los textos más similares a una consulta
        
        Args:
            query: Texto de consulta
            candidates: Lista de textos candidatos
            top_k: Número de resultados a retornar
            
        Returns:
            Lista de tuplas (índice, texto, similitud)
        """
        if not candidates:
            return []
        
        # Generar embeddings
        query_emb = self.encode_single(query)
        candidate_embs = self.encode(candidates)
        
        # Calcular similitudes
        similarities = np.dot(candidate_embs, query_emb)
        
        # Obtener top-k
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = [
            (int(idx), candidates[idx], float(similarities[idx]))
            for idx in top_indices
        ]
        
        return results
    
    def get_stats(self) -> dict:
        """
        Obtiene estadísticas del motor de embeddings
        
        Returns:
            Diccionario con estadísticas
        """
        return {
            'model_name': self.model_name,
            'dimension': self.dimension,
            'device': self.device,
            'batch_size': self.batch_size,
            'normalize_embeddings': self.normalize_embeddings,
            'total_encoded': self._total_encoded
        }
    
    def warm_up(self):
        """
        Precalienta el modelo con una inferencia de prueba
        """
        logger.info("Precalentando modelo de embeddings...")
        dummy_text = "This is a warm-up text for the embedding model."
        _ = self.encode_single(dummy_text)
        logger.info("Modelo precalentado")
    
    def __repr__(self) -> str:
        return (f"EmbeddingEngine(model='{self.model_name}', "
                f"dimension={self.dimension}, device='{self.device}')")
