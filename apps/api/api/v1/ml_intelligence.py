"""
🧠 API Endpoints para Sistema de Inteligência ML
Permite frontend interagir com sistema de aprendizado
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from pydantic import BaseModel
import logging

from database.connection import get_db
from ml_engine.active_learning import (
    ActiveLearningSystem, 
    create_active_learning_request,
    process_active_learning_feedback
)
from ml_engine.feedback_integration import FeedbackIntegrationSystem
from tasks.ml_tasks import manual_retrain_model_task

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/ml", tags=["ML Intelligence"])


# Modelos Pydantic para requests/responses
class FeedbackRequest(BaseModel):
    job_id: str
    feedback: Dict
    
class UncertainPredictionResponse(BaseModel):
    job_id: str
    filename: str
    confidence: float
    lead_score: float
    uncertainty_reason: str
    questions: List[Dict]

class ModelStatsResponse(BaseModel):
    model_name: str
    performance: float
    days_since_training: int
    total_samples: int
    feedback_samples: int


@router.get("/uncertain-predictions", response_model=List[UncertainPredictionResponse])
async def get_uncertain_predictions(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    🤔 Busca predições onde o modelo tem dúvida
    Frontend pode mostrar estes casos para o usuário dar feedback
    """
    try:
        active_learner = ActiveLearningSystem()
        uncertain_cases = active_learner.identify_uncertain_predictions(db, limit)
        
        # Converter para formato de resposta
        responses = []
        for case in uncertain_cases:
            # Buscar perguntas para este caso
            feedback_request = create_active_learning_request(case['job_id'])
            
            responses.append(UncertainPredictionResponse(
                job_id=case['job_id'],
                filename=case['filename'],
                confidence=case['confidence'],
                lead_score=case.get('lead_score', 0.5),
                uncertainty_reason=case['uncertainty_reason'],
                questions=feedback_request.get('questions', [])
            ))
        
        return responses
        
    except Exception as e:
        logger.error(f"Erro ao buscar predições incertas: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/feedback")
async def submit_feedback(
    feedback_request: FeedbackRequest,
    db: Session = Depends(get_db)
):
    """
    📝 Recebe feedback do usuário sobre uma predição
    Sistema usa este feedback para ficar mais inteligente
    """
    try:
        result = process_active_learning_feedback(
            feedback_request.job_id,
            feedback_request.feedback
        )
        
        return {
            "message": "Feedback recebido com sucesso",
            "will_trigger_retraining": result.get('trigger_retraining', False),
            "feedback_count": result.get('feedback_count', 0)
        }
        
    except Exception as e:
        logger.error(f"Erro ao processar feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/feedback-request/{job_id}")
async def get_feedback_request(job_id: str):
    """
    📋 Busca informações formatadas para pedir feedback sobre um job específico
    """
    try:
        feedback_data = create_active_learning_request(job_id)
        
        if 'error' in feedback_data:
            raise HTTPException(status_code=404, detail=feedback_data['error'])
        
        return feedback_data
        
    except Exception as e:
        logger.error(f"Erro ao criar request de feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/model-stats")
async def get_model_statistics(db: Session = Depends(get_db)):
    """
    📊 Estatísticas dos modelos ML (performance, feedback, etc.)
    """
    try:
        from ml_engine.auto_retraining import AutoRetrainingSystem
        
        auto_trainer = AutoRetrainingSystem()
        feedback_system = FeedbackIntegrationSystem()
        
        models = ['random_forest_classifier', 'gradient_boosting_regressor']
        stats = []
        
        for model_name in models:
            # Performance atual
            performance = auto_trainer._get_current_performance(model_name, db)
            days_since_training = auto_trainer._days_since_last_training(model_name)
            new_samples = auto_trainer._count_new_samples_since_last_training(model_name, db)
            
            stats.append(ModelStatsResponse(
                model_name=model_name,
                performance=performance,
                days_since_training=days_since_training,
                total_samples=new_samples,
                feedback_samples=0  # TODO: implementar contagem de feedback por modelo
            ))
        
        # Estatísticas gerais de feedback
        feedback_stats = feedback_system.get_feedback_statistics()
        
        return {
            "models": stats,
            "feedback_statistics": feedback_stats
        }
        
    except Exception as e:
        logger.error(f"Erro ao buscar estatísticas: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/retrain/{model_name}")
async def manual_retrain(
    model_name: str,
    background_tasks: BackgroundTasks,
    include_feedback: bool = True
):
    """
    🔧 Força retreinamento manual de um modelo
    Útil para admins testarem ou forçarem atualização
    """
    try:
        if model_name not in ['random_forest_classifier', 'gradient_boosting_regressor']:
            raise HTTPException(status_code=400, detail="Modelo não suportado")
        
        # Executar retreinamento em background
        background_tasks.add_task(
            manual_retrain_model_task.delay,
            model_name,
            include_feedback
        )
        
        return {
            "message": f"Retreinamento de {model_name} iniciado",
            "include_feedback": include_feedback,
            "status": "in_progress"
        }
        
    except Exception as e:
        logger.error(f"Erro ao iniciar retreinamento: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/learning-insights")
async def get_learning_insights(db: Session = Depends(get_db)):
    """
    💡 Insights sobre o aprendizado do sistema
    Mostra como o sistema está evoluindo
    """
    try:
        feedback_system = FeedbackIntegrationSystem()
        feedback_stats = feedback_system.get_feedback_statistics()
        
        # Calcular insights
        insights = {
            "total_feedback_received": feedback_stats.get('total_feedback', 0),
            "user_satisfaction": {
                "average_rating": feedback_stats.get('average_scores', {}).get('overall_quality', 0),
                "investment_intention_rate": 0
            },
            "common_issues": feedback_stats.get('most_common_issues', {}),
            "learning_trend": "stable",  # TODO: calcular tendência real
            "model_improvements": {
                "accuracy_trend": "+2.5%",  # TODO: calcular real
                "prediction_confidence": "+5.1%"  # TODO: calcular real
            }
        }
        
        # Calcular taxa de intenção de investimento
        invest_data = feedback_stats.get('investment_intention', {'yes': 0, 'no': 0})
        total_invest_responses = invest_data['yes'] + invest_data['no']
        if total_invest_responses > 0:
            insights['user_satisfaction']['investment_intention_rate'] = \
                invest_data['yes'] / total_invest_responses * 100
        
        return insights
        
    except Exception as e:
        logger.error(f"Erro ao buscar insights: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/system-intelligence")
async def get_system_intelligence_status():
    """
    🤖 Status geral do sistema de inteligência
    Dashboard overview para admins
    """
    try:
        return {
            "auto_retraining": {
                "enabled": True,
                "last_check": "2025-01-11T10:00:00Z",  # TODO: buscar real
                "next_check": "2025-01-12T10:00:00Z"   # TODO: calcular real
            },
            "active_learning": {
                "enabled": True,
                "uncertain_predictions_count": 15,  # TODO: buscar real
                "feedback_requests_pending": 8      # TODO: buscar real
            },
            "feedback_integration": {
                "enabled": True,
                "total_feedback": 45,               # TODO: buscar real
                "processed_feedback": 32,           # TODO: buscar real
                "pending_processing": 13            # TODO: buscar real
            },
            "model_performance": {
                "random_forest": 0.87,              # TODO: buscar real
                "gradient_boosting": 0.84,          # TODO: buscar real
                "ensemble_score": 0.89               # TODO: calcular real
            }
        }
        
    except Exception as e:
        logger.error(f"Erro ao buscar status de inteligência: {e}")
        raise HTTPException(status_code=500, detail=str(e))