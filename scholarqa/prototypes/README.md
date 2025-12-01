# Prototypes / Experimentos

Esta carpeta está destinada para experimentos y prototipos durante el desarrollo.

## 📝 Propósito

- Probar nuevas características antes de integrarlas
- Experimentar con diferentes modelos
- Benchmarks de rendimiento
- Pruebas de concepto

## 🔬 Ejemplos de Prototipos

### 1. Test de diferentes modelos de embedding
```python
# test_embeddings.py
from sentence_transformers import SentenceTransformer

models = [
    "all-MiniLM-L6-v2",
    "all-mpnet-base-v2",
    "multi-qa-MiniLM-L6-cos-v1"
]

for model_name in models:
    model = SentenceTransformer(model_name)
    # Comparar velocidad y calidad
```

### 2. Benchmark de procesamiento de PDFs
```python
# benchmark_pdf.py
import time
from pathlib import Path

pdfs = Path("test_pdfs").glob("*.pdf")
for pdf in pdfs:
    start = time.time()
    # Procesar PDF
    duration = time.time() - start
    print(f"{pdf.name}: {duration:.2f}s")
```

### 3. Comparación de estrategias de chunking
```python
# test_chunking.py
strategies = [
    {"size": 500, "overlap": 50},
    {"size": 1000, "overlap": 200},
    {"size": 1500, "overlap": 300}
]

for strategy in strategies:
    # Comparar resultados de Q&A
```

## 🎯 Mejores Prácticas

1. **Nombra descriptivamente**: `experiment_table_extraction.py`
2. **Documenta resultados**: Añade comentarios con findings
3. **Mantén separado del core**: No importar desde aquí en producción
4. **Limpia regularmente**: Elimina prototipos obsoletos

## 📊 Resultados Esperados

Documenta tus hallazgos aquí para referencia futura.

### Embeddings Comparison (Ejemplo)
| Modelo | Dimensiones | Tamaño | Velocidad | Calidad |
|--------|-------------|--------|-----------|---------|
| MiniLM-L6 | 384 | 80MB | ⚡⚡⚡ | ⭐⭐⭐ |
| mpnet-base | 768 | 420MB | ⚡⚡ | ⭐⭐⭐⭐ |

### LLM Models Tested (Ejemplo)
| Modelo | RAM Needed | Tokens/s | Calidad |
|--------|------------|----------|---------|
| TinyLlama 1.1B | 2GB | 50 | ⭐⭐ |
| Mistral 7B Q4 | 4GB | 15 | ⭐⭐⭐⭐ |

## 🚀 Próximos Experimentos

- [ ] Soporte para tablas en PDFs
- [ ] Multimodal (imágenes en papers)
- [ ] Fine-tuning de embeddings
- [ ] RAG con reranking
