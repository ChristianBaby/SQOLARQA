# Referencia de API

## Endpoints de la API REST

### GET /api/status

Retorna el estado del sistema.

**Respuesta:**
```json
{
  "status": "ok",
  "components": {
    "pdf_processor": true,
    "embedding_engine": true,
    "vector_store": true,
    "llm_engine": true
  },
  "documents_count": 42
}
```

### POST /api/upload

Sube y procesa un PDF.

**Petición:**
- Content-Type: `multipart/form-data`
- Body: `file` (archivo PDF)

**Respuesta:**
```json
{
  "success": true,
  "filename": "documento.pdf",
  "chunks": 15,
  "metadata": {
    "title": "Título del Documento",
    "author": "Nombre del Autor"
  }
}
```

### POST /api/ask

Hace una pregunta sobre los documentos.

**Petición:**
```json
{
  "question": "¿Cuál es la conclusión principal?"
}
```

**Respuesta:**
```json
{
  "answer": "La conclusión principal es...",
  "sources": [
    {"source": "documento.pdf", "chunk_id": 3}
  ],
  "context_used": 5
}
```

### GET /api/documents

Lista documentos en la base de datos.

**Respuesta:**
```json
{
  "total_chunks": 42,
  "message": "42 fragmentos en la base de datos"
}
```

## Comandos CLI

### upload

Sube un archivo PDF al sistema.

```bash
python src/cli.py upload ruta/al/documento.pdf
```

**Opciones:**
- `pdf_path`: Ruta al archivo PDF (requerido)

**Ejemplo:**
```bash
python src/cli.py upload data/pdfs/articulo_investigacion.pdf
```

### ask

Hace una pregunta sobre los documentos procesados.

```bash
python src/cli.py ask "¿Cuál es la metodología?"
```

**Opciones:**
- `question`: La pregunta a realizar (requerido)

**Ejemplo:**
```bash
python src/cli.py ask "¿Cuáles son los hallazgos principales del estudio?"
```

### list

Lista todos los documentos en la base de datos.

```bash
python src/cli.py list
```

**Opciones:**
- `-v, --verbose`: Muestra información detallada

**Ejemplo:**
```bash
python src/cli.py list -v
```

### stats

Muestra estadísticas del sistema.

```bash
python src/cli.py stats
```

**Información mostrada:**
- Número total de documentos
- Número de fragmentos
- Uso de memoria
- Uso de caché (si está habilitado)

### clear

Limpia la base de datos vectorial.

```bash
python src/cli.py clear -y
```

**Opciones:**
- `-y, --yes`: Confirma la operación sin preguntar

**Advertencia:** Esta operación eliminará todos los documentos procesados.

## API Programática (Python)

### PDFProcessor

```python
from src.core.pdf_processor import PDFProcessor

processor = PDFProcessor()

# Extraer texto de un PDF
texto = processor.extract_text("documento.pdf")

# Validar PDF
validacion = processor.validate_pdf("documento.pdf")
if validacion['valid']:
    print("PDF válido")
```

### EmbeddingEngine

```python
from src.core.embeddings import EmbeddingEngine

engine = EmbeddingEngine(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    device="cpu"
)

# Generar embeddings
embeddings = engine.encode(["texto 1", "texto 2"])

# Calcular similitud
similitud = engine.similarity("texto 1", "texto 2")
```

### VectorStore

```python
from src.core.vector_store import VectorStore

store = VectorStore(
    persist_directory="data/vector_store",
    collection_name="documentos"
)

# Añadir documentos
store.add_documents(
    texts=["fragmento 1", "fragmento 2"],
    metadatas=[{"source": "doc1.pdf"}, {"source": "doc2.pdf"}]
)

# Buscar documentos similares
resultados = store.query(
    query_text="¿Qué es IA?",
    n_results=5
)
```

### LLMEngine

```python
from src.core.llm_engine import LLMEngine

llm = LLMEngine(
    model_path="models/downloaded/modelo.gguf",
    n_ctx=2048
)

# Generar texto
respuesta = llm.generate(
    prompt="Explica el concepto de...",
    max_tokens=500
)

# Responder pregunta con contexto
answer = llm.answer_question(
    question="¿Qué es IA?",
    context="La inteligencia artificial es..."
)
```

## Códigos de Error

| Código | Descripción |
|--------|-------------|
| 200 | Éxito |
| 400 | Petición inválida |
| 404 | Recurso no encontrado |
| 500 | Error interno del servidor |

### Ejemplos de Errores

**PDF Inválido:**
```json
{
  "error": "Archivo PDF inválido o corrupto",
  "code": 400
}
```

**Modelo No Encontrado:**
```json
{
  "error": "Modelo LLM no encontrado en la ruta especificada",
  "code": 500
}
```

**Base de Datos Vacía:**
```json
{
  "error": "No hay documentos en la base de datos",
  "code": 404
}
```

## Ejemplos Completos

### Ejemplo: Subir y Consultar un Documento

```python
import requests

# Subir PDF
with open("documento.pdf", "rb") as f:
    response = requests.post(
        "http://localhost:5000/api/upload",
        files={"file": f}
    )
    print(response.json())

# Hacer pregunta
response = requests.post(
    "http://localhost:5000/api/ask",
    json={"question": "¿Cuál es el tema principal?"}
)
print(response.json()["answer"])
```

### Ejemplo: Pipeline Completo

```python
from src.core.pdf_processor import PDFProcessor
from src.core.embeddings import EmbeddingEngine
from src.core.vector_store import VectorStore
from src.core.llm_engine import LLMEngine

# Inicializar componentes
pdf_processor = PDFProcessor()
embedding_engine = EmbeddingEngine()
vector_store = VectorStore()
llm_engine = LLMEngine()

# Procesar PDF
texto = pdf_processor.extract_text("documento.pdf")
fragmentos = pdf_processor.chunk_text(texto)

# Almacenar en base de datos vectorial
vector_store.add_documents(
    texts=fragmentos,
    metadatas=[{"source": "documento.pdf"}] * len(fragmentos)
)

# Consultar
pregunta = "¿Cuál es la conclusión?"
resultados = vector_store.query(pregunta, n_results=3)
contexto = " ".join([r["text"] for r in resultados])

# Generar respuesta
respuesta = llm_engine.answer_question(pregunta, contexto)
print(respuesta)
```

## Límites y Restricciones

| Límite | Valor | Notas |
|--------|-------|-------|
| Tamaño máximo de PDF | 100 MB | Configurable |
| Número de documentos | Sin límite | Depende de RAM |
| Longitud de pregunta | 500 caracteres | Recomendado |
| Tokens de respuesta | 2048 | Configurable en .env |

## Mejores Prácticas

1. **Validar PDFs antes de procesar**: Usa `validate_pdf()` para evitar errores
2. **Batch processing**: Procesa múltiples documentos en lotes
3. **Caché**: Habilita caché para consultas frecuentes
4. **Manejo de errores**: Implementa retry logic para operaciones críticas
5. **Monitoreo**: Usa las estadísticas del sistema para optimizar

---

**Para más información, consulta:**
- [ARCHITECTURE.md](ARCHITECTURE.md) - Arquitectura del sistema
- [OPTIMIZATIONS.md](OPTIMIZATIONS.md) - Guía de optimización
- [CONTRIBUTING.md](CONTRIBUTING.md) - Guía de contribución
