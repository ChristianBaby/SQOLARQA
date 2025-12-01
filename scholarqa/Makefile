# Makefile for ScholarQA

.PHONY: help install verify test clean run dev lint format

help:
	@echo "ScholarQA - Available commands:"
	@echo ""
	@echo "  make install    - Install dependencies"
	@echo "  make verify     - Verify installation"
	@echo "  make test       - Run tests"
	@echo "  make run        - Start web server"
	@echo "  make cli        - Open CLI help"
	@echo "  make stats      - Show system statistics"
	@echo "  make clean      - Clean cache and temporary files"
	@echo "  make lint       - Run code linters"
	@echo "  make format     - Format code"
	@echo "  make docs       - Generate documentation"
	@echo ""

install:
	@echo "Installing dependencies..."
	pip install --upgrade pip
	pip install -r requirements.txt
	@echo "✓ Installation complete"

verify:
	@echo "Verifying installation..."
	python scripts/verify_optimizations.py

test:
	@echo "Running tests..."
	pytest tests/ -v

test-cov:
	@echo "Running tests with coverage..."
	pytest tests/ -v --cov=src --cov-report=html

run:
	@echo "Starting web server..."
	python src/app.py

cli:
	@echo "Opening CLI help..."
	python src/cli.py --help

stats:
	@echo "System statistics:"
	python src/cli.py stats

clean:
	@echo "Cleaning cache and temporary files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache 2>/dev/null || true
	rm -rf htmlcov 2>/dev/null || true
	rm -rf .coverage 2>/dev/null || true
	@echo "✓ Cleanup complete"

lint:
	@echo "Running linters..."
	flake8 src/ tests/ --max-line-length=100

format:
	@echo "Formatting code..."
	black src/ tests/

type-check:
	@echo "Running type checker..."
	mypy src/

dev-setup: install
	@echo "Setting up development environment..."
	pip install black flake8 mypy pytest-cov
	@echo "✓ Development environment ready"

docs:
	@echo "Documentation available in docs/ folder"
	@echo "- docs/OPTIMIZATIONS.md"
	@echo "- docs/API.md"
	@echo "- docs/ARCHITECTURE.md"
	@echo "- docs/CONTRIBUTING.md"
