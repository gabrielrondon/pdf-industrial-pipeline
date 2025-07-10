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
@app.post("/api/v1/upload")
async def upload_file():
    return {"message": "Upload endpoint - to be implemented"}

@app.get("/api/v1/jobs/{job_id}")
async def get_job(job_id: str):
    return {"job_id": job_id, "status": "pending", "message": "Job endpoint - to be implemented"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    logger.info(f"Starting server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")