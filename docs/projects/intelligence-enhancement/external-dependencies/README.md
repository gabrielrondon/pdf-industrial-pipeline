# External Dependencies Guide

## 📋 Overview

This document details all external services, APIs, and dependencies required for the Intelligence Enhancement project. Dependencies are organized by phase and priority level.

## 🏷️ Dependency Classification

### Priority Levels
- **🔴 Critical**: Project cannot proceed without these
- **🟡 Important**: Significant impact on quality/features
- **🟢 Optional**: Nice-to-have improvements

### Implementation Phases
- **Phase 1**: Foundation Intelligence (0-3 months)
- **Phase 2**: Core Intelligence (3-6 months)  
- **Phase 3**: Advanced Features (6-12 months)

## 🔴 Phase 1 Critical Dependencies

### Google Cloud Vision API
**Purpose**: Enhanced OCR with high accuracy  
**Priority**: 🔴 Critical  
**Cost**: $150-200/month  

```bash
# Setup Instructions
1. Create Google Cloud Project
2. Enable Vision API
3. Create service account and download JSON key
4. Set environment variable: GOOGLE_APPLICATION_CREDENTIALS
```

**Configuration**:
```python
# Environment Variables
GOOGLE_VISION_API_KEY=your_api_key
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json

# Rate Limits
- 1,800 requests per minute
- 600 requests per minute per feature
- 10MB max file size
```

**Integration Code**:
```python
from google.cloud import vision

class GoogleVisionOCR:
    def __init__(self):
        self.client = vision.ImageAnnotatorClient()
        
    async def extract_text(self, image_bytes):
        image = vision.Image(content=image_bytes)
        response = self.client.text_detection(image=image)
        
        if response.error.message:
            raise Exception(f'Google Vision error: {response.error.message}')
            
        return response.text_annotations[0].description
```

### ZAP Imóveis API
**Purpose**: Real estate market data  
**Priority**: 🔴 Critical  
**Cost**: $200/month  

```bash
# Setup Instructions
1. Contact ZAP Imóveis API team
2. Sign partnership agreement
3. Obtain API credentials
4. Configure rate limiting
```

**Configuration**:
```python
# Environment Variables
ZAP_API_KEY=your_api_key
ZAP_API_ENDPOINT=https://api.zapimoveis.com.br/v2/

# Rate Limits
- 1,000 requests per hour
- 50 concurrent requests
- Property search, valuation, market trends
```

### Railway GPU Instances
**Purpose**: ML model training and inference  
**Priority**: 🔴 Critical  
**Cost**: $100-200/month  

```bash
# Setup Instructions
1. Upgrade Railway plan to Pro
2. Add GPU service to your project
3. Configure environment variables
4. Deploy ML training pipeline
```

**Configuration**:
```yaml
# railway.toml
[deploy]
runtime = "python"
gpu = true

[env]
CUDA_VERSION = "11.8"
PYTORCH_VERSION = "2.0.0"
```

## 🟡 Phase 2 Important Dependencies

### AWS Textract
**Purpose**: Advanced table and form extraction  
**Priority**: 🟡 Important  
**Cost**: $300/month  

```bash
# Setup Instructions
1. Create AWS account
2. Enable Textract service
3. Create IAM user with Textract permissions
4. Configure AWS credentials
```

**Configuration**:
```python
# Environment Variables
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1

# Rate Limits
- 15 requests per second (standard)
- 2 requests per second (async)
- 10MB max file size
```

### OpenAI GPT-4 API
**Purpose**: Legal reasoning and natural language processing  
**Priority**: 🟡 Important  
**Cost**: $150/month  

```bash
# Setup Instructions
1. Create OpenAI account
2. Add payment method
3. Generate API key
4. Set usage limits
```

**Configuration**:
```python
# Environment Variables
OPENAI_API_KEY=your_api_key
OPENAI_ORGANIZATION=your_org_id

# Rate Limits
- 3,500 requests per minute (GPT-4)
- 40,000 tokens per minute
- 200 requests per day (free tier)
```

### CNJ API Access
**Purpose**: Government legal data  
**Priority**: 🟡 Important  
**Cost**: $100/month + $1,000 setup  

```bash
# Setup Instructions
1. Contact CNJ (Conselho Nacional de Justiça)
2. Submit formal request for API access
3. Provide technical documentation
4. Complete legal compliance review
5. Sign data usage agreement
```

**Configuration**:
```python
# Environment Variables
CNJ_API_KEY=your_api_key
CNJ_API_ENDPOINT=https://api.cnj.jus.br/v1/

# Rate Limits
- 100 requests per minute
- 10,000 requests per day
- Court data, process validation
```

### JusBrasil Pro
**Purpose**: Legal database and jurisprudence  
**Priority**: 🟡 Important  
**Cost**: $200/month + $2,000 setup  

```bash
# Setup Instructions
1. Contact JusBrasil sales team
2. Choose Pro API plan
3. Complete technical integration
4. Configure search parameters
```

**Configuration**:
```python
# Environment Variables
JUSBRASIL_API_KEY=your_api_key
JUSBRASIL_ENDPOINT=https://api.jusbrasil.com.br/

# Features
- Case law search
- Legal precedent analysis
- Court decision database
- Lawyer and firm information
```

## 🟢 Phase 3 Optional Dependencies

### Azure Form Recognizer
**Purpose**: Advanced document structure analysis  
**Priority**: 🟢 Optional  
**Cost**: $200/month  

```bash
# Setup Instructions
1. Create Azure account
2. Create Form Recognizer resource
3. Configure custom models
4. Train on legal document types
```

**Configuration**:
```python
# Environment Variables
AZURE_FORM_RECOGNIZER_ENDPOINT=your_endpoint
AZURE_FORM_RECOGNIZER_KEY=your_key

# Features
- Custom model training
- Layout analysis
- Table extraction
- Key-value pair detection
```

### Serasa/SPC APIs
**Purpose**: Credit risk analysis  
**Priority**: 🟢 Optional  
**Cost**: $400/month + $5,000 setup  

```bash
# Setup Instructions
1. Contact Serasa Experian
2. Complete enterprise onboarding
3. Legal compliance review
4. Technical integration setup
```

**Configuration**:
```python
# Environment Variables
SERASA_API_KEY=your_api_key
SERASA_ENDPOINT=https://api.serasaexperian.com.br/

# Features
- CPF/CNPJ credit analysis
- Financial behavior scoring
- Risk assessment indicators
- Fraud detection
```

## 🛠️ Setup Scripts and Automation

### Automated Setup Script
```bash
#!/bin/bash
# scripts/setup_external_dependencies.sh

echo "Setting up Intelligence Enhancement external dependencies..."

# Phase 1 Setup
echo "Phase 1: Critical Dependencies"

# Google Cloud Vision
if [ -z "$GOOGLE_APPLICATION_CREDENTIALS" ]; then
    echo "❌ Google Cloud Vision not configured"
    echo "   Please set GOOGLE_APPLICATION_CREDENTIALS environment variable"
else
    echo "✅ Google Cloud Vision configured"
fi

# ZAP API
if [ -z "$ZAP_API_KEY" ]; then
    echo "❌ ZAP Imóveis API not configured"
    echo "   Please contact ZAP team for API access"
else
    echo "✅ ZAP Imóveis API configured"
    # Test API connection
    python scripts/test_zap_connection.py
fi

# Railway GPU
railway status | grep -q "gpu" && echo "✅ Railway GPU enabled" || echo "❌ Railway GPU not enabled"

# Phase 2 Setup
echo "Phase 2: Important Dependencies"

# AWS Textract
aws sts get-caller-identity > /dev/null 2>&1 && echo "✅ AWS configured" || echo "❌ AWS not configured"

# OpenAI
if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ OpenAI API not configured"
else
    echo "✅ OpenAI API configured"
    # Test API connection
    python scripts/test_openai_connection.py
fi

echo "Setup complete. Check individual service documentation for detailed configuration."
```

### Dependency Testing Scripts
```python
# scripts/test_dependencies.py
import asyncio
import os
from typing import Dict, Any

class DependencyTester:
    def __init__(self):
        self.results = {}
        
    async def test_all_dependencies(self) -> Dict[str, Any]:
        """Test all external dependencies and return status"""
        
        # Phase 1 Tests
        self.results['google_vision'] = await self.test_google_vision()
        self.results['zap_api'] = await self.test_zap_api()
        self.results['railway_gpu'] = await self.test_railway_gpu()
        
        # Phase 2 Tests
        self.results['aws_textract'] = await self.test_aws_textract()
        self.results['openai'] = await self.test_openai()
        self.results['cnj_api'] = await self.test_cnj_api()
        
        return self.results
        
    async def test_google_vision(self) -> Dict[str, Any]:
        """Test Google Cloud Vision API"""
        try:
            from google.cloud import vision
            client = vision.ImageAnnotatorClient()
            
            # Test with small image
            with open('tests/fixtures/test_document.jpg', 'rb') as f:
                image = vision.Image(content=f.read())
                response = client.text_detection(image=image)
                
            return {
                'status': 'success',
                'latency': response.response_time,
                'message': 'Google Vision API working'
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }
```

### Cost Monitoring
```python
# monitoring/cost_tracking.py
class CostMonitor:
    def __init__(self):
        self.cost_thresholds = {
            'google_vision': 200,  # USD per month
            'zap_api': 200,
            'aws_textract': 300,
            'openai': 150
        }
        
    async def check_monthly_costs(self):
        """Monitor external API costs and alert when approaching limits"""
        
        current_costs = await self.get_current_month_costs()
        alerts = []
        
        for service, cost in current_costs.items():
            threshold = self.cost_thresholds.get(service, 100)
            if cost > threshold * 0.8:  # 80% of threshold
                alerts.append({
                    'service': service,
                    'current_cost': cost,
                    'threshold': threshold,
                    'percentage': (cost / threshold) * 100
                })
                
        return alerts
```

## 📊 Cost Summary by Phase

### Phase 1 (Months 1-3)
| Service | Setup Cost | Monthly Cost | 3-Month Total |
|---------|------------|--------------|---------------|
| Google Vision API | $0 | $150 | $450 |
| ZAP Imóveis API | $500 | $200 | $1,100 |
| Railway GPU | $0 | $100 | $300 |
| **Total Phase 1** | **$500** | **$450** | **$1,850** |

### Phase 2 (Months 4-6)
| Service | Setup Cost | Monthly Cost | 3-Month Total |
|---------|------------|--------------|---------------|
| AWS Textract | $0 | $300 | $900 |
| OpenAI GPT-4 | $0 | $150 | $450 |
| CNJ API | $1,000 | $100 | $1,300 |
| JusBrasil Pro | $2,000 | $200 | $2,600 |
| **Total Phase 2** | **$3,000** | **$750** | **$5,250** |

### Phase 3 (Months 7-12)
| Service | Setup Cost | Monthly Cost | 6-Month Total |
|---------|------------|--------------|---------------|
| Azure Form Recognizer | $0 | $200 | $1,200 |
| Serasa/SPC APIs | $5,000 | $400 | $7,400 |
| Municipal APIs | $2,000 | $150 | $2,900 |
| **Total Phase 3** | **$7,000** | **$750** | **$11,500** |

### **Total External Dependencies Cost**
- **Setup Costs**: $10,500
- **Monthly Operating**: $1,950 (full deployment)
- **Annual Operating**: $23,400
- **3-Year Total**: $80,700

## 🚨 Risk Mitigation

### API Reliability
- **Multiple Providers**: Use backup APIs for critical services
- **Graceful Degradation**: Fallback to local processing when APIs fail
- **Circuit Breakers**: Prevent cascade failures
- **Caching**: Reduce API dependency with intelligent caching

### Cost Control
- **Usage Monitoring**: Real-time tracking of API usage
- **Rate Limiting**: Prevent unexpected cost spikes
- **Budget Alerts**: Automated notifications at 80% of budget
- **Optimization**: Regular review and optimization of API usage

### Compliance & Security
- **Data Privacy**: Ensure all APIs comply with LGPD
- **API Keys Management**: Secure storage and rotation
- **Audit Logging**: Track all external API calls
- **SLA Monitoring**: Monitor service availability and performance

This external dependencies guide provides the foundation for successfully integrating all required services for the Intelligence Enhancement project.