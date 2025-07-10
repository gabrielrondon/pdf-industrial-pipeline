# PDF Pipeline API

Python FastAPI backend for PDF processing and analysis.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
python main.py

# Run with Celery workers (for background processing)
celery -A celery_app worker --loglevel=info
```

## API Documentation

Start the server and visit:
- Swagger UI: http://localhost:8000/docs  
- ReDoc: http://localhost:8000/redoc

## Deployment

This API is designed to be deployed on Render or similar Python hosting platforms.

## Features

- PDF processing and OCR
- Machine learning models for document analysis
- Vector embeddings and semantic search
- Background job processing with Celery
- Comprehensive API for document management