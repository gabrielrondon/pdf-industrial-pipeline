"""
Enhanced ML Processor - Integration Layer
Integrates enhanced features with existing ML pipeline for improved predictions
"""

import logging
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import json

# Import existing components
from .feature_engineering import FeatureEngineer, FeatureSet
from .enhanced_features import EnhancedFeatureExtractor, EnhancedFeatureSet
from .lead_scoring_models import ModelPrediction

try:
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.preprocessing import StandardScaler
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

logger = logging.getLogger(__name__)

class EnhancedMLProcessor:
    """
    Enhanced ML processor that combines original and enhanced features
    for better predictions while maintaining backward compatibility
    """
    
    def __init__(self):
        """Initialize with both original and enhanced feature extractors"""
        self.original_engineer = FeatureEngineer()
        self.enhanced_extractor = EnhancedFeatureExtractor()
        
        # Initialize improved models
        self.models = {}
        self.scalers = {}
        self.feature_weights = self._calculate_feature_weights()
        
        logger.info("Enhanced ML Processor initialized")
    
    def _calculate_feature_weights(self) -> Dict[str, float]:
        """Calculate weights for different feature categories based on domain knowledge"""
        return {
            # Enhanced features (higher weights for proven valuable features)
            'financial_features': 0.25,      # Financial info is crucial
            'legal_compliance': 0.20,        # Legal aspects are critical
            'risk_assessment': 0.20,         # Risk evaluation is key
            'document_quality': 0.15,        # Quality affects reliability
            'temporal_urgency': 0.10,        # Timing matters
            'structural_analysis': 0.10      # Document structure indicates quality
        }
    
    def process_document_enhanced(self, 
                                text_analysis: Dict[str, Any],
                                job_metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process document with enhanced features for better predictions
        
        Args:
            text_analysis: Original text analysis results
            job_metadata: Optional job metadata
            
        Returns:
            Enhanced analysis results with improved predictions
        """
        start_time = datetime.now()
        
        try:
            # Extract text for processing
            text = text_analysis.get('cleaned_text', text_analysis.get('original_text', ''))
            job_id = text_analysis.get('job_id', '')
            
            # 1. Extract original features (maintain compatibility)
            original_features = self.original_engineer.extract_features(
                text_analysis, 
                job_metadata=job_metadata
            )
            
            # 2. Extract enhanced features
            enhanced_features = self.enhanced_extractor.extract_enhanced_features(
                text, 
                job_id=job_id
            )
            
            # 3. Combine features intelligently
            combined_prediction = self._combine_predictions(original_features, enhanced_features)
            
            # 4. Generate insights and recommendations
            insights = self._generate_intelligent_insights(enhanced_features, combined_prediction)
            
            # 5. Assess quality and confidence
            quality_assessment = self._assess_analysis_quality(enhanced_features, text_analysis)
            
            # 6. Calculate processing metrics
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Build enhanced result
            enhanced_result = {
                # Original compatibility
                'lead_score': combined_prediction['lead_score'],
                'confidence': combined_prediction['confidence'],
                'classification': combined_prediction['classification'],
                
                # Enhanced information
                'enhanced_features': self.enhanced_extractor.features_to_dict(enhanced_features),
                'original_features': self._features_to_dict(original_features),
                'combined_prediction': combined_prediction,
                'quality_assessment': quality_assessment,
                'intelligent_insights': insights,
                
                # Metadata
                'processing_metadata': {
                    'enhanced_processing_time': processing_time,
                    'total_features_extracted': len(self.enhanced_extractor.features_to_dict(enhanced_features)),
                    'enhancement_version': '1.0',
                    'processing_timestamp': datetime.now().isoformat()
                }
            }
            
            logger.info(f"Enhanced processing completed for {job_id}: "
                       f"score={combined_prediction['lead_score']:.2f}, "
                       f"quality={quality_assessment['overall_score']:.1f}")
            
            return enhanced_result
            
        except Exception as e:
            logger.error(f"Error in enhanced ML processing: {e}")
            # Fallback to original processing
            return self._fallback_processing(text_analysis, job_metadata)
    
    def _combine_predictions(self, 
                           original_features: FeatureSet, 
                           enhanced_features: EnhancedFeatureSet) -> Dict[str, Any]:
        """Intelligently combine original and enhanced predictions"""
        
        # Extract key metrics from both feature sets
        original_score = original_features.original_lead_score
        
        # Calculate enhanced score using domain-specific rules
        enhanced_score = self._calculate_enhanced_score(enhanced_features)
        
        # Weighted combination (favor enhanced features if confidence is high)
        enhanced_weight = 0.7 if enhanced_features.extraction_confidence > 70 else 0.4
        original_weight = 1.0 - enhanced_weight
        
        combined_score = (enhanced_score * enhanced_weight + 
                         original_score * original_weight)
        
        # Calculate confidence based on consistency and feature quality
        confidence = self._calculate_prediction_confidence(
            original_features, enhanced_features, original_score, enhanced_score
        )
        
        # Determine classification
        classification = self._classify_lead_score(combined_score)
        
        return {
            'lead_score': round(combined_score, 2),
            'confidence': round(confidence, 2),
            'classification': classification,
            'score_breakdown': {
                'original_score': round(original_score, 2),
                'enhanced_score': round(enhanced_score, 2),
                'original_weight': original_weight,
                'enhanced_weight': enhanced_weight
            },
            'prediction_factors': self._identify_prediction_factors(enhanced_features)
        }
    
    def _calculate_enhanced_score(self, features: EnhancedFeatureSet) -> float:
        """Calculate enhanced lead score using improved algorithm"""
        
        score_components = {}
        
        # Financial attractiveness (0-30 points)
        financial_score = 0
        if features.currency_mentions > 0:
            financial_score += 10
        if features.max_amount > 100000:  # High-value property
            financial_score += 10
        if features.debt_indicators < 3:  # Low debt concerns
            financial_score += 10
        score_components['financial'] = min(30, financial_score)
        
        # Legal quality (0-25 points) 
        legal_score = 0
        legal_score += min(15, features.legal_bigrams * 3)  # Proper legal terminology
        legal_score += min(10, features.cpc_references * 5)  # Legal references
        if features.high_risk_patterns == 0:  # No high risk indicators
            legal_score += 5
        score_components['legal'] = min(25, legal_score)
        
        # Document quality (0-20 points)
        quality_score = features.completeness_score * 0.15 + features.clarity_score * 0.05
        score_components['quality'] = min(20, quality_score)
        
        # Investment opportunity (0-15 points)
        opportunity_score = features.investment_attractiveness * 0.15
        score_components['opportunity'] = min(15, opportunity_score)
        
        # Risk mitigation (0-10 points)
        risk_score = 10
        risk_score -= features.high_risk_patterns * 3
        risk_score += features.risk_mitigation_mentions * 2
        score_components['risk'] = max(0, min(10, risk_score))
        
        # Total score
        total_score = sum(score_components.values())
        
        return min(100, total_score)
    
    def _calculate_prediction_confidence(self, 
                                       original_features: FeatureSet,
                                       enhanced_features: EnhancedFeatureSet,
                                       original_score: float,
                                       enhanced_score: float) -> float:
        """Calculate confidence in the prediction"""
        
        confidence_factors = []
        
        # Score consistency (how close are original and enhanced scores?)
        score_diff = abs(original_score - enhanced_score)
        consistency_score = max(0, 100 - score_diff * 2)  # Penalty for large differences
        confidence_factors.append(consistency_score * 0.3)
        
        # Feature quality
        feature_quality = enhanced_features.extraction_confidence
        confidence_factors.append(feature_quality * 0.3)
        
        # Document completeness
        completeness = enhanced_features.completeness_score
        confidence_factors.append(completeness * 0.2)
        
        # Information density (more information = higher confidence)
        density_score = min(100, enhanced_features.information_density * 10)
        confidence_factors.append(density_score * 0.2)
        
        return sum(confidence_factors)
    
    def _classify_lead_score(self, score: float) -> str:
        """Classify lead score into categories"""
        if score >= 75:
            return 'high'
        elif score >= 50:
            return 'medium'
        else:
            return 'low'
    
    def _identify_prediction_factors(self, features: EnhancedFeatureSet) -> List[str]:
        """Identify key factors influencing the prediction"""
        factors = []
        
        # Positive factors
        if features.currency_mentions > 2:
            factors.append("Múltiplas informações financeiras disponíveis")
        
        if features.legal_bigrams > 3:
            factors.append("Terminologia legal apropriada")
        
        if features.low_risk_patterns > features.high_risk_patterns:
            factors.append("Indicadores de baixo risco")
        
        if features.completeness_score > 80:
            factors.append("Documento completo e bem estruturado")
        
        # Negative factors
        if features.high_risk_patterns > 2:
            factors.append("Múltiplos indicadores de risco identificados")
        
        if features.debt_indicators > 4:
            factors.append("Muitas menções de dívidas ou débitos")
        
        if features.completeness_score < 50:
            factors.append("Documento incompleto ou mal estruturado")
        
        return factors
    
    def _generate_intelligent_insights(self, 
                                     features: EnhancedFeatureSet, 
                                     prediction: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate intelligent insights based on analysis"""
        insights = []
        
        # Financial insights
        if features.max_amount > 0:
            ratio_insight = self._analyze_financial_ratio(features)
            if ratio_insight:
                insights.append(ratio_insight)
        
        # Risk insights
        risk_insight = self._analyze_risk_profile(features)
        if risk_insight:
            insights.append(risk_insight)
        
        # Temporal insights
        if features.deadline_mentions > 0:
            temporal_insight = {
                'type': 'temporal',
                'category': 'deadline',
                'message': f"Documento menciona {features.deadline_mentions} prazo(s) - atenção aos vencimentos",
                'priority': 'medium',
                'action_required': True
            }
            insights.append(temporal_insight)
        
        # Quality insights
        if features.completeness_score < 60:
            quality_insight = {
                'type': 'quality',
                'category': 'completeness',
                'message': f"Qualidade documental baixa ({features.completeness_score:.1f}%) - resultados podem ser imprecisos",
                'priority': 'high',
                'action_required': True
            }
            insights.append(quality_insight)
        
        # Legal insights
        if features.cpc_references == 0 and features.legal_bigrams < 2:
            legal_insight = {
                'type': 'legal',
                'category': 'compliance',
                'message': "Poucas referências legais encontradas - verifique conformidade processual",
                'priority': 'medium',
                'action_required': True
            }
            insights.append(legal_insight)
        
        return insights
    
    def _analyze_financial_ratio(self, features: EnhancedFeatureSet) -> Optional[Dict[str, Any]]:
        """Analyze financial ratios and provide insights"""
        if features.max_amount == 0:
            return None
        
        # Estimate debt-to-value ratio based on mentions
        debt_ratio_estimate = features.debt_indicators / max(1, features.currency_mentions)
        
        if debt_ratio_estimate > 0.5:
            return {
                'type': 'financial',
                'category': 'debt_ratio',
                'message': f"Alta proporção de menções de dívida - possível alto endividamento",
                'priority': 'high',
                'action_required': True,
                'confidence': 0.6
            }
        elif debt_ratio_estimate < 0.2:
            return {
                'type': 'financial',
                'category': 'debt_ratio',
                'message': f"Baixa proporção de menções de dívida - situação financeira aparentemente positiva",
                'priority': 'low',
                'action_required': False,
                'confidence': 0.7
            }
        
        return None
    
    def _analyze_risk_profile(self, features: EnhancedFeatureSet) -> Optional[Dict[str, Any]]:
        """Analyze risk profile and provide insights"""
        total_risk_indicators = (features.high_risk_patterns + 
                               features.medium_risk_patterns * 0.5)
        
        if total_risk_indicators > 3:
            return {
                'type': 'risk',
                'category': 'high_risk',
                'message': f"Múltiplos indicadores de risco ({int(total_risk_indicators)}) - análise cuidadosa necessária",
                'priority': 'high',
                'action_required': True,
                'confidence': 0.8
            }
        elif features.low_risk_patterns > 2 and total_risk_indicators == 0:
            return {
                'type': 'risk',
                'category': 'low_risk',
                'message': f"Múltiplos indicadores positivos - baixo perfil de risco",
                'priority': 'low',
                'action_required': False,
                'confidence': 0.75
            }
        
        return None
    
    def _assess_analysis_quality(self, 
                               features: EnhancedFeatureSet, 
                               text_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Assess the quality of the analysis"""
        
        quality_scores = {
            'completeness': features.completeness_score,
            'clarity': features.clarity_score,
            'information_density': min(100, features.information_density * 10),
            'extraction_confidence': features.extraction_confidence
        }
        
        # Calculate weighted overall score
        weights = {'completeness': 0.3, 'clarity': 0.25, 'information_density': 0.25, 'extraction_confidence': 0.2}
        overall_score = sum(score * weights[metric] for metric, score in quality_scores.items())
        
        # Generate quality level
        if overall_score >= 80:
            quality_level = "Excelente"
            recommendations = ["Análise completa e confiável"]
        elif overall_score >= 60:
            quality_level = "Boa"
            recommendations = ["Análise adequada para decisão"]
        elif overall_score >= 40:
            quality_level = "Regular"
            recommendations = ["Considere obter informações adicionais"]
        else:
            quality_level = "Baixa"
            recommendations = ["Recomenda-se nova análise com melhor qualidade documental"]
        
        # Add specific recommendations
        if features.completeness_score < 70:
            recommendations.append("Documento incompleto - verifique informações essenciais")
        
        if features.clarity_score < 60:
            recommendations.append("Baixa clareza do texto - considere melhor qualidade de digitalização")
        
        return {
            'overall_score': round(overall_score, 1),
            'quality_level': quality_level,
            'breakdown': {k: round(v, 1) for k, v in quality_scores.items()},
            'recommendations': recommendations,
            'confidence_level': 'high' if overall_score >= 70 else 'medium' if overall_score >= 50 else 'low'
        }
    
    def _fallback_processing(self, 
                           text_analysis: Dict[str, Any], 
                           job_metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Fallback to original processing in case of errors"""
        logger.warning("Falling back to original processing due to enhancement errors")
        
        try:
            # Use original feature engineer
            original_features = self.original_engineer.extract_features(text_analysis, job_metadata=job_metadata)
            
            return {
                'lead_score': original_features.original_lead_score,
                'confidence': 70.0,  # Default confidence
                'classification': self._classify_lead_score(original_features.original_lead_score),
                'enhanced_features': None,
                'original_features': self._features_to_dict(original_features),
                'quality_assessment': {
                    'overall_score': 60.0,
                    'quality_level': "Processamento básico",
                    'recommendations': ["Processado com sistema básico devido a erro no sistema avançado"]
                },
                'intelligent_insights': [],
                'processing_metadata': {
                    'enhancement_status': 'fallback',
                    'processing_timestamp': datetime.now().isoformat()
                }
            }
        except Exception as e:
            logger.error(f"Even fallback processing failed: {e}")
            return {
                'lead_score': 50.0,
                'confidence': 30.0,
                'classification': 'medium',
                'error': f"Processing failed: {str(e)}"
            }
    
    def _features_to_dict(self, features: FeatureSet) -> Dict[str, Any]:
        """Convert FeatureSet to dictionary"""
        try:
            return asdict(features)
        except:
            # Manual conversion if asdict fails
            return {
                'job_id': features.job_id,
                'page_number': features.page_number,
                'text_length': features.text_length,
                'word_count': features.word_count,
                'entity_count': features.entity_count,
                'original_lead_score': features.original_lead_score
            }
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get processing statistics"""
        return {
            'enhanced_extractor_ready': bool(self.enhanced_extractor),
            'original_engineer_ready': bool(self.original_engineer),
            'sklearn_available': SKLEARN_AVAILABLE,
            'feature_weights': self.feature_weights,
            'initialization_time': datetime.now().isoformat()
        }

# Global instance for easy integration
enhanced_ml_processor = EnhancedMLProcessor()