# 🔌 Integration Documentation

Complete guides for integrating with the PDF Industrial Pipeline system.

## 📋 Available Documentation

### Core Integration Guides
- **[API Integration Guide](API_INTEGRATION_GUIDE.md)** - Complete integration workflow and examples

## 🎯 Integration Overview

The PDF Industrial Pipeline provides a comprehensive REST API for document processing and analysis integration.

### Integration Patterns
- **Synchronous Processing** - Real-time document uploads and immediate responses
- **Asynchronous Processing** - Background job processing with status polling
- **Webhook Integration** - Event-driven notifications (coming soon)
- **Batch Processing** - Multiple document processing

## 🚀 Quick Integration Steps

### 1. Basic Setup
```bash
# Base URL
API_BASE = "http://localhost:8000"

# Health check
curl ${API_BASE}/health
```

### 2. Document Upload
```bash
# Upload a PDF document
curl -X POST "${API_BASE}/api/v1/jobs/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@document.pdf" \
  -F "priority=5"
```

### 3. Monitor Processing
```bash
# Check job status
curl "${API_BASE}/api/v1/jobs/{job_id}/status"

# Get results when ready
curl "${API_BASE}/api/v1/jobs/{job_id}/results"
```

## 🔧 SDK and Libraries

### Python Integration
```python
import requests

class PDFPipelineClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    def upload_document(self, file_path, priority=5):
        with open(file_path, 'rb') as f:
            response = requests.post(
                f"{self.base_url}/api/v1/jobs/upload",
                files={"file": f},
                data={"priority": priority}
            )
        return response.json()
```

### JavaScript/Node.js Integration
```javascript
const FormData = require('form-data');
const fs = require('fs');

class PDFPipelineClient {
    constructor(baseUrl = 'http://localhost:8000') {
        this.baseUrl = baseUrl;
    }
    
    async uploadDocument(filePath, priority = 5) {
        const form = new FormData();
        form.append('file', fs.createReadStream(filePath));
        form.append('priority', priority);
        
        const response = await fetch(`${this.baseUrl}/api/v1/jobs/upload`, {
            method: 'POST',
            body: form
        });
        
        return response.json();
    }
}
```

## 🎯 Common Integration Scenarios

### Document Processing Workflow
1. **Upload Document** → Get job ID
2. **Poll Status** → Wait for completion
3. **Retrieve Results** → Get processed data
4. **Optional: Judicial Analysis** → Specialized processing

### Judicial Analysis Workflow
1. **Standard Processing** → Upload and process document
2. **Trigger Judicial Analysis** → Run specialized analysis
3. **Get Judicial Results** → Retrieve legal analysis data

## 🔒 Authentication & Security

### API Keys (Recommended)
```bash
# Include API key in headers
curl -H "X-API-Key: your-api-key" \
  "${API_BASE}/api/v1/jobs/upload"
```

### JWT Tokens
```bash
# Include JWT token in headers
curl -H "Authorization: Bearer your-jwt-token" \
  "${API_BASE}/api/v1/jobs/upload"
```

## 📊 Rate Limiting

### Default Limits
- **Upload Rate**: 100 requests/hour per API key
- **Status Polling**: 1000 requests/hour per API key
- **File Size**: 500MB maximum per upload

### Best Practices
- Implement exponential backoff for polling
- Cache results to avoid redundant requests
- Use appropriate request timeouts
- Monitor rate limit headers

## 🛠️ Error Handling

### Common Error Responses
```json
{
    "error": "FILE_TOO_LARGE",
    "message": "File exceeds maximum size limit",
    "details": {
        "max_size": "500MB",
        "received_size": "750MB"
    }
}
```

### HTTP Status Codes
- `200` - Success
- `202` - Accepted (async processing)
- `400` - Bad Request
- `401` - Unauthorized
- `413` - Payload Too Large
- `429` - Too Many Requests
- `500` - Internal Server Error

## 📖 Related Documentation
- [API Reference](../api-reference/) - Complete endpoint documentation
- [Postman Collections](../postman/) - Ready-to-use API testing
- [Judicial Analysis](../judicial-analysis/) - Specialized processing guides