#!/usr/bin/env python3
"""
Script de verificación de optimizaciones de ScholarQA
"""

import sys
from pathlib import Path
import time

# Añadir src al path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from utils.config import Config
from utils.logger import setup_logging

logger = setup_logging("INFO")


def print_section(title):
    """Imprime una sección"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def check_dependencies():
    """Verifica dependencias instaladas"""
    print_section("1. Verificando Dependencias")
    
    dependencies = {
        'pypdf': 'Procesamiento de PDFs',
        'sentence_transformers': 'Embeddings',
        'chromadb': 'Base de datos vectorial',
        'llama_cpp': 'Motor LLM',
        'flask': 'Servidor web',
        'torch': 'PyTorch',
        'psutil': 'Monitoreo de rendimiento'
    }
    
    missing = []
    
    for module, description in dependencies.items():
        try:
            __import__(module)
            print(f"  ✓ {module:25s} - {description}")
        except ImportError:
            print(f"  ✗ {module:25s} - {description} (FALTANTE)")
            missing.append(module)
    
    if missing:
        print(f"\n⚠️  Dependencias faltantes: {', '.join(missing)}")
        print("   Ejecuta: pip install -r requirements.txt")
        return False
    
    return True


def check_directories():
    """Verifica estructura de directorios"""
    print_section("2. Verificando Directorios")
    
    dirs = {
        'data': Config.DATA_DIR,
        'uploads': Config.get_upload_folder(),
        'pdfs': Config.get_pdfs_folder(),
        'vector_store': Config.get_vector_store_path(),
        'cache': Config.get_cache_dir(),
        'logs': Config.get_logs_dir(),
        'models': Config.MODELS_DIR
    }
    
    all_ok = True
    
    for name, path in dirs.items():
        if path.exists():
            print(f"  ✓ {name:15s} - {path}")
        else:
            print(f"  ✗ {name:15s} - {path} (creando...)")
            try:
                path.mkdir(parents=True, exist_ok=True)
                print(f"    → Creado exitosamente")
            except Exception as e:
                print(f"    → Error: {e}")
                all_ok = False
    
    return all_ok


def check_configuration():
    """Verifica configuración"""
    print_section("3. Verificando Configuración")
    
    validation = Config.validate()
    
    if validation['valid']:
        print("  ✓ Configuración válida")
    else:
        print("  ✗ Problemas en la configuración:")
        for issue in validation['issues']:
            print(f"    - {issue}")
    
    if validation['warnings']:
        print("\n  ⚠️  Advertencias:")
        for warning in validation['warnings']:
            print(f"    - {warning}")
    
    print("\n  Configuración actual:")
    print(f"    Chunk size: {Config.CHUNK_SIZE}")
    print(f"    Chunk overlap: {Config.CHUNK_OVERLAP}")
    print(f"    Chunking semántico: {Config.USE_SEMANTIC_CHUNKING}")
    print(f"    Cache habilitado: {Config.ENABLE_CACHE}")
    print(f"    Batch size (embeddings): {Config.EMBEDDING_BATCH_SIZE}")
    print(f"    Workers: {Config.MAX_WORKERS}")
    print(f"    GPU: {Config.USE_GPU}")
    
    return validation['valid']


def check_models():
    """Verifica modelos"""
    print_section("4. Verificando Modelos")
    
    # Modelo de embeddings
    print(f"  Modelo de embeddings: {Config.EMBEDDING_MODEL}")
    try:
        from core.embeddings import EmbeddingEngine
        engine = EmbeddingEngine(Config.EMBEDDING_MODEL)
        print(f"    ✓ Cargado (dimensión: {engine.dimension})")
        print(f"    ✓ Dispositivo: {engine.device}")
    except Exception as e:
        print(f"    ✗ Error: {e}")
        return False
    
    # Modelo LLM
    llm_path = Config.get_llm_model_path()
    print(f"\n  Modelo LLM: {Config.LLM_MODEL}")
    if llm_path.exists():
        print(f"    ✓ Archivo encontrado ({llm_path.stat().st_size / 1024 / 1024:.1f} MB)")
        try:
            from core.llm_engine import LLMEngine
            llm = LLMEngine(str(llm_path), n_ctx=512)  # Contexto pequeño para test
            print(f"    ✓ Modelo cargado correctamente")
        except Exception as e:
            print(f"    ⚠️  Advertencia al cargar: {e}")
    else:
        print(f"    ✗ Archivo no encontrado: {llm_path}")
        print(f"    → Descarga un modelo .gguf y colócalo en {llm_path.parent}")
        return False
    
    return True


def check_optimizations():
    """Verifica optimizaciones implementadas"""
    print_section("5. Verificando Optimizaciones")
    
    optimizations = {
        'Sistema de caché': 'src/core/cache_manager.py',
        'Chunking semántico': 'src/core/text_splitter.py',
        'PDF optimizado': 'src/core/pdf_processor.py',
        'Embeddings optimizados': 'src/core/embeddings.py',
        'Vector store optimizado': 'src/core/vector_store.py',
        'LLM optimizado': 'src/core/llm_engine.py',
        'Sistema de logging': 'src/utils/logger.py',
        'Monitor de rendimiento': 'src/utils/performance.py',
        'Validadores': 'src/utils/validators.py'
    }
    
    base_path = Path(__file__).parent
    
    for name, file_path in optimizations.items():
        full_path = base_path / file_path
        if full_path.exists():
            print(f"  ✓ {name}")
        else:
            print(f"  ✗ {name} - Archivo no encontrado: {file_path}")
    
    return True


def performance_test():
    """Realiza tests básicos de rendimiento"""
    print_section("6. Tests de Rendimiento")
    
    try:
        from core.embeddings import EmbeddingEngine
        from core.text_splitter import SemanticTextSplitter
        import numpy as np
        
        # Test de embeddings
        print("  Probando motor de embeddings...")
        engine = EmbeddingEngine(Config.EMBEDDING_MODEL, batch_size=32)
        
        test_texts = [f"Test text number {i}" for i in range(50)]
        
        start = time.time()
        embeddings = engine.encode(test_texts, show_progress=False)
        elapsed = time.time() - start
        
        print(f"    ✓ 50 embeddings en {elapsed:.2f}s ({50/elapsed:.1f} emb/s)")
        
        # Test de chunking
        print("\n  Probando chunking semántico...")
        splitter = SemanticTextSplitter(chunk_size=500, chunk_overlap=50)
        
        test_text = "Lorem ipsum. " * 1000
        
        start = time.time()
        chunks = splitter.split_text(test_text)
        elapsed = time.time() - start
        
        print(f"    ✓ Texto dividido en {len(chunks)} chunks en {elapsed:.3f}s")
        
        # Test de memoria
        print("\n  Verificando uso de memoria...")
        from utils.performance import PerformanceMonitor
        mem = PerformanceMonitor.get_memory_usage()
        print(f"    ✓ Uso actual: {mem['rss_mb']:.2f} MB ({mem['percent']:.1f}%)")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Error en tests: {e}")
        return False


def main():
    """Función principal"""
    print("\n" + "=" * 70)
    print("  🚀 VERIFICACIÓN DE OPTIMIZACIONES - SCHOLARQA")
    print("=" * 70)
    
    results = []
    
    # Ejecutar verificaciones
    results.append(("Dependencias", check_dependencies()))
    results.append(("Directorios", check_directories()))
    results.append(("Configuración", check_configuration()))
    results.append(("Modelos", check_models()))
    results.append(("Optimizaciones", check_optimizations()))
    results.append(("Rendimiento", performance_test()))
    
    # Resumen
    print_section("RESUMEN")
    
    all_passed = True
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {status:10s} - {name}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 70)
    
    if all_passed:
        print("\n✅ Todas las verificaciones pasaron exitosamente!")
        print("\n📚 Para más información, consulta OPTIMIZACION.md")
        print("\n🚀 Puedes iniciar la aplicación con:")
        print("   python src/app.py")
        print("   o")
        print("   python src/cli.py --help")
    else:
        print("\n⚠️  Algunas verificaciones fallaron.")
        print("   Revisa los mensajes de error arriba para más detalles.")
    
    print("\n" + "=" * 70 + "\n")
    
    return 0 if all_passed else 1


if __name__ == '__main__':
    sys.exit(main())
