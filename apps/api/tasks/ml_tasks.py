"""
🤖 Celery Tasks para Machine Learning Inteligente
Tasks que fazem o sistema ficar mais inteligente automaticamente
"""

import logging
from celery import current_app
from database.connection import get_db

# Importar nossos sistemas de inteligência
from ml_engine.auto_retraining import run_auto_retraining
from ml_engine.active_learning import ActiveLearningSystem
from ml_engine.feedback_integration import run_feedback_enhanced_retraining

logger = logging.getLogger(__name__)

@current_app.task(name='tasks.ml_tasks.run_auto_retraining')
def run_auto_retraining_task():
    """
    🤖 Task diário: Verifica se modelos precisam de retreinamento
    Executa automaticamente se:
    - Muitos documentos novos
    - Performance baixa
    - Muito tempo sem treinar
    """
    try:
        logger.info("🤖 Iniciando verificação de auto-retreinamento...")
        
        result = run_auto_retraining()
        
        # Log dos resultados
        for model_name, analysis in result.items():
            if analysis['should_retrain']:
                logger.info(f"✅ {model_name} foi retreinado: {analysis['reasons']}")
            else:
                logger.info(f"👍 {model_name} não precisa de retreinamento")
        
        return {
            'success': True,
            'results': result,
            'timestamp': str(datetime.now())
        }
        
    except Exception as e:
        logger.error(f"❌ Erro no auto-retreinamento: {e}")
        return {'success': False, 'error': str(e)}


@current_app.task(name='tasks.ml_tasks.identify_uncertain_cases')
def identify_uncertain_cases_task():
    """
    🤔 Task a cada 6h: Identifica casos onde modelo tem dúvida
    Cria lista de documentos para pedir feedback humano
    """
    try:
        logger.info("🤔 Identificando predições incertas...")
        
        active_learner = ActiveLearningSystem()
        
        with next(get_db()) as db:
            uncertain_cases = active_learner.identify_uncertain_predictions(db, limit=20)
        
        if uncertain_cases:
            logger.info(f"🎯 Encontrados {len(uncertain_cases)} casos incertos")
            
            # Aqui você pode enviar notificação para admin ou criar dashboard
            # Por agora, vamos só logar os casos mais incertos
            for case in uncertain_cases[:5]:  # Top 5 mais incertos
                logger.info(f"❓ {case['filename']} - confidence: {case['confidence']:.2f}")
        
        return {
            'success': True,
            'uncertain_count': len(uncertain_cases),
            'cases': uncertain_cases[:10]  # Retornar só os top 10
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao identificar casos incertos: {e}")
        return {'success': False, 'error': str(e)}


@current_app.task(name='tasks.ml_tasks.process_feedback_batch')
def process_feedback_batch_task():
    """
    📚 Task a cada 12h: Processa feedback acumulado dos usuários
    Se tem feedback suficiente, retreina modelos automaticamente
    """
    try:
        logger.info("📚 Processando batch de feedback...")
        
        from ml_engine.feedback_integration import FeedbackIntegrationSystem
        
        feedback_system = FeedbackIntegrationSystem()
        
        # Verificar se tem feedback suficiente
        stats = feedback_system.get_feedback_statistics()
        
        if stats['total_feedback'] < feedback_system.min_feedback_for_update:
            logger.info(f"📊 Feedback insuficiente: {stats['total_feedback']} < {feedback_system.min_feedback_for_update}")
            return {
                'success': True,
                'action': 'skipped',
                'reason': 'Feedback insuficiente',
                'stats': stats
            }
        
        # Tem feedback suficiente, retreinar modelos
        results = {}
        models = ['random_forest_classifier', 'gradient_boosting_regressor']
        
        for model_name in models:
            logger.info(f"🔄 Retreinando {model_name} com feedback...")
            result = run_feedback_enhanced_retraining(model_name)
            results[model_name] = result
            
            if result['success']:
                logger.info(f"✅ {model_name} retreinado com {result['feedback_samples']} feedbacks")
            else:
                logger.warning(f"⚠️ Falha no retreinamento de {model_name}: {result.get('reason', 'Unknown')}")
        
        return {
            'success': True,
            'action': 'retrained',
            'results': results,
            'stats': stats
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao processar feedback: {e}")
        return {'success': False, 'error': str(e)}


@current_app.task(name='tasks.ml_tasks.check_model_performance')
def check_model_performance_task():
    """
    📊 Task diário: Monitora performance dos modelos
    Detecta degradação e alerta se necessário
    """
    try:
        logger.info("📊 Verificando performance dos modelos...")
        
        from ml_engine.auto_retraining import AutoRetrainingSystem
        
        auto_trainer = AutoRetrainingSystem()
        performance_data = {}
        
        models = ['random_forest_classifier', 'gradient_boosting_regressor']
        
        with next(get_db()) as db:
            for model_name in models:
                current_performance = auto_trainer._get_current_performance(model_name, db)
                days_since_training = auto_trainer._days_since_last_training(model_name)
                
                performance_data[model_name] = {
                    'performance': current_performance,
                    'days_since_training': days_since_training,
                    'status': 'good' if current_performance > 0.8 else 'degraded'
                }
                
                if current_performance < 0.7:
                    logger.warning(f"⚠️ {model_name} com performance baixa: {current_performance:.2f}")
                else:
                    logger.info(f"✅ {model_name} performance: {current_performance:.2f}")
        
        return {
            'success': True,
            'performance_data': performance_data,
            'timestamp': str(datetime.now())
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao verificar performance: {e}")
        return {'success': False, 'error': str(e)}


@current_app.task(name='tasks.ml_tasks.manual_retrain_model')
def manual_retrain_model_task(model_name: str, include_feedback: bool = True):
    """
    🔧 Task manual: Retreina modelo específico
    Pode ser chamado via API admin quando necessário
    """
    try:
        logger.info(f"🔧 Retreinamento manual de {model_name}...")
        
        if include_feedback:
            # Retreinar com feedback
            result = run_feedback_enhanced_retraining(model_name)
        else:
            # Retreinar só com dados automáticos
            with next(get_db()) as db:
                from ml_engine.auto_retraining import AutoRetrainingSystem
                auto_trainer = AutoRetrainingSystem()
                result = auto_trainer._execute_retraining(model_name, db)
        
        if result['success']:
            logger.info(f"✅ Retreinamento manual de {model_name} concluído")
        else:
            logger.error(f"❌ Falha no retreinamento manual de {model_name}")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Erro no retreinamento manual: {e}")
        return {'success': False, 'error': str(e)}


# Import necessário para datetime
from datetime import datetime