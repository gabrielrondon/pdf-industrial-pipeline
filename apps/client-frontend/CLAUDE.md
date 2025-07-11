# CLAUDE.md - CLIENT FRONTEND

This file provides guidance to Claude Code (claude.ai/code) when working with the client frontend of this repository.

## Project Overview

PDF Industrial Pipeline Client Frontend - React/TypeScript application for analyzing Brazilian judicial auction documents. **Uses Railway API as primary backend**, with Supabase only for authentication, profiles, and subscription management.

## Common Commands

```bash
# Development
npm run dev          # Start development server on localhost:8080
npm run build        # Production build
npm run build:dev    # Development build
npm run lint         # Run ESLint
npm run preview      # Preview production build

# Supabase (if working locally)
supabase start                    # Start local Supabase
supabase functions serve         # Serve Edge functions locally
supabase functions secrets set   # Set environment variables for functions
```

## Architecture

### Frontend Stack
- **React 18** with TypeScript and Vite
- **UI Components**: shadcn/ui (Radix UI + Tailwind CSS)
- **State Management**: React Context for Auth, Document, and Plan state
- **Data Fetching**: React Query (@tanstack/react-query)
- **Routing**: React Router v6
- **Forms**: React Hook Form with Zod validation

### Backend Architecture
**PRIMARY: Railway API (PostgreSQL + FastAPI)**
- **Database**: PostgreSQL with comprehensive models (Job, User, TextAnalysis, MLPrediction, JudicialAnalysis)
- **Processing**: 7-stage PDF pipeline with ML/AI capabilities
- **Storage**: File uploads and document processing
- **APIs**: FastAPI with async/await, comprehensive endpoints

**SECONDARY: Supabase (Auth + UI Support Only)**
- **Authentication**: Supabase Auth with persistent sessions
- **Profiles**: User profiles, credits, subscription management
- **Payments**: Stripe integration via Edge Functions
- **Edge Functions**: Limited to auth/payments/credits (NOT document processing)

### Authentication System
- Context-based authentication with SSR-safe patterns
- Session persistence using Supabase client with localStorage
- Protected routes via `ProtectedRoute` wrapper component
- Recent fixes for SSR/hydration issues and session management

### Document Processing Workflow
**⚠️ IMPORTANT: ALL DOCUMENT PROCESSING VIA RAILWAY API**
1. PDF upload via `railwayApi.uploadDocument()` → Railway FastAPI
2. Processing via Railway's 7-stage pipeline (ingestion → chunking → OCR → NLP → ML → judicial analysis → delivery)
3. Status monitoring via `railwayApi.getJobStatus(jobId)`
4. Results retrieved from Railway PostgreSQL database
5. UI displays results via `getUserDocuments()` → Railway API

**Document display flow:**
- `SimpleDocumentUploader` → Railway API upload
- `useDocumentUpload` hook → Railway API processing  
- `SupabaseService.getUserDocuments()` → **FETCHES FROM RAILWAY** (not Supabase)
- `getDashboardStats()` → **FETCHES FROM RAILWAY** (not Supabase)

### Payment System
- Stripe integration with subscription tiers: Free, Pro (R$39), Premium (R$99)
- Credit-based usage system with earning/spending tracking
- Plan management with feature gates and usage limits
- Automated billing with proration calculations

## Key Contexts

- **AuthContext**: User authentication state, session management
- **DocumentContext**: Document upload/analysis state management  
- **PlanContext**: Subscription plan state and credit tracking

## Environment Variables

Required in `.env` file:
- `SUPABASE_URL`: Supabase project URL
- `SUPABASE_ANON_KEY`: Supabase anonymous key
- `SUPABASE_SERVICE_ROLE_KEY`: Supabase service role key (for Edge functions)
- `STRIPE_SECRET_KEY`: Stripe secret key

## Database Schema

**Railway PostgreSQL (PRIMARY - Document Processing):**
- `jobs`: PDF processing jobs (equivalent to documents)
- `job_chunks`: PDF page chunks for parallel processing
- `text_analyses`: NLP analysis results
- `ml_predictions`: Machine learning predictions
- `judicial_analyses`: Brazilian legal document analysis
- `embeddings`: Vector embeddings for semantic search
- `users`: Railway's own user management

**Supabase PostgreSQL (SECONDARY - Auth & UI):**
- `profiles`: User profiles with plan and credit information
- `subscriptions`: Stripe subscription management
- `credit_transactions`: Credit earning/spending tracking
- ⚠️ `documents` & `analysis_points`: **DEPRECATED** - não usar mais

## Key Features

### Semantic Search System
- AI-powered document search using OpenAI embeddings
- Fallback to text-based search when OpenAI API unavailable
- Cosine similarity calculations for relevance scoring
- Cross-document search capabilities

### Advanced Document Processing
- Background processing with job tracking
- Document chunking with intelligent segmentation
- Vector embedding generation with batch processing
- Real-time processing status updates

### Enhanced Authentication
- Password reset and change password functionality
- SSR-safe authentication patterns with proper hydration
- Session persistence and automatic recovery

## Development Notes

- Uses Vite for fast development with HMR
- Tailwind CSS with shadcn/ui component system
- PDF processing handled by `pdf-parse` library
- Vector search with OpenAI embeddings and TF-IDF fallback
- Background job processing for compute-intensive operations
- Deployment configured for Netlify (see `netlify.toml`)
- SSR-safe patterns implemented for proper hydration
- All window/localStorage access protected with `typeof window !== 'undefined'` checks