# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PDF Industrial Pipeline is a monorepo for processing and analyzing Brazilian judicial auction PDFs. It has three apps: customer-facing React frontend, admin React interface, and a Python FastAPI backend with ML/AI capabilities.

## Common Development Commands

### Full Stack
```bash
npm install
cd apps/api && pip install -r requirements.txt && cd ../..

npm run dev          # All three apps concurrently (client:9080, admin:9081, API:9082)
npm run dev:client   # Client only
npm run dev:admin    # Admin only
npm run dev:api      # Python API only (PORT=9082)

npm run build        # Build all frontends
npm run lint         # Lint all frontend code
```

### Python API
```bash
cd apps/api

python main.py       # Dev server

# Tests
pytest tests/unit/ -v
pytest tests/integration/ -v
pytest tests/unit/test_pipeline.py
pytest tests/unit/test_judicial_analysis.py
pytest tests/integration/test_judicial_endpoint.py

# Database & workers
alembic upgrade head
celery -A celery_app worker --loglevel=info
redis-server
```

> **No frontend test framework is configured.** Neither `apps/client-frontend` nor `apps/admin-frontend` has jest/vitest installed. `npm run test` at root will no-op for frontends.

## Architecture Overview

### Monorepo Structure
- **apps/client-frontend** (port 9080): Customer React app
- **apps/admin-frontend** (port 9081): Admin React app; Vite proxies `/api` requests to `http://localhost:9082`
- **apps/api** (port 9082): Python FastAPI backend

### Two-Backend Architecture (Critical to Understand)

The client frontend uses **two separate backends** with distinct responsibilities:

| Responsibility | Backend | Service File |
|---|---|---|
| PDF upload & processing | Railway API | `src/services/railwayApiService.ts` |
| All document data queries | Railway API | `src/services/railwayApiService.ts` |
| User auth & sessions | Supabase | `src/services/supabaseService.ts` |
| Subscriptions & credits | Supabase | `src/services/supabaseService.ts` |
| Stripe payments | Supabase Edge Functions | `supabase/functions/` |

The admin frontend uses Supabase only for admin authentication (`src/contexts/AdminAuthContext.tsx`) and communicates with the Railway API via Vite's proxy.

### Supabase Edge Functions
Located in `apps/client-frontend/supabase/functions/`. Key functions:
- `create-checkout/`, `customer-portal/` — Stripe payment integration
- `check-subscription/`, `manage-credits/` — plan management
- `process-large-document/`, `analyze-document/` — delegate heavy processing to Railway API
- `semantic-search/`, `setup-vector-tables/` — vector search setup

### Client-Side PDF Processing
Before sending to the API, the client pre-processes PDFs using utilities in `apps/client-frontend/src/utils/`:
- `pdfAnalyzer.ts` — extracts metadata and initial analysis
- `textChunking.ts` — splits text for chunked upload
- `dataTransformers.ts` — normalizes API responses for display
- `embeddingGenerator.ts` — local embedding generation

### Technology Stack
**Frontend**: React 18 + TypeScript + Vite, shadcn/ui (Radix UI + Tailwind), React Query v5, React Router v6, React Hook Form + Zod

**Backend**: FastAPI with async/await, SQLAlchemy + PostgreSQL, Celery + Redis, PyMuPDF, scikit-learn + NLTK

### 7-Stage PDF Processing Pipeline
1. **Ingestion** — Streaming upload with validation
2. **Chunking** — Smart page segmentation with overlap
3. **OCR** — Multi-engine text extraction
4. **NLP** — Text analysis with entity recognition
5. **ML** — Ensemble models (Random Forest + XGBoost + LightGBM)
6. **Judicial Analysis** — Brazilian legal compliance (CPC Art. 889)
7. **Delivery** — Real-time results with notifications

## Key File Locations

### API
- `apps/api/main.py` — FastAPI entry point
- `apps/api/config/settings.py` — Pydantic settings
- `apps/api/database/models.py` — SQLAlchemy models
- `apps/api/database/migrations/` — Alembic migrations
- `apps/api/core/exceptions.py` — Custom exception hierarchy
- `apps/api/api/v1/` — Route handlers; interactive docs at `http://localhost:9082/docs`

### Client Frontend
- `src/services/railwayApiService.ts` — All Railway API calls
- `src/services/supabaseService.ts` — All Supabase calls (auth, credits, subscriptions)
- `src/contexts/AuthContext.tsx` — Auth state
- `src/contexts/DocumentContext.tsx` — Document upload/analysis state
- `src/contexts/PlanContext.tsx` — Subscription and credit state
- `src/integrations/supabase/types.ts` — Auto-generated Supabase schema types

### Admin Frontend
- `src/contexts/AdminAuthContext.tsx` — Supabase-based admin auth
- `src/components/APITester.tsx` — Manual Railway API testing UI
- `src/components/SystemHealth.tsx` — System monitoring UI

## Environment Variables

### Client Frontend (`apps/client-frontend/.env`)
```
VITE_SUPABASE_URL=
VITE_SUPABASE_ANON_KEY=
VITE_API_BASE_URL=http://localhost:9082
```

### Admin Frontend (`apps/admin-frontend/.env`)
```
VITE_SUPABASE_URL=
VITE_SUPABASE_ANON_KEY=
VITE_API_BASE_URL=http://localhost:9082
VITE_RAILWAY_API_URL=          # Production Railway URL
VITE_ADMIN_MODE=true
```

### API (`apps/api/.env`)
```
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
SECRET_KEY=
API_PORT=9082
STORAGE_BACKEND=local|s3
S3_BUCKET=
EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
OCR_LANGUAGES=por,eng
```

## Database Schema

Core models in `apps/api/database/models.py`: `Job`, `JobChunk`, `User`, `APIKey`, `TextAnalysis`, `MLPrediction`, `JudicialAnalysis`, `Embedding`, `QualityAssessment`, `UserFeedback`.

The Supabase database (separate from Railway PostgreSQL) has an admin system schema in `apps/client-frontend/supabase/migrations/20250123_admin_system.sql`, with tables for `admin_profiles`, `admin_invitations`, `admin_sessions`, and `admin_audit_logs`.

## Deployment

Deployed on Railway Hobby Plan ($5/month, 8GB RAM / 8 vCPU per service). See `docs/architecture/CAPACITY_PLANNING_STUDY.md` for detailed scaling analysis before making infrastructure changes.

**Railway deployment** uses an optimized `apps/api/requirements.txt` (minimal dependencies). Docker multi-stage builds are configured for production.

## Active Projects

- **Intelligence Enhancement** (`docs/projects/intelligence-enhancement/`): Transforming from document processor to investment advisor; currently in Phase 1 (Foundation Intelligence)
- **Zero-Cost Improvements** (`docs/projects/zero-cost-improvements/`): 15-20% accuracy improvement using existing infrastructure only
