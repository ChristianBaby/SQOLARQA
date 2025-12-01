# ScholarQA - Project Structure

This document describes the organization of the ScholarQA project following best practices.

---

## Directory Structure

```
scholarqa/
├── src/                          # Source code
│   ├── core/                     # Core functionality
│   │   ├── __init__.py
│   │   ├── pdf_processor.py      # PDF processing (optimized)
│   │   ├── embeddings.py         # Embedding generation (GPU support)
│   │   ├── vector_store.py       # Vector database (batch operations)
│   │   ├── llm_engine.py         # LLM inference (GPU acceleration)
│   │   ├── text_splitter.py      # Semantic text chunking (NEW)
│   │   └── cache_manager.py      # Caching system (NEW)
│   │
│   ├── utils/                    # Utilities
│   │   ├── __init__.py
│   │   ├── config.py             # Configuration management
│   │   ├── logger.py             # Logging system (NEW)
│   │   ├── performance.py        # Performance monitoring (NEW)
│   │   └── validators.py         # Input validation (NEW)
│   │
│   ├── templates/                # Web templates
│   │   └── index.html
│   │
│   ├── app.py                    # Flask web application
│   └── cli.py                    # Command-line interface
│
├── tests/                        # Test suite
│   ├── __init__.py
│   ├── test_core.py              # Core functionality tests
│   └── test_optimizations.py    # Optimization tests (NEW)
│
├── docs/                         # Documentation
│   ├── API.md                    # API documentation
│   ├── ARCHITECTURE.md           # System architecture
│   ├── CONTRIBUTING.md           # Contribution guidelines
│   └── OPTIMIZATIONS.md          # Optimization guide (NEW)
│
├── scripts/                      # Utility scripts (NEW)
│   ├── README.md                 # Scripts documentation
│   ├── verify_optimizations.py  # System verification
│   ├── setup.py                  # Initial setup
│   └── install_windows.bat       # Windows installer
│
├── data/                         # Data directory
│   ├── pdfs/                     # Sample PDFs
│   ├── uploads/                  # User uploaded PDFs
│   ├── vector_store/             # ChromaDB storage
│   └── cache/                    # Cache directory (NEW)
│
├── models/                       # Models directory
│   └── downloaded/               # Downloaded LLM models
│
├── prototypes/                   # Experimental code
│   ├── README.md
│   └── example_basic_test.py
│
├── logs/                         # Log files (NEW)
│
├── .env.example                  # Environment template
├── .gitignore                    # Git ignore rules
├── .gitattributes                # Git attributes (NEW)
├── CHANGELOG.md                  # Version history (NEW)
├── docker-compose.yml            # Docker configuration
├── Dockerfile                    # Docker image
├── GETTING_STARTED.md            # Quick start guide (NEW)
├── LICENSE                       # MIT License
├── Makefile                      # Build automation
├── pytest.ini                    # Pytest configuration
├── README.md                     # Main documentation
└── requirements.txt              # Python dependencies
```

---

## Key Directories

### `src/` - Source Code
Contains all application source code, organized by functionality.

**Subdirectories:**
- `core/` - Core business logic
- `utils/` - Reusable utilities
- `templates/` - Web UI templates

### `tests/` - Test Suite
Comprehensive test coverage for all modules.

**Files:**
- `test_core.py` - Tests for core modules
- `test_optimizations.py` - Tests for v2.0 optimizations

### `docs/` - Documentation
Technical and user documentation.

**Files:**
- `API.md` - REST API documentation
- `ARCHITECTURE.md` - System design
- `CONTRIBUTING.md` - How to contribute
- `OPTIMIZATIONS.md` - Performance guide

### `scripts/` - Utility Scripts
Helper scripts for setup, verification, and maintenance.

**Files:**
- `verify_optimizations.py` - System health check
- `setup.py` - Initial setup wizard
- `install_windows.bat` - Windows installer

### `data/` - Application Data
Runtime data storage (excluded from git).

**Subdirectories:**
- `pdfs/` - Sample documents
- `uploads/` - User uploads (gitignored)
- `vector_store/` - Database (gitignored)
- `cache/` - Cache storage (gitignored)

### `models/` - AI Models
LLM and embedding models storage.

**Subdirectories:**
- `downloaded/` - Downloaded models (gitignored, large files)

---

## File Organization Principles

### 1. **Separation of Concerns**
- Core logic in `src/core/`
- Utilities in `src/utils/`
- Tests in `tests/`
- Documentation in `docs/`

### 2. **Modularity**
Each module has a single, well-defined responsibility:
- `pdf_processor.py` - PDF handling only
- `embeddings.py` - Embedding generation only
- `vector_store.py` - Database operations only
- `llm_engine.py` - LLM inference only

### 3. **Discoverability**
- Clear naming conventions
- Descriptive file and folder names
- README files in each major directory

### 4. **Scalability**
- Easy to add new modules
- Clear extension points
- Plugin-friendly architecture

---

## Naming Conventions

### Files
- **Python modules:** `snake_case.py`
- **Documentation:** `UPPERCASE.md` for root-level, `PascalCase.md` for docs/
- **Scripts:** `snake_case.py` or `kebab-case.sh`
- **Config:** `.lowercase` or `.lowercase.example`

### Code
- **Classes:** `PascalCase` (e.g., `PDFProcessor`)
- **Functions:** `snake_case` (e.g., `extract_text`)
- **Constants:** `UPPER_SNAKE_CASE` (e.g., `MAX_WORKERS`)
- **Private:** `_leading_underscore` (e.g., `_internal_method`)

---

## Import Organization

Standard import order:

```python
# 1. Standard library
import os
import sys
from pathlib import Path

# 2. Third-party packages
import numpy as np
from flask import Flask

# 3. Local modules
from core.pdf_processor import PDFProcessor
from utils.config import Config
```

---

## Configuration Management

### Environment Variables (`.env`)
```env
# Core settings
EMBEDDING_MODEL=...
LLM_MODEL=...

# Performance
MAX_WORKERS=4
ENABLE_CACHE=True

# Paths
DATA_DIR=data
MODELS_DIR=models
```

### Config Module (`src/utils/config.py`)
Centralizes all configuration with validation.

---

## Testing Structure

```
tests/
├── test_core.py              # Core module tests
├── test_optimizations.py     # Optimization tests
├── conftest.py              # Pytest fixtures (if needed)
└── fixtures/                 # Test data (if needed)
```

**Test naming:**
- Test files: `test_*.py`
- Test classes: `Test*`
- Test methods: `test_*`

---

## Documentation Standards

### Code Documentation
- Docstrings for all public functions/classes
- Type hints for function signatures
- Inline comments for complex logic

### Project Documentation
- `README.md` - Project overview
- `GETTING_STARTED.md` - Quick start
- `CHANGELOG.md` - Version history
- `docs/*.md` - Detailed guides

---

## Version Control

### Ignored Files (`.gitignore`)
- Python cache (`__pycache__/`)
- Virtual environments (`venv/`)
- User data (`data/uploads/`, `data/vector_store/`)
- Models (`models/downloaded/`)
- Logs (`logs/`)
- Environment files (`.env`)

### Tracked Files
- Source code (`src/`)
- Tests (`tests/`)
- Documentation (`docs/`, `*.md`)
- Configuration templates (`.env.example`)
- Build files (`requirements.txt`, `Makefile`)

---

## Dependencies Management

### `requirements.txt`
Production dependencies only.

**Categories:**
- Core (python-dotenv)
- Web (flask, flask-cors)
- PDF (pypdf)
- AI (sentence-transformers, llama-cpp-python)
- Database (chromadb)
- Utilities (psutil)
- Testing (pytest, pytest-cov)
- Development (black, flake8, mypy)

---

## Build and Automation

### Makefile
Common tasks automated:
```bash
make install     # Install dependencies
make verify      # Verify setup
make test        # Run tests
make run         # Start server
make clean       # Clean cache
```

---

## Best Practices Applied

✅ **Clear separation of concerns**  
✅ **Modular architecture**  
✅ **Comprehensive documentation**  
✅ **Extensive testing**  
✅ **Type hints throughout**  
✅ **Consistent naming conventions**  
✅ **Version control best practices**  
✅ **Automated build system**  
✅ **Environment configuration**  
✅ **Security (no secrets in repo)**  

---

## Adding New Features

When adding new functionality:

1. **Create module in appropriate directory**
   - Core logic → `src/core/`
   - Utilities → `src/utils/`

2. **Write tests**
   - Add to `tests/test_*.py`
   - Aim for >80% coverage

3. **Document**
   - Add docstrings
   - Update relevant `docs/*.md`
   - Update `CHANGELOG.md`

4. **Update configuration**
   - Add env vars to `.env.example`
   - Update `src/utils/config.py`

5. **Test integration**
   - Run `make verify`
   - Run `make test`

---

## Contributing

See [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) for contribution guidelines.

---

*This structure follows industry best practices for Python projects and is designed for maintainability and scalability.*
