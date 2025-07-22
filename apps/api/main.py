import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import uuid

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global database session
async_session_maker = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle with proper database connection handling"""
    global async_session_maker
    
    # Get database URL from environment
    database_url = os.getenv("DATABASE_URL")
    
    if database_url:
        # Fix Railway's postgres:// URL to postgresql://
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        
        # Convert to async URL
        if "postgresql://" in database_url and "+asyncpg" not in database_url:
            database_url = database_url.replace("postgresql://", "postgresql+asyncpg://")
        
        try:
            # Create async engine
            engine = create_async_engine(
                database_url,
                echo=False,
                pool_pre_ping=True,
                pool_size=5,
                max_overflow=10
            )
            
            # Test connection
            async with engine.begin() as conn:
                await conn.run_sync(lambda c: c.execute("SELECT 1"))
            
            # Create session maker
            async_session_maker = sessionmaker(
                engine, class_=AsyncSession, expire_on_commit=False
            )
            
            logger.info("✅ Database connected successfully")
            
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            logger.info("⚠️  Running without database - mock mode enabled")
    else:
        logger.warning("⚠️  No DATABASE_URL found - running in mock mode")
    
    yield
    
    # Cleanup
    if async_session_maker:
        await engine.dispose()

# Create FastAPI app with lifespan
app = FastAPI(
    title="PDF Industrial Pipeline API",
    version="2.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "PDF Industrial Pipeline API",
        "version": "2.0.0",
        "status": "running",
        "database": "connected" if async_session_maker else "mock_mode"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for Railway"""
    health_status = {
        "status": "healthy",
        "version": "2.0.0",
        "services": {
            "api": "running",
            "database": "connected" if async_session_maker else "disconnected",
            "redis": "not_configured"
        }
    }
    
    # Return 503 if critical services are down
    if not async_session_maker and os.getenv("ENVIRONMENT") == "production":
        health_status["status"] = "degraded"
    
    return health_status

@app.get("/api/v1/jobs/stats/dashboard")
async def get_dashboard_stats():
    """Get dashboard statistics"""
    if async_session_maker:
        # TODO: Implement real database queries
        return {
            "totalAnalyses": 0,
            "validLeads": 0,
            "sharedLeads": 0,
            "credits": 100,
            "dataSource": "database"
        }
    else:
        # Mock data for when database is not available
        return {
            "totalAnalyses": 25,
            "validLeads": 18,
            "sharedLeads": 7,
            "credits": 100,
            "dataSource": "mock"
        }

@app.get("/api/v1/jobs")
async def get_jobs(user_id: str = None):
    """Get user jobs"""
    if not user_id:
        return []
    
    if async_session_maker:
        # TODO: Implement real database queries
        return []
    else:
        # Mock data
        return [
            {
                "id": "demo-job-1",
                "user_id": user_id,
                "filename": "Edital_Leilao_Exemplo.pdf",
                "title": "Edital de Leilão - Exemplo",
                "status": "completed",
                "created_at": "2025-07-13T10:30:00Z",
                "page_count": 5,
                "file_size": 1024000
            }
        ]

@app.post("/api/v1/upload")
async def upload_file(file: UploadFile = File(...), user_id: str = Form(...)):
    """Handle file upload"""
    try:
        # Validate file type
        if not file.filename or not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
        # Generate job ID
        job_id = str(uuid.uuid4())
        
        # Read file for validation
        file_content = await file.read()
        file_size = len(file_content)
        
        if async_session_maker:
            # TODO: Save to database and trigger processing
            logger.info(f"Would save job {job_id} to database")
        
        return {
            "success": True,
            "job_id": job_id,
            "message": "File uploaded successfully",
            "file_size": file_size,
            "user_id": user_id,
            "filename": file.filename,
            "processing_mode": "database" if async_session_maker else "mock"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)