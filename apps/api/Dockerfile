# Stage 8: Production Deployment & DevOps - PDF Industrial Pipeline
FROM python:3.12-slim AS base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    # Essential build tools
    build-essential \
    gcc \
    g++ \
    # Tesseract OCR
    tesseract-ocr \
    tesseract-ocr-por \
    tesseract-ocr-eng \
    # PDF processing
    qpdf \
    poppler-utils \
    # Image processing
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    # System utilities
    curl \
    wget \
    git \
    # Cleanup
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create app user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# ================================
# Stage 2: Python Dependencies
# ================================
FROM base AS dependencies

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt

# Download NLTK data (handle SSL issues)
RUN python -c "import ssl; ssl._create_default_https_context = ssl._create_unverified_context; import nltk; nltk.download('punkt', quiet=True); nltk.download('stopwords', quiet=True); nltk.download('averaged_perceptron_tagger', quiet=True); nltk.download('maxent_ne_chunker', quiet=True); nltk.download('words', quiet=True)" || echo "NLTK download failed, will use fallback"

# Create model directory and pre-download BERT model
RUN mkdir -p /app/models/bert && \
    python -c "from transformers import AutoTokenizer, AutoModel; tokenizer = AutoTokenizer.from_pretrained('neuralmind/bert-base-portuguese-cased'); model = AutoModel.from_pretrained('neuralmind/bert-base-portuguese-cased'); tokenizer.save_pretrained('/app/models/bert'); model.save_pretrained('/app/models/bert')" || echo "Model download failed, will download at runtime"

# ================================
# Stage 3: Application
# ================================
FROM dependencies AS application

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p uploads temp_splits storage embeddings ml_analysis logs && \
    chown -R appuser:appuser /app

# Build frontend if it exists
RUN if [ -f "build_frontend.sh" ]; then \
        chmod +x build_frontend.sh && \
        ./build_frontend.sh || echo "Frontend build failed, using existing build"; \
    fi

# ================================
# Stage 4: Production
# ================================
FROM application AS production

# Set production environment
ENV ENVIRONMENT=production \
    PYTHONPATH=/app \
    LOG_LEVEL=INFO

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Start command
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]

# ================================
# Stage 5: Development (Default)
# ================================
FROM application AS development

# Install development dependencies
RUN pip install pytest pytest-asyncio pytest-cov black flake8 mypy

# Set development environment
ENV ENVIRONMENT=development \
    LOG_LEVEL=DEBUG

# Development command with auto-reload
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"] 