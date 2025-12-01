# Carpeta de PDFs de Ejemplo

## 📚 Uso

Coloca aquí tus PDFs académicos para procesarlos con ScholarQA.

## ✅ Formatos Soportados

- PDF (.pdf) con texto seleccionable

## 💡 Mejores Prácticas

1. **Texto seleccionable**: Los PDFs deben tener texto, no solo imágenes
2. **Tamaño**: Recomendado < 50MB por archivo
3. **Nomenclatura**: Usa nombres descriptivos (ej: `smith_2024_ml_review.pdf`)
4. **Idioma**: Funciona mejor en inglés, pero soporta español

## 🚫 No Soportado (por ahora)

- PDFs escaneados sin OCR
- PDFs protegidos con contraseña
- Archivos corruptos

## 📖 Ejemplo de Uso

```bash
# Copiar PDF aquí
cp ~/Downloads/paper.pdf data/pdfs/

# Procesar desde CLI
python src/cli.py upload data/pdfs/paper.pdf

# O usa la interfaz web
python src/app.py
# Luego sube el PDF en http://localhost:5000
```

## 🎯 PDFs Recomendados para Probar

Para probar el sistema, puedes descargar papers de:

- [arXiv.org](https://arxiv.org) - Papers científicos gratuitos
- [PubMed Central](https://www.ncbi.nlm.nih.gov/pmc/) - Artículos biomédicos
- [PLOS](https://plos.org) - Journals de acceso abierto
- [bioRxiv](https://www.biorxiv.org) - Preprints de biología

## 📊 Estadísticas

Después de procesar PDFs, verás:
- Número de chunks generados
- Metadatos extraídos (título, autor)
- Tiempo de procesamiento
