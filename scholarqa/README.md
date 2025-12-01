# ScholarQA 📚

> **Sistema Inteligente de Preguntas y Respuestas para PDFs con LLMs Locales**

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Licencia: MIT](https://img.shields.io/badge/Licencia-MIT-yellow.svg)](LICENSE)
[![Versión](https://img.shields.io/badge/versión-2.0-green.svg)](CHANGELOG.md)

ScholarQA es un sistema RAG (Generación Aumentada por Recuperación) optimizado que te permite conversar con tus documentos PDF usando modelos LLM locales. **La versión 2.0** incluye optimizaciones de rendimiento completas que lo hacen **2-20x más rápido**.

---

## ✨ Características Principales

- 🔒 **100% Local y Privado** - Ningún dato sale de tu máquina
- ⚡ **Altamente Optimizado** - 2-20x más rápido que la v1.0
- 🧠 **Fragmentación Semántica** - Mejor comprensión del contexto
- 💾 **Caché Inteligente** - Consultas repetidas dramáticamente más rápidas
- 🎯 **Soporte GPU** - Aceleración GPU opcional
- 🌐 **Interfaz Web** - Interfaz Flask moderna
- 💻 **CLI Potente** - Automatización por línea de comandos
- 📊 **Monitoreo de Rendimiento** - Métricas en tiempo real

---

## 🚀 Inicio Rápido

### Requisitos Previos

- Python 3.9 o superior
- 4GB RAM mínimo (8GB recomendado)
- 2GB de espacio en disco

### Instalación

```bash
# Clonar repositorio
git clone <tu-repositorio>
cd scholarqa

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar entorno
cp .env.example .env

# Verificar instalación
python scripts/verify_optimizations.py
```

### Descargar Modelo LLM

Descarga un modelo `.gguf` de [HuggingFace](https://huggingface.co/models?search=gguf) y colócalo en `models/downloaded/`

**Modelos Recomendados:**
- TinyLlama-1.1B (~600MB) - Rápido, bueno para pruebas
- Mistral-7B (~4GB) - Mejor calidad
- Llama-2-7B (~4GB) - Rendimiento equilibrado

---

## 💡 Uso

### Interfaz Web

```bash
python src/app.py
```

Abre http://localhost:5000 en tu navegador.

### Interfaz de Línea de Comandos

```bash
# Subir un PDF
python src/cli.py upload ruta/al/documento.pdf

# Hacer una pregunta
python src/cli.py ask "¿Cuál es el tema principal?"

# Ver estadísticas
python src/cli.py stats

# Listar documentos (modo detallado)
python src/cli.py list -v

# Limpiar base de datos
python src/cli.py clear -y
```

---

## 📊 Rendimiento

### Resultados de Benchmark (v2.0 vs v1.0)

| Operación | v1.0 | v2.0 | Mejora |
|-----------|------|------|--------|
| Procesar PDF de 50 páginas | 15s | 6s | **2.5x más rápido** ⚡ |
| Generar 100 embeddings | 8s | 2s | **4x más rápido** ⚡ |
| Insertar 1000 documentos | 45s | 12s | **3.75x más rápido** ⚡ |
| Consulta en caché | 2s | 0.1s | **20x más rápido** ⚡ |

### Uso de Recursos

- Uso de memoria: **-30%**
- Uso de CPU: **-31%**
- Mejor utilización de GPU

---

## 🎯 Configuración

Variables de entorno clave en `.env`:

```env
# Rendimiento
MAX_WORKERS=4                  # Hilos de procesamiento paralelo
ENABLE_CACHE=True              # Habilitar caché inteligente
USE_GPU=False                  # Habilitar aceleración GPU
EMBEDDING_BATCH_SIZE=32        # Tamaño de lote para embeddings

# Procesamiento de Texto
USE_SEMANTIC_CHUNKING=True     # Fragmentos de mejor calidad
CHUNK_SIZE=1000               # Caracteres por fragmento
CHUNK_OVERLAP=200             # Superposición entre fragmentos

# Modelos
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
LLM_MODEL=models/downloaded/tu-modelo.gguf
```

Consulta [docs/OPTIMIZATIONS.md](docs/OPTIMIZATIONS.md) para configuración avanzada.

---

## 🏗️ Arquitectura

```
┌─────────────┐
│  Usuario    │
└──────┬──────┘
       │
   ┌───▼────┐
   │Flask/CLI│
   └───┬────┘
       │
   ┌───▼──────────┐      ┌──────────────┐
   │Procesador PDF│─────▶│Divisor Texto │
   └──────────────┘      └──────┬───────┘
                                │
                         ┌──────▼─────────┐
                         │Motor Embedding │
                         └──────┬─────────┘
                                │
                         ┌──────▼────────┐
                         │Almacén Vector │
                         │  (ChromaDB)   │
                         └──────┬────────┘
                                │
                         ┌──────▼────────┐
                         │  Motor LLM    │
                         └──────┬────────┘
                                │
                            Respuesta
```

---

## 📚 Documentación

- **[OPTIMIZATIONS.md](docs/OPTIMIZATIONS.md)** - Guía de optimizaciones de rendimiento
- **[API.md](docs/API.md)** - Documentación de API
- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - Arquitectura del sistema
- **[CONTRIBUTING.md](docs/CONTRIBUTING.md)** - Guías de contribución

---

## 🆕 Novedades en v2.0

### Características Principales
- ✅ **Sistema de caché inteligente** (50-90% más rápido en consultas repetidas)
- ✅ **Fragmentación semántica de texto** (mejor calidad de respuestas)
- ✅ **Procesamiento paralelo de PDF** (2.5x más rápido)
- ✅ **Soporte de aceleración GPU**
- ✅ **Monitoreo de rendimiento** (CPU, memoria, tiempo)
- ✅ **Validación robusta** (validación de entrada, manejo de errores)
- ✅ **CLI mejorada** (comando stats, modo detallado)

### Mejoras Técnicas
- Más de 2000 líneas de código optimizado
- 39 pruebas completas
- Type hints en todo el código
- Documentación extensa
- Mejor manejo de errores

---

## 🛠️ Stack Tecnológico

| Componente | Tecnología |
|-----------|-----------|
| **LLM** | llama.cpp (modelos GGUF) |
| **Embeddings** | Sentence Transformers |
| **Base de Datos Vectorial** | ChromaDB |
| **Framework Web** | Flask |
| **Procesamiento PDF** | pypdf |
| **Async/Threading** | ThreadPoolExecutor |
| **Monitoreo** | psutil |

---

## 🧪 Pruebas

```bash
# Ejecutar todas las pruebas
pytest tests/ -v

# Ejecutar pruebas de optimización
pytest tests/test_optimizations.py -v

# Ejecutar con cobertura
pytest tests/ -v --cov=src --cov-report=html
```

---

## 🤝 Contribuir

¡Las contribuciones son bienvenidas! Por favor consulta [CONTRIBUTING.md](docs/CONTRIBUTING.md) para las guías.

### Configuración de Desarrollo

```bash
# Instalar dependencias de desarrollo
pip install -r requirements.txt

# Ejecutar pruebas
pytest tests/ -v

# Ejecutar linter
flake8 src/ tests/

# Verificación de tipos
mypy src/
```

---

## 📄 Licencia

Licencia MIT - consulta el archivo [LICENSE](LICENSE) para detalles.

---

## 🙏 Agradecimientos

- [llama.cpp](https://github.com/ggerganov/llama.cpp) - Inferencia rápida de LLM
- [Sentence Transformers](https://www.sbert.net/) - Embeddings de última generación
- [ChromaDB](https://www.trychroma.com/) - Base de datos vectorial nativa para IA
- [Flask](https://flask.palletsprojects.com/) - Framework web

---

## 🗺️ Hoja de Ruta

- [ ] Soporte async/await
- [ ] Respuestas streaming del LLM
- [ ] Índices vectoriales FAISS
- [ ] Conversaciones multi-documento
- [ ] API REST
- [ ] Despliegue Docker
- [ ] Panel web para monitoreo

---

**Hecho con ❤️ para la comunidad académica**

*ScholarQA v2.0 - Rápido, Inteligente, Privado*
