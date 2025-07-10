# 📮 Postman Documentation

Ready-to-use Postman collections for testing the PDF Industrial Pipeline API.

## 📋 Available Collections

### Core Collections
- **[Complete Postman Guide](POSTMAN_COMPLETE_GUIDE.md)** - Full setup and usage guide
- **[Judicial Analysis Examples](POSTMAN_JUDICIAL_EXAMPLE.md)** - Specific examples for judicial document processing

## 🚀 Quick Setup

### 1. Import Collections
Download and import the Postman collections:
- `PDF_Pipeline_Complete.postman_collection.json`
- `PDF_Pipeline_Judicial.postman_collection.json`
- `PDF_Pipeline_Environment.postman_environment.json`

### 2. Configure Environment
Set up your Postman environment variables:
```json
{
    "base_url": "http://localhost:8000",
    "api_key": "your-api-key-here",
    "job_id": "{{generated_job_id}}"
}
```

### 3. Test Basic Endpoints
1. **Health Check** - Verify API is running
2. **Upload Document** - Test file upload
3. **Check Status** - Monitor processing
4. **Get Results** - Retrieve processed data

## 📚 Collection Overview

### Core API Collection
**Endpoints included:**
- Health and status checks
- Document upload and management
- Job status monitoring
- Results retrieval
- Search functionality
- Performance metrics

### Judicial Analysis Collection
**Specialized endpoints:**
- Judicial document upload
- Legal analysis processing
- Compliance verification
- Risk assessment retrieval
- Property valuation data

## 🎯 Common Testing Workflows

### Basic Document Processing
```
1. Health Check (GET /health)
2. Upload PDF (POST /api/v1/jobs/upload)
3. Check Status (GET /api/v1/jobs/{job_id}/status)
4. Get Results (GET /api/v1/jobs/{job_id}/results)
```

### Judicial Analysis Workflow
```
1. Upload Document (POST /api/v1/jobs/upload)
2. Trigger Analysis (POST /judicial-analysis/{job_id})
3. Monitor Progress (GET /judicial-analysis/{job_id})
4. Get Analysis Results (GET /judicial-analysis/{job_id}/results)
```

### Performance Testing
```
1. Upload Large Document (500MB test file)
2. Monitor Processing Time
3. Check Memory Usage (GET /metrics)
4. Verify Results Quality
```

## 🔧 Environment Variables

### Required Variables
| Variable | Description | Example |
|----------|-------------|---------|
| `base_url` | API base URL | `http://localhost:8000` |
| `api_key` | Authentication key | `your-api-key` |
| `job_id` | Current job ID | `auto-generated` |

### Optional Variables
| Variable | Description | Default |
|----------|-------------|---------|
| `timeout` | Request timeout | `30000` |
| `file_path` | Test file path | `./test_document.pdf` |
| `priority` | Job priority | `5` |

## 📊 Pre-request Scripts

### Auto-generate Job IDs
```javascript
// Generate UUID for job tracking
pm.environment.set("job_id", pm.variables.uuid());
```

### Authentication Headers
```javascript
// Set API key header
pm.request.headers.add({
    key: "X-API-Key",
    value: pm.environment.get("api_key")
});
```

## 🧪 Test Scripts

### Status Code Validation
```javascript
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});
```

### Response Time Validation
```javascript
pm.test("Response time is less than 1000ms", function () {
    pm.expect(pm.response.responseTime).to.be.below(1000);
});
```

### JSON Response Validation
```javascript
pm.test("Response has job_id", function () {
    const jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('job_id');
    pm.environment.set("job_id", jsonData.job_id);
});
```

## 🔍 Debugging Tips

### Common Issues
1. **Connection Refused** - Check if API is running on correct port
2. **File Not Found** - Verify file path in form-data
3. **Authentication Failed** - Check API key in environment
4. **Timeout Errors** - Increase timeout for large files

### Debug Workflow
1. Check Postman Console for detailed logs
2. Verify environment variables are set
3. Test individual endpoints first
4. Use smaller files for initial testing

## 📖 Related Documentation
- [API Integration Guide](../integration/API_INTEGRATION_GUIDE.md) - Complete integration workflow
- [API Reference](../api-reference/) - Detailed endpoint documentation
- [Judicial Analysis](../judicial-analysis/) - Specialized processing guides