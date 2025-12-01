"""
Gestión de base de datos vectorial optimizada usando ChromaDB
"""

import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional, Any
import logging
from pathlib import Path
import time

logger = logging.getLogger(__name__)


class VectorStore:
    """Gestiona almacenamiento y búsqueda en ChromaDB con optimizaciones"""
    
    def __init__(self, persist_directory: str, collection_name: str = "academic_papers"):
        """
        Inicializa la conexión con ChromaDB
        
        Args:
            persist_directory: Directorio para persistir datos
            collection_name: Nombre de la colección
        """
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Inicializando ChromaDB en {persist_directory}")
        
        # Configurar cliente con settings optimizados
        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        self.collection_name = collection_name
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "Academic papers collection"}
        )
        
        # Estadísticas
        self._query_count = 0
        self._add_count = 0
        
        logger.info(f"Colección '{collection_name}' lista con {self.get_collection_count()} documentos")
    
    def add_documents(self, texts: List[str], metadatas: List[Dict], 
                     ids: Optional[List[str]] = None,
                     batch_size: int = 100):
        """
        Añade documentos a la colección con procesamiento por lotes
        
        Args:
            texts: Lista de textos
            metadatas: Lista de metadatos
            ids: Lista de IDs (opcional)
            batch_size: Tamaño de batch para inserción
        """
        if not texts:
            logger.warning("No hay textos para añadir")
            return
        
        if ids is None:
            timestamp = int(time.time() * 1000)
            ids = [f"doc_{timestamp}_{i}" for i in range(len(texts))]
        
        if len(texts) != len(metadatas) or len(texts) != len(ids):
            raise ValueError("Las listas texts, metadatas e ids deben tener la misma longitud")
        
        logger.info(f"Añadiendo {len(texts)} documentos a la colección")
        
        # Procesar por lotes para mejor rendimiento
        total_batches = (len(texts) + batch_size - 1) // batch_size
        
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i + batch_size]
            batch_metadatas = metadatas[i:i + batch_size]
            batch_ids = ids[i:i + batch_size]
            
            try:
                self.collection.add(
                    documents=batch_texts,
                    metadatas=batch_metadatas,
                    ids=batch_ids
                )
                
                batch_num = i // batch_size + 1
                logger.debug(f"Batch {batch_num}/{total_batches} añadido")
                
            except Exception as e:
                logger.error(f"Error añadiendo batch {i//batch_size + 1}: {e}")
                raise
        
        self._add_count += len(texts)
        logger.info(f"✓ {len(texts)} documentos añadidos exitosamente")
    
    def query(self, query_text: str, n_results: int = 5, 
              where: Optional[Dict] = None,
              where_document: Optional[Dict] = None) -> Dict:
        """
        Busca documentos similares con filtros opcionales
        
        Args:
            query_text: Texto de consulta
            n_results: Número de resultados a retornar
            where: Filtros de metadatos
            where_document: Filtros de documento
            
        Returns:
            Diccionario con resultados
        """
        logger.debug(f"Buscando: '{query_text[:50]}...' (n_results={n_results})")
        
        try:
            # Asegurar que n_results no exceda el número de documentos
            collection_count = self.get_collection_count()
            n_results = min(n_results, collection_count) if collection_count > 0 else n_results
            
            results = self.collection.query(
                query_texts=[query_text],
                n_results=n_results,
                where=where,
                where_document=where_document
            )
            
            self._query_count += 1
            
            num_results = len(results['documents'][0]) if results['documents'] else 0
            logger.debug(f"Encontrados {num_results} resultados")
            
            return results
            
        except Exception as e:
            logger.error(f"Error en query: {e}", exc_info=True)
            raise
    
    def query_with_scores(self, query_text: str, n_results: int = 5) -> List[Dict]:
        """
        Busca documentos y retorna resultados con scores de relevancia
        
        Args:
            query_text: Texto de consulta
            n_results: Número de resultados
            
        Returns:
            Lista de diccionarios con documento, metadata, distancia y score
        """
        results = self.query(query_text, n_results)
        
        formatted_results = []
        
        if results['documents'] and results['documents'][0]:
            for i in range(len(results['documents'][0])):
                formatted_results.append({
                    'document': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                    'id': results['ids'][0][i] if results['ids'] else None,
                    'distance': results['distances'][0][i] if 'distances' in results else None,
                    'relevance_score': 1.0 / (1.0 + results['distances'][0][i]) if 'distances' in results else None
                })
        
        return formatted_results
    
    def update_document(self, doc_id: str, text: Optional[str] = None, 
                       metadata: Optional[Dict] = None):
        """
        Actualiza un documento existente
        
        Args:
            doc_id: ID del documento
            text: Nuevo texto (opcional)
            metadata: Nuevos metadatos (opcional)
        """
        try:
            update_kwargs = {'ids': [doc_id]}
            
            if text is not None:
                update_kwargs['documents'] = [text]
            
            if metadata is not None:
                update_kwargs['metadatas'] = [metadata]
            
            self.collection.update(**update_kwargs)
            logger.info(f"Documento {doc_id} actualizado")
            
        except Exception as e:
            logger.error(f"Error actualizando documento {doc_id}: {e}")
            raise
    
    def delete_documents(self, ids: List[str]):
        """
        Elimina documentos por IDs
        
        Args:
            ids: Lista de IDs a eliminar
        """
        try:
            self.collection.delete(ids=ids)
            logger.info(f"Eliminados {len(ids)} documentos")
        except Exception as e:
            logger.error(f"Error eliminando documentos: {e}")
            raise
    
    def delete_by_metadata(self, where: Dict):
        """
        Elimina documentos por filtro de metadatos
        
        Args:
            where: Filtro de metadatos
        """
        try:
            self.collection.delete(where=where)
            logger.info(f"Eliminados documentos con filtro: {where}")
        except Exception as e:
            logger.error(f"Error eliminando documentos por metadata: {e}")
            raise
    
    def get_document(self, doc_id: str) -> Optional[Dict]:
        """
        Obtiene un documento por ID
        
        Args:
            doc_id: ID del documento
            
        Returns:
            Diccionario con documento y metadata, o None
        """
        try:
            results = self.collection.get(ids=[doc_id])
            
            if results['documents']:
                return {
                    'id': doc_id,
                    'document': results['documents'][0],
                    'metadata': results['metadatas'][0] if results['metadatas'] else {}
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error obteniendo documento {doc_id}: {e}")
            return None
    
    def list_documents(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """
        Lista documentos de la colección
        
        Args:
            limit: Número máximo de documentos a retornar
            offset: Offset para paginación
            
        Returns:
            Lista de documentos
        """
        try:
            results = self.collection.get(
                limit=limit,
                offset=offset
            )
            
            documents = []
            if results['documents']:
                for i in range(len(results['documents'])):
                    documents.append({
                        'id': results['ids'][i],
                        'document': results['documents'][i],
                        'metadata': results['metadatas'][i] if results['metadatas'] else {}
                    })
            
            return documents
            
        except Exception as e:
            logger.error(f"Error listando documentos: {e}")
            return []
    
    def delete_collection(self):
        """Elimina la colección actual"""
        logger.warning(f"Eliminando colección '{self.collection_name}'")
        try:
            self.client.delete_collection(name=self.collection_name)
            logger.info(f"Colección '{self.collection_name}' eliminada")
        except Exception as e:
            logger.error(f"Error eliminando colección: {e}")
            raise
    
    def reset_collection(self):
        """Resetea la colección (elimina y recrea)"""
        logger.warning(f"Reseteando colección '{self.collection_name}'")
        self.delete_collection()
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"description": "Academic papers collection"}
        )
        self._query_count = 0
        self._add_count = 0
        logger.info("Colección reseteada")
    
    def get_collection_count(self) -> int:
        """Retorna el número de documentos en la colección"""
        try:
            return self.collection.count()
        except Exception as e:
            logger.error(f"Error obteniendo conteo: {e}")
            return 0
    
    def get_stats(self) -> Dict:
        """
        Obtiene estadísticas de la colección
        
        Returns:
            Diccionario con estadísticas
        """
        return {
            'collection_name': self.collection_name,
            'document_count': self.get_collection_count(),
            'total_queries': self._query_count,
            'total_adds': self._add_count,
            'persist_directory': str(self.persist_directory)
        }
    
    def peek(self, limit: int = 10) -> Dict:
        """
        Muestra una vista previa de documentos
        
        Args:
            limit: Número de documentos a mostrar
            
        Returns:
            Resultados de peek
        """
        try:
            return self.collection.peek(limit=limit)
        except Exception as e:
            logger.error(f"Error en peek: {e}")
            return {'documents': [], 'metadatas': [], 'ids': []}
    
    def __repr__(self) -> str:
        return (f"VectorStore(collection='{self.collection_name}', "
                f"documents={self.get_collection_count()}, "
                f"path='{self.persist_directory}')")
