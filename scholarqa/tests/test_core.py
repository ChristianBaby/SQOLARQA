"""
Tests para los componentes core de ScholarQA
"""

import pytest
from pathlib import Path
import sys
import tempfile
import shutil

# Añadir src al path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from core.pdf_processor import PDFProcessor
from core.embeddings import EmbeddingEngine
from core.vector_store import VectorStore


class TestPDFProcessor:
    """Tests para PDFProcessor"""
    
    def setup_method(self):
        """Setup para cada test"""
        self.processor = PDFProcessor()
    
    def test_chunk_text_basic(self):
        """Test chunking básico"""
        text = "a" * 500
        chunks = self.processor.chunk_text(text, chunk_size=100, chunk_overlap=20)
        
        assert len(chunks) > 0
        assert len(chunks[0]) <= 100
    
    def test_chunk_text_overlap(self):
        """Test que el overlap funciona"""
        text = "0123456789" * 20  # 200 caracteres
        chunks = self.processor.chunk_text(text, chunk_size=50, chunk_overlap=10)
        
        assert len(chunks) > 1
        # Verificar que hay overlap
        assert chunks[0][-10:] == chunks[1][:10]
    
    def test_chunk_empty_text(self):
        """Test con texto vacío"""
        chunks = self.processor.chunk_text("", chunk_size=100)
        assert len(chunks) == 0


class TestEmbeddingEngine:
    """Tests para EmbeddingEngine"""
    
    def setup_method(self):
        """Setup para cada test"""
        # Usar un modelo pequeño para tests
        self.engine = EmbeddingEngine("sentence-transformers/all-MiniLM-L6-v2")
    
    def test_encode_single(self):
        """Test encoding de un texto"""
        text = "This is a test sentence"
        embedding = self.engine.encode_single(text)
        
        assert embedding is not None
        assert len(embedding) == self.engine.dimension
    
    def test_encode_multiple(self):
        """Test encoding de múltiples textos"""
        texts = ["First sentence", "Second sentence", "Third sentence"]
        embeddings = self.engine.encode(texts)
        
        assert embeddings is not None
        assert len(embeddings) == 3
        assert len(embeddings[0]) == self.engine.dimension
    
    def test_embeddings_are_different(self):
        """Test que textos diferentes tienen embeddings diferentes"""
        text1 = "Machine learning is great"
        text2 = "I love pizza"
        
        emb1 = self.engine.encode_single(text1)
        emb2 = self.engine.encode_single(text2)
        
        # Embeddings deben ser diferentes
        assert not (emb1 == emb2).all()


class TestVectorStore:
    """Tests para VectorStore"""
    
    def setup_method(self):
        """Setup para cada test"""
        # Crear directorio temporal
        self.temp_dir = tempfile.mkdtemp()
        self.vector_store = VectorStore(
            self.temp_dir,
            collection_name="test_collection"
        )
    
    def teardown_method(self):
        """Cleanup después de cada test"""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    def test_add_documents(self):
        """Test añadir documentos"""
        texts = ["Document 1", "Document 2", "Document 3"]
        metadatas = [{"source": "test"} for _ in texts]
        ids = ["doc1", "doc2", "doc3"]
        
        self.vector_store.add_documents(texts, metadatas, ids)
        
        count = self.vector_store.get_collection_count()
        assert count == 3
    
    def test_query_documents(self):
        """Test búsqueda de documentos"""
        texts = [
            "Machine learning is a subset of artificial intelligence",
            "Python is a programming language",
            "Neural networks are used in deep learning"
        ]
        metadatas = [{"source": f"doc{i}"} for i in range(len(texts))]
        
        self.vector_store.add_documents(texts, metadatas)
        
        # Buscar algo relacionado con ML
        results = self.vector_store.query("artificial intelligence", n_results=2)
        
        assert len(results['documents'][0]) > 0
        assert "machine learning" in results['documents'][0][0].lower()
    
    def test_empty_query(self):
        """Test query en colección vacía"""
        results = self.vector_store.query("test query", n_results=5)
        
        # Debe retornar estructura válida aunque esté vacía
        assert 'documents' in results
        assert isinstance(results['documents'][0], list)


class TestIntegration:
    """Tests de integración"""
    
    def setup_method(self):
        """Setup para tests de integración"""
        self.temp_dir = tempfile.mkdtemp()
        self.processor = PDFProcessor()
        self.embedding_engine = EmbeddingEngine("sentence-transformers/all-MiniLM-L6-v2")
        self.vector_store = VectorStore(self.temp_dir, "integration_test")
    
    def teardown_method(self):
        """Cleanup"""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    def test_full_pipeline(self):
        """Test del pipeline completo: chunk -> embed -> store -> query"""
        # Simular texto de un PDF
        text = """
        Machine learning is a method of data analysis that automates analytical model building.
        It is a branch of artificial intelligence based on the idea that systems can learn from data,
        identify patterns and make decisions with minimal human intervention.
        """
        
        # 1. Chunk
        chunks = self.processor.chunk_text(text, chunk_size=100, chunk_overlap=20)
        assert len(chunks) > 0
        
        # 2. Preparar metadatos
        metadatas = [{"source": "test_paper.pdf", "chunk_id": i} for i in range(len(chunks))]
        
        # 3. Almacenar
        self.vector_store.add_documents(chunks, metadatas)
        
        # 4. Query
        results = self.vector_store.query("What is machine learning?", n_results=2)
        
        # 5. Verificar
        assert len(results['documents'][0]) > 0
        assert "machine learning" in results['documents'][0][0].lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
