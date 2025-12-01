#!/usr/bin/env python3
"""
Ejemplo básico de uso de ScholarQA sin interfaz web
Este es un prototipo para entender cómo funciona el sistema
"""

import sys
from pathlib import Path

# Añadir src al path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from core.pdf_processor import PDFProcessor
from core.embeddings import EmbeddingEngine
from core.vector_store import VectorStore
from utils.config import Config


def main():
    """Ejemplo básico de procesamiento"""
    
    print("=" * 60)
    print("ScholarQA - Ejemplo Básico")
    print("=" * 60)
    
    # 1. Inicializar componentes
    print("\n1️⃣  Inicializando componentes...")
    processor = PDFProcessor()
    embedding_engine = EmbeddingEngine("sentence-transformers/all-MiniLM-L6-v2")
    vector_store = VectorStore("temp_vector_store", "test_collection")
    
    print("   ✓ Componentes inicializados")
    
    # 2. Simular procesamiento de texto (sin PDF real)
    print("\n2️⃣  Procesando texto de ejemplo...")
    
    sample_text = """
    Machine learning is a subset of artificial intelligence that focuses on the 
    development of algorithms and statistical models that enable computers to 
    perform tasks without explicit instructions. Deep learning, a subset of 
    machine learning, uses neural networks with multiple layers to progressively 
    extract higher-level features from raw input.
    
    Natural language processing (NLP) is another important area of AI that deals 
    with the interaction between computers and human language. It enables 
    computers to understand, interpret, and generate human language in a 
    valuable way.
    """
    
    # 3. Crear chunks
    chunks = processor.chunk_text(sample_text, chunk_size=200, chunk_overlap=50)
    print(f"   ✓ Texto dividido en {len(chunks)} chunks")
    
    # 4. Añadir a vector store
    print("\n3️⃣  Almacenando en base de datos vectorial...")
    metadatas = [
        {"source": "example.txt", "chunk_id": i} 
        for i in range(len(chunks))
    ]
    vector_store.add_documents(chunks, metadatas)
    print(f"   ✓ {len(chunks)} documentos almacenados")
    
    # 5. Hacer queries de prueba
    print("\n4️⃣  Probando búsqueda semántica...")
    
    queries = [
        "What is machine learning?",
        "Tell me about neural networks",
        "How does NLP work?"
    ]
    
    for query in queries:
        print(f"\n   🔍 Query: {query}")
        results = vector_store.query(query, n_results=2)
        
        if results['documents'][0]:
            best_match = results['documents'][0][0]
            print(f"   📝 Mejor resultado: {best_match[:100]}...")
        else:
            print("   ❌ No se encontraron resultados")
    
    # 6. Estadísticas
    print("\n5️⃣  Estadísticas:")
    print(f"   📊 Total documentos: {vector_store.get_collection_count()}")
    print(f"   📏 Dimensión embeddings: {embedding_engine.dimension}")
    
    # 7. Limpiar
    print("\n6️⃣  Limpiando recursos temporales...")
    vector_store.delete_collection()
    
    import shutil
    if Path("temp_vector_store").exists():
        shutil.rmtree("temp_vector_store")
    
    print("   ✓ Limpieza completada")
    
    print("\n" + "=" * 60)
    print("✅ Ejemplo completado exitosamente!")
    print("=" * 60)
    print("\n💡 Ahora prueba:")
    print("   - python src/app.py (interfaz web)")
    print("   - python src/cli.py upload <pdf> (procesar PDF real)")
    print()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Asegúrate de haber ejecutado:")
        print("   pip install -r requirements.txt")
        sys.exit(1)
