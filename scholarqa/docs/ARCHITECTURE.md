# Arquitectura de ScholarQA

## 🏗️ Visión General

ScholarQA es un sistema de RAG (Retrieval-Augmented Generation) que permite hacer preguntas sobre documentos PDF académicos usando modelos de IA completamente locales.

## 📊 Diagrama de Componentes

```
┌─────────────────────────────────────────────────────────────┐
│                         Usuario                              │
│                    (Web UI / CLI)                            │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    Flask Application                         │
│                      (src/app.py)                            │
└────────┬────────────────────────────────────────┬───────────┘
         │                                        │
         ▼                                        ▼
┌──────────────────┐                    ┌──────────────────┐
│  PDF Processor   │                    │   LLM Engine     │
│ (pdf_processor)  │                    │  (llm_engine)    │
│                  │                    │                  │
│  - Extract text  │                    │  - Generate text │
│  - Chunk text    │                    │  - Answer Q&A    │
│  - Metadata      │                    │  - llama.cpp     │
└────────┬─────────┘                    └────────▲─────────┘
         │                                        │
         ▼                                        │
┌──────────────────┐                              │
│ Embedding Engine │                              │
│  (embeddings)    │                              │
│                  │                              │
│  - Sentence      │                              │
│    Transformers  │                              │
└────────┬─────────┘                              │
         │                                        │
         ▼                                        │
┌─────────────────────────────────────────────────┴──────────┐
│              Vector Store (ChromaDB)                        │
│                  (vector_store)                             │
│                                                             │
│  - Store embeddings                                         │
│  - Semantic search                                          │
│  - Retrieve context                                         │
└─────────────────────────────────────────────────────────────┘
```

## 🔄 Flujo de Datos

### 1. Ingesta de Documentos

```
PDF File → PDFProcessor.extract_text() → Raw Text
                                           ↓
                              PDFProcessor.chunk_text() → Text Chunks
                                           ↓
                           EmbeddingEngine.encode() → Embeddings
                                           ↓
                           VectorStore.add_documents() → Stored in ChromaDB
```

### 2. Respuesta a Preguntas

```
User Question → EmbeddingEngine.encode() → Query Embedding
                                             ↓
                          VectorStore.query() → Relevant Chunks
                                             ↓
                    LLMEngine.create_qa_prompt() → Formatted Prompt
                                             ↓
                        LLMEngine.generate() → Answer
                                             ↓
                              Flask → User Interface
```

## 📦 Componentes Principales

### 1. PDFProcessor (`src/core/pdf_processor.py`)

**Responsabilidad:** Procesamiento de archivos PDF

**Funciones principales:**
- `extract_text(pdf_path)`: Extrae texto de un PDF
- `extract_metadata(pdf_path)`: Extrae metadatos (título, autor, etc.)
- `chunk_text(text, chunk_size, overlap)`: Divide el texto en fragmentos

**Dependencias:**
- pypdf: Lectura de PDFs
- pdfplumber: Extracción avanzada (opcional)

### 2. EmbeddingEngine (`src/core/embeddings.py`)

**Responsabilidad:** Generación de embeddings vectoriales

**Funciones principales:**
- `encode(texts)`: Genera embeddings para múltiples textos
- `encode_single(text)`: Genera embedding para un texto

**Modelo por defecto:**
- `all-MiniLM-L6-v2` (384 dimensiones, 80MB)
- Alternativa: `all-mpnet-base-v2` (768 dimensiones, mejor calidad)

### 3. VectorStore (`src/core/vector_store.py`)

**Responsabilidad:** Almacenamiento y búsqueda vectorial

**Funciones principales:**
- `add_documents(texts, metadatas, ids)`: Añade documentos
- `query(query_text, n_results)`: Búsqueda semántica
- `get_collection_count()`: Cuenta documentos

**Base de datos:**
- ChromaDB (local, persistente)
- Ubicación: `data/vector_store/`

### 4. LLMEngine (`src/core/llm_engine.py`)

**Responsabilidad:** Generación de respuestas con LLM local

**Funciones principales:**
- `generate(prompt, max_tokens, ...)`: Generación de texto
- `answer_question(question, context)`: Q&A con contexto
- `create_qa_prompt(question, context)`: Formato de prompts

**Modelos soportados:**
- Cualquier modelo GGUF (llama.cpp)
- TinyLlama, Mistral, Llama 2, etc.

### 5. Flask Application (`src/app.py`)

**Responsabilidad:** API web y frontend

**Endpoints:**
- `GET /`: Interfaz web
- `GET /api/status`: Estado del sistema
- `POST /api/upload`: Subir PDF
- `POST /api/ask`: Hacer pregunta
- `GET /api/documents`: Listar documentos

## 🔧 Configuración (`src/utils/config.py`)

Gestiona todas las variables de configuración desde `.env`:

```python
- EMBEDDING_MODEL: Modelo de embeddings
- LLM_MODEL: Ruta al modelo LLM
- CHROMA_PERSIST_DIR: Directorio ChromaDB
- CHUNK_SIZE: Tamaño de chunks
- CHUNK_OVERLAP: Overlap entre chunks
- MAX_TOKENS: Tokens máximos de respuesta
- TEMPERATURE: Temperature del LLM
```

## 🗂️ Estructura de Datos

### Chunk Metadata

```python
{
    'source': 'paper.pdf',
    'chunk_id': 0,
    'title': 'Paper Title'
}
```

### Query Response

```python
{
    'answer': 'Generated answer...',
    'sources': [{'source': 'paper.pdf', 'chunk_id': 0}],
    'context_used': 5
}
```

## 🚀 Optimizaciones

### Actuales
- Lazy loading de componentes
- Chunking con overlap para contexto
- Embeddings cacheados por Sentence Transformers
- ChromaDB persistente

### Futuras
- Cache de embeddings de queries frecuentes
- Batch processing para múltiples PDFs
- Reranking de resultados
- Cuantización de modelos

## 🔒 Privacidad y Seguridad

- **100% Local**: Ningún dato sale de tu máquina
- **Sin APIs externas**: No se envía información a servicios cloud
- **Datos persistentes**: Vector store local en disco
- **Sin tracking**: No hay analytics ni telemetría

## 📈 Escalabilidad

### Límites actuales
- ~1000 PDFs en memoria
- ChromaDB soporta millones de vectores
- Depende de RAM disponible

### Para escalar
- Usar ChromaDB en modo cliente-servidor
- Implementar paginación en queries
- Batch processing asíncrono

## 🛠️ Tecnologías

| Componente | Tecnología | Licencia |
|------------|------------|----------|
| Framework Web | Flask | BSD |
| Embeddings | Sentence Transformers | Apache 2.0 |
| Vector DB | ChromaDB | Apache 2.0 |
| LLM Runtime | llama.cpp | MIT |
| PDF Processing | PyPDF | BSD |
| Frontend | Vanilla JS | - |

## 📝 Decisiones de Diseño

### ¿Por qué ChromaDB?
- Fácil de usar
- Completamente local
- Excelente para prototipos y producción
- Sin configuración compleja

### ¿Por qué llama.cpp?
- Mejor rendimiento CPU
- Soporte GGUF amplio
- Baja huella de memoria
- Comunidad activa

### ¿Por qué Sentence Transformers?
- Modelos pre-entrenados excelentes
- Fácil integración
- Caching automático
- Soporte multilingüe

### ¿Por qué Flask?
- Simple y ligero
- Fácil de entender
- Sin dependencias complejas
- Perfecto para proyectos educativos

## 🔄 Ciclo de Vida

1. **Inicialización**: Cargar modelos y configuración
2. **Ingesta**: Procesar PDFs y almacenar embeddings
3. **Query**: Búsqueda semántica + generación LLM
4. **Respuesta**: Formato y entrega al usuario

## 🧪 Testing

- Unit tests: Cada componente independiente
- Integration tests: Flujo completo
- E2E tests: Interfaz web

## 📚 Referencias

- [LangChain Docs](https://python.langchain.com/)
- [ChromaDB Docs](https://docs.trychroma.com/)
- [Sentence Transformers](https://www.sbert.net/)
- [llama.cpp](https://github.com/ggerganov/llama.cpp)
