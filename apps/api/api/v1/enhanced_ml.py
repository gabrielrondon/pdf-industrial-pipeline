"""
Enhanced ML API Endpoints
Testing and management endpoints for the enhanced ML features
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, Optional
import logging

from ml_engine.integration_layer import (
    ml_integrator, 
    process_with_enhanced_features,
    get_ml_processor_status,
    test_ml_processing
)
from auth.middleware import get_current_user
from database.models import User

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/enhanced-ml", tags=["Enhanced ML"])

@router.get("/status")
async def get_enhancement_status():
    """Get current status of enhanced ML processing"""
    try:
        status = get_ml_processor_status()
        return {
            "success": True,
            "data": status
        }
    except Exception as e:
        logger.error(f"Error getting ML status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/test")
async def test_enhanced_processing(
    sample_text: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Test enhanced ML processing with sample data"""
    try:
        if sample_text:
            # Use provided sample text
            sample_analysis = {
                'job_id': f'test_{current_user.id}',
                'original_text': sample_text,
                'cleaned_text': sample_text,
                'entities': [],
                'lead_indicators': {'lead_score': 50.0}
            }
            result = process_with_enhanced_features(sample_analysis)
        else:
            # Use built-in test
            result = test_ml_processing()
        
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        logger.error(f"Error in enhanced ML test: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/process")
async def process_document_enhanced(
    request_data: Dict[str, Any],
    current_user: User = Depends(get_current_user)
):
    """
    Process document with enhanced features
    
    Request body should contain:
    - text: Document text to analyze
    - job_id: Optional job ID
    - metadata: Optional metadata
    """
    try:
        text = request_data.get('text')
        if not text:
            raise HTTPException(status_code=400, detail="Text is required")
        
        # Build analysis structure
        text_analysis = {
            'job_id': request_data.get('job_id', f'user_{current_user.id}'),
            'original_text': text,
            'cleaned_text': text,
            'entities': request_data.get('entities', []),
            'lead_indicators': request_data.get('lead_indicators', {'lead_score': 50.0})
        }
        
        job_metadata = request_data.get('metadata', {})
        
        # Process with enhanced features
        result = process_with_enhanced_features(text_analysis, job_metadata)
        
        return {
            "success": True,
            "data": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in enhanced processing: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/enable")
async def enable_enhancement(current_user: User = Depends(get_current_user)):
    """Enable enhanced ML processing"""
    try:
        ml_integrator.enable_enhancement()
        return {
            "success": True,
            "message": "Enhanced ML processing enabled"
        }
    except Exception as e:
        logger.error(f"Error enabling enhancement: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/disable")
async def disable_enhancement(current_user: User = Depends(get_current_user)):
    """Disable enhanced ML processing (use original only)"""
    try:
        ml_integrator.disable_enhancement()
        return {
            "success": True,
            "message": "Enhanced ML processing disabled - using original features only"
        }
    except Exception as e:
        logger.error(f"Error disabling enhancement: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/features/comparison")
async def compare_feature_extraction(
    sample_text: str,
    current_user: User = Depends(get_current_user)
):
    """
    Compare original vs enhanced feature extraction
    Useful for understanding improvements
    """
    try:
        # Test with enhanced features
        enhanced_result = process_with_enhanced_features({
            'job_id': f'comparison_{current_user.id}',
            'original_text': sample_text,
            'cleaned_text': sample_text,
            'entities': [],
            'lead_indicators': {'lead_score': 50.0}
        })
        
        # Test with original features only
        original_result = ml_integrator._process_original_only({
            'job_id': f'comparison_{current_user.id}',
            'original_text': sample_text,
            'cleaned_text': sample_text,
            'entities': [],
            'lead_indicators': {'lead_score': 50.0}
        })
        
        return {
            "success": True,
            "data": {
                "enhanced_result": {
                    "lead_score": enhanced_result.get('lead_score'),
                    "confidence": enhanced_result.get('confidence'),
                    "classification": enhanced_result.get('classification'),
                    "quality_score": enhanced_result.get('quality_assessment', {}).get('overall_score'),
                    "insights_count": len(enhanced_result.get('intelligent_insights', [])),
                    "feature_count": len(enhanced_result.get('enhanced_features', {}))
                },
                "original_result": {
                    "lead_score": original_result.get('lead_score'),
                    "confidence": original_result.get('confidence'),
                    "classification": original_result.get('classification'),
                    "feature_count": len(original_result.get('features', {}))
                },
                "improvements": {
                    "score_difference": enhanced_result.get('lead_score', 0) - original_result.get('lead_score', 0),
                    "confidence_difference": enhanced_result.get('confidence', 0) - original_result.get('confidence', 0),
                    "additional_features": len(enhanced_result.get('enhanced_features', {})) - len(original_result.get('features', {}))
                }
            }
        }
        
    except Exception as e:
        logger.error(f"Error in feature comparison: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/metrics")
async def get_enhancement_metrics(current_user: User = Depends(get_current_user)):
    """Get metrics about enhanced ML processing"""
    try:
        # Get current status
        status = get_ml_processor_status()
        
        # Get processing stats
        processor_stats = ml_integrator.enhanced_processor.get_processing_stats()
        
        return {
            "success": True,
            "data": {
                "status": status,
                "processor_stats": processor_stats,
                "feature_categories": {
                    "enhanced_features_count": 50,  # From EnhancedFeatureSet
                    "original_features_count": 30,  # Approximate from FeatureSet
                    "improvement_ratio": "67% more features"
                },
                "capabilities": {
                    "advanced_legal_patterns": True,
                    "brazilian_domain_knowledge": True,
                    "tfidf_analysis": True,
                    "risk_assessment": True,
                    "quality_scoring": True,
                    "intelligent_insights": True
                }
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting enhancement metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))