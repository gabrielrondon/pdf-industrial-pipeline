# 📚 Tutorials

Step-by-step guides for common tasks and workflows.

## 📋 Available Tutorials

### Navigation and Usage
- **[Documentation Navigation Guide](DOCS_NAVIGATION_GUIDE.md)** - How to navigate the FastAPI documentation interface

## 🎯 Tutorial Categories

### Getting Started Tutorials
- **API Navigation** - Understanding the interactive documentation
- **First Upload** - Your first document processing workflow
- **Basic Integration** - Simple API integration examples

### Advanced Workflows
- **Judicial Analysis** - Complete judicial document processing
- **Batch Processing** - Multiple document handling
- **Performance Optimization** - Best practices for large files

### Development Tutorials
- **Custom Integration** - Building your own client
- **Webhook Setup** - Event-driven processing (coming soon)
- **Testing Strategies** - Comprehensive API testing

## 🚀 Quick Start Tutorial

### 1. Explore the API Documentation
1. Start the API server: `python main_v2.py`
2. Open browser to: `http://localhost:8000/docs`
3. Explore the interactive Swagger interface
4. Try the health check endpoint first

### 2. Upload Your First Document
1. Use the `/api/v1/jobs/upload` endpoint
2. Select a PDF file (< 500MB)
3. Set priority level (1-10)
4. Execute and note the job ID

### 3. Monitor Processing
1. Use the job ID from step 2
2. Call `/api/v1/jobs/{job_id}/status`
3. Wait for status to change to "completed"
4. Retrieve results from `/api/v1/jobs/{job_id}/results`

### 4. Try Judicial Analysis (Optional)
1. Upload a judicial document
2. Call `/judicial-analysis/{job_id}`
3. Get specialized legal analysis results

## 📖 Learning Path

### Beginner Level
1. **[Navigation Guide](DOCS_NAVIGATION_GUIDE.md)** - Learn the documentation interface
2. **Basic API Calls** - Health check and simple uploads
3. **Status Monitoring** - Understanding job lifecycle

### Intermediate Level
1. **Judicial Analysis** - Specialized document processing
2. **Error Handling** - Managing failed uploads and timeouts
3. **Performance Tuning** - Optimizing for large files

### Advanced Level
1. **Custom Integration** - Building production clients
2. **Batch Processing** - Multiple document workflows
3. **Monitoring & Metrics** - Production deployment considerations

## 🛠️ Tutorial Tools

### Required Tools
- **Web Browser** - For interactive documentation
- **Postman or cURL** - For API testing
- **Sample PDFs** - Test documents for upload

### Optional Tools
- **Python/JavaScript** - For custom integration
- **Docker** - For containerized testing
- **Monitoring Tools** - For performance analysis

## 📊 Tutorial Examples

### Example 1: Basic Health Check
```bash
# Check if API is running
curl http://localhost:8000/health

# Expected response
{
    "status": "healthy",
    "timestamp": "2024-01-01T12:00:00Z"
}
```

### Example 2: Document Upload
```bash
# Upload a PDF document
curl -X POST "http://localhost:8000/api/v1/jobs/upload" \
  -F "file=@sample_document.pdf" \
  -F "priority=5"

# Expected response
{
    "job_id": "12345-67890-abcdef",
    "status": "processing",
    "message": "Document uploaded successfully"
}
```

### Example 3: Status Check
```bash
# Check processing status
curl "http://localhost:8000/api/v1/jobs/12345-67890-abcdef/status"

# Expected response
{
    "job_id": "12345-67890-abcdef",
    "status": "completed",
    "progress": 100,
    "results_available": true
}
```

## 🎯 Best Practices

### File Upload Tips
- Start with small files (< 10MB) for testing
- Use common PDF formats (avoid encrypted files)
- Check file permissions before upload
- Monitor processing time for large files

### API Usage Tips
- Always check health endpoint first
- Implement proper error handling
- Use appropriate timeouts
- Monitor rate limits

### Integration Tips
- Test in development environment first
- Implement retry logic for failed requests
- Cache results when appropriate
- Use environment variables for configuration

## 📖 Related Documentation
- [API Reference](../api-reference/) - Complete endpoint documentation
- [Integration Guide](../integration/) - Detailed integration workflows
- [Postman Collections](../postman/) - Ready-to-use API testing