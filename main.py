from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import uuid
import os
from typing import Optional
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Importar nossos módulos
from workers.split_worker import split_pdf_task, pdf_split_worker
from workers.ocr_worker import ocr_worker
from workers.text_worker import text_worker
from utils.file_utils import validate_pdf_file, clean_filename, format_file_size
from utils.storage_manager import storage_manager
from ocr.tesseract_engine import tesseract_engine

app = FastAPI(
    title="PDF Industrial Pipeline",
    description="Pipeline para processamento industrial de arquivos PDF",
    version="1.0.0"
)

UPLOAD_DIR = "uploads/"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """
    Upload de arquivo PDF e início do processamento
    """
    try:
        # Validar se é PDF
        if not file.filename or not file.filename.endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Apenas arquivos PDF são permitidos")

        # Gerar job_id único
        job_id = str(uuid.uuid4())
        
        # Limpar nome do arquivo
        clean_name = clean_filename(file.filename)
        out_path = os.path.join(UPLOAD_DIR, f"{job_id}.pdf")

        # Salvar arquivo
        with open(out_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # Validar arquivo salvo
        validation = validate_pdf_file(out_path)
        if not validation["is_valid"]:
            # Remover arquivo inválido
            os.remove(out_path)
            raise HTTPException(
                status_code=400, 
                detail=f"Arquivo PDF inválido: {validation['error']}"
            )

        # Processar divisão do PDF
        result = split_pdf_task(out_path, job_id)
        
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=f"Erro no processamento: {result['error']}")

        return {
            "job_id": job_id,
            "status": "processed",
            "original_filename": clean_name,
            "file_size": format_file_size(validation["file_size"]),
            "page_count": result["page_count"],
            "output_directory": result["output_dir"],
            "manifest_path": result["manifest_path"]
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@app.get("/job/{job_id}/status")
async def get_job_status(job_id: str):
    """
    Consultar status de um job
    """
    try:
        status = pdf_split_worker.get_job_status(job_id)
        
        if not status:
            raise HTTPException(status_code=404, detail="Job não encontrado")
        
        return status
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao consultar status: {str(e)}")

@app.get("/job/{job_id}/manifest")
async def get_job_manifest(job_id: str):
    """
    Obter manifest completo de um job
    """
    try:
        manifest = pdf_split_worker.get_job_status(job_id)
        
        if not manifest:
            raise HTTPException(status_code=404, detail="Manifest não encontrado")
        
        return manifest
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter manifest: {str(e)}")

@app.delete("/job/{job_id}")
async def cleanup_job(job_id: str):
    """
    Limpar arquivos temporários de um job
    """
    try:
        success = pdf_split_worker.cleanup_job(job_id)
        
        if success:
            return {"message": f"Job {job_id} removido com sucesso"}
        else:
            raise HTTPException(status_code=404, detail="Job não encontrado ou erro na remoção")
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao remover job: {str(e)}")

@app.post("/process-text/{job_id}")
async def process_text_analysis(job_id: str):
    """
    Processa análise de texto para um job específico (Etapa 3)
    """
    try:
        # Simular resultado OCR para teste
        test_ocr_result = {
            'job_id': job_id,
            'page_number': 1,
            'text_extracted': 'Esta é uma empresa de tecnologia chamada TechSolutions Brasil Ltda. CNPJ: 12.345.678/0001-90. Contato: João Silva, telefone (11) 99999-8888, email: joao@techsolutions.com.br. Projeto de desenvolvimento de sistema de gestão empresarial no valor de R$ 250.000,00. Prazo urgente de 6 meses.',
            'confidence_avg': 85.0
        }
        
        # Processar com o text worker
        result = text_worker.process_text_job(job_id, test_ocr_result)
        
        return {
            "job_id": job_id,
            "status": "text_processed",
            "result": result,
            "processing_stats": text_worker.get_processing_stats()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no processamento de texto: {str(e)}")

@app.get("/job/{job_id}/text-analysis")
async def get_text_analysis(job_id: str):
    """
    Obter resultados da análise de texto de um job
    """
    try:
        # Verificar se existem análises de texto para o job
        text_dir = f"text_analysis/{job_id}"
        
        if not storage_manager.directory_exists(text_dir):
            raise HTTPException(status_code=404, detail="Análise de texto não encontrada para este job")
        
        # Listar arquivos de análise
        analysis_files = storage_manager.list_files(text_dir)
        
        if not analysis_files:
            raise HTTPException(status_code=404, detail="Nenhum arquivo de análise encontrado")
        
        # Carregar primeira análise como exemplo
        first_analysis_file = None
        for file_path in analysis_files:
            if file_path.endswith('_analysis.json'):
                first_analysis_file = file_path
                break
        
        if not first_analysis_file:
            raise HTTPException(status_code=404, detail="Arquivo de análise não encontrado")
        
        analysis_data = storage_manager.load_json(first_analysis_file)
        
        return {
            "job_id": job_id,
            "analysis_files": analysis_files,
            "sample_analysis": analysis_data,
            "total_files": len(analysis_files)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter análise de texto: {str(e)}")

@app.get("/text-processing/stats")
async def get_text_processing_stats():
    """
    Obter estatísticas do processamento de texto
    """
    try:
        stats = text_worker.get_processing_stats()
        
        return {
            "text_processing_stats": stats,
            "system_status": "operational"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter estatísticas: {str(e)}")

@app.get("/")
async def root():
    """
    Endpoint de saúde da API
    """
    return {
        "message": "PDF Industrial Pipeline API",
        "status": "online",
        "version": "1.0.0",
        "stages": {
            "stage_1": "✅ Ingestion & Partitioning (Complete)",
            "stage_2": "✅ OCR Processing (Complete)", 
            "stage_3": "🔄 Text Processing & NLP (In Development)"
        },
        "endpoints": {
            "upload": "/upload (POST) - Upload e processamento de PDF",
            "status": "/job/{job_id}/status (GET) - Status do job",
            "manifest": "/job/{job_id}/manifest (GET) - Manifest completo",
            "cleanup": "/job/{job_id} (DELETE) - Remover arquivos do job",
            "process_text": "/process-text/{job_id} (POST) - Processar análise de texto",
            "text_analysis": "/job/{job_id}/text-analysis (GET) - Obter análise de texto",
            "text_stats": "/text-processing/stats (GET) - Estatísticas de processamento de texto",
            "docs": "/docs - Documentação interativa"
        }
    }

@app.get("/health")
async def health_check():
    """
    Verificação de saúde do sistema
    """
    try:
        # Verificar se diretórios existem
        upload_exists = os.path.exists(UPLOAD_DIR)
        temp_exists = os.path.exists("temp_splits")
        
        # Verificar se qpdf está disponível
        import subprocess
        qpdf_result = subprocess.run(["qpdf", "--version"], capture_output=True)
        qpdf_available = qpdf_result.returncode == 0
        
        # Verificar storage
        storage_info = storage_manager.get_storage_info()
        
        return {
            "status": "healthy",
            "checks": {
                "upload_directory": upload_exists,
                "temp_directory": temp_exists,
                "qpdf_available": qpdf_available,
                "storage_available": storage_info["available"]
            },
            "storage": storage_info
        }
    
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e)
            }
        )
