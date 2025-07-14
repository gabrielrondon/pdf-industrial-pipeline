import os
import uuid
import uvicorn
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Create FastAPI app
app = FastAPI(title="PDF Industrial Pipeline API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
        "version": "1.0.0",
        "api_file": "main.py"
    }

@app.get("/api/v1/jobs/stats/dashboard")
async def get_dashboard_stats():
    return {
        "totalAnalyses": 25,
        "validLeads": 18,
        "sharedLeads": 7,
        "credits": 100,
        "dataSource": "demo"
    }

@app.get("/api/v1/jobs")
async def get_jobs(user_id: str = None):
    if user_id:
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
    return []

@app.post("/api/v1/upload")
async def upload_file(file: UploadFile = File(...), user_id: str = Form(...)):
    """Basic upload endpoint"""
    try:
        # Validate file type
        if not file.filename or not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
        # Generate a job ID
        job_id = str(uuid.uuid4())
        
        # Read file content for size
        file_content = await file.read()
        file_size = len(file_content)
        
        return {
            "success": True,
            "job_id": job_id,
            "message": "Arquivo processado com sucesso",
            "file_size": file_size,
            "user_id": user_id,
            "filename": file.filename
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)