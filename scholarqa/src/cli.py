#!/usr/bin/env python3
"""
ScholarQA - Command Line Interface Optimizado
"""

import sys
import argparse
from pathlib import Path

# Añadir src al path
sys.path.insert(0, str(Path(__file__).parent))

from core.pdf_processor import PDFProcessor
from core.embeddings import EmbeddingEngine
from core.vector_store import VectorStore
from core.llm_engine import LLMEngine
from core.text_splitter import SemanticTextSplitter
from utils.config import Config
from utils.logger import setup_logging
from utils.performance import Timer

# Configurar logging
logger = setup_logging(Config.LOG_LEVEL)


def init_components():
    """Inicializa componentes necesarios con optimizaciones"""
    logger.info("Inicializando componentes...")
    
    with Timer("Inicialización"):
        pdf_processor = PDFProcessor(max_workers=Config.MAX_WORKERS)
        
        embedding_engine = EmbeddingEngine(
            Config.EMBEDDING_MODEL,
            batch_size=Config.EMBEDDING_BATCH_SIZE,
            normalize_embeddings=Config.NORMALIZE_EMBEDDINGS
        )
        
        vector_store = VectorStore(
            str(Config.get_vector_store_path()),
            Config.COLLECTION_NAME
        )
        
        try:
            llm_engine = LLMEngine(
                str(Config.get_llm_model_path()),
                n_ctx=Config.N_CTX,
                n_gpu_layers=Config.N_GPU_LAYERS
            )
        except FileNotFoundError as e:
            logger.warning(f"Modelo LLM no disponible: {e}")
            llm_engine = None
    
    return pdf_processor, embedding_engine, vector_store, llm_engine


def upload_command(args):
    """Procesa y sube un PDF con optimizaciones"""
    pdf_processor, _, vector_store, _ = init_components()
    
    pdf_path = Path(args.pdf_path)
    if not pdf_path.exists():
        print(f"❌ Archivo no encontrado: {pdf_path}")
        return
    
    # Validar PDF
    print(f"🔍 Validando: {pdf_path.name}")
    validation = pdf_processor.validate_pdf(str(pdf_path))
    
    if not validation['valid']:
        print(f"❌ PDF no válido:")
        for error in validation['errors']:
            print(f"  - {error}")
        return
    
    if validation['warnings']:
        for warning in validation['warnings']:
            print(f"⚠️  {warning}")
    
    print(f"📄 Procesando: {pdf_path.name}")
    
    with Timer("Extracción de texto"):
        # Extraer texto
        text = pdf_processor.extract_text(pdf_path)
        metadata = pdf_processor.extract_metadata(pdf_path)
    
    print(f"📊 Metadatos: {metadata.get('num_pages', 0)} páginas, {len(text)} caracteres")
    
    with Timer("Chunking"):
        # Crear chunks (usar chunking semántico si está habilitado)
        if Config.USE_SEMANTIC_CHUNKING:
            from core.text_splitter import SemanticTextSplitter
            splitter = SemanticTextSplitter(Config.CHUNK_SIZE, Config.CHUNK_OVERLAP)
            chunks = splitter.split_text(text)
        else:
            chunks = pdf_processor.chunk_text(text, Config.CHUNK_SIZE, Config.CHUNK_OVERLAP)
    
    print(f"📦 Dividido en {len(chunks)} chunks")
    
    # Preparar metadatos
    metadatas = [
        {
            'source': pdf_path.name,
            'chunk_id': i,
            'title': metadata.get('title', pdf_path.name),
            'num_pages': metadata.get('num_pages', 0)
        }
        for i in range(len(chunks))
    ]
    
    ids = [f"{pdf_path.name}_chunk_{i}" for i in range(len(chunks))]
    
    # Añadir a vector store con batches
    with Timer("Almacenamiento"):
        vector_store.add_documents(
            chunks, 
            metadatas, 
            ids,
            batch_size=Config.CHROMA_BATCH_SIZE
        )
    
    print(f"✅ Procesado exitosamente")
    print(f"📊 Total en base de datos: {vector_store.get_collection_count()} chunks")


def ask_command(args):
    """Hace una pregunta sobre los documentos con optimizaciones"""
    _, _, vector_store, llm_engine = init_components()
    
    if llm_engine is None:
        print("❌ Modelo LLM no disponible")
        return
    
    question = args.question
    print(f"\n❓ Pregunta: {question}\n")
    
    # Buscar contexto con timing
    with Timer("Búsqueda vectorial"):
        results = vector_store.query(question, n_results=Config.MAX_CHUNKS_PER_QUERY)
    
    if not results['documents'][0]:
        print("❌ No hay documentos en la base de datos")
        return
    
    print(f"🔍 Encontrados {len(results['documents'][0])} chunks relevantes\n")
    
    # Generar respuesta
    context_chunks = results['documents'][0]
    
    print("🤖 Generando respuesta...")
    with Timer("Generación LLM"):
        response = llm_engine.answer_question(
            question, 
            context_chunks,
            max_tokens=Config.MAX_TOKENS,
            temperature=Config.TEMPERATURE
        )
    
    print(f"\n💡 Respuesta:\n{response['answer']}\n")
    
    # Mostrar fuentes y estadísticas
    sources = set(m['source'] for m in results['metadatas'][0])
    print(f"📚 Fuentes: {', '.join(sources)}")
    print(f"📊 Contexto usado: {response['context_used']} chunks")
    print(f"⏱️  Tiempo de generación: {response.get('generation_time', 0):.2f}s")


def list_command(args):
    """Lista información de la base de datos con estadísticas"""
    _, _, vector_store, _ = init_components()
    
    stats = vector_store.get_stats()
    
    print("\n" + "=" * 60)
    print("📊 ESTADÍSTICAS DE LA BASE DE DATOS")
    print("=" * 60)
    print(f"Colección: {stats['collection_name']}")
    print(f"Total de chunks: {stats['document_count']}")
    print(f"Total de queries: {stats['total_queries']}")
    print(f"Total de inserciones: {stats['total_adds']}")
    print(f"Directorio: {stats['persist_directory']}")
    print("=" * 60 + "\n")
    
    # Mostrar preview de documentos
    if args.verbose and stats['document_count'] > 0:
        print("📄 Vista previa de documentos:")
        preview = vector_store.peek(limit=5)
        for i, (doc, meta) in enumerate(zip(preview['documents'], preview['metadatas'])):
            print(f"\n{i+1}. {meta.get('source', 'Unknown')}")
            print(f"   {doc[:100]}...")


def clear_command(args):
    """Limpia la base de datos"""
    _, _, vector_store, _ = init_components()
    
    if not args.yes:
        response = input("⚠️  ¿Estás seguro de eliminar toda la base de datos? (si/no): ")
        if response.lower() not in ['si', 'sí', 'yes', 'y']:
            print("Operación cancelada")
            return
    
    vector_store.delete_collection()
    print("✅ Base de datos eliminada")


def stats_command(args):
    """Muestra estadísticas de rendimiento"""
    pdf_processor, embedding_engine, vector_store, llm_engine = init_components()
    
    print("\n" + "=" * 70)
    print("📊 ESTADÍSTICAS DEL SISTEMA")
    print("=" * 70)
    
    # Estadísticas de embeddings
    emb_stats = embedding_engine.get_stats()
    print("\n🧮 Motor de Embeddings:")
    print(f"  Modelo: {emb_stats['model_name']}")
    print(f"  Dimensión: {emb_stats['dimension']}")
    print(f"  Dispositivo: {emb_stats['device']}")
    print(f"  Batch size: {emb_stats['batch_size']}")
    print(f"  Total codificado: {emb_stats['total_encoded']} textos")
    
    # Estadísticas de vector store
    vs_stats = vector_store.get_stats()
    print("\n💾 Vector Store:")
    print(f"  Colección: {vs_stats['collection_name']}")
    print(f"  Documentos: {vs_stats['document_count']}")
    print(f"  Queries realizadas: {vs_stats['total_queries']}")
    print(f"  Inserciones: {vs_stats['total_adds']}")
    
    # Estadísticas de LLM
    if llm_engine:
        llm_stats = llm_engine.get_stats()
        print("\n🤖 Motor LLM:")
        print(f"  Modelo: {llm_stats['model_path']}")
        print(f"  Tamaño de contexto: {llm_stats['context_size']}")
        print(f"  Tokens generados: {llm_stats['total_tokens_generated']}")
        print(f"  Requests: {llm_stats['total_requests']}")
    
    # Uso de memoria
    from utils.performance import PerformanceMonitor
    mem_stats = PerformanceMonitor.get_memory_usage()
    sys_stats = PerformanceMonitor.get_system_info()
    
    print("\n💻 Sistema:")
    print(f"  CPUs: {sys_stats['cpu_count']}")
    print(f"  Uso CPU: {sys_stats['cpu_percent']:.1f}%")
    print(f"  Memoria total: {sys_stats['memory_total_gb']:.2f} GB")
    print(f"  Memoria disponible: {sys_stats['memory_available_gb']:.2f} GB")
    print(f"  Memoria del proceso: {mem_stats['rss_mb']:.2f} MB")
    
    print("\n" + "=" * 70 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="ScholarQA - Chat con PDFs Académicos (Optimizado)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  %(prog)s upload paper.pdf              # Subir un PDF
  %(prog)s ask "¿Qué es machine learning?"  # Hacer pregunta
  %(prog)s list -v                       # Listar con detalles
  %(prog)s stats                         # Ver estadísticas
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Comandos disponibles')
    
    # Upload command
    upload_parser = subparsers.add_parser('upload', help='Subir y procesar un PDF')
    upload_parser.add_argument('pdf_path', help='Ruta al archivo PDF')
    
    # Ask command
    ask_parser = subparsers.add_parser('ask', help='Hacer una pregunta')
    ask_parser.add_argument('question', help='Pregunta sobre los documentos')
    
    # List command
    list_parser = subparsers.add_parser('list', help='Listar información de la base de datos')
    list_parser.add_argument('-v', '--verbose', action='store_true', help='Mostrar detalles')
    
    # Clear command
    clear_parser = subparsers.add_parser('clear', help='Limpiar base de datos')
    clear_parser.add_argument('-y', '--yes', action='store_true', help='No pedir confirmación')
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Mostrar estadísticas del sistema')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == 'upload':
            upload_command(args)
        elif args.command == 'ask':
            ask_command(args)
        elif args.command == 'list':
            list_command(args)
        elif args.command == 'clear':
            clear_command(args)
        elif args.command == 'stats':
            stats_command(args)
    except KeyboardInterrupt:
        print("\n\n⏸️  Operación cancelada por el usuario")
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        print(f"\n❌ Error: {e}")


if __name__ == '__main__':
    main()
