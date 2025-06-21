# 📝 User & Developer Guides

*Comprehensive guides for all users and developers*

## 📋 Available Guides

### 👥 **For End Users**
- **[User Guide](user-guide.md)** - Complete end-user documentation
- **[FAQ](faq.md)** - Frequently asked questions
- **[Troubleshooting](troubleshooting.md)** - Common issues and solutions

### 👨‍💻 **For Developers**
- **[Developer Guide](developer-guide.md)** - Development environment setup
- **[API Integration](api-integration.md)** - How to integrate with the API
- **[Contributing](contributing.md)** - How to contribute to the project

## 👥 End User Guide

### Getting Started
1. **Upload PDF**: Select and upload your PDF document
2. **Wait for Processing**: System automatically processes the document
3. **View Results**: Access analysis results and insights
4. **Download Reports**: Export findings in various formats

### Features Overview

#### 📄 Document Processing
- **Automatic OCR**: Extracts text from scanned documents
- **Multi-language Support**: Processes Portuguese and English documents
- **Large File Handling**: Supports documents up to 100MB
- **Batch Processing**: Handle multiple documents simultaneously

#### 🔍 Text Analysis
- **Entity Extraction**: Finds emails, phones, CNPJ, CPF, financial values
- **Sentiment Analysis**: Determines document tone and sentiment
- **Lead Scoring**: Automatically scores business opportunities (0-100)
- **Keyword Detection**: Identifies important terms and phrases

#### 🧠 Smart Search
- **Semantic Search**: Natural language search across all documents
- **Similarity Search**: Find documents similar to selected ones
- **Filter Options**: Search by date, score, type, and other criteria
- **Real-time Results**: Instant search results as you type

#### 📊 Analytics Dashboard
- **Performance Metrics**: View processing statistics
- **Lead Analytics**: Analyze lead quality and distribution
- **Trend Analysis**: Track performance over time
- **Export Options**: Download data in CSV, PDF, or JSON formats

## 👨‍💻 Developer Guide

### Quick Start
```bash
# Clone and setup
git clone <repository-url>
cd pdf-industrial-pipeline
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Start development server
python -m uvicorn main:app --reload --port 8000
```

### Development Workflow

#### 1. **Environment Setup**
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Setup pre-commit hooks
pre-commit install

# Run tests
python -m pytest tests/ -v
```

#### 2. **Code Structure**
```
pdf-industrial-pipeline/
├── main.py              # FastAPI application
├── app/                 # Application modules
├── workers/             # Background workers
├── ml_engine/           # Machine learning components
├── embeddings/          # Vector processing
├── text_processing/     # NLP processing
├── ocr/                # OCR processing
├── utils/              # Utility functions
├── performance/        # Performance monitoring
└── tests/              # Test suite
```

#### 3. **API Development**
```python
from fastapi import FastAPI, UploadFile
from typing import Dict, Any

app = FastAPI()

@app.post("/upload")
async def upload_file(file: UploadFile) -> Dict[str, Any]:
    # File processing logic
    return {"job_id": job_id, "status": "processing"}
```

#### 4. **Testing**
```python
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_upload_endpoint():
    with open("test.pdf", "rb") as f:
        response = client.post("/upload", files={"file": f})
    assert response.status_code == 200
    assert "job_id" in response.json()
```

### Architecture Patterns

#### 1. **Worker Pattern**
```python
# workers/base_worker.py
class BaseWorker:
    def __init__(self):
        self.queue = Queue()
    
    async def process_job(self, job_id: str):
        # Processing logic
        pass
```

#### 2. **Plugin System**
```python
# Plugin interface
class ProcessorPlugin:
    def process(self, data: Any) -> Any:
        raise NotImplementedError
```

#### 3. **Configuration Management**
```python
from pydantic import BaseSettings

class Settings(BaseSettings):
    api_host: str = "localhost"
    api_port: int = 8000
    redis_url: str = "redis://localhost:6379"
    
    class Config:
        env_file = ".env"
```

## 🔧 Integration Examples

### Python Integration
```python
import requests
import asyncio
from typing import Optional

class PDFPipelineClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
    
    def upload_document(self, file_path: str) -> str:
        with open(file_path, 'rb') as f:
            response = requests.post(
                f"{self.base_url}/upload",
                files={"file": f}
            )
        return response.json()["job_id"]
    
    def get_results(self, job_id: str) -> dict:
        response = requests.get(f"{self.base_url}/job/{job_id}/ml-analysis")
        return response.json()
```

### JavaScript Integration
```javascript
class PDFPipelineAPI {
    constructor(baseURL = 'http://localhost:8000') {
        this.baseURL = baseURL;
    }

    async uploadFile(file) {
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await fetch(`${this.baseURL}/upload`, {
            method: 'POST',
            body: formData
        });
        
        return await response.json();
    }

    async getJobStatus(jobId) {
        const response = await fetch(`${this.baseURL}/job/${jobId}/status`);
        return await response.json();
    }
}
```

## 🚨 Troubleshooting Guide

### Common Issues

#### 1. **Server Won't Start**
```bash
# Check Python version
python --version  # Should be 3.11+

# Check dependencies
pip list | grep fastapi

# Check ports
lsof -i :8000

# Solution
pkill -f uvicorn  # Kill existing processes
python -m uvicorn main:app --reload --port 8000
```

#### 2. **File Upload Fails**
- **Check file size**: Maximum 100MB
- **Check file type**: Only PDF files accepted
- **Check permissions**: Ensure write access to uploads/ directory
- **Check disk space**: Ensure sufficient storage

#### 3. **Processing Errors**
```bash
# Check Redis connection
redis-cli ping

# Check logs
tail -f logs/app.log

# Check worker status
curl http://localhost:8000/performance/parallel/stats
```

#### 4. **Memory Issues**
```bash
# Monitor memory usage
free -h
htop

# Adjust worker settings
export MAX_WORKERS=4
export WORKER_MEMORY_LIMIT=2GB
```

### Debug Tools

#### 1. **API Testing**
```bash
# Health check
curl http://localhost:8000/health

# Upload test
curl -X POST "http://localhost:8000/upload" \
  -F "file=@test.pdf"

# Check job status
curl "http://localhost:8000/job/{job_id}/status"
```

#### 2. **Performance Monitoring**
```bash
# System health
curl http://localhost:8000/performance/system/health

# Cache statistics
curl http://localhost:8000/performance/cache/stats

# Worker statistics
curl http://localhost:8000/performance/parallel/stats
```

#### 3. **Log Analysis**
```bash
# Real-time logs
tail -f logs/app.log

# Error logs
grep ERROR logs/app.log

# Performance logs
grep "Processing time" logs/app.log
```

## 📊 Best Practices

### Development
- **Use type hints**: All functions should include type annotations
- **Write tests**: Aim for >80% code coverage
- **Follow PEP 8**: Use black for code formatting
- **Document code**: Include docstrings for all functions
- **Use async/await**: For I/O operations

### Performance
- **Cache frequently accessed data**: Use Redis caching
- **Optimize database queries**: Use proper indexing
- **Monitor resource usage**: Set up alerting
- **Profile code**: Use cProfile for bottlenecks
- **Batch operations**: Process multiple items together

### Security
- **Validate all inputs**: Sanitize user data
- **Use HTTPS in production**: Enable SSL/TLS
- **Implement rate limiting**: Prevent abuse
- **Log security events**: Monitor for attacks
- **Keep dependencies updated**: Regular security updates

## 📚 Additional Resources

### Learning Materials
- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **Redis Documentation**: https://redis.io/documentation
- **Docker Guide**: https://docs.docker.com/
- **Python Testing**: https://pytest.org/

### Community
- **GitHub Issues**: Report bugs and request features
- **Discussions**: Ask questions and share ideas
- **Stack Overflow**: Tag questions with `pdf-industrial-pipeline`
- **Discord/Slack**: Real-time community chat

### Support
- **Documentation**: This comprehensive guide
- **API Reference**: Interactive API docs at `/docs`
- **Examples**: Sample code and integrations
- **Professional Support**: Enterprise support available 