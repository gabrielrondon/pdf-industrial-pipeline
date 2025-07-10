"""
Lead Scoring Models - Etapa 5
Modelos de Machine Learning para scoring avançado de leads
"""

import logging
import pickle
import json
import joblib
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime
import numpy as np
from dataclasses import dataclass, asdict

try:
    import pandas as pd
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
    from sklearn.linear_model import LogisticRegression, LinearRegression
    from sklearn.model_selection import train_test_split, cross_val_score
    from sklearn.preprocessing import StandardScaler, LabelEncoder
    from sklearn.metrics import classification_report, mean_squared_error, r2_score
    from sklearn.pipeline import Pipeline
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logging.warning("scikit-learn não disponível - usando modelos básicos")

from ml_engine.feature_engineering import FeatureSet, feature_engineer

logger = logging.getLogger(__name__)

@dataclass
class ModelPrediction:
    """Resultado de predição de um modelo"""
    lead_score: float
    confidence: float
    classification: str  # 'high', 'medium', 'low'
    probability_distribution: Dict[str, float]
    feature_importance: Dict[str, float]
    model_name: str
    prediction_time: float
    metadata: Dict[str, Any]

@dataclass
class ModelPerformance:
    """Performance de um modelo"""
    model_name: str
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    rmse: float
    r2_score: float
    cross_val_score: float
    feature_importance: Dict[str, float]
    training_time: float
    samples_trained: int
    last_trained: str

class LeadScoringModel:
    """Classe base para modelos de lead scoring"""
    
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.model = None
        self.scaler = None
        self.feature_columns = None
        self.is_trained = False
        self.training_history = []
        self.model_path = Path(f"storage/models/{model_name}")
        self.model_path.mkdir(parents=True, exist_ok=True)
    
    def preprocess_features(self, features_df: pd.DataFrame) -> pd.DataFrame:
        """Pré-processa features para treinamento/predição"""
        # Remover colunas não numéricas
        numeric_cols = features_df.select_dtypes(include=['int64', 'float64']).columns
        X = features_df[numeric_cols].copy()
        
        # Preencher valores faltantes
        X = X.fillna(0)
        
        return X
    
    def save_model(self) -> bool:
        """Salva modelo treinado"""
        try:
            # Salvar modelo
            joblib.dump(self.model, self.model_path / "model.pkl")
            
            # Salvar scaler se existir
            if self.scaler is not None:
                joblib.dump(self.scaler, self.model_path / "scaler.pkl")
            
            # Salvar metadados
            metadata = {
                'model_name': self.model_name,
                'is_trained': self.is_trained,
                'feature_columns': self.feature_columns,
                'training_history': self.training_history,
                'saved_at': datetime.now().isoformat()
            }
            
            with open(self.model_path / "metadata.json", 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Modelo {self.model_name} salvo com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao salvar modelo {self.model_name}: {e}")
            return False
    
    def load_model(self) -> bool:
        """Carrega modelo salvo"""
        model_file = self.model_path / "model.pkl"
        scaler_file = self.model_path / "scaler.pkl"
        metadata_file = self.model_path / "metadata.json"
        
        try:
            # Carregar metadados
            if metadata_file.exists():
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                
                self.feature_columns = metadata.get('feature_columns')
                self.training_history = metadata.get('training_history', [])
            
            # Carregar modelo
            if SKLEARN_AVAILABLE and model_file.exists():
                self.model = joblib.load(model_file)
                
                if scaler_file.exists():
                    self.scaler = joblib.load(scaler_file)
                
                self.is_trained = True
                logger.info(f"Modelo {self.model_name} carregado com sucesso")
                return True
        
        except Exception as e:
            logger.error(f"Erro ao carregar modelo {self.model_name}: {e}")
        
        return False

class RandomForestLeadScorer(LeadScoringModel):
    """Modelo Random Forest para classificação de leads"""
    
    def __init__(self):
        super().__init__("random_forest_classifier")
        if SKLEARN_AVAILABLE:
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42
            )
    
    def train(self, features_list: List[FeatureSet], target_scores: List[float]) -> ModelPerformance:
        """Treina o Random Forest com dados de features"""
        start_time = datetime.now()
        
        if not SKLEARN_AVAILABLE:
            logger.error("scikit-learn não disponível para treinamento")
            return self._create_dummy_performance()
        
        try:
            # Converter features para DataFrame
            features_df = feature_engineer.features_to_dataframe(features_list)
            
            if features_df is None or len(features_df) < 2:
                logger.error("Dados insuficientes para treinamento")
                return self._create_dummy_performance()
            
            # Pré-processar features
            X = self.preprocess_features(features_df)
            
            # Converter scores para classes
            y = np.array(['high' if s >= 80 else 'medium' if s >= 50 else 'low' 
                         for s in target_scores])
            
            # Dividir dados
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Escalar features
            self.scaler = StandardScaler()
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Treinar modelo
            self.model.fit(X_train_scaled, y_train)
            self.feature_columns = list(X.columns)
            self.is_trained = True
            
            # Avaliar performance
            y_pred = self.model.predict(X_test_scaled)
            
            # Métricas
            report = classification_report(y_test, y_pred, output_dict=True)
            
            # Cross-validation (ajustar CV baseado no tamanho dos dados)
            cv_folds = min(3, len(X_train) // 2) if len(X_train) >= 4 else 2
            if cv_folds >= 2:
                cv_scores = cross_val_score(self.model, X_train_scaled, y_train, cv=cv_folds)
            else:
                cv_scores = [self.model.score(X_train_scaled, y_train)]
            
            # Feature importance
            feature_importance = dict(zip(
                self.feature_columns,
                self.model.feature_importances_
            ))
            
            training_time = (datetime.now() - start_time).total_seconds()
            
            performance = ModelPerformance(
                model_name=self.model_name,
                accuracy=report['accuracy'],
                precision=report['weighted avg']['precision'],
                recall=report['weighted avg']['recall'],
                f1_score=report['weighted avg']['f1-score'],
                rmse=0.0,  # N/A para classificação
                r2_score=0.0,  # N/A para classificação
                cross_val_score=cv_scores.mean(),
                feature_importance=feature_importance,
                training_time=training_time,
                samples_trained=len(X_train),
                last_trained=datetime.now().isoformat()
            )
            
            # Salvar histórico
            self.training_history.append({
                'timestamp': datetime.now().isoformat(),
                'samples': len(X_train),
                'accuracy': report['accuracy'],
                'cv_score': performance.cross_val_score
            })
            
            # Salvar modelo
            self.save_model()
            
            logger.info(f"Random Forest treinado: Acurácia {report['accuracy']:.3f}, "
                       f"F1 {report['weighted avg']['f1-score']:.3f}, "
                       f"{len(X_train)} amostras")
            
            return performance
            
        except Exception as e:
            logger.error(f"Erro no treinamento Random Forest: {e}")
            return self._create_dummy_performance()
    
    def predict(self, features: FeatureSet) -> ModelPrediction:
        """Faz predição com Random Forest"""
        start_time = datetime.now()
        
        if not self.is_trained or not SKLEARN_AVAILABLE:
            return self._create_dummy_prediction()
        
        try:
            # Converter para DataFrame
            features_df = feature_engineer.features_to_dataframe([features])
            X = self.preprocess_features(features_df)
            
            # Garantir que as colunas sejam as mesmas do treinamento
            X = X.reindex(columns=self.feature_columns, fill_value=0)
            
            # Escalar
            X_scaled = self.scaler.transform(X)
            
            # Predição
            predicted_class = self.model.predict(X_scaled)[0]
            probabilities = self.model.predict_proba(X_scaled)[0]
            
            # Mapear probabilidades para classes
            prob_dict = dict(zip(
                self.model.classes_,
                probabilities
            ))
            
            # Score baseado nas probabilidades
            lead_score = (
                prob_dict.get('high', 0) * 100 +
                prob_dict.get('medium', 0) * 60 +
                prob_dict.get('low', 0) * 20
            )
            
            # Feature importance
            feature_importance = dict(zip(
                self.feature_columns,
                self.model.feature_importances_
            ))
            
            prediction_time = (datetime.now() - start_time).total_seconds()
            
            return ModelPrediction(
                lead_score=lead_score,
                confidence=max(probabilities),
                classification=predicted_class,
                probability_distribution=prob_dict,
                feature_importance=feature_importance,
                model_name=self.model_name,
                prediction_time=prediction_time,
                metadata={
                    'input_features': len(self.feature_columns),
                    'model_type': 'RandomForestClassifier'
                }
            )
            
        except Exception as e:
            logger.error(f"Erro na predição Random Forest: {e}")
            return self._create_dummy_prediction()
    
    def _create_dummy_performance(self) -> ModelPerformance:
        """Cria performance dummy para casos de erro"""
        return ModelPerformance(
            model_name=self.model_name,
            accuracy=0.0,
            precision=0.0,
            recall=0.0,
            f1_score=0.0,
            rmse=0.0,
            r2_score=0.0,
            cross_val_score=0.0,
            feature_importance={},
            training_time=0.0,
            samples_trained=0,
            last_trained=datetime.now().isoformat()
        )
    
    def _create_dummy_prediction(self) -> ModelPrediction:
        """Cria predição dummy para casos de erro"""
        return ModelPrediction(
            lead_score=50.0,
            confidence=0.5,
            classification='medium',
            probability_distribution={'low': 0.3, 'medium': 0.4, 'high': 0.3},
            feature_importance={},
            model_name=self.model_name,
            prediction_time=0.0,
            metadata={'error': 'Modelo não disponível'}
        )

class GradientBoostingLeadScorer(LeadScoringModel):
    """Modelo Gradient Boosting para regressão de scores"""
    
    def __init__(self):
        super().__init__("gradient_boosting_regressor")
        if SKLEARN_AVAILABLE:
            # Use numpy's default_rng for random number generation
            rng = np.random.default_rng(42)
            self.model = GradientBoostingRegressor(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=6,
                random_state=rng
            )
    
    def train(self, features_list: List[FeatureSet], target_scores: List[float]) -> ModelPerformance:
        """Treina o Gradient Boosting com dados de features"""
        start_time = datetime.now()
        
        if not SKLEARN_AVAILABLE:
            logger.error("scikit-learn não disponível para treinamento")
            return self._create_dummy_performance()
        
        try:
            # Converter features para DataFrame
            features_df = feature_engineer.features_to_dataframe(features_list)
            
            if features_df is None or len(features_df) < 2:
                logger.error("Dados insuficientes para treinamento")
                return self._create_dummy_performance()
            
            # Pré-processar features
            X = self.preprocess_features(features_df)
            y = np.array(target_scores)
            
            # Dividir dados
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Escalar features
            self.scaler = StandardScaler()
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Treinar modelo
            self.model.fit(X_train_scaled, y_train)
            self.feature_columns = list(X.columns)
            self.is_trained = True
            
            # Avaliar performance
            y_pred = self.model.predict(X_test_scaled)
            
            # Métricas
            rmse = mean_squared_error(y_test, y_pred, squared=False)
            r2 = r2_score(y_test, y_pred)
            
            # Cross-validation (ajustar CV baseado no tamanho dos dados)
            cv_folds = min(3, len(X_train) // 2) if len(X_train) >= 4 else 2
            if cv_folds >= 2:
                cv_scores = cross_val_score(self.model, X_train_scaled, y_train, cv=cv_folds)
            else:
                cv_scores = [self.model.score(X_train_scaled, y_train)]
            
            # Feature importance
            feature_importance = dict(zip(
                self.feature_columns,
                self.model.feature_importances_
            ))
            
            training_time = (datetime.now() - start_time).total_seconds()
            
            performance = ModelPerformance(
                model_name=self.model_name,
                accuracy=0.0,  # N/A para regressão
                precision=0.0,  # N/A para regressão
                recall=0.0,     # N/A para regressão
                f1_score=0.0,   # N/A para regressão
                rmse=rmse,
                r2_score=r2,
                cross_val_score=cv_scores.mean(),
                feature_importance=feature_importance,
                training_time=training_time,
                samples_trained=len(X_train),
                last_trained=datetime.now().isoformat()
            )
            
            # Salvar histórico
            self.training_history.append({
                'timestamp': datetime.now().isoformat(),
                'samples': len(X_train),
                'rmse': rmse,
                'r2_score': r2,
                'cv_score': performance.cross_val_score
            })
            
            # Salvar modelo
            self.save_model()
            
            logger.info(f"Gradient Boosting treinado: RMSE {rmse:.3f}, R² {r2:.3f}, "
                       f"{len(X_train)} amostras")
            
            return performance
            
        except Exception as e:
            logger.error(f"Erro no treinamento Gradient Boosting: {e}")
            return self._create_dummy_performance()
    
    def predict(self, features: FeatureSet) -> ModelPrediction:
        """Faz predição com Gradient Boosting"""
        start_time = datetime.now()
        
        if not self.is_trained or not SKLEARN_AVAILABLE:
            return self._create_dummy_prediction()
        
        try:
            # Converter para DataFrame
            features_df = feature_engineer.features_to_dataframe([features])
            X = self.preprocess_features(features_df)
            
            # Garantir que as colunas sejam as mesmas do treinamento
            X = X.reindex(columns=self.feature_columns, fill_value=0)
            
            # Escalar
            X_scaled = self.scaler.transform(X)
            
            # Predição
            predicted_score = self.model.predict(X_scaled)[0]
            
            # Limitar score entre 0 e 100
            predicted_score = max(0, min(100, predicted_score))
            
            # Classificação baseada no score
            if predicted_score >= 80:
                classification = 'high'
                confidence = 0.9
            elif predicted_score >= 50:
                classification = 'medium'
                confidence = 0.7
            else:
                classification = 'low'
                confidence = 0.8
            
            # Probabilidades aproximadas
            prob_dict = self._score_to_probabilities(predicted_score)
            
            # Feature importance
            feature_importance = dict(zip(
                self.feature_columns,
                self.model.feature_importances_
            ))
            
            prediction_time = (datetime.now() - start_time).total_seconds()
            
            return ModelPrediction(
                lead_score=predicted_score,
                confidence=confidence,
                classification=classification,
                probability_distribution=prob_dict,
                feature_importance=feature_importance,
                model_name=self.model_name,
                prediction_time=prediction_time,
                metadata={
                    'input_features': len(self.feature_columns),
                    'model_type': 'GradientBoostingRegressor'
                }
            )
            
        except Exception as e:
            logger.error(f"Erro na predição Gradient Boosting: {e}")
            return self._create_dummy_prediction()
    
    def _score_to_probabilities(self, score: float) -> Dict[str, float]:
        """Converte score numérico para distribuição de probabilidades"""
        if score >= 80:
            return {'high': 0.8, 'medium': 0.15, 'low': 0.05}
        elif score >= 60:
            return {'high': 0.4, 'medium': 0.5, 'low': 0.1}
        elif score >= 40:
            return {'high': 0.1, 'medium': 0.6, 'low': 0.3}
        else:
            return {'high': 0.05, 'medium': 0.2, 'low': 0.75}
    
    def _create_dummy_performance(self) -> ModelPerformance:
        """Cria performance dummy para casos de erro"""
        return ModelPerformance(
            model_name=self.model_name,
            accuracy=0.0,
            precision=0.0,
            recall=0.0,
            f1_score=0.0,
            rmse=999.0,  # Use large finite number instead of infinity
            r2_score=0.0,
            cross_val_score=0.0,
            feature_importance={},
            training_time=0.0,
            samples_trained=0,
            last_trained=datetime.now().isoformat()
        )
    
    def _create_dummy_prediction(self) -> ModelPrediction:
        """Cria predição dummy para casos de erro"""
        return ModelPrediction(
            lead_score=50.0,
            confidence=0.5,
            classification='medium',
            probability_distribution={'low': 0.3, 'medium': 0.4, 'high': 0.3},
            feature_importance={},
            model_name=self.model_name,
            prediction_time=0.0,
            metadata={'error': 'Modelo não disponível'}
        )

class EnsembleLeadScorer:
    """Ensemble de modelos para lead scoring"""
    
    def __init__(self):
        # Use global instances instead of creating new ones
        self.models = {}
        self.weights = {'random_forest': 0.6, 'gradient_boosting': 0.4}
        self.is_trained = False
    
    def _initialize_models(self):
        """Initialize models using global instances"""
        global random_forest_model, gradient_boosting_model
        self.models = {
            'random_forest': random_forest_model,
            'gradient_boosting': gradient_boosting_model
        }
    
    def train(self, features_list: List[FeatureSet], target_scores: List[float]) -> Dict[str, ModelPerformance]:
        """Treina todos os modelos do ensemble"""
        # Initialize models with global instances
        self._initialize_models()
        
        performances = {}
        
        for model_name, model in self.models.items():
            logger.info(f"Treinando modelo {model_name}...")
            performance = model.train(features_list, target_scores)
            performances[model_name] = performance
        
        self.is_trained = True
        logger.info(f"Ensemble treinado com {len(self.models)} modelos")
        
        return performances
    
    def predict(self, features: FeatureSet) -> ModelPrediction:
        """Faz predição usando ensemble de modelos"""
        start_time = datetime.now()
        
        # Initialize models with global instances if not already done
        if not self.models:
            self._initialize_models()
        
        if not self.is_trained:
            logger.warning("Ensemble não está treinado")
            return self._create_dummy_prediction()
        
        predictions = {}
        total_weight = 0
        
        # Obter predições de todos os modelos
        for model_name, model in self.models.items():
            if model.is_trained:
                pred = model.predict(features)
                predictions[model_name] = pred
                total_weight += self.weights[model_name]
        
        if not predictions:
            logger.warning(f"Nenhum modelo individual está treinado: RF={self.models['random_forest'].is_trained}, GB={self.models['gradient_boosting'].is_trained}")
            return self._create_dummy_prediction()
        
        # Combinar predições
        weighted_score = sum(
            pred.lead_score * self.weights[model_name] 
            for model_name, pred in predictions.items()
        ) / total_weight
        
        # Combinar confiança
        weighted_confidence = sum(
            pred.confidence * self.weights[model_name] 
            for model_name, pred in predictions.items()
        ) / total_weight
        
        # Classificação baseada no score final
        if weighted_score >= 80:
            classification = 'high'
        elif weighted_score >= 50:
            classification = 'medium'
        else:
            classification = 'low'
        
        # Combinar probabilidades
        combined_probs = {'high': 0, 'medium': 0, 'low': 0}
        for model_name, pred in predictions.items():
            weight = self.weights[model_name] / total_weight
            for class_name, prob in pred.probability_distribution.items():
                combined_probs[class_name] += prob * weight
        
        # Combinar feature importance
        combined_importance = {}
        for model_name, pred in predictions.items():
            weight = self.weights[model_name] / total_weight
            for feature, importance in pred.feature_importance.items():
                if feature not in combined_importance:
                    combined_importance[feature] = 0
                combined_importance[feature] += importance * weight
        
        prediction_time = (datetime.now() - start_time).total_seconds()
        
        return ModelPrediction(
            lead_score=weighted_score,
            confidence=weighted_confidence,
            classification=classification,
            probability_distribution=combined_probs,
            feature_importance=combined_importance,
            model_name="ensemble",
            prediction_time=prediction_time,
            metadata={
                'models_used': list(predictions.keys()),
                'weights': self.weights,
                'model_type': 'EnsembleModel'
            }
        )
    
    def _create_dummy_prediction(self) -> ModelPrediction:
        """Cria predição dummy para casos de erro"""
        return ModelPrediction(
            lead_score=50.0,
            confidence=0.5,
            classification='medium',
            probability_distribution={'low': 0.3, 'medium': 0.4, 'high': 0.3},
            feature_importance={},
            model_name="ensemble",
            prediction_time=0.0,
            metadata={'error': 'Ensemble não treinado'}
        )

# Instâncias globais dos modelos
random_forest_model = RandomForestLeadScorer()
gradient_boosting_model = GradientBoostingLeadScorer()
ensemble_model = EnsembleLeadScorer() 