"""
Integration Layer for Enhanced Features
Seamlessly integrates enhanced ML features with existing pipeline
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

# Import existing components
from .enhanced_ml_processor import enhanced_ml_processor
from .feature_engineering import feature_engineer
from .lead_scoring_models import ModelPrediction

logger = logging.getLogger(__name__)

class MLPipelineIntegrator:
    """
    Integration layer that provides enhanced ML capabilities
    while maintaining full backward compatibility
    """
    
    def __init__(self):
        self.enhanced_processor = enhanced_ml_processor
        self.original_engineer = feature_engineer
        self.enhancement_enabled = True
        self.fallback_enabled = True
        
        logger.info("ML Pipeline Integrator initialized - enhanced features enabled")
    
    def process_text_analysis(self, 
                             text_analysis: Dict[str, Any],
                             job_metadata: Optional[Dict[str, Any]] = None,
                             use_enhanced: bool = True) -> Dict[str, Any]:
        """
        Main integration point for enhanced ML processing
        
        Args:
            text_analysis: Original text analysis results
            job_metadata: Optional job metadata
            use_enhanced: Whether to use enhanced features (default: True)
            
        Returns:
            Enhanced analysis results with backward compatibility
        """
        
        # Check if enhancement should be used
        if not use_enhanced or not self.enhancement_enabled:
            return self._process_original_only(text_analysis, job_metadata)
        
        try:
            # Process with enhanced features
            enhanced_result = self.enhanced_processor.process_document_enhanced(
                text_analysis, job_metadata
            )
            
            # Add compatibility layer for existing code
            enhanced_result.update({
                # Backward compatibility fields
                'lead_indicators': {
                    'lead_score': enhanced_result['lead_score'],
                    'confidence': enhanced_result['confidence'],
                    'classification': enhanced_result['classification']
                },
                'features': enhanced_result.get('original_features', {}),
                
                # Enhancement status
                'enhancement_status': 'enabled',
                'enhancement_version': '1.0'
            })
            
            logger.info(f"Enhanced processing successful for job {text_analysis.get('job_id', 'unknown')}")
            return enhanced_result
            
        except Exception as e:
            logger.error(f"Enhanced processing failed: {e}")
            
            if self.fallback_enabled:
                logger.info("Falling back to original processing")
                return self._process_original_with_fallback_info(text_analysis, job_metadata, str(e))
            else:
                raise e
    
    def _process_original_only(self, 
                              text_analysis: Dict[str, Any],
                              job_metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process using only original features"""
        
        try:
            # Extract features using original engineer
            features = self.original_engineer.extract_features(text_analysis, job_metadata=job_metadata)
            
            # Build compatible result
            return {
                'lead_score': features.original_lead_score,
                'confidence': 75.0,  # Default confidence for original processing
                'classification': self._classify_score(features.original_lead_score),
                'lead_indicators': {
                    'lead_score': features.original_lead_score,
                    'confidence': 75.0,
                    'classification': self._classify_score(features.original_lead_score)
                },
                'features': self._convert_features_to_dict(features),
                'enhancement_status': 'disabled',
                'processing_metadata': {
                    'processing_mode': 'original_only',
                    'processing_timestamp': datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Original processing also failed: {e}")
            return self._generate_minimal_response(text_analysis, str(e))
    
    def _process_original_with_fallback_info(self, 
                                           text_analysis: Dict[str, Any],
                                           job_metadata: Optional[Dict[str, Any]],
                                           error_info: str) -> Dict[str, Any]:
        """Process with original features but include fallback information"""
        
        result = self._process_original_only(text_analysis, job_metadata)
        
        # Add fallback information
        result.update({
            'enhancement_status': 'fallback',
            'fallback_reason': error_info,
            'quality_assessment': {
                'overall_score': 60.0,
                'quality_level': "Processamento básico",
                'recommendations': [
                    "Processado com sistema básico devido a erro no sistema avançado",
                    "Resultado pode ter menor precisão que o processamento avançado"
                ]
            }
        })
        
        return result
    
    def _generate_minimal_response(self, 
                                 text_analysis: Dict[str, Any],
                                 error_info: str) -> Dict[str, Any]:
        """Generate minimal response when all processing fails"""
        
        return {
            'lead_score': 50.0,  # Neutral score
            'confidence': 30.0,  # Low confidence
            'classification': 'medium',
            'lead_indicators': {
                'lead_score': 50.0,
                'confidence': 30.0,
                'classification': 'medium'
            },
            'features': {},
            'enhancement_status': 'error',
            'error_info': error_info,
            'processing_metadata': {
                'processing_mode': 'minimal_fallback',
                'processing_timestamp': datetime.now().isoformat()
            }
        }
    
    def _classify_score(self, score: float) -> str:
        """Classify lead score into categories"""
        if score >= 75:
            return 'high'
        elif score >= 50:
            return 'medium'
        else:
            return 'low'
    
    def _convert_features_to_dict(self, features) -> Dict[str, Any]:
        """Convert features to dictionary format"""
        try:
            if hasattr(features, '__dict__'):
                return {k: v for k, v in features.__dict__.items() 
                       if not k.startswith('_')}
            else:
                return {}
        except Exception:
            return {}
    
    def enable_enhancement(self):
        """Enable enhanced processing"""
        self.enhancement_enabled = True
        logger.info("Enhanced processing enabled")
    
    def disable_enhancement(self):
        """Disable enhanced processing (use original only)"""
        self.enhancement_enabled = False
        logger.info("Enhanced processing disabled - using original features only")
    
    def enable_fallback(self):
        """Enable fallback to original processing on errors"""
        self.fallback_enabled = True
        logger.info("Fallback to original processing enabled")
    
    def disable_fallback(self):
        """Disable fallback (raise errors instead)"""
        self.fallback_enabled = False
        logger.info("Fallback disabled - errors will be raised")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status of the integration layer"""
        return {
            'enhancement_enabled': self.enhancement_enabled,
            'fallback_enabled': self.fallback_enabled,
            'enhanced_processor_ready': bool(self.enhanced_processor),
            'original_engineer_ready': bool(self.original_engineer),
            'integration_version': '1.0',
            'status_timestamp': datetime.now().isoformat()
        }
    
    def test_processing(self, sample_text: str = None) -> Dict[str, Any]:
        """Test the processing pipeline with sample data"""
        
        if sample_text is None:
            sample_text = """
            EDITAL DE LEILÃO JUDICIAL
            
            O Juiz de Direito da 1ª Vara Cível da Comarca de São Paulo, no processo nº 1234567-89.2023.8.26.0100,
            torna público que será realizada hasta pública do imóvel localizado na Rua das Flores, 123.
            
            VALOR DA AVALIAÇÃO: R$ 350.000,00
            LANCE MÍNIMO: R$ 233.333,33 (2/3 do valor da avaliação)
            DÉBITO TOTAL: R$ 45.000,00
            
            O imóvel encontra-se livre de ocupação e com documentação regular.
            """
        
        sample_analysis = {
            'job_id': 'test_job_001',
            'original_text': sample_text,
            'cleaned_text': sample_text,
            'entities': [],
            'lead_indicators': {'lead_score': 70.0}
        }
        
        try:
            result = self.process_text_analysis(sample_analysis)
            return {
                'test_status': 'success',
                'result_summary': {
                    'lead_score': result.get('lead_score'),
                    'confidence': result.get('confidence'),
                    'classification': result.get('classification'),
                    'enhancement_status': result.get('enhancement_status')
                },
                'test_timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'test_status': 'failed',
                'error': str(e),
                'test_timestamp': datetime.now().isoformat()
            }

# Global integrator instance
ml_integrator = MLPipelineIntegrator()

# Convenience functions for easy integration
def process_with_enhanced_features(text_analysis: Dict[str, Any], 
                                 job_metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Convenience function for enhanced processing
    Drop-in replacement for existing ML processing calls
    """
    return ml_integrator.process_text_analysis(text_analysis, job_metadata, use_enhanced=True)

def process_with_original_features(text_analysis: Dict[str, Any], 
                                 job_metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Convenience function for original processing only
    """
    return ml_integrator.process_text_analysis(text_analysis, job_metadata, use_enhanced=False)

def get_ml_processor_status() -> Dict[str, Any]:
    """Get current ML processor status"""
    return ml_integrator.get_status()

def test_ml_processing() -> Dict[str, Any]:
    """Test ML processing with sample data"""
    return ml_integrator.test_processing()