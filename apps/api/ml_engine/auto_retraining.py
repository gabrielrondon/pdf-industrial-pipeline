"""
🤖 Sistema de Retreinamento Automático
Faz os modelos ficarem mais inteligentes automaticamente
"""

import os
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import logging

from sqlalchemy.orm import Session
from database.models import Job, MLPrediction, TextAnalysis
from database.connection import get_db
from ml_engine.lead_scoring_models import RandomForestLeadScorer, GradientBoostingLeadScorer
from ml_engine.optimized_models import EnsembleModelRegistry

logger = logging.getLogger(__name__)

class AutoRetrainingSystem:
    """Sistema que faz os modelos ficarem mais inteligentes automaticamente"""
    
    def __init__(self):
        self.min_new_samples = 50  # Mínimo de novos documentos para retreinar
        self.performance_threshold = 0.85  # Se accuracy cair abaixo, retreina
        self.max_days_without_training = 30  # Máximo de dias sem treinar
        
    def should_retrain(self, model_name: str, db: Session) -> Dict[str, any]:
        """Decide se deve retreinar o modelo"""
        
        reasons = []
        
        # 1. Verificar quantidade de novos dados
        new_samples = self._count_new_samples_since_last_training(model_name, db)
        if new_samples >= self.min_new_samples:
            reasons.append(f"📊 {new_samples} novos documentos (limite: {self.min_new_samples})")
        
        # 2. Verificar performance atual
        current_performance = self._get_current_performance(model_name, db)
        if current_performance < self.performance_threshold:
            reasons.append(f"📉 Performance baixa: {current_performance:.2f} (limite: {self.performance_threshold})")
        
        # 3. Verificar tempo desde último treino
        days_since_training = self._days_since_last_training(model_name)
        if days_since_training > self.max_days_without_training:
            reasons.append(f"⏰ {days_since_training} dias sem treinar (limite: {self.max_days_without_training})")
        
        should_retrain = len(reasons) > 0
        
        return {
            'should_retrain': should_retrain,
            'reasons': reasons,
            'new_samples': new_samples,
            'current_performance': current_performance,
            'days_since_training': days_since_training
        }
    
    def _count_new_samples_since_last_training(self, model_name: str, db: Session) -> int:
        """Conta documentos novos desde último treino"""
        
        # Buscar último treino
        last_training_date = self._get_last_training_date(model_name)
        
        # Contar jobs processados desde então
        query = db.query(Job).filter(
            Job.status == 'completed',
            Job.processing_completed_at > last_training_date
        )
        
        return query.count()
    
    def _get_current_performance(self, model_name: str, db: Session) -> float:
        """Calcula performance atual do modelo"""
        
        # Buscar predições recentes (últimos 7 dias)
        week_ago = datetime.now() - timedelta(days=7)
        
        predictions = db.query(MLPrediction).filter(
            MLPrediction.model_name == model_name,
            MLPrediction.created_at > week_ago
        ).all()
        
        if not predictions:
            return 0.5  # Performance neutra se não há dados
        
        # Calcular accuracy baseado em confidence scores
        # (Em produção, você compararia com resultados reais)
        avg_confidence = sum(p.confidence or 0.5 for p in predictions) / len(predictions)
        return avg_confidence
    
    def _days_since_last_training(self, model_name: str) -> int:
        """Dias desde último treino"""
        last_training = self._get_last_training_date(model_name)
        return (datetime.now() - last_training).days
    
    def _get_last_training_date(self, model_name: str) -> datetime:
        """Busca data do último treino"""
        
        model_path = Path(f"storage/models/{model_name}/metadata.json")
        
        if model_path.exists():
            with open(model_path, 'r') as f:
                metadata = json.load(f)
                
            if metadata.get('training_history'):
                last_training = metadata['training_history'][-1]['timestamp']
                return datetime.fromisoformat(last_training.replace('Z', '+00:00'))
        
        # Se não tem histórico, assume treino muito antigo
        return datetime.now() - timedelta(days=365)
    
    def auto_retrain_if_needed(self, db: Session) -> Dict[str, any]:
        """Verifica e retreina modelos se necessário"""
        
        results = {}
        models_to_check = ['random_forest_classifier', 'gradient_boosting_regressor']
        
        for model_name in models_to_check:
            logger.info(f"🔍 Verificando modelo {model_name}...")
            
            analysis = self.should_retrain(model_name, db)
            results[model_name] = analysis
            
            if analysis['should_retrain']:
                logger.info(f"🚀 Iniciando retreinamento de {model_name}")
                logger.info(f"📋 Razões: {', '.join(analysis['reasons'])}")
                
                # Executar retreinamento
                retrain_result = self._execute_retraining(model_name, db)
                analysis['retrain_result'] = retrain_result
                
                logger.info(f"✅ Retreinamento concluído para {model_name}")
            else:
                logger.info(f"✅ Modelo {model_name} não precisa de retreinamento")
        
        return results
    
    def _execute_retraining(self, model_name: str, db: Session) -> Dict[str, any]:
        """Executa o retreinamento do modelo"""
        
        try:
            if model_name == 'random_forest_classifier':
                model = RandomForestLeadScorer()
            elif model_name == 'gradient_boosting_regressor':
                model = GradientBoostingLeadScorer()
            else:
                raise ValueError(f"Modelo desconhecido: {model_name}")
            
            # Carregar dados de treino atualizados
            training_data = self._prepare_training_data(db)
            
            # Treinar modelo
            success = model.train(training_data['features'], training_data['targets'])
            
            if success:
                # Salvar modelo atualizado
                model.save_model()
                
                return {
                    'success': True,
                    'samples_used': len(training_data['features']),
                    'timestamp': datetime.now().isoformat()
                }
            else:
                return {'success': False, 'error': 'Training failed'}
                
        except Exception as e:
            logger.error(f"❌ Erro no retreinamento: {e}")
            return {'success': False, 'error': str(e)}
    
    def _prepare_training_data(self, db: Session) -> Dict[str, List]:
        """Prepara dados de treino com documentos mais recentes"""
        
        # Buscar jobs completados com análise de texto
        jobs_with_analysis = db.query(Job, TextAnalysis).join(
            TextAnalysis, Job.id == TextAnalysis.job_id
        ).filter(
            Job.status == 'completed'
        ).limit(1000).all()  # Últimos 1000 documentos
        
        features = []
        targets = []
        
        for job, analysis in jobs_with_analysis:
            # Extrair features do documento
            feature_vector = self._extract_features(job, analysis)
            
            # Target: score baseado em resultados conhecidos
            # (Em produção, você teria labels reais de "bom/ruim negócio")
            target_score = self._calculate_target_score(job, analysis)
            
            features.append(feature_vector)
            targets.append(target_score)
        
        logger.info(f"📊 Preparados {len(features)} exemplos de treino")
        
        return {
            'features': features,
            'targets': targets
        }
    
    def _extract_features(self, job: Job, analysis: TextAnalysis) -> List[float]:
        """Extrai features de um job para treino"""
        
        # Features básicas
        features = [
            len(job.filename),  # text_length aproximado
            analysis.keywords and len(analysis.keywords) or 0,  # word_count aproximado
            analysis.entities and len(analysis.entities.get('persons', [])) or 0,  # entity_count
            0.9,  # language_confidence (assumir português)
            0.7,  # readability_score (assumir médio)
        ]
        
        # Features financeiras
        financial_data = analysis.financial_data or {}
        features.extend([
            len(financial_data.get('amounts', [])),  # money_count
            financial_data.get('total_value', 0),    # total_financial_value
            financial_data.get('max_value', 0),      # max_financial_value
        ])
        
        # Features legais (baseado em indicators)
        business_indicators = analysis.business_indicators or {}
        features.extend([
            business_indicators.get('legal_score', 0),        # legal_compliance_score
            business_indicators.get('risk_score', 0.5),       # risk_level_score
            business_indicators.get('viability_score', 0.5),  # investment_viability_score
        ])
        
        # Preencher até 40 features (como no metadata original)
        while len(features) < 40:
            features.append(0.0)
        
        return features[:40]  # Garantir exatamente 40 features
    
    def _calculate_target_score(self, job: Job, analysis: TextAnalysis) -> float:
        """Calcula score target para um documento"""
        
        # Lógica simplificada baseada em indicators
        business_indicators = analysis.business_indicators or {}
        
        legal_score = business_indicators.get('legal_score', 0.5)
        risk_score = 1.0 - business_indicators.get('risk_score', 0.5)  # Inverter risco
        viability_score = business_indicators.get('viability_score', 0.5)
        
        # Score final: média ponderada
        target = (legal_score * 0.3 + risk_score * 0.4 + viability_score * 0.3)
        
        return max(0.0, min(1.0, target))  # Clamp entre 0 e 1


# Função para usar no Celery
def run_auto_retraining():
    """Função para executar via Celery schedule"""
    
    auto_trainer = AutoRetrainingSystem()
    
    with next(get_db()) as db:
        results = auto_trainer.auto_retrain_if_needed(db)
    
    return results


if __name__ == "__main__":
    # Teste manual
    logging.basicConfig(level=logging.INFO)
    result = run_auto_retraining()
    print("🤖 Resultado do auto-retreinamento:")
    print(json.dumps(result, indent=2, default=str))