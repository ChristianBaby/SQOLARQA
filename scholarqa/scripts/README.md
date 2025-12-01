# Scripts

This directory contains utility scripts for ScholarQA.

## Available Scripts

### `verify_optimizations.py`
Comprehensive system verification script.

**Usage:**
```bash
python scripts/verify_optimizations.py
```

**Checks:**
- Dependencies installed
- Directory structure
- Configuration validity
- Models availability
- System performance

### `setup.py`
Initial setup script for first-time installation.

**Usage:**
```bash
python scripts/setup.py
```

**Actions:**
- Creates necessary directories
- Downloads embedding models
- Configures environment
- Validates setup

### `install_windows.bat`
Windows installation batch script.

**Usage:**
```bash
scripts\install_windows.bat
```

**Actions:**
- Creates virtual environment
- Installs dependencies
- Sets up configuration

---

## Creating Custom Scripts

When adding new utility scripts:

1. Place them in this `scripts/` directory
2. Add appropriate documentation
3. Make them executable (Unix): `chmod +x script.py`
4. Add to Makefile if frequently used
5. Update this README

---

*For more information, see the main [README.md](../README.md)*
