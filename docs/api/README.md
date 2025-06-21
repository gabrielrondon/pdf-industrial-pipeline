# 🌐 API Documentation

*Complete API reference and integration guides*

## 📋 Available Documentation

### 🚀 Quick Start
- **[Postman Setup Guide](postman-setup-guide.md)** - Complete step-by-step Postman configuration with automation
- **[API Reference](reference.md)** - Comprehensive endpoint documentation
- **[Authentication](authentication.md)** - Security and token management

### 📊 Core Endpoints

#### File Processing
- `POST /upload` - Upload PDF files for processing
- `GET /job/{job_id}/status` - Check processing status
- `GET /job/{job_id}/manifest` - Get job details and metadata
- `DELETE /job/{job_id}` - Clean up job files

#### Text & Analysis
- `POST /process-text/{job_id}` - Extract and analyze text
- `POST /generate-embeddings/{job_id}` - Generate semantic embeddings
- `POST /extract-features/{job_id}` - Extract ML features
- `POST /predict-leads/{job_id}` - Generate lead predictions

#### Search & Discovery
- `POST /search/semantic` - Natural language semantic search
- `GET /search/leads` - Find high-scoring leads
- `GET /search/similar/{job_id}` - Find similar documents

#### System & Monitoring
- `GET /health` - System health check
- `GET /performance/system/health` - Detailed system metrics
- `GET /performance/cache/stats` - Cache performance statistics

## 🔧 Integration Examples

### Python
```python
import requests

# Upload document
with open('document.pdf', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/upload',
        files={'file': f}
    )
job_id = response.json()['job_id']

# Process and get results
requests.post(f'http://localhost:8000/process-text/{job_id}')
requests.post(f'http://localhost:8000/predict-leads/{job_id}')
```

### JavaScript
```javascript
// Upload with fetch
const formData = new FormData();
formData.append('file', fileInput.files[0]);

fetch('/upload', {
    method: 'POST',
    body: formData
}).then(response => response.json())
  .then(data => console.log('Job ID:', data.job_id));
```

### cURL
```bash
# Upload and process pipeline
curl -X POST "http://localhost:8000/upload" -F "file=@document.pdf"
curl -X POST "http://localhost:8000/process-text/{job_id}"
curl -X POST "http://localhost:8000/predict-leads/{job_id}"
```

## 📝 API Standards

- **REST Architecture**: Standard HTTP methods and status codes
- **JSON Responses**: All responses in JSON format
- **File Uploads**: Multipart form-data for file uploads
- **Error Handling**: Detailed error messages with HTTP status codes
- **Rate Limiting**: Built-in protection against abuse
- **Versioning**: API version in URL path

## 🔒 Security

- **Input Validation**: All inputs validated and sanitized
- **File Type Checking**: Only PDF files accepted
- **Size Limits**: Maximum file size restrictions
- **CORS**: Configurable cross-origin resource sharing
- **Authentication**: Token-based authentication (optional)

## 📊 Performance

- **Response Times**: < 100ms for most endpoints
- **File Processing**: ~2 pages/second average
- **Concurrent Requests**: 50+ simultaneous jobs
- **Caching**: Redis-based response caching
- **Load Balancing**: Horizontal scaling support 