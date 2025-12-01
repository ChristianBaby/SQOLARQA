#!/usr/bin/env python3
"""
ScholarQA - Setup Script
Configura el entorno inicial del proyecto
"""

import os
import sys
from pathlib import Path
import shutil


def create_directories():
    """Crea la estructura de directorios del proyecto"""
    print("📁 Creando estructura de directorios...")
    
    directories = [
        "src/core",
        "src/utils",
        "src/templates",
        "src/static/css",
        "src/static/js",
        "data/pdfs",
        "data/uploads",
        "data/vector_store",
        "models/downloaded",
        "tests",
        "docs",
        "prototypes",
        "logs",
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"  ✓ {directory}")
    
    # Crear archivos .gitkeep para mantener carpetas vacías en git
    gitkeep_dirs = [
        "data/pdfs",
        "data/uploads",
        "data/vector_store",
        "models/downloaded",
        "logs",
    ]
    
    for directory in gitkeep_dirs:
        gitkeep_path = Path(directory) / ".gitkeep"
        gitkeep_path.touch(exist_ok=True)


def create_env_file():
    """Crea el archivo .env con configuración por defecto"""
    print("\n⚙️  Creando archivo de configuración (.env)...")
    
    env_content = """# ScholarQA Configuration

# Modelos
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
LLM_MODEL=models/downloaded/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf

# ChromaDB
CHROMA_PERSIST_DIR=data/vector_store
COLLECTION_NAME=academic_papers

# Flask
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
FLASK_DEBUG=False

# Procesamiento de texto
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
MAX_CHUNKS_PER_QUERY=5

# LLM Settings
MAX_TOKENS=512
TEMPERATURE=0.7
TOP_P=0.95

# Sistema
LOG_LEVEL=INFO
"""
    
    env_path = Path(".env")
    if env_path.exists():
        print("  ⚠️  .env ya existe, creando .env.example")
        env_path = Path(".env.example")
    
    with open(env_path, "w", encoding="utf-8") as f:
        f.write(env_content)
    
    print(f"  ✓ {env_path} creado")


def download_embedding_model():
    """Descarga el modelo de embeddings por defecto"""
    print("\n🤖 Descargando modelo de embeddings...")
    print("  Esto puede tardar unos minutos en la primera ejecución...")
    
    try:
        from sentence_transformers import SentenceTransformer
        
        model_name = "sentence-transformers/all-MiniLM-L6-v2"
        print(f"  Descargando: {model_name}")
        
        # Esto descarga y cachea el modelo
        model = SentenceTransformer(model_name)
        print(f"  ✓ Modelo descargado correctamente (dimensión: {model.get_sentence_embedding_dimension()})")
        
        return True
    except Exception as e:
        print(f"  ⚠️  Error al descargar modelo: {e}")
        print("  Puedes descargarlo manualmente más tarde ejecutando el servidor")
        return False


def show_llm_instructions():
    """Muestra instrucciones para descargar modelos LLM"""
    print("\n🦙 Modelos LLM Locales")
    print("=" * 60)
    print("\nPara usar ScholarQA necesitas un modelo LLM local.")
    print("\n📥 Opciones de descarga:\n")
    
    print("1️⃣  RECOMENDADO - TinyLlama (1.1GB, rápido)")
    print("   wget https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf")
    print("   mv tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf models/downloaded/")
    
    print("\n2️⃣  Mistral 7B (4GB, mejor calidad)")
    print("   wget https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf")
    print("   mv mistral-7b-instruct-v0.2.Q4_K_M.gguf models/downloaded/")
    
    print("\n3️⃣  Llama 2 7B (4GB)")
    print("   wget https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGUF/resolve/main/llama-2-7b-chat.Q4_K_M.gguf")
    print("   mv llama-2-7b-chat.Q4_K_M.gguf models/downloaded/")
    
    print("\n" + "=" * 60)
    print("\n💡 Tip: Coloca cualquier modelo .gguf en models/downloaded/")
    print("        y actualiza LLM_MODEL en el archivo .env")


def create_init_files():
    """Crea archivos __init__.py necesarios"""
    print("\n📝 Creando archivos __init__.py...")
    
    init_files = [
        "src/__init__.py",
        "src/core/__init__.py",
        "src/utils/__init__.py",
        "tests/__init__.py",
    ]
    
    for init_file in init_files:
        path = Path(init_file)
        if not path.exists():
            path.touch()
            print(f"  ✓ {init_file}")


def check_dependencies():
    """Verifica que las dependencias estén instaladas"""
    print("\n🔍 Verificando dependencias...")
    
    required_packages = [
        "flask",
        "sentence_transformers",
        "chromadb",
        "langchain",
        "pypdf",
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ✗ {package} (falta)")
            missing.append(package)
    
    if missing:
        print(f"\n⚠️  Faltan dependencias: {', '.join(missing)}")
        print("   Ejecuta: pip install -r requirements.txt")
        return False
    
    print("\n✅ Todas las dependencias instaladas")
    return True


def create_sample_documents():
    """Crea documentos de ejemplo para testing"""
    print("\n📄 Creando documentos de ejemplo...")
    
    sample_readme = """# Documentos de Ejemplo

Coloca tus PDFs académicos aquí para procesarlos.

## Formatos soportados
- PDF (.pdf)

## Mejores prácticas
- Usa PDFs con texto seleccionable (no escaneos sin OCR)
- Tamaño recomendado: < 50MB por archivo
- Nombra los archivos de forma descriptiva

## Ejemplo de uso
1. Copia tu PDF a esta carpeta
2. Usa la interfaz web o CLI para procesarlo
3. Haz preguntas sobre el contenido
"""
    
    readme_path = Path("data/pdfs/README.md")
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(sample_readme)
    
    print(f"  ✓ {readme_path}")


def main():
    """Función principal del script de setup"""
    print("\n" + "=" * 60)
    print("🎓 ScholarQA - Setup Inicial")
    print("=" * 60)
    
    # Verificar que estamos en el directorio correcto
    if not Path("requirements.txt").exists():
        print("\n❌ Error: Ejecuta este script desde el directorio raíz de scholarqa/")
        sys.exit(1)
    
    # Crear estructura
    create_directories()
    create_init_files()
    create_env_file()
    create_sample_documents()
    
    # Verificar dependencias
    deps_ok = check_dependencies()
    
    if deps_ok:
        # Descargar modelo de embeddings
        download_embedding_model()
    
    # Mostrar instrucciones para LLM
    show_llm_instructions()
    
    print("\n" + "=" * 60)
    print("✅ Setup completado!")
    print("=" * 60)
    
    print("\n📋 Próximos pasos:\n")
    print("1. Descarga un modelo LLM (ver instrucciones arriba)")
    print("2. Ajusta configuración en .env si es necesario")
    print("3. Ejecuta: python src/app.py")
    print("4. Abre: http://localhost:5000")
    
    print("\n💡 Para ayuda: python src/cli.py --help")
    print("\n¡Disfruta usando ScholarQA! 🚀\n")


if __name__ == "__main__":
    main()
