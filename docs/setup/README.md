# 🔧 Setup & Configuration

*Complete installation and configuration guides*

## 📋 Setup Documentation

### 🚀 Quick Start
- **[Installation Guide](installation.md)** - Step-by-step installation instructions
- **[Configuration Guide](configuration.md)** - Environment variables and settings
- **[Docker Setup](docker.md)** - Container deployment guide

## 🛠️ Installation Options

### Option 1: Local Development
```bash
# Clone repository
git clone <repo-url>
cd pdf-industrial-pipeline

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# or .venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Start services
python -m uvicorn main:app --reload --port 8000
```

### Option 2: Docker Deployment
```bash
# Using Docker Compose
docker-compose up -d

# Or build from source
docker build -t pdf-pipeline .
docker run -p 8000:8000 pdf-pipeline
```

## 📋 Prerequisites

### System Requirements
- **OS**: macOS 10.15+, Ubuntu 20.04+, Windows 10+
- **Python**: 3.11 or higher
- **Memory**: 4GB RAM minimum, 8GB recommended
- **Storage**: 10GB free space
- **Network**: Internet connection for model downloads

### Dependencies
- **Redis**: Caching and job queue
- **Tesseract**: OCR processing
- **PDF tools**: qpdf for PDF manipulation
- **Build tools**: gcc/clang for compiling packages

## ⚙️ Configuration

### Environment Variables
```bash
# Core settings
ENVIRONMENT=development
API_HOST=0.0.0.0
API_PORT=8000

# Redis configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

# Storage settings
STORAGE_PATH=./storage
UPLOAD_PATH=./uploads
MAX_FILE_SIZE=100MB

# ML settings
ML_MODEL_PATH=./models
EMBEDDING_MODEL=neuralmind/bert-base-portuguese-cased
```

### Service Configuration
```yaml
# docker-compose.yml example
services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - REDIS_HOST=redis
    depends_on:
      - redis
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
```

## 🔍 Verification

### Health Check
```bash
# Test installation
curl http://localhost:8000/health

# Expected response
{
  "status": "healthy",
  "checks": {
    "upload_directory": true,
    "temp_directory": true,
    "qpdf_available": true,
    "storage_available": true
  }
}
```

### Component Tests
```bash
# Test Redis connection
redis-cli ping

# Test Tesseract
tesseract --version

# Test Python environment
python -c "import fastapi, redis, tesseract; print('All packages available')"
```

## 🚨 Troubleshooting

### Common Issues
- **Redis connection failed**: Check if Redis is running
- **Tesseract not found**: Install with package manager
- **Permission denied**: Check file/directory permissions
- **Port already in use**: Change port or stop conflicting service
- **Model download fails**: Check internet connection

### Platform-Specific Notes

#### macOS
```bash
# Install with Homebrew
brew install redis tesseract qpdf
brew services start redis
```

#### Ubuntu/Debian
```bash
# Install with apt
sudo apt update
sudo apt install redis-server tesseract-ocr qpdf
sudo systemctl start redis
```

#### Windows
```powershell
# Install with Chocolatey
choco install redis-64 tesseract qpdf
```

## 🔒 Security Setup

### Production Considerations
- Change default passwords
- Configure firewall rules
- Enable SSL/TLS certificates
- Set up authentication tokens
- Configure CORS policies
- Enable request rate limiting

### File Permissions
```bash
# Set proper permissions
chmod 755 storage/
chmod 644 .env
chown -R app:app storage/
```

## 📊 Performance Tuning

### System Optimization
- Allocate sufficient RAM for ML models
- Use SSD storage for better I/O performance
- Configure Redis memory limits
- Optimize Python garbage collection
- Set appropriate worker processes

### Resource Monitoring
```bash
# Monitor system resources
htop
df -h
free -m
redis-cli info memory
``` 