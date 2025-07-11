"""
🔄 Sistema de Incorporação de Feedback
Pega feedback dos usuários e treina os modelos automaticamente
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Tuple
import numpy as np
from pathlib import Path

from sqlalchemy.orm import Session
from database.models import Job, MLPrediction, TextAnalysis
from database.connection import get_db
from ml_engine.lead_scoring_models import RandomForestLeadScorer, GradientBoostingLeadScorer

logger = logging.getLogger(__name__)

class FeedbackIntegrationSystem:
    """Sistema que incorpora feedback dos usuários no treinamento dos modelos"""
    
    def __init__(self):
        self.feedback_weight = 2.0  # Peso do feedback humano vs predições automáticas
        self.min_feedback_for_update = 20  # Mínimo de feedbacks para atualizar modelo
        
    def convert_feedback_to_training_labels(self, feedback_data: List[Dict]) -> List[Tuple[str, float]]:
        """Converte feedback dos usuários em labels de treino"""
        
        training_labels = []
        
        for feedback in feedback_data:
            job_id = feedback['job_id']
            user_responses = feedback['user_feedback']
            
            # Converter respostas do usuário em score numérico
            score = self._calculate_score_from_feedback(user_responses)
            
            training_labels.append((job_id, score))
            
            logger.debug(f"Job {job_id}: feedback convertido em score {score:.2f}")
        
        logger.info(f"📊 Convertidos {len(training_labels)} feedbacks em labels de treino")
        
        return training_labels
    
    def _calculate_score_from_feedback(self, user_responses: Dict) -> float:
        """Converte respostas do usuário em score de 0 a 1"""
        
        score_components = []
        
        # 1. Rating geral (1-5) -> 0-1
        if 'overall_quality' in user_responses:
            rating = int(user_responses['overall_quality'].split(' - ')[0])
            score_components.append((rating - 1) / 4)  # Normalizar 1-5 para 0-1
        
        # 2. Intenção de investir (sim/não) -> 1/0
        if 'would_invest' in user_responses:
            invest_score = 1.0 if user_responses['would_invest'] == 'Sim' else 0.0
            score_components.append(invest_score)
        
        # 3. Problema/oportunidade principal
        if 'main_issue' in user_responses:
            issue = user_responses['main_issue']
            if issue in ['Boa oportunidade', 'Preço atrativo', 'Localização excelente', 'Documentação completa']:
                score_components.append(0.8)  # Positivo
            elif issue in ['Preço muito alto', 'Documentação incompleta', 'Localização ruim', 'Riscos legais']:
                score_components.append(0.2)  # Negativo
        
        # 4. Validação do score do modelo
        if 'high_score_validation' in user_responses:
            if user_responses['high_score_validation'] == 'Concordo':
                score_components.append(0.9)  # Usuário confirma score alto
            else:
                score_components.append(0.3)  # Usuário discorda do score alto
                
        if 'low_score_validation' in user_responses:
            if user_responses['low_score_validation'] == 'Concordo':
                score_components.append(0.1)  # Usuário confirma score baixo
            else:
                score_components.append(0.7)  # Usuário discorda do score baixo
        
        # Calcular score final como média ponderada
        if score_components:
            final_score = sum(score_components) / len(score_components)
        else:
            final_score = 0.5  # Score neutro se não há componentes
        
        return max(0.0, min(1.0, final_score))  # Clamp entre 0 e 1
    
    def create_feedback_enhanced_training_set(self, db: Session) -> Dict[str, List]:
        """Cria conjunto de treino combinando dados automáticos + feedback humano"""
        
        # 1. Carregar feedback dos usuários
        feedback_data = self._load_feedback_data()
        feedback_labels = self.convert_feedback_to_training_labels(feedback_data)
        feedback_dict = dict(feedback_labels)
        
        # 2. Buscar todos os jobs com análises
        jobs_with_analysis = db.query(Job, TextAnalysis, MLPrediction).join(
            TextAnalysis, Job.id == TextAnalysis.job_id
        ).outerjoin(
            MLPrediction, Job.id == MLPrediction.job_id
        ).filter(
            Job.status == 'completed'
        ).all()
        
        features = []
        labels = []
        weights = []
        
        for job, analysis, prediction in jobs_with_analysis:
            # Extrair features
            feature_vector = self._extract_features_from_job(job, analysis)
            features.append(feature_vector)
            
            # Determinar label e peso
            if str(job.id) in feedback_dict:
                # Usar feedback humano (peso maior)
                label = feedback_dict[str(job.id)]
                weight = self.feedback_weight
                logger.debug(f"Job {job.id}: usando feedback humano (label={label:.2f})")
            else:
                # Usar predição automática (peso menor)
                label = prediction.lead_score if prediction and prediction.lead_score else 0.5
                weight = 1.0
                logger.debug(f"Job {job.id}: usando predição automática (label={label:.2f})")
            
            labels.append(label)
            weights.append(weight)
        
        logger.info(f"📚 Dataset criado: {len(features)} exemplos, {len(feedback_dict)} com feedback humano")
        
        return {
            'features': features,
            'labels': labels,
            'weights': weights,
            'feedback_count': len(feedback_dict)
        }
    
    def _load_feedback_data(self) -> List[Dict]:
        """Carrega dados de feedback dos arquivos"""
        
        feedback_dir = Path('storage/feedback')
        if not feedback_dir.exists():
            return []
        
        feedback_data = []
        
        for file in feedback_dir.glob('feedback_*.jsonl'):
            with open(file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        feedback_data.append(json.loads(line))
        
        return feedback_data
    
    def _extract_features_from_job(self, job: Job, analysis: TextAnalysis) -> List[float]:
        """Extrai features de um job (mesmo que auto_retraining.py)"""
        
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
        
        # Features legais
        business_indicators = analysis.business_indicators or {}
        features.extend([
            business_indicators.get('legal_score', 0),        # legal_compliance_score
            business_indicators.get('risk_score', 0.5),       # risk_level_score
            business_indicators.get('viability_score', 0.5),  # investment_viability_score
        ])
        
        # Preencher até 40 features
        while len(features) < 40:
            features.append(0.0)
        
        return features[:40]
    
    def retrain_with_feedback(self, model_name: str, db: Session) -> Dict[str, any]:
        """Retreina modelo incorporando feedback dos usuários"""
        
        try:
            logger.info(f"🔄 Iniciando retreinamento com feedback para {model_name}")
            
            # Criar dataset com feedback
            training_data = self.create_feedback_enhanced_training_set(db)
            
            if training_data['feedback_count'] < self.min_feedback_for_update:
                return {
                    'success': False,
                    'reason': f'Feedback insuficiente ({training_data[\"feedback_count\"]} < {self.min_feedback_for_update})'
                }
            
            # Carregar modelo
            if model_name == 'random_forest_classifier':
                model = RandomForestLeadScorer()
            elif model_name == 'gradient_boosting_regressor':
                model = GradientBoostingLeadScorer()
            else:
                raise ValueError(f"Modelo desconhecido: {model_name}")
            
            # Treinar com pesos (feedback humano tem mais peso)
            success = self._train_with_weights(
                model,
                training_data['features'],
                training_data['labels'],
                training_data['weights']
            )\n            \n            if success:\n                # Salvar modelo atualizado\n                model.save_model()\n                \n                # Marcar feedback como processado\n                self._mark_feedback_as_processed()\n                \n                result = {\n                    'success': True,\n                    'samples_used': len(training_data['features']),\n                    'feedback_samples': training_data['feedback_count'],\n                    'timestamp': datetime.now().isoformat()\n                }\n                \n                logger.info(f\"✅ Retreinamento com feedback concluído para {model_name}\")\n                return result\n            else:\n                return {'success': False, 'reason': 'Training failed'}\n                \n        except Exception as e:\n            logger.error(f\"❌ Erro no retreinamento com feedback: {e}\")\n            return {'success': False, 'error': str(e)}\n    \n    def _train_with_weights(self, model, features: List[List[float]], \n                          labels: List[float], weights: List[float]) -> bool:\n        \"\"\"Treina modelo com pesos para dar mais importância ao feedback humano\"\"\"\n        \n        try:\n            # Converter para numpy arrays\n            X = np.array(features)\n            y = np.array(labels)\n            sample_weight = np.array(weights)\n            \n            # Treinar modelo (a maioria dos sklearn models suporta sample_weight)\n            if hasattr(model, 'model') and hasattr(model.model, 'fit'):\n                model.model.fit(X, y, sample_weight=sample_weight)\n                model.is_trained = True\n                return True\n            else:\n                logger.warning(\"Modelo não suporta sample_weight, treinando sem pesos\")\n                return model.train(features, labels)\n                \n        except Exception as e:\n            logger.error(f\"Erro no treinamento com pesos: {e}\")\n            return False\n    \n    def _mark_feedback_as_processed(self):\n        \"\"\"Marca feedback como processado (move para arquivo de histórico)\"\"\"\n        \n        feedback_dir = Path('storage/feedback')\n        processed_dir = Path('storage/feedback/processed')\n        processed_dir.mkdir(exist_ok=True)\n        \n        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')\n        \n        for file in feedback_dir.glob('feedback_*.jsonl'):\n            if file.parent.name != 'processed':  # Não mover se já está em processed\n                new_path = processed_dir / f\"{file.stem}_processed_{timestamp}{file.suffix}\"\n                file.rename(new_path)\n                logger.info(f\"📁 Feedback movido para: {new_path}\")\n    \n    def get_feedback_statistics(self) -> Dict[str, any]:\n        \"\"\"Retorna estatísticas do feedback coletado\"\"\"\n        \n        feedback_data = self._load_feedback_data()\n        \n        if not feedback_data:\n            return {'total_feedback': 0}\n        \n        # Analisar padrões no feedback\n        stats = {\n            'total_feedback': len(feedback_data),\n            'feedback_by_month': {},\n            'average_scores': {},\n            'most_common_issues': {},\n            'investment_intention': {'yes': 0, 'no': 0}\n        }\n        \n        for feedback in feedback_data:\n            # Contagem por mês\n            month = feedback['timestamp'][:7]  # YYYY-MM\n            stats['feedback_by_month'][month] = stats['feedback_by_month'].get(month, 0) + 1\n            \n            # Análise das respostas\n            responses = feedback['user_feedback']\n            \n            if 'overall_quality' in responses:\n                rating = int(responses['overall_quality'].split(' - ')[0])\n                if 'overall_quality' not in stats['average_scores']:\n                    stats['average_scores']['overall_quality'] = []\n                stats['average_scores']['overall_quality'].append(rating)\n            \n            if 'would_invest' in responses:\n                if responses['would_invest'] == 'Sim':\n                    stats['investment_intention']['yes'] += 1\n                else:\n                    stats['investment_intention']['no'] += 1\n            \n            if 'main_issue' in responses:\n                issue = responses['main_issue']\n                stats['most_common_issues'][issue] = stats['most_common_issues'].get(issue, 0) + 1\n        \n        # Calcular médias\n        for key, values in stats['average_scores'].items():\n            stats['average_scores'][key] = sum(values) / len(values)\n        \n        return stats\n\n\n# Função para usar na API\ndef run_feedback_enhanced_retraining(model_name: str) -> Dict:\n    \"\"\"Executa retreinamento incorporando feedback dos usuários\"\"\"\n    \n    feedback_system = FeedbackIntegrationSystem()\n    \n    with next(get_db()) as db:\n        return feedback_system.retrain_with_feedback(model_name, db)\n\n\nif __name__ == \"__main__\":\n    # Teste do sistema\n    logging.basicConfig(level=logging.INFO)\n    \n    feedback_system = FeedbackIntegrationSystem()\n    \n    # Mostrar estatísticas de feedback\n    stats = feedback_system.get_feedback_statistics()\n    print(\"📊 Estatísticas de Feedback:\")\n    print(json.dumps(stats, indent=2, default=str))\n    \n    # Testar retreinamento com feedback\n    result = run_feedback_enhanced_retraining('random_forest_classifier')\n    print(\"\\n🔄 Resultado do retreinamento:\")\n    print(json.dumps(result, indent=2, default=str))"