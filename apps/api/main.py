import os
import uvicorn
from fastapi import FastAPI
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

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)