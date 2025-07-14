import os
import logging
import time
import uuid
from datetime import datetime
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
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
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "api_file": "main.py"
    }

# Database import - simplified to avoid startup issues
DATABASE_AVAILABLE = False
jobs_storage = {}

print("🚀 Starting API without database dependencies for now")
print("📝 Will try to load database models after startup")

@app.get("/api/v1/jobs/stats/dashboard")
async def get_dashboard_stats():
    """Get dashboard statistics - SIMPLIFIED VERSION"""
    try:
        logger.info("📊 Getting dashboard stats - demo mode")
        return {
            "totalAnalyses": 25,
            "validLeads": 18,
            "sharedLeads": 7,
            "credits": 100,
            "documentTypes": [
                {"type": "edital", "count": 15},
                {"type": "processo", "count": 8},
                {"type": "outro", "count": 2}
            ],
            "statusDistribution": [
                {"status": "confirmado", "count": 18},
                {"status": "alerta", "count": 5},
                {"status": "não identificado", "count": 2}
            ],
            "commonIssues": [
                {"issue": "Documentação incompleta", "count": 8},
                {"issue": "Valor de avaliação divergente", "count": 5},
                {"issue": "Pendências fiscais", "count": 3}
            ],
            "monthlyAnalyses": [
                {"month": "Jan", "analyses": 2, "leads": 1},
                {"month": "Fev", "analyses": 3, "leads": 2},
                {"month": "Mar", "analyses": 4, "leads": 3},
                {"month": "Abr", "analyses": 6, "leads": 4},
                {"month": "Mai", "analyses": 5, "leads": 4},
                {"month": "Jun", "analyses": 5, "leads": 4}
            ],
            "successRate": 72.0,
            "averageProcessingTime": 2.3,
            "totalFileSize": 1024000,
            "averageConfidence": 0.87,
            "topPerformingDocumentType": "edital",
            "fromCache": False,
            "responseTimeMs": 10,
            "dataSource": "demo"
        }
    except Exception as e:
        logger.error(f"❌ Dashboard stats error: {e}")
        return {"error": str(e), "status": "failed"}

@app.get("/api/v1/jobs")
async def get_jobs(user_id: str = None):
    """Get jobs - demo mode for now"""
    try:
        logger.info(f"📋 Getting jobs for user_id: {user_id}")
        
        # Return demo data for now
        if user_id:
            logger.info(f"📄 Using demo data for user {user_id}")
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
                },
                {
                    "id": "demo-job-2", 
                    "user_id": user_id,
                    "filename": "Processo_Judicial_Demo.pdf",
                    "title": "Processo Judicial - Demo",
                    "status": "completed",
                    "created_at": "2025-07-12T15:45:00Z",
                    "page_count": 3,
                    "file_size": 856000
                }
            ]
        else:
            return []
            
    except Exception as e:
        logger.error(f"❌ Error fetching jobs: {str(e)}")
        return []

@app.get("/api/v1/jobs/{job_id}/page/{page_number}")
async def get_job_page_content(job_id: str, page_number: int):
    """Get page content"""
    try:
        logger.info(f"📄 Getting page {page_number} for job {job_id}")
        
        return {
            "page_content": f"Documento: Exemplo de conteúdo\\nPágina: {page_number}\\n\\nEste é o conteúdo extraído da página {page_number} do documento.\\n\\nConteúdo de exemplo para demonstrar a funcionalidade do visualizador de PDF.",
            "filename": "Documento.pdf",
            "total_pages": 5,
            "page_number": page_number,
            "chunk_id": f"demo-{job_id}-{page_number}"
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting page content: {str(e)}")
        return {"error": str(e)}

@app.post("/api/v1/upload")
async def upload_file(file: UploadFile = File(...), user_id: str = Form(...)):
    """Upload endpoint - demo mode for now"""
    try:
        logger.info(f"🚀 Processing upload for user: {user_id}")
        logger.info(f"📄 File: {file.filename}")
        
        # Validate file type
        if not file.filename or not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
        # Generate a job ID
        job_id = str(uuid.uuid4())
        
        # Read file content for size
        file_content = await file.read()
        file_size = len(file_content)
        
        logger.info(f"📄 File read successfully: {file_size} bytes")
        
        # Return demo response for now
        return {
            "success": True,
            "job_id": job_id,
            "message": "Arquivo processado com sucesso (demo)",
            "file_size": file_size,
            "user_id": user_id,
            "filename": file.filename
        }
        
    except Exception as e:
        logger.error(f"❌ Upload error: {str(e)}")
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    logger.info(f"Starting server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")