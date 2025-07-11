"""
🎯 Sistema de Active Learning
O modelo pergunta ao usuário quando tem dúvida, ficando mais inteligente
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session

from database.models import Job, MLPrediction, TextAnalysis
from database.connection import get_db

logger = logging.getLogger(__name__)

class ActiveLearningSystem:
    """Sistema que identifica quando o modelo tem dúvida e pede feedback humano"""
    
    def __init__(self):
        self.uncertainty_threshold = 0.3  # Se confidence < 30%, pedir feedback
        self.disagreement_threshold = 0.2  # Se modelos discordam >20%, pedir feedback
        self.min_samples_for_feedback = 10  # Mínimo de amostras incertas para treinar
        
    def identify_uncertain_predictions(self, db: Session, limit: int = 50) -> List[Dict]:
        """Identifica predições onde o modelo tem dúvida"""
        
        # Buscar predições recentes com baixa confidence
        uncertain_predictions = db.query(MLPrediction, Job).join(
            Job, MLPrediction.job_id == Job.id
        ).filter(
            MLPrediction.confidence < self.uncertainty_threshold
        ).order_by(
            MLPrediction.confidence.asc()  # Mais incertas primeiro
        ).limit(limit).all()
        
        uncertain_cases = []
        
        for prediction, job in uncertain_predictions:
            # Calcular disagreement entre modelos ensemble
            disagreement = self._calculate_model_disagreement(prediction.job_id, db)
            
            uncertain_cases.append({
                'job_id': str(job.id),
                'filename': job.filename,
                'confidence': prediction.confidence,
                'lead_score': prediction.lead_score,
                'disagreement': disagreement,
                'uncertainty_reason': self._get_uncertainty_reason(prediction, disagreement),
                'created_at': prediction.created_at.isoformat()
            })
        
        # Ordenar por nível de incerteza (menor confidence + maior disagreement)
        uncertain_cases.sort(key=lambda x: x['confidence'] + x['disagreement'])
        
        logger.info(f"🤔 Identificadas {len(uncertain_cases)} predições incertas")
        
        return uncertain_cases
    
    def _calculate_model_disagreement(self, job_id: str, db: Session) -> float:
        """Calcula o disagreement entre diferentes modelos para o mesmo job"""
        
        # Buscar todas as predições para este job
        predictions = db.query(MLPrediction).filter(
            MLPrediction.job_id == job_id
        ).all()
        
        if len(predictions) < 2:
            return 0.0  # Sem disagreement se só tem 1 modelo
        
        # Calcular desvio padrão dos lead_scores
        scores = [p.lead_score for p in predictions if p.lead_score is not None]
        
        if len(scores) < 2:
            return 0.0
        
        mean_score = sum(scores) / len(scores)
        variance = sum((score - mean_score) ** 2 for score in scores) / len(scores)
        std_dev = variance ** 0.5
        
        return std_dev
    
    def _get_uncertainty_reason(self, prediction: MLPrediction, disagreement: float) -> str:
        """Explica por que o modelo está incerto"""
        
        reasons = []
        
        if prediction.confidence < 0.2:
            reasons.append("Confidence muito baixa")
        elif prediction.confidence < 0.3:
            reasons.append("Confidence baixa")
            
        if disagreement > self.disagreement_threshold:
            reasons.append("Modelos discordam")
            
        if 0.4 < prediction.lead_score < 0.6:
            reasons.append("Score próximo da fronteira")
            
        return "; ".join(reasons) if reasons else "Incerteza geral"
    
    def create_feedback_request(self, job_id: str, db: Session) -> Dict:
        """Cria uma solicitação de feedback para o usuário"""
        
        # Buscar informações do job
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            return {'error': 'Job não encontrado'}
        
        # Buscar análise existente
        analysis = db.query(TextAnalysis).filter(
            TextAnalysis.job_id == job_id
        ).first()
        
        # Buscar predição atual
        prediction = db.query(MLPrediction).filter(
            MLPrediction.job_id == job_id
        ).order_by(MLPrediction.created_at.desc()).first()
        
        # Extrair informações relevantes para o feedback
        feedback_data = {
            'job_id': str(job.id),
            'filename': job.filename,
            'document_summary': self._create_document_summary(job, analysis),
            'current_prediction': {
                'lead_score': prediction.lead_score if prediction else None,
                'confidence': prediction.confidence if prediction else None,
                'model_reasoning': prediction.predictions if prediction else None
            },
            'questions': self._generate_feedback_questions(job, analysis, prediction),
            'created_at': datetime.now().isoformat()
        }
        
        return feedback_data
    
    def _create_document_summary(self, job: Job, analysis: Optional[TextAnalysis]) -> Dict:
        """Cria resumo do documento para o usuário avaliar"""
        
        summary = {
            'filename': job.filename,
            'file_size_mb': round(job.file_size / (1024 * 1024), 2) if job.file_size else None,
            'page_count': job.page_count,
            'processing_time': job.processing_time_seconds
        }
        
        if analysis:
            # Adicionar informações da análise
            summary.update({
                'keywords': analysis.keywords[:10] if analysis.keywords else [],  # Top 10
                'entities_found': len(analysis.entities.get('persons', [])) if analysis.entities else 0,
                'financial_indicators': analysis.financial_data if analysis.financial_data else {},
                'business_indicators': analysis.business_indicators if analysis.business_indicators else {}
            })
        
        return summary
    
    def _generate_feedback_questions(self, job: Job, analysis: Optional[TextAnalysis], 
                                   prediction: Optional[MLPrediction]) -> List[Dict]:
        """Gera perguntas específicas para o usuário responder"""
        
        questions = [
            {
                'id': 'overall_quality',
                'type': 'rating',
                'question': 'De 1 a 5, qual a qualidade deste lead?',
                'options': ['1 - Péssimo', '2 - Ruim', '3 - Médio', '4 - Bom', '5 - Excelente']
            },
            {
                'id': 'would_invest',
                'type': 'boolean',
                'question': 'Você investiria neste leilão?',
                'options': ['Sim', 'Não']
            },
            {
                'id': 'main_issue',
                'type': 'multiple_choice',
                'question': 'Principal problema/oportunidade identificado:',
                'options': [
                    'Preço muito alto',
                    'Documentação incompleta', 
                    'Localização ruim',
                    'Riscos legais',
                    'Boa oportunidade',
                    'Preço atrativo',
                    'Localização excelente',
                    'Documentação completa'
                ]
            }
        ]
        
        # Adicionar perguntas específicas baseadas na predição
        if prediction and prediction.lead_score:
            if prediction.lead_score > 0.7:
                questions.append({
                    'id': 'high_score_validation',
                    'type': 'boolean',
                    'question': f'O modelo deu score alto ({prediction.lead_score:.2f}). Você concorda?',
                    'options': ['Concordo', 'Discordo']
                })
            elif prediction.lead_score < 0.3:
                questions.append({
                    'id': 'low_score_validation',
                    'type': 'boolean',
                    'question': f'O modelo deu score baixo ({prediction.lead_score:.2f}). Você concorda?',
                    'options': ['Concordo', 'Discordo']
                })
        
        return questions
    
    def process_user_feedback(self, job_id: str, feedback: Dict, db: Session) -> Dict:
        """Processa feedback do usuário e atualiza sistema de aprendizado"""
        
        try:
            # Salvar feedback no banco
            feedback_record = {
                'job_id': job_id,
                'user_feedback': feedback,
                'timestamp': datetime.now().isoformat(),
                'processed': False
            }
            
            # Aqui você salvaria no banco - criar tabela user_feedback se necessário
            # Por agora, vamos logar e armazenar em arquivo
            self._save_feedback_to_file(feedback_record)
            
            # Verificar se temos feedback suficiente para retreinar
            feedback_count = self._count_pending_feedback()
            
            result = {
                'success': True,
                'message': 'Feedback recebido com sucesso',
                'feedback_count': feedback_count
            }
            
            if feedback_count >= self.min_samples_for_feedback:
                result['trigger_retraining'] = True
                result['message'] += f'. {feedback_count} feedbacks coletados - retreinamento será iniciado.'
            
            logger.info(f"✅ Feedback processado para job {job_id}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Erro ao processar feedback: {e}")
            return {'success': False, 'error': str(e)}
    
    def _save_feedback_to_file(self, feedback_record: Dict):
        """Salva feedback em arquivo JSON (temporário até criar tabela)"""
        
        import os
        from pathlib import Path
        
        feedback_dir = Path('storage/feedback')
        feedback_dir.mkdir(exist_ok=True)
        
        feedback_file = feedback_dir / f"feedback_{datetime.now().strftime('%Y%m')}.jsonl"
        
        with open(feedback_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(feedback_record, default=str) + '\\n')
    
    def _count_pending_feedback(self) -> int:
        """Conta feedback pendente de processamento"""
        
        import os
        from pathlib import Path
        
        feedback_dir = Path('storage/feedback')
        if not feedback_dir.exists():
            return 0
        
        count = 0
        for file in feedback_dir.glob('feedback_*.jsonl'):
            with open(file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        count += 1
        
        return count
    
    def get_feedback_for_training(self) -> List[Dict]:
        """Recupera feedback para usar no retreinamento"""
        
        import os
        from pathlib import Path
        
        feedback_dir = Path('storage/feedback')
        if not feedback_dir.exists():
            return []
        
        feedback_data = []
        
        for file in feedback_dir.glob('feedback_*.jsonl'):
            with open(file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        feedback_data.append(json.loads(line))
        
        logger.info(f"📚 Carregados {len(feedback_data)} feedbacks para treino")
        
        return feedback_data


# Função para integrar com API
def create_active_learning_request(job_id: str) -> Dict:
    """Cria request de active learning para um job específico"""
    
    active_learner = ActiveLearningSystem()
    
    with next(get_db()) as db:
        return active_learner.create_feedback_request(job_id, db)


def process_active_learning_feedback(job_id: str, feedback: Dict) -> Dict:
    """Processa feedback de active learning"""
    
    active_learner = ActiveLearningSystem()
    
    with next(get_db()) as db:
        return active_learner.process_user_feedback(job_id, feedback, db)


if __name__ == "__main__":
    # Teste do sistema
    logging.basicConfig(level=logging.INFO)
    
    active_learner = ActiveLearningSystem()
    
    with next(get_db()) as db:
        uncertain = active_learner.identify_uncertain_predictions(db, limit=5)
        
    print("🤔 Predições incertas encontradas:")
    print(json.dumps(uncertain, indent=2, default=str))