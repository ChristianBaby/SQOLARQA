"""
Tests para las optimizaciones realizadas
"""

import pytest
from pathlib import Path
import sys
import tempfile
import shutil

# Añadir src al path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from core.text_splitter import SemanticTextSplitter, RecursiveTextSplitter
from core.cache_manager import CacheManager, EmbeddingCache
from core.pdf_processor import PDFProcessor
from core.embeddings import EmbeddingEngine
from core.vector_store import VectorStore


class TestSemanticTextSplitter:
    """Tests para el divisor de texto semántico"""
    
    def test_split_by_paragraphs(self):
        """Test división por párrafos"""
        text = "Párrafo uno.\n\nPárrafo dos.\n\nPárrafo tres."
        splitter = SemanticTextSplitter(chunk_size=50, chunk_overlap=10)
        chunks = splitter.split_text(text)
        
        assert len(chunks) > 0
        assert all(len(chunk) <= 70 for chunk in chunks)  # 50 + overlap
    
    def test_split_long_text(self):
        """Test división de texto largo"""
        text = "a" * 5000
        splitter = SemanticTextSplitter(chunk_size=1000, chunk_overlap=100)
        chunks = splitter.split_text(text)
        
        assert len(chunks) > 1
        assert all(len(chunk) <= 1100 for chunk in chunks)
    
    def test_empty_text(self):
        """Test con texto vacío"""
        splitter = SemanticTextSplitter()
        chunks = splitter.split_text("")
        
        assert len(chunks) == 0


class TestRecursiveTextSplitter:
    """Tests para el divisor recursivo"""
    
    def test_recursive_split(self):
        """Test división recursiva"""
        text = "Line 1\nLine 2\nLine 3\nLine 4\nLine 5"
        splitter = RecursiveTextSplitter(chunk_size=20, chunk_overlap=5)
        chunks = splitter.split_text(text)
        
        assert len(chunks) > 0
    
    def test_split_with_overlap(self):
        """Test que el overlap funciona correctamente"""
        text = "0123456789" * 10
        splitter = RecursiveTextSplitter(chunk_size=30, chunk_overlap=5)
        chunks = splitter.split_text(text)
        
        assert len(chunks) > 1


class TestCacheManager:
    """Tests para el gestor de caché"""
    
    def setup_method(self):
        """Setup para cada test"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.cache = CacheManager(cache_dir=self.temp_dir, ttl=60)
    
    def teardown_method(self):
        """Cleanup después de cada test"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_cache_set_get(self):
        """Test guardar y recuperar de caché"""
        key = self.cache._generate_key("test", "data")
        value = {"data": "test_value"}
        
        self.cache.set(key, value)
        cached = self.cache.get(key)
        
        assert cached == value
    
    def test_cache_miss(self):
        """Test cache miss"""
        result = self.cache.get("nonexistent_key")
        assert result is None
    
    def test_cache_clear(self):
        """Test limpiar caché"""
        key = self.cache._generate_key("test")
        self.cache.set(key, "value")
        
        self.cache.clear()
        result = self.cache.get(key)
        
        assert result is None
    
    def test_cache_stats(self):
        """Test estadísticas de caché"""
        self.cache.set("key1", "value1")
        self.cache.set("key2", "value2")
        
        stats = self.cache.get_stats()
        
        assert stats['memory_items'] == 2


class TestEmbeddingCache:
    """Tests para caché de embeddings"""
    
    def setup_method(self):
        """Setup para cada test"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.emb_cache = EmbeddingCache(cache_dir=self.temp_dir)
    
    def teardown_method(self):
        """Cleanup después de cada test"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_embedding_cache(self):
        """Test caché de embeddings"""
        text = "Test embedding text"
        embedding = [0.1, 0.2, 0.3, 0.4, 0.5]
        
        self.emb_cache.set_embedding(text, embedding)
        cached = self.emb_cache.get_embedding(text)
        
        assert cached == embedding


class TestOptimizedPDFProcessor:
    """Tests para el procesador de PDF optimizado"""
    
    def setup_method(self):
        """Setup para cada test"""
        self.processor = PDFProcessor(max_workers=2)
    
    def test_validate_pdf_nonexistent(self):
        """Test validación de PDF inexistente"""
        result = self.processor.validate_pdf("nonexistent.pdf")
        
        assert result['valid'] is False
        assert len(result['errors']) > 0
    
    def test_validate_pdf_wrong_extension(self):
        """Test validación de extensión incorrecta"""
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            temp_file = Path(f.name)
        
        try:
            result = self.processor.validate_pdf(str(temp_file))
            assert result['valid'] is False
        finally:
            temp_file.unlink()
    
    def test_clear_cache(self):
        """Test limpiar caché de páginas"""
        self.processor.clear_cache()
        assert len(self.processor._page_cache) == 0


class TestOptimizedEmbeddingEngine:
    """Tests para el motor de embeddings optimizado"""
    
    def setup_method(self):
        """Setup para cada test"""
        self.engine = EmbeddingEngine(
            "sentence-transformers/all-MiniLM-L6-v2",
            batch_size=16
        )
    
    def test_similarity(self):
        """Test cálculo de similitud"""
        text1 = "Machine learning is great"
        text2 = "I love machine learning"
        
        similarity = self.engine.similarity(text1, text2)
        
        assert 0 <= similarity <= 1
        assert similarity > 0.5  # Textos similares
    
    def test_find_most_similar(self):
        """Test búsqueda de textos similares"""
        query = "artificial intelligence"
        candidates = [
            "AI and machine learning",
            "Cooking recipes",
            "Neural networks"
        ]
        
        results = self.engine.find_most_similar(query, candidates, top_k=2)
        
        assert len(results) == 2
        assert results[0][2] > results[1][2]  # Primer resultado más similar
    
    def test_get_stats(self):
        """Test obtener estadísticas"""
        self.engine.encode_single("Test text")
        
        stats = self.engine.get_stats()
        
        assert stats['total_encoded'] >= 1
        assert stats['dimension'] > 0


class TestOptimizedVectorStore:
    """Tests para el vector store optimizado"""
    
    def setup_method(self):
        """Setup para cada test"""
        self.temp_dir = tempfile.mkdtemp()
        self.vector_store = VectorStore(
            self.temp_dir,
            collection_name="test_optimized"
        )
    
    def teardown_method(self):
        """Cleanup después de cada test"""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    def test_add_documents_batch(self):
        """Test añadir documentos por lotes"""
        texts = [f"Document {i}" for i in range(150)]
        metadatas = [{"id": i} for i in range(150)]
        
        self.vector_store.add_documents(texts, metadatas, batch_size=50)
        
        assert self.vector_store.get_collection_count() == 150
    
    def test_query_with_scores(self):
        """Test query con scores de relevancia"""
        texts = ["Machine learning", "Python programming", "Data science"]
        metadatas = [{"topic": t} for t in texts]
        
        self.vector_store.add_documents(texts, metadatas)
        
        results = self.vector_store.query_with_scores("machine learning", n_results=2)
        
        assert len(results) > 0
        assert 'relevance_score' in results[0]
    
    def test_update_document(self):
        """Test actualizar documento"""
        texts = ["Original text"]
        metadatas = [{"version": 1}]
        ids = ["doc1"]
        
        self.vector_store.add_documents(texts, metadatas, ids)
        
        # Actualizar
        self.vector_store.update_document("doc1", metadata={"version": 2})
        
        doc = self.vector_store.get_document("doc1")
        assert doc['metadata']['version'] == 2
    
    def test_delete_documents(self):
        """Test eliminar documentos"""
        texts = ["Doc 1", "Doc 2", "Doc 3"]
        metadatas = [{"id": i} for i in range(3)]
        ids = ["doc1", "doc2", "doc3"]
        
        self.vector_store.add_documents(texts, metadatas, ids)
        
        self.vector_store.delete_documents(["doc2"])
        
        assert self.vector_store.get_collection_count() == 2
    
    def test_get_stats(self):
        """Test obtener estadísticas"""
        texts = ["Doc 1", "Doc 2"]
        metadatas = [{"id": i} for i in range(2)]
        
        self.vector_store.add_documents(texts, metadatas)
        
        stats = self.vector_store.get_stats()
        
        assert stats['document_count'] == 2
        assert stats['total_adds'] == 2


class TestPerformance:
    """Tests de rendimiento"""
    
    def test_large_batch_embeddings(self):
        """Test procesamiento de lote grande de embeddings"""
        engine = EmbeddingEngine(batch_size=64)
        
        texts = [f"Text number {i}" for i in range(200)]
        
        import time
        start = time.time()
        embeddings = engine.encode(texts, show_progress=False)
        elapsed = time.time() - start
        
        assert len(embeddings) == 200
        assert elapsed < 60  # Debería completarse en menos de 60 segundos
    
    def test_chunking_performance(self):
        """Test rendimiento de chunking"""
        splitter = SemanticTextSplitter(chunk_size=1000, chunk_overlap=200)
        
        # Texto grande
        text = "Lorem ipsum. " * 10000
        
        import time
        start = time.time()
        chunks = splitter.split_text(text)
        elapsed = time.time() - start
        
        assert len(chunks) > 0
        assert elapsed < 5  # Debería ser rápido


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
