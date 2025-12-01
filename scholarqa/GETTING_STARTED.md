# Comenzando con ScholarQA

Esta guía te ayudará a tener ScholarQA funcionando en minutos.

---

## Requisitos Previos

Antes de comenzar, asegúrate de tener:

- ✅ **Python 3.9 o superior** instalado
- ✅ **4GB RAM** mínimo (8GB recomendado)
- ✅ **2GB de espacio en disco** para modelos y datos
- ✅ **Git** (para clonar el repositorio)

---

## Paso 1: Instalación

### Clonar el Repositorio

```bash
git clone <url-de-tu-repositorio>
cd scholarqa
```

### Crear Entorno Virtual

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Instalar Dependencias

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## Paso 2: Configuración

### Copiar Archivo de Entorno

```bash
cp .env.example .env
```

### Configuración Básica

Edita `.env` con tus configuraciones preferidas:

```env
# Configuraciones esenciales
ENABLE_CACHE=True
USE_SEMANTIC_CHUNKING=True
MAX_WORKERS=4

# Rutas de modelos (ajustar si es necesario)
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
LLM_MODEL=models/downloaded/tu-modelo.gguf
```

---

## Paso 3: Descargar Modelo LLM

Descarga un modelo GGUF de HuggingFace:

### Modelos Recomendados

**Para Pruebas (Rápido):**
- [TinyLlama-1.1B-Chat](https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF) (~600MB)

**Para Producción (Calidad):**
- [Mistral-7B-Instruct](https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF) (~4GB)
- [Llama-2-7B-Chat](https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGUF) (~4GB)

### Ejemplo de Descarga

```bash
# Crear directorio de modelos
mkdir -p models/downloaded

# Descargar con wget (Linux/Mac) o usar el navegador
wget https://huggingface.co/.../model.gguf -O models/downloaded/model.gguf
```

Actualiza `.env` con la ruta del modelo:
```env
LLM_MODEL=models/downloaded/model.gguf
```

---

## Paso 4: Verificar Instalación

Ejecuta el script de verificación:

```bash
python scripts/verify_optimizations.py
```

Esto verificará:
- ✅ Todas las dependencias instaladas
- ✅ Estructura de directorios
- ✅ Configuración válida
- ✅ Modelos disponibles
- ✅ Rendimiento del sistema

---

## Paso 5: Primera Ejecución

### Interfaz Web

Iniciar el servidor web:

```bash
python src/app.py
```

Abre tu navegador en: **http://localhost:5000**

### Línea de Comandos

Prueba estos comandos:

```bash
# Ver ayuda
python src/cli.py --help

# Ver estadísticas del sistema
python src/cli.py stats

# Subir un PDF (usa una muestra de data/pdfs/)
python src/cli.py upload data/pdfs/sample.pdf

# Hacer una pregunta
python src/cli.py ask "¿Cuál es el tema principal del documento?"
```

---

## Paso 6: Subir Tu Primer Documento

### Vía Interfaz Web

1. Abre http://localhost:5000
2. Haz clic en "Subir PDF"
3. Selecciona tu archivo PDF
4. Espera el procesamiento
5. Haz preguntas en el chat

### Vía CLI

```bash
# Subir
python src/cli.py upload ruta/a/tu/documento.pdf

# Preguntar
python src/cli.py ask "Resume la metodología"
```

---

## Problemas Comunes y Soluciones

### Problema: "Modelo no encontrado"

**Solución:**
1. Descarga un modelo GGUF (ver Paso 3)
2. Actualiza `LLM_MODEL` en `.env`
3. Verifica con: `python scripts/verify_optimizations.py`

### Problema: "Sin memoria"

**Solución:**
Reduce el uso de recursos en `.env`:
```env
MAX_WORKERS=2
EMBEDDING_BATCH_SIZE=16
CHUNK_SIZE=800
```

### Problema: "Rendimiento lento"

**Solución:**
Habilita optimizaciones en `.env`:
```env
ENABLE_CACHE=True
USE_SEMANTIC_CHUNKING=True
MAX_WORKERS=4
```

Si tienes una GPU:
```env
USE_GPU=True
N_GPU_LAYERS=32
```

### Problema: "Falló la instalación de dependencias"

**Solución:**
```bash
# Actualizar pip y setuptools
pip install --upgrade pip setuptools wheel

# Instalar dependencias una por una
pip install python-dotenv flask pypdf sentence-transformers chromadb llama-cpp-python psutil
```

---

## Próximos Pasos

### Aprende Más
- 📚 Lee [docs/OPTIMIZATIONS.md](docs/OPTIMIZATIONS.md) para ajuste de rendimiento
- 🏗️ Consulta [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) para diseño del sistema
- 🔌 Revisa [docs/API.md](docs/API.md) para detalles de la API

### Personaliza
- Ajusta el tamaño de fragmentos para mejor contexto
- Prueba diferentes modelos de embeddings
- Configura aceleración GPU
- Configura monitoreo

### Explora
- Ejecuta pruebas: `pytest tests/ -v`
- Ver código: Navega el directorio `src/`
- Revisa ejemplos: Consulta la carpeta `prototypes/`

---

## Referencia Rápida

### Comandos Esenciales

```bash
# Interfaz Web
python src/app.py

# CLI - Subir
python src/cli.py upload <ruta-pdf>

# CLI - Preguntar
python src/cli.py ask "tu pregunta"

# CLI - Estadísticas
python src/cli.py stats

# CLI - Listar
python src/cli.py list -v

# Verificar Sistema
python verify_optimizations.py

# Ejecutar Pruebas
pytest tests/ -v
```

### Archivos Importantes

- `.env` - Configuración
- `requirements.txt` - Dependencias
- `verify_optimizations.py` - Verificación del sistema
- `src/cli.py` - Interfaz de línea de comandos
- `src/app.py` - Servidor web

---

## Obtener Ayuda

- 📖 **Documentación:** Revisa la carpeta `docs/`
- 🐛 **Problemas:** Reporta en GitHub
- 💬 **Preguntas:** Abre una discusión
- 📧 **Contacto:** Consulta los mantenedores del proyecto

---

## Resumen

Ahora deberías tener:
- ✅ ScholarQA instalado y configurado
- ✅ Modelo LLM descargado
- ✅ Sistema verificado y funcionando
- ✅ Primer PDF procesado
- ✅ Preguntas respondidas

**¡Felicitaciones! ¡Estás listo para usar ScholarQA! 🎉**

---

*Para uso avanzado y consejos de optimización, consulta la documentación completa.*
