# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PDF Industrial Pipeline is a comprehensive monorepo containing a complete PDF document processing and analysis platform specialized for Brazilian judicial auction documents. It consists of three main applications: a customer-facing React frontend, an administrative interface, and a Python FastAPI backend with ML/AI capabilities.

## Common Development Commands

### Full Stack Development
```bash
# Install all dependencies
npm install
cd apps/api && pip install -r requirements.txt && cd ../..

# Start all applications in development
npm run dev          # Start both frontends (client on 8080, admin on 3001)
npm run dev:api      # Start Python API on port 8000 (separate terminal)

# Or start applications individually
npm run dev:client   # Client frontend only (port 8080)
npm run dev:admin    # Admin frontend only (port 3001)
npm run start:api    # Python API only (port 8000)

# Build applications
npm run build        # Build all frontends
npm run build:client # Build client frontend only
npm run build:admin  # Build admin frontend only

# Quality checks
npm run lint         # Lint all frontend code
npm run test         # Run frontend tests
```

### Python API Commands
```bash
cd apps/api

# Development server
python main_v2.py

# Run tests (located in apps/api/)
python test_pipeline.py            # Test PDF processing pipeline
python test_judicial_analysis.py   # Test judicial analysis features
python test_judicial_endpoint.py   # Test API endpoints

# Performance testing (in docs/testing/)
python docs/testing/test_stage6_performance.py
```

### Database and Background Tasks
```bash
# Database migrations (PostgreSQL with SQLAlchemy)
cd apps/api
alembic upgrade head

# Start Celery workers for background processing
celery -A celery_app worker --loglevel=info

# Redis for caching and task queues
redis-server
```

## Architecture Overview

### Monorepo Structure
- **apps/client-frontend**: Customer React app (port 8080) for document analysis
- **apps/admin-frontend**: Administrative React app (port 3001) for system management  
- **apps/api**: Python FastAPI backend (port 8000) with ML/AI processing
- **packages/**: Shared utilities and types

### Technology Stack

**Frontend (Both Apps)**:
- React 18 + TypeScript + Vite
- shadcn/ui components (Radix UI + Tailwind CSS)
- React Query for data fetching
- React Router v6 for routing
- React Hook Form + Zod validation

**Backend (Python API)**:
- FastAPI 2.0 with async/await
- SQLAlchemy ORM with PostgreSQL
- Celery + Redis for background tasks
- PyMuPDF for PDF processing
- scikit-learn for ML models
- NLTK for text processing

**Infrastructure**:
- Docker containerization
- Railway cloud deployment
- Prometheus + Grafana monitoring
- Nginx load balancing

## 7-Stage PDF Processing Pipeline

The system uses a sophisticated industrial pipeline for PDF processing:

1. **Ingestion**: Streaming upload with validation and virus scanning
2. **Chunking**: Smart page segmentation with context-preserving overlap
3. **OCR**: Multi-engine text extraction with language detection
4. **NLP**: Advanced text analysis with entity recognition
5. **ML**: Ensemble models for lead scoring and classification
6. **Judicial Analysis**: Brazilian legal document compliance checking
7. **Delivery**: Real-time results with notifications

## Key Business Logic

### Brazilian Judicial Auction Specialization
- CPC Article 889 legal compliance verification
- Property type classification (residential, commercial, rural)
- Market-based property valuation
- Risk assessment with 50+ factors
- Portuguese language optimization

### Machine Learning Pipeline
- Ensemble models: Random Forest + XGBoost + LightGBM
- ONNX optimization for 10x faster inference
- Vector embeddings for semantic search
- Feature engineering with automated selection

### Authentication & Security
- JWT token-based authentication
- API key management with scoped permissions
- Role-based access control (RBAC)
- Encryption at rest (AES-256) and in transit (TLS 1.3)

## Database Schema

**Core Models** (apps/api/database/models.py):
- `Job`: PDF processing jobs with status tracking
- `JobChunk`: PDF page chunks for parallel processing
- `User`: Authentication and user management
- `TextAnalysis`: NLP analysis results
- `MLPrediction`: Machine learning predictions
- `JudicialAnalysis`: Brazilian legal document analysis
- `Embedding`: Vector embeddings for semantic search

**Key Features**:
- PostgreSQL with full-text search (TSVECTOR)
- JSONB columns for flexible metadata storage
- UUID primary keys for scalability
- Optimized indexing for performance queries

## API Endpoints

**Core Routes** (apps/api/api/v1/):
- `POST /api/v1/jobs/upload`: PDF upload with multipart/form-data
- `GET /api/v1/jobs/{job_id}/status`: Job status tracking
- `POST /api/v1/search/semantic`: AI-powered semantic search
- `GET /api/v1/analysis/{job_id}/judicial`: Judicial analysis results
- `POST /api/v1/auth/login`: JWT authentication

**Interactive Documentation**: http://localhost:8000/docs

## Environment Configuration

### Required Environment Variables
```bash
# Database
DATABASE_URL=postgresql://user:pass@host:5432/db

# API Configuration  
SECRET_KEY=your-secret-key
API_WORKERS=4

# Storage (S3/MinIO)
STORAGE_BACKEND=s3
S3_BUCKET=pdf-pipeline-storage

# ML Configuration
MODEL_PATH=/app/models
EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
```

## Performance Targets

- **API Response Time**: <100ms (p95)
- **PDF Processing Rate**: <1 second per page
- **ML Inference**: <200ms per prediction
- **Search Latency**: <50ms semantic search
- **File Size Support**: Up to 500MB PDFs
- **Concurrent Users**: 1000+ simultaneous

## Testing Strategy

**Test Locations**:
- Unit tests: `apps/api/test_*.py`
- Performance tests: `docs/testing/test_stage6_performance.py`
- Frontend tests: `docs/testing/test_stage7_frontend.py`
- Integration tests: `docs/testing/test_documentation.py`

**Coverage Areas**:
- PDF processing pipeline validation
- Judicial analysis accuracy
- API endpoint functionality
- ML model performance
- Authentication and security

## Monitoring & Observability

**Available Dashboards**:
- Grafana: http://localhost:3000 (metrics and business insights)
- Prometheus: http://localhost:9090 (system metrics)
- Flower: http://localhost:5555 (Celery task monitoring)

**Key Metrics**:
- Processing success rates
- Queue depths and processing times
- ML model accuracy and performance
- User engagement and conversion rates

## Development Best Practices

### Code Quality
- Follow existing patterns in component structure
- Use TypeScript strictly for type safety
- Implement proper error handling and user feedback
- Maintain consistent naming conventions

### Frontend Patterns
- Use React Context for global state (Auth, Document, Plan)
- Implement proper loading states and error boundaries
- Follow shadcn/ui component patterns
- Use React Hook Form for complex forms

### Backend Patterns
- Implement async/await for all I/O operations
- Use proper SQLAlchemy session management
- Follow FastAPI dependency injection patterns
- Implement comprehensive error handling and logging

### Security Considerations
- Never expose sensitive data in API responses
- Validate all inputs with Pydantic models
- Use proper authentication middleware
- Implement rate limiting for public endpoints

## Capacity Planning & Infrastructure

### Railway Deployment Configuration
The system is deployed on Railway **Hobby Plan** ($5/month):
- **8GB RAM / 8 vCPU per service** 
- **Capacity**: 3,000-5,000 light users or 150-250 heavy users
- **Throughput**: 15,000-25,000 files per month
- **Concurrent Processing**: 8-15 files simultaneously

**IMPORTANT**: When discussing infrastructure options, scaling decisions, or capacity planning, always reference the comprehensive analysis in `docs/architecture/CAPACITY_PLANNING_STUDY.md`. This document contains detailed breakdowns of:
- Memory usage patterns (client vs server-side processing)
- Concurrent user capacity calculations
- Storage requirements and costs
- Performance characteristics by file size
- Scaling strategies and upgrade triggers
- Revenue requirements and pricing recommendations

### Production Deployment Features
- Multi-container Docker setup
- Horizontal scaling capabilities  
- Automated health checks
- Zero-downtime deployments
- Comprehensive logging and monitoring