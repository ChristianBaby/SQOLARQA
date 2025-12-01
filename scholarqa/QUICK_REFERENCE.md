# 📋 Quick Reference - ScholarQA

Fast access to common commands and information.

---

## 🚀 Installation

```bash
# Clone and setup
git clone <repo-url>
cd scholarqa
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate

# Install
pip install -r requirements.txt

# Verify
python scripts/verify_optimizations.py
```

---

## 💻 Common Commands

### Using Makefile (Recommended)

```bash
make install       # Install dependencies
make verify        # Verify installation
make test          # Run tests
make run           # Start web server
make stats         # Show statistics
make clean         # Clean cache
make help          # Show all commands
```

### Direct Commands

```bash
# Web Interface
python src/app.py

# CLI - Upload PDF
python src/cli.py upload path/to/file.pdf

# CLI - Ask question
python src/cli.py ask "Your question here"

# CLI - List documents
python src/cli.py list -v

# CLI - Statistics
python src/cli.py stats

# CLI - Clear database
python src/cli.py clear -y

# Verify system
python scripts/verify_optimizations.py

# Run tests
pytest tests/ -v

# Run optimization tests
pytest tests/test_optimizations.py -v
```

---

## 📂 Project Structure

```
scholarqa/
├── src/              # Source code
├── tests/            # Tests
├── docs/             # Documentation
├── scripts/          # Utility scripts
├── data/             # Data storage
└── models/           # AI models
```

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| [README.md](README.md) | Main documentation |
| [GETTING_STARTED.md](GETTING_STARTED.md) | Installation guide |
| [CHANGELOG.md](CHANGELOG.md) | Version history |
| [INDEX.md](INDEX.md) | Documentation index |
| [docs/OPTIMIZATIONS.md](docs/OPTIMIZATIONS.md) | Performance guide |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | System design |
| [docs/API.md](docs/API.md) | API reference |
| [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) | Code organization |

---

## ⚙️ Configuration

```env
# Essential settings (.env)
ENABLE_CACHE=True
USE_SEMANTIC_CHUNKING=True
MAX_WORKERS=4
EMBEDDING_BATCH_SIZE=32

# Models
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
LLM_MODEL=models/downloaded/your-model.gguf
```

---

## 🔧 Scripts

```bash
# Verify system
python scripts/verify_optimizations.py

# Initial setup
python scripts/setup.py

# Windows installer
scripts\install_windows.bat
```

---

## 🧪 Testing

```bash
# All tests
pytest tests/ -v

# Specific test file
pytest tests/test_optimizations.py -v

# With coverage
pytest tests/ -v --cov=src --cov-report=html

# Watch mode (with pytest-watch)
ptw tests/
```

---

## 📊 Performance

### Benchmarks (v2.0)

| Operation | Time | Improvement |
|-----------|------|-------------|
| 50-page PDF | 6s | 2.5x faster |
| 100 embeddings | 2s | 4x faster |
| 1000 inserts | 12s | 3.75x faster |
| Cached query | 0.1s | 20x faster |

---

## 🐛 Troubleshooting

### Common Issues

**Model not found:**
```bash
# Download model to models/downloaded/
# Update LLM_MODEL in .env
python scripts/verify_optimizations.py
```

**Out of memory:**
```env
MAX_WORKERS=2
EMBEDDING_BATCH_SIZE=16
CHUNK_SIZE=800
```

**Slow performance:**
```env
ENABLE_CACHE=True
USE_GPU=True  # If available
MAX_WORKERS=8
```

---

## 📁 Important Paths

```bash
# Source code
src/core/                # Core modules
src/utils/               # Utilities
src/app.py               # Web app
src/cli.py               # CLI

# Data
data/pdfs/               # Sample PDFs
data/uploads/            # User uploads
data/vector_store/       # Database
data/cache/              # Cache

# Models
models/downloaded/       # LLM models

# Logs
logs/                    # Application logs

# Config
.env                     # Environment variables
```

---

## 🌐 Web Interface

```bash
# Start server
python src/app.py

# Access
http://localhost:5000

# Default port: 5000
# Change in .env: FLASK_PORT=8080
```

---

## 💡 Tips

- Always activate virtual environment before running commands
- Use `make verify` after configuration changes
- Check logs in `logs/scholarqa.log` for debugging
- Run tests before committing changes
- Use `make stats` to monitor performance

---

## 🔗 Quick Links

- **GitHub:** [Repository URL]
- **Issues:** [Issues URL]
- **Discussions:** [Discussions URL]
- **Documentation:** `docs/` folder

---

## 📞 Getting Help

1. Check [GETTING_STARTED.md](GETTING_STARTED.md)
2. Read [docs/OPTIMIZATIONS.md](docs/OPTIMIZATIONS.md)
3. Run `python scripts/verify_optimizations.py`
4. Check logs: `logs/scholarqa.log`
5. Open an issue on GitHub

---

**For complete documentation, see [INDEX.md](INDEX.md)**

*Last updated: 2024 - Version 2.0*
