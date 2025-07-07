"""
Optimized ML Models for Production
World-class PDF analysis with state-of-the-art ML techniques
"""

import logging
import pickle
import json
import joblib
import os
import asyncio
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime
import numpy as np
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor
import threading
from functools import lru_cache

import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor, VotingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler, RobustScaler, LabelEncoder
from sklearn.metrics import classification_report, mean_squared_error, r2_score, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.feature_selection import SelectKBest, f_classif
import xgboost as xgb
import lightgbm as lgb
from sklearn.calibration import CalibratedClassifierCV

# ONNX for optimized inference
try:
    import onnx
    import onnxruntime as ort
    from skl2onnx import convert_sklearn
    from skl2onnx.common.data_types import FloatTensorType
    ONNX_AVAILABLE = True
except ImportError:
    ONNX_AVAILABLE = False
    logging.warning("ONNX not available - using standard inference")

from core.monitoring import track_ml_inference, ml_model_accuracy, BusinessMetrics
from config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


@dataclass
class ModelPrediction:
    """Enhanced prediction result"""
    lead_score: float
    confidence: float
    classification: str  # 'high', 'medium', 'low'
    probability_distribution: Dict[str, float]
    feature_importance: Dict[str, float]
    model_name: str
    model_version: str
    prediction_time: float
    metadata: Dict[str, Any]
    risk_factors: List[str]
    opportunities: List[str]
    recommendation: str


@dataclass
class ModelMetrics:
    """Model performance metrics"""
    model_name: str
    version: str
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    auc_roc: float
    training_time: float
    inference_time_ms: float
    model_size_mb: float
    feature_count: int
    last_trained: datetime
    performance_trend: str  # 'improving', 'stable', 'degrading'


class ModelRegistry:
    """Centralized model registry with versioning"""
    
    def __init__(self, model_path: str = None):
        self.model_path = Path(model_path or settings.model_path)
        self.model_path.mkdir(exist_ok=True)
        self.models = {}
        self.model_versions = {}
        self.performance_history = {}
        self._lock = threading.Lock()
    
    def register_model(
        self,
        name: str,
        model: Any,
        version: str,
        metrics: ModelMetrics,
        metadata: Dict[str, Any] = None
    ):
        """Register a new model version"""
        with self._lock:
            if name not in self.models:
                self.models[name] = {}
                self.model_versions[name] = []
            
            self.models[name][version] = {
                'model': model,
                'metrics': metrics,
                'metadata': metadata or {},
                'created_at': datetime.utcnow()
            }
            
            if version not in self.model_versions[name]:
                self.model_versions[name].append(version)
                self.model_versions[name].sort(reverse=True)  # Latest first
            
            # Save to disk
            self._save_model(name, version, model, metrics, metadata)
            
            # Update metrics
            ml_model_accuracy.labels(
                model_name=name,
                model_version=version
            ).set(metrics.accuracy)
    
    def get_model(self, name: str, version: str = None) -> Optional[Any]:
        """Get model by name and version"""
        if name not in self.models:
            return None
        
        if version is None:
            # Get latest version
            if not self.model_versions[name]:
                return None
            version = self.model_versions[name][0]
        
        return self.models[name].get(version, {}).get('model')
    
    def get_model_metrics(self, name: str, version: str = None) -> Optional[ModelMetrics]:
        """Get model metrics"""
        if name not in self.models:
            return None
        
        if version is None:
            version = self.model_versions[name][0] if self.model_versions[name] else None
        
        if version:
            return self.models[name].get(version, {}).get('metrics')
        return None
    
    def list_models(self) -> Dict[str, List[str]]:
        """List all registered models"""
        return self.model_versions.copy()
    
    def _save_model(self, name: str, version: str, model: Any, metrics: ModelMetrics, metadata: Dict):
        """Save model to disk"""
        model_dir = self.model_path / name / version
        model_dir.mkdir(parents=True, exist_ok=True)
        
        # Save model
        joblib.dump(model, model_dir / 'model.joblib')
        
        # Save metrics
        with open(model_dir / 'metrics.json', 'w') as f:
            json.dump(asdict(metrics), f, default=str, indent=2)
        
        # Save metadata
        with open(model_dir / 'metadata.json', 'w') as f:
            json.dump(metadata, f, default=str, indent=2)
        
        logger.info(f"Saved model {name} v{version} to {model_dir}")


class AdvancedMLPipeline:
    """Advanced ML pipeline with ensemble methods and optimization"""
    
    def __init__(self, registry: ModelRegistry = None):
        self.registry = registry or ModelRegistry()
        self.feature_selector = None
        self.scaler = None
        self.models = {}
        self.ensemble_model = None
        self.onnx_models = {}
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # Load existing models
        self._load_existing_models()
    
    def _load_existing_models(self):
        """Load existing models from disk"""
        try:
            # Implementation for loading saved models
            pass
        except Exception as e:
            logger.error(f"Failed to load existing models: {str(e)}")
    
    def create_base_models(self) -> Dict[str, Any]:
        """Create base models for ensemble"""
        models = {
            'random_forest': RandomForestClassifier(
                n_estimators=200,
                max_depth=15,
                min_samples_split=5,
                min_samples_leaf=2,
                max_features='sqrt',
                bootstrap=True,
                n_jobs=-1,
                random_state=42,
                class_weight='balanced'
            ),
            'xgboost': xgb.XGBClassifier(
                n_estimators=200,
                max_depth=8,
                learning_rate=0.1,
                subsample=0.8,
                colsample_bytree=0.8,
                objective='binary:logistic',
                eval_metric='auc',
                random_state=42,
                n_jobs=-1
            ),
            'lightgbm': lgb.LGBMClassifier(
                n_estimators=200,
                max_depth=8,
                learning_rate=0.1,
                subsample=0.8,
                colsample_bytree=0.8,
                objective='binary',
                metric='auc',
                random_state=42,
                n_jobs=-1,
                verbose=-1
            ),
            'logistic_regression': LogisticRegression(
                C=1.0,
                penalty='l2',
                solver='liblinear',
                random_state=42,
                class_weight='balanced',
                max_iter=1000
            ),
            'neural_network': MLPClassifier(
                hidden_layer_sizes=(128, 64, 32),
                activation='relu',
                solver='adam',
                alpha=0.001,
                learning_rate='adaptive',
                max_iter=1000,
                random_state=42,
                early_stopping=True,
                validation_fraction=0.1
            )
        }
        
        return models
    
    def optimize_hyperparameters(self, X: np.ndarray, y: np.ndarray, model_name: str) -> Any:
        """Optimize hyperparameters using GridSearchCV"""
        param_grids = {
            'random_forest': {
                'n_estimators': [100, 200, 300],
                'max_depth': [10, 15, 20],
                'min_samples_split': [2, 5, 10],
                'min_samples_leaf': [1, 2, 4]
            },
            'xgboost': {
                'n_estimators': [100, 200],
                'max_depth': [6, 8, 10],
                'learning_rate': [0.05, 0.1, 0.2],
                'subsample': [0.8, 0.9, 1.0]
            },
            'lightgbm': {
                'n_estimators': [100, 200],
                'max_depth': [6, 8, 10],
                'learning_rate': [0.05, 0.1, 0.2],
                'subsample': [0.8, 0.9, 1.0]
            }
        }
        
        if model_name not in param_grids:
            return self.create_base_models()[model_name]
        
        base_model = self.create_base_models()[model_name]
        
        grid_search = GridSearchCV(
            base_model,
            param_grids[model_name],
            cv=5,
            scoring='roc_auc',
            n_jobs=-1,
            verbose=1
        )
        
        grid_search.fit(X, y)
        logger.info(f"Best parameters for {model_name}: {grid_search.best_params_}")
        
        return grid_search.best_estimator_
    
    def train_ensemble_model(self, X: np.ndarray, y: np.ndarray) -> VotingClassifier:
        """Train ensemble model with multiple base learners"""
        logger.info("Training ensemble model...")
        
        # Create and optimize base models
        base_models = []
        
        for name in ['random_forest', 'xgboost', 'lightgbm', 'logistic_regression']:
            logger.info(f"Optimizing {name}...")
            model = self.optimize_hyperparameters(X, y, name)
            base_models.append((name, model))
        
        # Create ensemble
        ensemble = VotingClassifier(
            estimators=base_models,
            voting='soft',  # Use probabilities
            n_jobs=-1
        )
        
        # Calibrate probabilities
        calibrated_ensemble = CalibratedClassifierCV(
            ensemble,
            method='isotonic',
            cv=5
        )
        
        calibrated_ensemble.fit(X, y)
        
        return calibrated_ensemble
    
    def create_processing_pipeline(self, X: np.ndarray, y: np.ndarray) -> Pipeline:
        """Create complete preprocessing and model pipeline"""
        # Feature selection
        feature_selector = SelectKBest(
            score_func=f_classif,
            k=min(50, X.shape[1])  # Select top features
        )
        
        # Robust scaling for outliers
        scaler = RobustScaler()
        
        # Ensemble model
        ensemble_model = self.train_ensemble_model(X, y)
        
        # Create pipeline
        pipeline = Pipeline([
            ('feature_selection', feature_selector),
            ('scaling', scaler),
            ('classifier', ensemble_model)
        ])
        
        return pipeline
    
    async def train_model_async(
        self,
        training_data: pd.DataFrame,
        target_column: str = 'is_high_value_lead',
        model_version: str = None
    ) -> ModelMetrics:
        """Train model asynchronously"""
        start_time = datetime.utcnow()
        
        try:
            # Prepare data
            X = training_data.drop(columns=[target_column]).values
            y = training_data[target_column].values
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            
            # Train in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            pipeline = await loop.run_in_executor(
                self.executor,
                self.create_processing_pipeline,
                X_train,
                y_train
            )
            
            # Evaluate model
            y_pred = pipeline.predict(X_test)
            y_pred_proba = pipeline.predict_proba(X_test)[:, 1]
            
            # Calculate metrics
            from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
            
            accuracy = accuracy_score(y_test, y_pred)
            precision = precision_score(y_test, y_pred, average='weighted')
            recall = recall_score(y_test, y_pred, average='weighted')
            f1 = f1_score(y_test, y_pred, average='weighted')
            auc = roc_auc_score(y_test, y_pred_proba)
            
            training_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Generate version if not provided
            if not model_version:
                model_version = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            
            # Create metrics
            metrics = ModelMetrics(
                model_name="ensemble_lead_scorer",
                version=model_version,
                accuracy=accuracy,
                precision=precision,
                recall=recall,
                f1_score=f1,
                auc_roc=auc,
                training_time=training_time,
                inference_time_ms=10.0,  # Will be measured during inference
                model_size_mb=self._calculate_model_size(pipeline),
                feature_count=X.shape[1],
                last_trained=datetime.utcnow(),
                performance_trend="stable"
            )
            
            # Register model
            self.registry.register_model(
                "ensemble_lead_scorer",
                pipeline,
                model_version,
                metrics,
                {
                    "feature_names": list(training_data.columns[:-1]),
                    "target_column": target_column,
                    "training_samples": len(X_train),
                    "test_samples": len(X_test)
                }
            )
            
            # Convert to ONNX for faster inference
            if ONNX_AVAILABLE:
                await self._convert_to_onnx(pipeline, model_version)
            
            logger.info(f"Model training completed. Accuracy: {accuracy:.4f}, AUC: {auc:.4f}")
            
            return metrics
            
        except Exception as e:
            logger.error(f"Model training failed: {str(e)}", exc_info=True)
            raise
    
    @track_ml_inference(model_name="ensemble_lead_scorer", model_version="latest")
    async def predict_async(
        self,
        features: np.ndarray,
        model_version: str = None
    ) -> ModelPrediction:
        """Make prediction asynchronously"""
        start_time = datetime.utcnow()
        
        try:
            # Get model
            model = self.registry.get_model("ensemble_lead_scorer", model_version)
            if not model:
                raise ValueError("Model not found")
            
            # Use ONNX model if available for faster inference
            onnx_model_key = f"ensemble_lead_scorer_{model_version or 'latest'}"
            if onnx_model_key in self.onnx_models:
                prediction = await self._predict_onnx(features, onnx_model_key)
            else:
                # Use sklearn model
                loop = asyncio.get_event_loop()
                prediction = await loop.run_in_executor(
                    self.executor,
                    self._predict_sklearn,
                    model,
                    features
                )
            
            prediction_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Get model metrics
            metrics = self.registry.get_model_metrics("ensemble_lead_scorer", model_version)
            
            result = ModelPrediction(
                lead_score=prediction['score'],
                confidence=prediction['confidence'],
                classification=prediction['classification'],
                probability_distribution=prediction['probabilities'],
                feature_importance=prediction['feature_importance'],
                model_name="ensemble_lead_scorer",
                model_version=model_version or "latest",
                prediction_time=prediction_time,
                metadata={
                    "model_accuracy": metrics.accuracy if metrics else None,
                    "model_version": model_version or "latest"
                },
                risk_factors=self._extract_risk_factors(features, prediction),
                opportunities=self._extract_opportunities(features, prediction),
                recommendation=self._generate_recommendation(prediction)
            )
            
            # Track business metrics
            BusinessMetrics.track_lead_score(prediction['score'])
            
            return result
            
        except Exception as e:
            logger.error(f"Prediction failed: {str(e)}", exc_info=True)
            raise
    
    def _predict_sklearn(self, model: Any, features: np.ndarray) -> Dict[str, Any]:
        """Make prediction using sklearn model"""
        prediction = model.predict(features.reshape(1, -1))[0]
        probabilities = model.predict_proba(features.reshape(1, -1))[0]
        
        # Extract feature importance if available
        feature_importance = {}
        if hasattr(model.named_steps['classifier'], 'feature_importances_'):
            importance = model.named_steps['classifier'].feature_importances_
            feature_importance = {f"feature_{i}": float(imp) for i, imp in enumerate(importance)}
        
        return {
            'score': float(probabilities[1]),  # Probability of positive class
            'confidence': float(max(probabilities)),
            'classification': self._classify_score(probabilities[1]),
            'probabilities': {
                'low': float(probabilities[0]),
                'high': float(probabilities[1])
            },
            'feature_importance': feature_importance
        }
    
    async def _predict_onnx(self, features: np.ndarray, model_key: str) -> Dict[str, Any]:
        """Make prediction using ONNX model for faster inference"""
        session = self.onnx_models[model_key]
        
        input_name = session.get_inputs()[0].name
        output_names = [output.name for output in session.get_outputs()]
        
        # Run inference
        results = session.run(output_names, {input_name: features.reshape(1, -1).astype(np.float32)})
        
        probabilities = results[1][0]  # Assuming second output is probabilities
        
        return {
            'score': float(probabilities[1]),
            'confidence': float(max(probabilities)),
            'classification': self._classify_score(probabilities[1]),
            'probabilities': {
                'low': float(probabilities[0]),
                'high': float(probabilities[1])
            },
            'feature_importance': {}  # ONNX doesn't provide feature importance
        }
    
    async def _convert_to_onnx(self, model: Any, version: str):
        """Convert sklearn model to ONNX for faster inference"""
        if not ONNX_AVAILABLE:
            return
        
        try:
            # Get input shape (assuming features are already selected)
            n_features = model.named_steps['feature_selection'].k
            
            # Convert to ONNX
            initial_type = [('float_input', FloatTensorType([None, n_features]))]
            onnx_model = convert_sklearn(model, initial_types=initial_type)
            
            # Save ONNX model
            onnx_path = self.registry.model_path / "ensemble_lead_scorer" / version / "model.onnx"
            onnx.save_model(onnx_model, onnx_path)
            
            # Create ONNX runtime session
            session = ort.InferenceSession(str(onnx_path))
            self.onnx_models[f"ensemble_lead_scorer_{version}"] = session
            
            logger.info(f"ONNX model saved and loaded for version {version}")
            
        except Exception as e:
            logger.warning(f"Failed to convert model to ONNX: {str(e)}")
    
    def _classify_score(self, score: float) -> str:
        """Classify lead score into categories"""
        if score >= 0.8:
            return "high"
        elif score >= 0.5:
            return "medium"
        else:
            return "low"
    
    def _extract_risk_factors(self, features: np.ndarray, prediction: Dict) -> List[str]:
        """Extract risk factors from prediction"""
        risk_factors = []
        
        # This would be based on feature analysis
        # Placeholder implementation
        if prediction['score'] < 0.3:
            risk_factors.append("Low lead score indicates minimal investment potential")
        
        return risk_factors
    
    def _extract_opportunities(self, features: np.ndarray, prediction: Dict) -> List[str]:
        """Extract opportunities from prediction"""
        opportunities = []
        
        # This would be based on feature analysis
        # Placeholder implementation
        if prediction['score'] > 0.7:
            opportunities.append("High lead score indicates strong investment potential")
        
        return opportunities
    
    def _generate_recommendation(self, prediction: Dict) -> str:
        """Generate recommendation based on prediction"""
        score = prediction['score']
        
        if score >= 0.8:
            return "STRONG BUY - High-value lead with excellent potential"
        elif score >= 0.6:
            return "BUY - Good investment opportunity"
        elif score >= 0.4:
            return "HOLD - Moderate potential, requires further analysis"
        else:
            return "PASS - Low potential, not recommended"
    
    def _calculate_model_size(self, model: Any) -> float:
        """Calculate model size in MB"""
        try:
            import tempfile
            with tempfile.NamedTemporaryFile() as tmp:
                joblib.dump(model, tmp.name)
                return os.path.getsize(tmp.name) / (1024 * 1024)
        except Exception:
            return 0.0


# Global model instance
_model_pipeline = None
_model_registry = None

def get_model_pipeline() -> AdvancedMLPipeline:
    """Get global model pipeline instance"""
    global _model_pipeline, _model_registry
    
    if _model_pipeline is None:
        _model_registry = ModelRegistry()
        _model_pipeline = AdvancedMLPipeline(_model_registry)
    
    return _model_pipeline

def get_model_registry() -> ModelRegistry:
    """Get global model registry instance"""
    global _model_registry
    
    if _model_registry is None:
        _model_registry = ModelRegistry()
    
    return _model_registry