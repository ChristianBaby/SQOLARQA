# Guía de Contribución

¡Gracias por tu interés en contribuir a ScholarQA! 🎉

## 🌟 Formas de Contribuir

1. **Reportar Bugs**: Abre un issue describiendo el problema
2. **Sugerir Features**: Propón nuevas características
3. **Mejorar Documentación**: Ayuda a clarificar el código
4. **Código**: Implementa nuevas features o fixes

## 🚀 Setup para Desarrollo

### 1. Fork y Clone

```bash
git clone https://github.com/tu-usuario/scholarqa.git
cd scholarqa
```

### 2. Crear Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### 3. Instalar en Modo Desarrollo

```bash
pip install -r requirements.txt
pip install -e .
```

### 4. Instalar Herramientas de Desarrollo

```bash
pip install black flake8 pytest pytest-cov
```

## 📝 Estándares de Código

### Formateo

Usamos **Black** para formateo consistente:

```bash
black src/
```

### Linting

Usamos **Flake8** para verificar estilo:

```bash
flake8 src/ --max-line-length=100
```

### Type Hints

Preferimos usar type hints cuando sea posible:

```python
def process_text(text: str, max_length: int = 100) -> List[str]:
    """Procesa texto y retorna chunks"""
    pass
```

## 🧪 Testing

### Ejecutar Tests

```bash
# Todos los tests
pytest

# Con cobertura
pytest --cov=src tests/

# Test específico
pytest tests/test_core.py::TestPDFProcessor -v
```

### Escribir Tests

Cada nueva feature debe incluir tests:

```python
def test_new_feature():
    """Test para la nueva feature"""
    # Arrange
    input_data = "test"
    
    # Act
    result = new_feature(input_data)
    
    # Assert
    assert result == expected_output
```

## 📋 Proceso de Contribución

### 1. Crear Branch

```bash
git checkout -b feature/amazing-feature
# o
git checkout -b fix/bug-description
```

### 2. Hacer Cambios

- Escribe código limpio y documentado
- Añade tests
- Actualiza documentación si es necesario

### 3. Commit

Usamos commits descriptivos:

```bash
git commit -m "feat: Add table extraction from PDFs"
git commit -m "fix: Handle empty PDF gracefully"
git commit -m "docs: Update installation guide"
```

**Tipos de commit:**
- `feat`: Nueva característica
- `fix`: Bug fix
- `docs`: Documentación
- `test`: Tests
- `refactor`: Refactorización
- `style`: Formateo
- `chore`: Tareas de mantenimiento

### 4. Push

```bash
git push origin feature/amazing-feature
```

### 5. Pull Request

Abre un PR con:
- **Título claro**: "Add support for DOCX files"
- **Descripción**: Qué, por qué y cómo
- **Tests**: Evidencia de que funciona
- **Screenshots**: Si aplica

## 🎯 Áreas para Contribuir

### 🔥 Alta Prioridad

- [ ] Soporte para más formatos (DOCX, TXT, EPUB)
- [ ] Extracción mejorada de tablas
- [ ] Interfaz de usuario mejorada
- [ ] Tests adicionales
- [ ] Optimización de rendimiento

### 🌟 Features Deseadas

- [ ] Modo de citación académica
- [ ] Exportar conversaciones
- [ ] Soporte multilingüe
- [ ] Chat con múltiples documentos
- [ ] Resumen automático de papers
- [ ] Extracción de figuras

### 📚 Documentación

- [ ] Tutoriales en video
- [ ] Ejemplos de uso
- [ ] FAQ expandido
- [ ] Traducciones

### 🐛 Bugs Conocidos

Revisa los issues etiquetados como `bug` en GitHub.

## 💡 Ideas para Experimentar

1. **Modelos alternativos**: Probar diferentes LLMs
2. **Chunking strategies**: Mejorar división de texto
3. **Reranking**: Implementar reordenamiento de resultados
4. **Cache**: Sistema de cache para queries frecuentes

## 📖 Recursos Útiles

- [LangChain Documentation](https://python.langchain.com/)
- [ChromaDB Guide](https://docs.trychroma.com/)
- [Sentence Transformers](https://www.sbert.net/)
- [Flask Documentation](https://flask.palletsprojects.com/)

## ❓ Preguntas

Si tienes dudas:
1. Revisa la documentación existente
2. Busca en issues cerrados
3. Abre un nuevo issue con tu pregunta

## 🎓 Código de Conducta

- Sé respetuoso y constructivo
- Ayuda a otros miembros de la comunidad
- Acepta críticas constructivas
- Enfócate en lo mejor para el proyecto

## 🏆 Reconocimientos

Todos los contribuidores serán reconocidos en el README.

---

¡Gracias por hacer ScholarQA mejor! 🚀
