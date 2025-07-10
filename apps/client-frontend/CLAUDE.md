# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Arremate360 Lead Analyzer is a React/TypeScript application for analyzing Brazilian auction documents (editais de leilão). It uses Supabase for backend services, Stripe for payments, and offers both native rule-based analysis and AI-powered analysis using multiple models.

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

### Backend Architecture (Supabase)
- **Database**: PostgreSQL with Row Level Security and vector embeddings
- **Authentication**: Supabase Auth with persistent sessions and password reset
- **Storage**: File storage for PDF documents
- **Edge Functions**: 11 serverless functions handling business logic:
  - `analyze-document`: Document processing and AI analysis
  - `process-document-chunks`: Background document chunking and embedding generation
  - `semantic-search`: AI-powered document search using OpenAI embeddings
  - `setup-vector-tables`: Database schema setup for vector operations
  - `create-checkout`: Stripe payment initialization
  - `create-upgrade`: Plan upgrade handling
  - `customer-portal`: Stripe portal access
  - `check-subscription`: Subscription validation
  - `calculate-proration`: Billing calculations
  - `manage-credits`: Credit system operations
  - `toggle-document-privacy`: Lead sharing controls

### Authentication System
- Context-based authentication with SSR-safe patterns
- Session persistence using Supabase client with localStorage
- Protected routes via `ProtectedRoute` wrapper component
- Recent fixes for SSR/hydration issues and session management

### Document Processing Workflow
1. PDF upload to Supabase Storage
2. Choice between native analyzer (Brazilian legal documents) or AI models
3. Background processing: document chunking and embedding generation
4. Native processing uses rule-based analysis with legal citations
5. AI processing supports OpenAI, Anthropic Claude, and Mistral models
6. Semantic search capability using vector embeddings and cosine similarity
7. Results stored in `documents`, `analysis_points`, `document_chunks`, and `document_embeddings` tables
8. Real-time processing status tracking with job management
9. Automatic lead extraction and community sharing features

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

Core tables:
- `profiles`: User profiles with plan and credit information
- `documents`: Uploaded PDF documents and metadata
- `analysis_points`: Extracted analysis results and legal citations
- `document_chunks`: Text chunks for semantic search processing
- `document_embeddings`: Vector embeddings for AI-powered search
- `processing_jobs`: Background job tracking and status management

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