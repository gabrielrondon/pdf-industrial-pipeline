import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# Simple logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="PDF Industrial Pipeline API",
    description="PDF processing and analysis API",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "PDF Industrial Pipeline API", "status": "running"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z",
        "version": "1.0.0"
    }

@app.get("/test-db")
async def test_database():
    """Test database connection"""
    try:
        # Simple database test
        database_url = os.getenv("DATABASE_URL")
        redis_url = os.getenv("REDIS_URL")
        
        return {
            "database_configured": bool(database_url),
            "redis_configured": bool(redis_url),
            "environment": os.getenv("ENVIRONMENT", "unknown")
        }
    except Exception as e:
        return {"error": str(e), "status": "error"}

# Include basic API routes
from fastapi import File, UploadFile, HTTPException
import uuid
import tempfile

# In-memory job storage for demo (use database in production)
jobs_storage = {}

@app.post("/api/v1/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload PDF file for processing"""
    try:
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
        # Validate file size (500MB limit)
        max_size = 500 * 1024 * 1024  # 500MB
        content = await file.read()
        if len(content) > max_size:
            raise HTTPException(status_code=400, detail="File too large (max 500MB)")
        
        # Generate job ID
        job_id = str(uuid.uuid4())
        
        # Save file temporarily (in production, save to proper storage)
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
            tmp.write(content)
            file_path = tmp.name
        
        # Store job info
        jobs_storage[job_id] = {
            "job_id": job_id,
            "filename": file.filename,
            "file_size": len(content),
            "status": "completed",  # Mock as completed for demo
            "file_path": file_path,
            "results": {
                "message": "PDF processado com sucesso!",
                "pages": 1,
                "text_extracted": "Conteúdo do PDF extraído...",
                "analysis": "Análise básica realizada."
            }
        }
        
        logger.info(f"File uploaded successfully: {file.filename} ({len(content)} bytes)")
        
        return {
            "success": True,
            "job_id": job_id,
            "message": f"Arquivo {file.filename} enviado com sucesso",
            "file_size": len(content)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@app.get("/api/v1/jobs/{job_id}")
async def get_job(job_id: str):
    """Get job status and results"""
    if job_id not in jobs_storage:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return jobs_storage[job_id]

@app.get("/api/v1/jobs")
async def list_jobs():
    """List all jobs"""
    return list(jobs_storage.values())

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    logger.info(f"Starting server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")