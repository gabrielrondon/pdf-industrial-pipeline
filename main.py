from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import uuid
import os
import logging
from typing import Optional, List
from dotenv import load_dotenv
from datetime import datetime
from dataclasses import asdict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Carregar variáveis de ambiente
load_dotenv()

# Importar nossos módulos
from workers.split_worker import split_pdf_task, pdf_split_worker
from workers.ocr_worker import ocr_worker
from workers.text_worker import text_worker
from workers.embedding_worker import embedding_worker
from utils.file_utils import validate_pdf_file, clean_filename, format_file_size
from utils.storage_manager import storage_manager
from ocr.tesseract_engine import tesseract_engine
from embeddings.embedding_engine import embedding_engine
from embeddings.vector_database import vector_db
from workers.ml_worker import ml_worker
from ml_engine.feature_engineering import feature_engineer
from ml_engine.lead_scoring_models import ensemble_model, random_forest_model, gradient_boosting_model
from performance.cache_manager import cache_manager
from performance.parallel_processor import parallel_processor
from performance.database_manager import database_manager
from performance.metrics_collector import metrics_collector, monitor_performance
from performance.monitoring import health_monitor, register_health_check
from performance.performance_utils import performance_utils

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

# ================================
# STAGE 4: EMBEDDINGS & VECTORIZATION ENDPOINTS  
# ================================

@app.post("/generate-embeddings/{job_id}")
async def generate_job_embeddings(job_id: str):
    """
    Gera embeddings para todas as análises de texto de um job (Etapa 4)
    """
    try:
        result = await embedding_worker.process_job_embeddings(job_id)
        
        return {
            "job_id": job_id,
            "status": "embeddings_processed",
            "result": result,
            "worker_stats": embedding_worker.get_worker_stats()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na geração de embeddings: {str(e)}")

@app.get("/job/{job_id}/embeddings")
async def get_job_embeddings_info(job_id: str):
    """
    Obter informações sobre embeddings de um job
    """
    try:
        info = await embedding_worker.get_job_embeddings_info(job_id)
        
        if info.get('status') == 'no_embeddings':
            raise HTTPException(status_code=404, detail=info.get('message', 'Embeddings não encontrados'))
        
        return info
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter informações de embeddings: {str(e)}")

@app.post("/search/semantic")
async def semantic_search(
    query: str,
    k: Optional[int] = 10,
    threshold: Optional[float] = 0.7,
    job_id: Optional[str] = None
):
    """
    Busca semântica por similaridade de texto
    """
    try:
        if not query or len(query.strip()) < 3:
            raise HTTPException(status_code=400, detail="Query deve ter pelo menos 3 caracteres")
        
        result = await embedding_worker.search_similar_documents(
            query_text=query,
            k=k,
            threshold=threshold,
            job_id=job_id
        )
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na busca semântica: {str(e)}")

@app.get("/search/leads")
async def search_high_score_leads(min_score: Optional[float] = 70.0):
    """
    Busca leads com alta pontuação no banco vectorial
    """
    try:
        # Buscar documentos com score alto
        high_score_docs = vector_db.search_by_lead_score(min_score)
        
        if not high_score_docs:
            return {
                "message": f"Nenhum lead encontrado com score >= {min_score}",
                "leads": [],
                "total": 0
            }
        
        # Preparar resultados
        leads = []
        for doc in high_score_docs[:50]:  # Limitar a 50 resultados
            lead_data = {
                'document_id': doc.id,
                'job_id': doc.job_id,
                'page_number': doc.page_number,
                'lead_score': doc.lead_score,
                'text_preview': doc.text[:200] + "..." if len(doc.text) > 200 else doc.text,
                'created_at': doc.created_at,
                'metadata': doc.metadata
            }
            leads.append(lead_data)
        
        return {
            "leads": leads,
            "total": len(leads),
            "min_score_used": min_score,
            "total_in_database": len(high_score_docs)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na busca de leads: {str(e)}")

@app.get("/embeddings/stats")
async def get_embeddings_stats():
    """
    Obter estatísticas do sistema de embeddings
    """
    try:
        worker_stats = embedding_worker.get_worker_stats()
        vector_db_stats = vector_db.get_stats()
        embedding_engine_info = embedding_engine.get_model_info()
        
        return {
            "worker_stats": worker_stats,
            "vector_database": vector_db_stats,
            "embedding_engine": embedding_engine_info,
            "system_status": "operational"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter estatísticas: {str(e)}")

@app.delete("/embeddings/clear")
async def clear_vector_database():
    """
    Limpar todo o banco de dados vectorial (USE COM CUIDADO!)
    """
    try:
        vector_db.clear_all()
        
        return {
            "message": "Banco de dados vectorial limpo com sucesso",
            "warning": "Todos os embeddings foram removidos permanentemente"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao limpar banco vectorial: {str(e)}")

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
            "stage_3": "✅ Text Processing & NLP (Complete)",
            "stage_4": "🚀 Embeddings & Vectorization (Ready)"
        },
        "endpoints": {
            "upload": "/upload (POST) - Upload e processamento de PDF",
            "status": "/job/{job_id}/status (GET) - Status do job",
            "manifest": "/job/{job_id}/manifest (GET) - Manifest completo",
            "cleanup": "/job/{job_id} (DELETE) - Remover arquivos do job",
            "process_text": "/process-text/{job_id} (POST) - Processar análise de texto",
            "text_analysis": "/job/{job_id}/text-analysis (GET) - Obter análise de texto",
            "text_stats": "/text-processing/stats (GET) - Estatísticas de processamento de texto",
            "generate_embeddings": "/generate-embeddings/{job_id} (POST) - Gerar embeddings",
            "job_embeddings": "/job/{job_id}/embeddings (GET) - Info embeddings do job",
            "semantic_search": "/search/semantic (POST) - Busca semântica",
            "lead_search": "/search/leads (GET) - Buscar leads alta pontuação",
            "embeddings_stats": "/embeddings/stats (GET) - Estatísticas de embeddings",
            "clear_vectors": "/embeddings/clear (DELETE) - Limpar banco vectorial",
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

# === ENDPOINTS ETAPA 5: MACHINE LEARNING & LEAD SCORING ===

@app.post("/extract-features/{job_id}")
async def extract_features(job_id: str):
    """
    Extrai features de ML das análises de texto de um job
    
    Converte análises de texto e embeddings em features estruturadas
    para uso em modelos de Machine Learning
    """
    try:
        logger.info(f"Iniciando extração de features ML para job {job_id}")
        
        result = await ml_worker.extract_features_from_job(job_id)
        
        if result['status'] == 'completed':
            return {
                "message": f"Features extraídas com sucesso para job {job_id}",
                "job_id": job_id,
                "features_extracted": result['features_extracted'],
                "statistics": result.get('feature_statistics', {}),
                "high_value_leads": result.get('high_value_leads', 0),
                "processing_time": result.get('processing_time', 0)
            }
        else:
            return {
                "message": f"Erro na extração de features: {result.get('message', 'Erro desconhecido')}",
                "job_id": job_id,
                "status": result['status'],
                "error": result.get('error')
            }
    
    except Exception as e:
        logger.error(f"Erro no endpoint de extração de features: {e}")
        raise HTTPException(status_code=500, detail=f"Erro na extração de features: {str(e)}")

@app.post("/train-models")
async def train_ml_models(
    job_ids: Optional[List[str]] = None,
    min_samples: int = 10
):
    """
    Treina modelos de Machine Learning para lead scoring
    
    Utiliza features extraídas para treinar ensemble de modelos
    incluindo Random Forest e Gradient Boosting
    """
    try:
        logger.info("Iniciando treinamento de modelos ML")
        
        result = await ml_worker.train_models(job_ids, min_samples)
        
        if result['status'] == 'completed':
            return {
                "message": "Modelos treinados com sucesso",
                "models_trained": result['models_trained'],
                "samples_used": result['samples_used'],
                "performances": result['performances'],
                "training_details": result['training_record']
            }
        elif result['status'] == 'insufficient_data':
            return {
                "message": result['message'],
                "samples_found": result['samples_found'],
                "min_samples_required": min_samples,
                "status": "insufficient_data"
            }
        else:
            return {
                "message": f"Erro no treinamento: {result.get('error', 'Erro desconhecido')}",
                "status": result['status'],
                "error": result.get('error')
            }
    
    except Exception as e:
        logger.error(f"Erro no endpoint de treinamento: {e}")
        raise HTTPException(status_code=500, detail=f"Erro no treinamento de modelos: {str(e)}")

@app.post("/predict-leads/{job_id}")
async def predict_job_leads(job_id: str):
    """
    Faz predições ML de lead scoring para um job
    
    Utiliza modelos treinados para avaliar qualidade dos leads
    identificados em cada página do documento
    """
    try:
        logger.info(f"Iniciando predições ML para job {job_id}")
        
        result = await ml_worker.predict_job_scores(job_id)
        
        if result['status'] == 'completed':
            return {
                "message": f"Predições ML completadas para job {job_id}",
                "job_id": job_id,
                "predictions": result['predictions'],
                "statistics": result['job_statistics'],
                "total_pages": result['total_pages_predicted']
            }
        elif result['status'] == 'no_features':
            return {
                "message": result['message'],
                "job_id": job_id,
                "status": "no_features",
                "suggestion": "Execute /extract-features/{job_id} primeiro"
            }
        else:
            return {
                "message": f"Erro nas predições: {result.get('error', 'Erro desconhecido')}",
                "job_id": job_id,
                "status": result['status'],
                "error": result.get('error')
            }
    
    except Exception as e:
        logger.error(f"Erro no endpoint de predições: {e}")
        raise HTTPException(status_code=500, detail=f"Erro nas predições ML: {str(e)}")

@app.get("/job/{job_id}/ml-analysis")
async def get_job_ml_analysis(job_id: str):
    """
    Retorna análise ML completa de um job
    
    Inclui features extraídas, predições e estatísticas
    """
    try:
        # Carregar features
        features = await ml_worker._load_job_features(job_id)
        
        # Carregar predições se existirem
        ml_dir = f"ml_analysis/{job_id}"
        predictions_file = f"{ml_dir}/ml_predictions.json"
        
        predictions_data = None
        if storage_manager.file_exists(predictions_file):
            predictions_data = storage_manager.load_json(predictions_file)
        
        # Carregar resumo das features
        summary_file = f"{ml_dir}/features_summary.json"
        features_summary = None
        if storage_manager.file_exists(summary_file):
            features_summary = storage_manager.load_json(summary_file)
        
        return {
            "job_id": job_id,
            "features": [asdict(f) for f in features] if features else None,
            "features_summary": features_summary,
            "predictions": predictions_data,
            "analysis_available": {
                "features_extracted": len(features) > 0,
                "predictions_made": predictions_data is not None,
                "total_pages": len(features) if features else 0
            }
        }
    
    except Exception as e:
        logger.error(f"Erro ao buscar análise ML do job {job_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Erro na análise ML: {str(e)}")

@app.get("/ml/lead-quality-analysis")
async def get_lead_quality_analysis(
    threshold_high: float = 80.0,
    threshold_medium: float = 50.0
):
    """
    Análise geral da qualidade dos leads no sistema
    
    Retorna estatísticas agregadas de todos os leads processados
    """
    try:
        result = await ml_worker.analyze_lead_quality(threshold_high, threshold_medium)
        
        if result['status'] == 'completed':
            return {
                "message": "Análise de qualidade completada",
                "analysis": result['analysis'],
                "generated_at": result['generated_at'],
                "thresholds": {
                    "high_quality": threshold_high,
                    "medium_quality": threshold_medium
                }
            }
        elif result['status'] == 'no_data':
            return {
                "message": result['message'],
                "status": "no_data",
                "suggestion": "Processe alguns documentos e execute predições primeiro"
            }
        else:
            return {
                "message": f"Erro na análise: {result.get('error', 'Erro desconhecido')}",
                "status": result['status'],
                "error": result.get('error')
            }
    
    except Exception as e:
        logger.error(f"Erro no endpoint de análise de qualidade: {e}")
        raise HTTPException(status_code=500, detail=f"Erro na análise de qualidade: {str(e)}")

@app.get("/ml/model-performance")
async def get_model_performance():
    """
    Retorna performance dos modelos ML treinados
    
    Inclui métricas de accuracy, precisão, recall e feature importance
    """
    try:
        performances = {}
        
        # Performance do ensemble
        if ensemble_model.is_trained:
            performances['ensemble'] = ensemble_model.get_model_performances()
        
        # Performance individual dos modelos
        models_info = {
            'random_forest': {
                'trained': random_forest_model.is_trained,
                'training_history': random_forest_model.training_history
            },
            'gradient_boosting': {
                'trained': gradient_boosting_model.is_trained,
                'training_history': gradient_boosting_model.training_history
            }
        }
        
        # Estatísticas do worker
        worker_stats = ml_worker.get_worker_stats()
        
        return {
            "message": "Performance dos modelos ML",
            "model_performances": performances,
            "models_info": models_info,
            "worker_statistics": worker_stats,
            "feature_engineering_stats": feature_engineer.get_feature_stats()
        }
    
    except Exception as e:
        logger.error(f"Erro ao buscar performance dos modelos: {e}")
        raise HTTPException(status_code=500, detail=f"Erro na performance dos modelos: {str(e)}")

@app.get("/ml/stats")
async def get_ml_stats():
    """
    Estatísticas gerais do módulo de Machine Learning
    
    Inclui contadores de features, predições e treinamentos
    """
    try:
        return {
            "message": "Estatísticas do módulo ML",
            "worker_stats": ml_worker.get_worker_stats(),
            "feature_engineering_stats": feature_engineer.get_feature_stats(),
            "models_status": {
                "ensemble_trained": ensemble_model.is_trained,
                "random_forest_trained": random_forest_model.is_trained,
                "gradient_boosting_trained": gradient_boosting_model.is_trained
            },
            "system_info": {
                "sklearn_available": feature_engineer.get_feature_stats().get('sklearn_available', False),
                "total_feature_categories": len(feature_engineer.business_keywords),
                "feature_importance_names": len(feature_engineer.get_feature_importance_names())
            }
        }
    
    except Exception as e:
        logger.error(f"Erro ao buscar estatísticas ML: {e}")
        raise HTTPException(status_code=500, detail=f"Erro nas estatísticas ML: {str(e)}")

# ====== STAGE 6: PERFORMANCE & SCALING ENDPOINTS ======

@app.get("/performance/cache/stats")
async def get_cache_stats():
    """
    Obter estatísticas do cache Redis
    """
    try:
        stats = cache_manager.get_stats()
        return {
            "cache_statistics": stats.__dict__,
            "cache_health": cache_manager.health_check()
        }
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas de cache: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@app.delete("/performance/cache/clear")
async def clear_cache():
    """
    Limpar todo o cache
    """
    try:
        success = cache_manager.clear_all()
        return {
            "cache_cleared": success,
            "message": "Cache limpo com sucesso" if success else "Erro ao limpar cache"
        }
    except Exception as e:
        logger.error(f"Erro ao limpar cache: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@app.get("/performance/parallel/stats")
async def get_parallel_stats():
    """
    Obter estatísticas do processamento paralelo
    """
    try:
        stats = parallel_processor.get_stats()
        return {
            "parallel_statistics": stats.__dict__,
            "parallel_health": parallel_processor.health_check()
        }
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas paralelas: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@app.get("/performance/metrics/stats")
async def get_metrics_stats():
    """
    Obter estatísticas de métricas de performance
    """
    try:
        stats = metrics_collector.get_stats()
        return {
            "metrics_statistics": stats,
            "metrics_health": metrics_collector.health_check()
        }
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas de métricas: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@app.get("/performance/system/health")
async def get_system_health():
    """
    Verificar saúde geral do sistema
    """
    try:
        # Registrar health checks dos componentes principais
        @register_health_check("redis_cache", critical=True)
        def check_cache():
            return cache_manager.health_check()
        
        @register_health_check("parallel_processor", critical=True)
        def check_parallel():
            return parallel_processor.health_check()
        
        @register_health_check("metrics_collector", critical=False)
        def check_metrics():
            return metrics_collector.health_check()
        
        @register_health_check("database_manager", critical=False)
        def check_database():
            return database_manager.health_check()
        
        # Executar health checks
        system_status = health_monitor.check_all_components()
        
        return {
            "system_status": system_status.overall_status.value,
            "uptime_seconds": system_status.uptime_seconds,
            "healthy_components": system_status.healthy_checks,
            "total_components": system_status.total_checks,
            "component_details": [
                {
                    "component": check.component,
                    "status": check.status.value,
                    "message": check.message,
                    "response_time_ms": check.response_time_ms
                }
                for check in system_status.components
            ],
            "alerts": health_monitor.get_alerts()
        }
    except Exception as e:
        logger.error(f"Erro ao verificar saúde do sistema: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@app.get("/performance/analytics")
async def get_performance_analytics():
    """
    Obter analytics de performance do sistema
    """
    try:
        # Analytics de disponibilidade
        availability_stats = health_monitor.get_availability_stats()
        
        # Resumo de performance
        performance_summary = performance_utils.get_performance_summary()
        
        # Analytics de database (se disponível)
        db_analytics = database_manager.get_pipeline_analytics()
        
        return {
            "availability_statistics": availability_stats,
            "performance_summary": performance_summary,
            "database_analytics": db_analytics,
            "generated_at": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Erro ao gerar analytics de performance: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@app.get("/performance/benchmark/{endpoint_name}")
async def benchmark_endpoint(endpoint_name: str, iterations: int = 100):
    """
    Executar benchmark de um endpoint específico
    """
    try:
        # Função de teste para benchmark
        def test_function():
            # Simular operação do endpoint
            import time
            time.sleep(0.001)  # 1ms de processamento simulado
            return {"status": "ok"}
        
        # Executar benchmark
        result = performance_utils.benchmark_function(test_function, iterations)
        
        return {
            "endpoint": endpoint_name,
            "benchmark_result": result.__dict__,
            "performance_rating": "excellent" if result.avg_time_per_iteration < 0.01 else
                                "good" if result.avg_time_per_iteration < 0.1 else
                                "needs_optimization"
        }
    except Exception as e:
        logger.error(f"Erro ao executar benchmark: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")
