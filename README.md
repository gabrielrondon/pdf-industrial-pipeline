# 🔧 PDF Industrial Pipeline

*Advanced PDF processing pipeline with ML-powered lead scoring and semantic search capabilities*

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104%2B-green.svg)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/your-org/pdf-industrial-pipeline.git
cd pdf-industrial-pipeline

# Install dependencies
pip install -r requirements.txt

# Start the server
python3 -m uvicorn main:app --reload --port 8000

# Visit http://localhost:8000/docs for interactive API documentation
```

## 📋 Overview

This is a comprehensive PDF processing pipeline that combines OCR, text analysis, machine learning, and semantic search to extract valuable insights from industrial documents. The system is designed for high-performance processing of large PDF documents with automated lead scoring and intelligent content analysis.

### ✨ Key Features

- **📄 PDF Processing**: Advanced PDF splitting and page extraction
- **🔍 OCR Integration**: Tesseract-powered text extraction from images
- **🧠 ML Pipeline**: Feature engineering and lead scoring models
- **🔗 Semantic Search**: BERT-based embeddings with FAISS indexing
- **⚡ High Performance**: Redis caching, parallel processing, monitoring
- **🌐 REST API**: FastAPI with comprehensive documentation
- **🐳 Docker Ready**: Production deployment with Docker Compose
- **📊 Frontend**: React-based dashboard for visualization

## 📚 Documentation

Our documentation is organized into specialized sections:

### 📖 **[Main Documentation](docs/README.md)**
Complete project documentation, architecture, and user guides

### 🔧 **Setup & Configuration**
- **[Installation Guide](docs/setup/installation.md)** - Step-by-step setup instructions
- **[Configuration](docs/setup/configuration.md)** - Environment variables and settings
- **[Docker Setup](docs/setup/docker.md)** - Container deployment guide

### 🌐 **API Documentation**
- **[Postman Setup Guide](docs/api/postman-setup-guide.md)** - Complete API testing setup
- **[API Reference](docs/api/reference.md)** - Endpoint documentation
- **[Authentication](docs/api/authentication.md)** - API security and tokens

### 🏗️ **Architecture**
- **[System Architecture](docs/architecture/pipeline_context.md)** - Overall system design
- **[Storage Implementation](docs/architecture/STORAGE_IMPLEMENTATION.md)** - Data storage patterns
- **[Performance](docs/architecture/performance.md)** - Optimization strategies

### 🧪 **Testing**
- **[Testing Guide](docs/testing/testing-guide.md)** - Test procedures and results
- **[Load Testing](docs/testing/load-testing.md)** - Performance benchmarks
- **[Stage Results](docs/testing/)** - Historical test results

### 🚀 **Deployment**
- **[Production Deployment](docs/deployment/production.md)** - Production setup guide
- **[Stage Completion Reports](docs/deployment/)** - Deployment milestones
- **[Monitoring](docs/deployment/monitoring.md)** - System monitoring setup

### 📝 **Guides**
- **[User Guide](docs/guides/user-guide.md)** - End-user documentation
- **[Developer Guide](docs/guides/developer-guide.md)** - Development setup
- **[Troubleshooting](docs/guides/troubleshooting.md)** - Common issues and solutions

## 🛠️ Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Backend** | FastAPI + Python 3.11+ | REST API and core processing |
| **ML/NLP** | SentenceTransformers, FAISS | Semantic search and embeddings |
| **OCR** | Tesseract | Text extraction from images |
| **Database** | Redis | Caching and job queue |
| **Frontend** | React + Tailwind CSS | User interface |
| **Storage** | Local/Cloud Storage | File and data persistence |
| **Monitoring** | Prometheus + Custom metrics | Performance monitoring |
| **Deployment** | Docker + Docker Compose | Containerized deployment |

## ⚡ Quick API Test

```bash
# Check server health
curl http://localhost:8000/health

# Upload a PDF file
curl -X POST "http://localhost:8000/upload" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@your-document.pdf"
```

## 📊 Project Status

- ✅ **Stage 1-6**: Core pipeline implementation
- ✅ **Stage 7**: Frontend integration
- ✅ **Stage 8**: Production deployment
- 🔄 **Stage 9**: Advanced ML features (in progress)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- 📖 **Documentation**: [docs/](docs/)
- 🐛 **Issues**: [GitHub Issues](https://github.com/your-org/pdf-industrial-pipeline/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/your-org/pdf-industrial-pipeline/discussions)
- 📧 **Contact**: your-email@domain.com

---

**Built with ❤️ for efficient industrial document processing** 