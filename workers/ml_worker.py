"""
ML Worker - Etapa 5
Worker responsável por orquestrar o pipeline de Machine Learning
"""

import logging
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import asdict
import asyncio

from ml_engine.feature_engineering import feature_engineer, FeatureSet
from ml_engine.lead_scoring_models import (
    ensemble_model, random_forest_model, gradient_boosting_model,
    ModelPrediction, ModelPerformance
)
from utils.storage_manager import storage_manager
from embeddings.vector_database import vector_db

logger = logging.getLogger(__name__)

class MLWorker:
    """Worker para processamento de Machine Learning"""
    
    def __init__(self):
        self.models_trained = 0
        self.predictions_made = 0
        self.features_extracted = 0
        self.start_time = datetime.now()
        self.training_history = []
        
        # Tentar carregar modelos salvos
        self._load_existing_models()
    
    def _load_existing_models(self):
        """Carrega modelos existentes se disponíveis"""
        try:
            rf_loaded = random_forest_model.load_model()
            gb_loaded = gradient_boosting_model.load_model()
            
            if rf_loaded or gb_loaded:
                ensemble_model.is_trained = True
                logger.info(f"Modelos carregados: RF={rf_loaded}, GB={gb_loaded}")
            
        except Exception as e:
            logger.warning(f"Erro ao carregar modelos existentes: {e}")
    
    async def extract_features_from_job(self, job_id: str) -> Dict[str, Any]:
        """
        Extrai features de todas as análises de texto de um job
        
        Args:
            job_id: ID do job para extrair features
            
        Returns:
            Resultado da extração de features
        """
        logger.info(f"Iniciando extração de features para job {job_id}")
        
        try:
            # Carregar análises de texto
            text_analyses = self._load_text_analyses(job_id)
            
            if not text_analyses:
                return {
                    'job_id': job_id,
                    'status': 'no_data',
                    'message': 'Nenhuma análise de texto encontrada',
                    'features_extracted': 0
                }
            
            # Carregar dados de embeddings se disponíveis
            job_documents = vector_db.search_by_job(job_id)
            embeddings_data = []
            
            for doc in job_documents:
                embeddings_data.append({
                    'page_number': doc.page_number,
                    'vector': doc.vector,
                    'vector_dimension': len(doc.vector)
                })
            
            # Extrair features para cada análise
            features_list = []
            for i, analysis in enumerate(text_analyses):
                try:
                    # Encontrar embedding correspondente
                    page_num = analysis.get('page_number')
                    embedding_data = None
                    
                    for emb_data in embeddings_data:
                        if emb_data['page_number'] == page_num:
                            embedding_data = emb_data
                            break
                    
                    # Extrair features
                    features = feature_engineer.extract_features(
                        text_analysis=analysis,
                        embedding_data=embedding_data
                    )
                    
                    features_list.append(features)
                    self.features_extracted += 1
                    
                except Exception as e:
                    logger.error(f"Erro na extração de features da página {page_num}: {e}")
                    continue
            
            # Salvar features extraídas
            await self._save_job_features(job_id, features_list)
            
            # Estatísticas
            feature_stats = self._calculate_feature_stats(features_list)
            
            logger.info(f"✅ Features extraídas para job {job_id}: {len(features_list)} páginas processadas")
            
            return {
                'job_id': job_id,
                'status': 'completed',
                'features_extracted': len(features_list),
                'feature_statistics': feature_stats,
                'high_value_leads': len([f for f in features_list if f.original_lead_score >= 80]),
                'processing_time': feature_stats.get('total_processing_time', 0)
            }
            
        except Exception as e:
            logger.error(f"Erro na extração de features para job {job_id}: {e}")
            return {
                'job_id': job_id,
                'status': 'error',
                'error': str(e),
                'features_extracted': 0
            }
    
    async def train_models(self, 
                          job_ids: Optional[List[str]] = None,
                          min_samples: int = 10) -> Dict[str, Any]:
        """
        Treina modelos de ML com dados disponíveis
        
        Args:
            job_ids: Lista de job IDs para usar no treinamento (None = todos)
            min_samples: Mínimo de amostras necessárias para treinamento
            
        Returns:
            Resultado do treinamento
        """
        logger.info("Iniciando treinamento de modelos ML")
        
        try:
            # Carregar todas as features disponíveis
            all_features = await self._load_all_features(job_ids)
            
            if len(all_features) < min_samples:
                return {
                    'status': 'insufficient_data',
                    'message': f'Apenas {len(all_features)} amostras disponíveis, mínimo {min_samples}',
                    'samples_found': len(all_features)
                }
            
            # Preparar dados de treinamento
            features_list = [features for features, _ in all_features]
            target_scores = [score for _, score in all_features]
            
            logger.info(f"Treinando com {len(features_list)} amostras")
            
            # Treinar ensemble de modelos
            performances = ensemble_model.train(features_list, target_scores)
            
            # Registrar treinamento
            training_record = {
                'timestamp': datetime.now().isoformat(),
                'samples_used': len(features_list),
                'job_ids': job_ids or 'all',
                'performances': {name: asdict(perf) for name, perf in performances.items()},
                'score_distribution': self._analyze_score_distribution(target_scores)
            }
            
            self.training_history.append(training_record)
            self.models_trained += 1
            
            # Salvar histórico de treinamento
            await self._save_training_history()
            
            logger.info(f"✅ Modelos treinados com sucesso: {len(performances)} modelos")
            
            return {
                'status': 'completed',
                'models_trained': list(performances.keys()),
                'samples_used': len(features_list),
                'performances': performances,
                'training_record': training_record
            }
            
        except Exception as e:
            logger.error(f"Erro no treinamento de modelos: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'models_trained': []
            }
    
    async def predict_job_scores(self, job_id: str) -> Dict[str, Any]:
        """
        Faz predições ML para todas as páginas de um job
        
        Args:
            job_id: ID do job para fazer predições
            
        Returns:
            Predições para o job
        """
        logger.info(f"Iniciando predições ML para job {job_id}")
        
        try:
            # Carregar features do job
            job_features = await self._load_job_features(job_id)
            
            if not job_features:
                return {
                    'job_id': job_id,
                    'status': 'no_features',
                    'message': 'Features não encontradas. Execute extração de features primeiro.',
                    'predictions': []
                }
            
            # Fazer predições para cada página
            predictions = []
            for features in job_features:
                try:
                    prediction = ensemble_model.predict(features)
                    
                    # Adicionar informações da página
                    prediction_data = {
                        'page_number': features.page_number,
                        'job_id': job_id,
                        'ml_prediction': asdict(prediction),
                        'original_score': features.original_lead_score,
                        'feature_summary': self._summarize_features(features)
                    }
                    
                    predictions.append(prediction_data)
                    self.predictions_made += 1
                    
                except Exception as e:
                    logger.error(f"Erro na predição da página {features.page_number}: {e}")
                    continue
            
            # Calcular estatísticas do job
            job_stats = self._calculate_job_predictions_stats(predictions)
            
            # Salvar predições
            await self._save_job_predictions(job_id, predictions, job_stats)
            
            logger.info(f"✅ Predições ML completadas para job {job_id}: {len(predictions)} páginas")
            
            return {
                'job_id': job_id,
                'status': 'completed',
                'predictions': predictions,
                'job_statistics': job_stats,
                'total_pages_predicted': len(predictions)
            }
            
        except Exception as e:
            logger.error(f"Erro nas predições para job {job_id}: {e}")
            return {
                'job_id': job_id,
                'status': 'error',
                'error': str(e),
                'predictions': []
            }
    
    async def analyze_lead_quality(self, 
                                 threshold_high: float = 80.0,
                                 threshold_medium: float = 50.0) -> Dict[str, Any]:
        """
        Analisa qualidade geral dos leads no sistema
        
        Args:
            threshold_high: Threshold para leads de alta qualidade
            threshold_medium: Threshold para leads de média qualidade
            
        Returns:
            Análise de qualidade dos leads
        """
        logger.info("Iniciando análise de qualidade dos leads")
        
        try:
            # Buscar todas as predições salvas
            all_predictions = await self._load_all_predictions()
            
            if not all_predictions:
                return {
                    'status': 'no_data',
                    'message': 'Nenhuma predição encontrada',
                    'analysis': {}
                }
            
            # Análise de qualidade
            quality_analysis = {
                'total_leads': len(all_predictions),
                'high_quality': len([p for p in all_predictions 
                                   if p['ml_prediction']['lead_score'] >= threshold_high]),
                'medium_quality': len([p for p in all_predictions 
                                     if threshold_medium <= p['ml_prediction']['lead_score'] < threshold_high]),
                'low_quality': len([p for p in all_predictions 
                                  if p['ml_prediction']['lead_score'] < threshold_medium]),
                'average_score': sum(p['ml_prediction']['lead_score'] for p in all_predictions) / len(all_predictions),
                'score_distribution': {},
                'confidence_analysis': {},
                'feature_importance': {},
                'model_performance': {}
            }
            
            # Distribuição de scores
            scores = [p['ml_prediction']['lead_score'] for p in all_predictions]
            quality_analysis['score_distribution'] = {
                'min': min(scores),
                'max': max(scores),
                'median': sorted(scores)[len(scores) // 2],
                'std_dev': self._calculate_std_dev(scores)
            }
            
            # Análise de confiança
            confidences = [p['ml_prediction']['confidence'] for p in all_predictions]
            quality_analysis['confidence_analysis'] = {
                'average_confidence': sum(confidences) / len(confidences),
                'high_confidence_leads': len([c for c in confidences if c >= 0.8]),
                'low_confidence_leads': len([c for c in confidences if c < 0.5])
            }
            
            # Features mais importantes (agregadas)
            all_importance = {}
            for pred in all_predictions:
                for feature, importance in pred['ml_prediction']['feature_importance'].items():
                    all_importance[feature] = all_importance.get(feature, 0) + importance
            
            # Top 10 features mais importantes
            sorted_features = sorted(all_importance.items(), key=lambda x: x[1], reverse=True)
            quality_analysis['feature_importance'] = dict(sorted_features[:10])
            
            # Performance dos modelos
            if ensemble_model.is_trained:
                quality_analysis['model_performance'] = ensemble_model.get_model_performances()
            
            logger.info(f"✅ Análise de qualidade completada: {quality_analysis['total_leads']} leads analisados")
            
            return {
                'status': 'completed',
                'analysis': quality_analysis,
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erro na análise de qualidade: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'analysis': {}
            }
    
    def _load_text_analyses(self, job_id: str) -> List[Dict[str, Any]]:
        """Carrega análises de texto de um job"""
        try:
            analysis_dir = f"text_analysis/{job_id}"
            
            if not storage_manager.directory_exists(analysis_dir):
                return []
            
            files = storage_manager.list_files(analysis_dir)
            analyses = []
            
            for file_path in files:
                if file_path.endswith('_analysis.json'):
                    try:
                        analysis_data = storage_manager.load_json(file_path)
                        analyses.append(analysis_data)
                    except Exception as e:
                        logger.warning(f"Erro ao carregar análise {file_path}: {e}")
                        continue
            
            return analyses
            
        except Exception as e:
            logger.error(f"Erro ao carregar análises de texto para job {job_id}: {e}")
            return []
    
    async def _save_job_features(self, job_id: str, features_list: List[FeatureSet]):
        """Salva features extraídas de um job"""
        try:
            # Criar diretório
            ml_dir = f"ml_analysis/{job_id}"
            storage_manager.ensure_directory(ml_dir)
            
            # Salvar features individuais
            for features in features_list:
                features_file = f"{ml_dir}/page_{features.page_number}_features.json"
                features_dict = asdict(features)
                storage_manager.save_json(features_file, features_dict)
            
            # Salvar resumo das features
            features_summary = {
                'job_id': job_id,
                'total_pages': len(features_list),
                'features_extracted_at': datetime.now().isoformat(),
                'average_lead_score': sum(f.original_lead_score for f in features_list) / len(features_list),
                'high_quality_pages': len([f for f in features_list if f.original_lead_score >= 80]),
                'feature_statistics': self._calculate_feature_stats(features_list)
            }
            
            summary_file = f"{ml_dir}/features_summary.json"
            storage_manager.save_json(summary_file, features_summary)
            
            logger.debug(f"Features salvas para job {job_id}: {len(features_list)} páginas")
            
        except Exception as e:
            logger.error(f"Erro ao salvar features do job {job_id}: {e}")
    
    async def _load_job_features(self, job_id: str) -> List[FeatureSet]:
        """Carrega features de um job"""
        try:
            ml_dir = f"ml_analysis/{job_id}"
            
            if not storage_manager.directory_exists(ml_dir):
                return []
            
            files = storage_manager.list_files(ml_dir)
            features_list = []
            
            for file_path in files:
                if file_path.endswith('_features.json'):
                    try:
                        features_dict = storage_manager.load_json(file_path)
                        features = FeatureSet(**features_dict)
                        features_list.append(features)
                    except Exception as e:
                        logger.warning(f"Erro ao carregar features {file_path}: {e}")
                        continue
            
            return features_list
            
        except Exception as e:
            logger.error(f"Erro ao carregar features do job {job_id}: {e}")
            return []
    
    async def _load_all_features(self, job_ids: Optional[List[str]] = None) -> List[Tuple[FeatureSet, float]]:
        """Carrega todas as features disponíveis para treinamento"""
        all_features = []
        
        try:
            ml_base_dir = "ml_analysis"
            
            if not storage_manager.directory_exists(ml_base_dir):
                return []
            
            # Listar jobs disponíveis
            available_jobs = []
            if job_ids:
                available_jobs = [job_id for job_id in job_ids 
                                if storage_manager.directory_exists(f"{ml_base_dir}/{job_id}")]
            else:
                # Buscar todos os jobs
                try:
                    # Simular listagem de diretórios
                    available_jobs = ['stage4-test-job']  # Adicionar lógica real depois
                except:
                    pass
            
            # Carregar features de cada job
            for job_id in available_jobs:
                job_features = await self._load_job_features(job_id)
                
                for features in job_features:
                    # Usar score original como target
                    target_score = features.original_lead_score
                    all_features.append((features, target_score))
            
            logger.info(f"Features carregadas para treinamento: {len(all_features)} amostras")
            return all_features
            
        except Exception as e:
            logger.error(f"Erro ao carregar todas as features: {e}")
            return []
    
    async def _save_job_predictions(self, job_id: str, predictions: List[Dict], job_stats: Dict):
        """Salva predições de um job"""
        try:
            ml_dir = f"ml_analysis/{job_id}"
            storage_manager.ensure_directory(ml_dir)
            
            # Salvar predições
            predictions_file = f"{ml_dir}/ml_predictions.json"
            predictions_data = {
                'job_id': job_id,
                'predictions': predictions,
                'statistics': job_stats,
                'predicted_at': datetime.now().isoformat(),
                'model_used': 'ensemble'
            }
            
            storage_manager.save_json(predictions_file, predictions_data)
            
            logger.debug(f"Predições salvas para job {job_id}")
            
        except Exception as e:
            logger.error(f"Erro ao salvar predições do job {job_id}: {e}")
    
    async def _load_all_predictions(self) -> List[Dict]:
        """Carrega todas as predições salvas"""
        all_predictions = []
        
        try:
            # Implementar busca real de predições
            # Por enquanto, retornar lista vazia
            return all_predictions
            
        except Exception as e:
            logger.error(f"Erro ao carregar todas as predições: {e}")
            return []
    
    async def _save_training_history(self):
        """Salva histórico de treinamento"""
        try:
            storage_manager.ensure_directory("ml_analysis")
            history_file = "ml_analysis/training_history.json"
            
            history_data = {
                'training_sessions': self.training_history,
                'total_trainings': self.models_trained,
                'last_updated': datetime.now().isoformat()
            }
            
            storage_manager.save_json(history_file, history_data)
            
        except Exception as e:
            logger.error(f"Erro ao salvar histórico de treinamento: {e}")
    
    def _calculate_feature_stats(self, features_list: List[FeatureSet]) -> Dict[str, Any]:
        """Calcula estatísticas das features extraídas"""
        if not features_list:
            return {}
        
        return {
            'total_features_extracted': len(features_list),
            'average_text_length': sum(f.text_length for f in features_list) / len(features_list),
            'average_entity_count': sum(f.entity_count for f in features_list) / len(features_list),
            'average_lead_score': sum(f.original_lead_score for f in features_list) / len(features_list),
            'financial_features_present': sum(1 for f in features_list if f.has_financial_values),
            'urgency_features_present': sum(1 for f in features_list if f.urgency_score > 0),
            'technology_features_present': sum(1 for f in features_list if f.technology_score > 0),
            'total_processing_time': sum(f.processing_time for f in features_list)
        }
    
    def _calculate_job_predictions_stats(self, predictions: List[Dict]) -> Dict[str, Any]:
        """Calcula estatísticas das predições de um job"""
        if not predictions:
            return {}
        
        scores = [p['ml_prediction']['lead_score'] for p in predictions]
        confidences = [p['ml_prediction']['confidence'] for p in predictions]
        
        return {
            'total_pages': len(predictions),
            'average_ml_score': sum(scores) / len(scores),
            'max_ml_score': max(scores),
            'min_ml_score': min(scores),
            'average_confidence': sum(confidences) / len(confidences),
            'high_quality_leads': len([s for s in scores if s >= 80]),
            'medium_quality_leads': len([s for s in scores if 50 <= s < 80]),
            'low_quality_leads': len([s for s in scores if s < 50]),
            'high_confidence_predictions': len([c for c in confidences if c >= 0.8])
        }
    
    def _summarize_features(self, features: FeatureSet) -> Dict[str, Any]:
        """Cria resumo das features para exibição"""
        return {
            'text_length': features.text_length,
            'entity_count': features.entity_count,
            'financial_value': features.max_financial_value,
            'urgency_score': features.urgency_score,
            'technology_score': features.technology_score,
            'contact_completeness': features.contact_completeness
        }
    
    def _analyze_score_distribution(self, scores: List[float]) -> Dict[str, Any]:
        """Analisa distribuição dos scores"""
        if not scores:
            return {}
        
        return {
            'count': len(scores),
            'min': min(scores),
            'max': max(scores),
            'average': sum(scores) / len(scores),
            'high_scores': len([s for s in scores if s >= 80]),
            'medium_scores': len([s for s in scores if 50 <= s < 80]),
            'low_scores': len([s for s in scores if s < 50])
        }
    
    def _calculate_std_dev(self, values: List[float]) -> float:
        """Calcula desvio padrão"""
        if len(values) < 2:
            return 0.0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1)
        return variance ** 0.5
    
    def get_worker_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do worker ML"""
        uptime = (datetime.now() - self.start_time).total_seconds()
        
        return {
            'models_trained': self.models_trained,
            'predictions_made': self.predictions_made,
            'features_extracted': self.features_extracted,
            'uptime_seconds': uptime,
            'ensemble_trained': ensemble_model.is_trained,
            'random_forest_trained': random_forest_model.is_trained,
            'gradient_boosting_trained': gradient_boosting_model.is_trained,
            'training_sessions': len(self.training_history),
            'last_training': self.training_history[-1]['timestamp'] if self.training_history else None
        }

# Instância global do worker ML
ml_worker = MLWorker() 