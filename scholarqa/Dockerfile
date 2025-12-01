# Dockerfile para ScholarQA (Opcional)
FROM python:3.10-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY . .

# Crear directorios necesarios
RUN mkdir -p data/pdfs data/uploads data/vector_store models/downloaded logs

# Exponer puerto
EXPOSE 5000

# Comando por defecto
CMD ["python", "src/app.py"]
