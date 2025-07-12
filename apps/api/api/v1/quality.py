"""
Quality Assessment API Endpoints - Week 3 Implementation
API endpoints for quality assessment, compliance checking, and recommendations
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, Optional
import logging

from quality_engine.quality_assessor import assess_document_quality, get_quality_insights
from quality_engine.compliance_checker import check_document_compliance, get_compliance_summary
from quality_engine.recommendation_engine import generate_document_recommendations
from auth.middleware import get_current_user
from database.models import User

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/quality", tags=["Quality Assessment"])

@router.post("/assess")
async def assess_document_quality_endpoint(
    request_data: Dict[str, Any],
    current_user: User = Depends(get_current_user)
):
    """
    Perform comprehensive quality assessment of document
    
    Request body should contain:
    - text: Document text to assess
    - job_id: Optional job ID
    - enhanced_features: Optional enhanced features from Week 1
    """
    try:
        text = request_data.get('text')
        if not text:
            raise HTTPException(status_code=400, detail="Text is required")
        
        job_id = request_data.get('job_id', f'quality_{current_user.id}')
        enhanced_features = request_data.get('enhanced_features')
        
        # Perform quality assessment
        quality_metrics = assess_document_quality(text, enhanced_features, job_id)
        
        # Get quality insights
        insights = get_quality_insights(quality_metrics)
        
        return {
            "success": True,
            "data": {
                "quality_metrics": {
                    "overall_score": quality_metrics.overall_score,
                    "quality_level": quality_metrics.quality_level,
                    "completeness_score": quality_metrics.completeness_score,
                    "compliance_score": quality_metrics.compliance_score,
                    "clarity_score": quality_metrics.clarity_score,
                    "information_score": quality_metrics.information_score,
                    "missing_elements": quality_metrics.missing_elements,
                    "compliance_issues": quality_metrics.compliance_issues,
                    "quality_indicators": quality_metrics.quality_indicators,
                    "improvement_potential": quality_metrics.improvement_potential,
                    "confidence_level": quality_metrics.confidence_level,
                    "assessment_timestamp": quality_metrics.assessment_timestamp
                },
                "insights": insights,
                "job_id": job_id
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in quality assessment: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/compliance")
async def check_document_compliance_endpoint(
    request_data: Dict[str, Any],
    current_user: User = Depends(get_current_user)
):
    """
    Perform comprehensive compliance check against Brazilian legal requirements
    
    Request body should contain:
    - text: Document text to check
    - job_id: Optional job ID
    - enhanced_features: Optional enhanced features from Week 1
    """
    try:
        text = request_data.get('text')
        if not text:
            raise HTTPException(status_code=400, detail="Text is required")
        
        job_id = request_data.get('job_id', f'compliance_{current_user.id}')
        enhanced_features = request_data.get('enhanced_features')
        
        # Perform compliance check
        compliance_result = check_document_compliance(text, enhanced_features, job_id)
        
        # Get compliance summary
        summary = get_compliance_summary(compliance_result)
        
        return {
            "success": True,
            "data": {
                "compliance_result": {
                    "is_compliant": compliance_result.is_compliant,
                    "compliance_score": compliance_result.compliance_score,
                    "compliance_level": compliance_result.compliance_level,
                    "cpc_889_compliance": compliance_result.cpc_889_compliance,
                    "mandatory_requirements": compliance_result.mandatory_requirements,
                    "optional_requirements": compliance_result.optional_requirements,
                    "violations": compliance_result.violations,
                    "warnings": compliance_result.warnings,
                    "recommendations": compliance_result.recommendations,
                    "confidence_level": compliance_result.confidence_level,
                    "check_timestamp": compliance_result.check_timestamp
                },
                "summary": summary,
                "job_id": job_id
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in compliance check: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/recommendations")
async def generate_document_recommendations_endpoint(
    request_data: Dict[str, Any],
    current_user: User = Depends(get_current_user)
):
    """
    Generate intelligent recommendations for document improvement
    
    Request body should contain:
    - text: Document text
    - quality_metrics: Quality assessment results (optional, will be generated if not provided)
    - compliance_result: Compliance check results (optional, will be generated if not provided)
    - job_id: Optional job ID
    """
    try:
        text = request_data.get('text')
        if not text:
            raise HTTPException(status_code=400, detail="Text is required")
        
        job_id = request_data.get('job_id', f'recommendations_{current_user.id}')
        
        # Get or generate quality metrics
        quality_metrics_data = request_data.get('quality_metrics')
        if quality_metrics_data:
            # Use provided metrics (assume they're in the right format)
            from quality_engine.quality_assessor import QualityMetrics
            quality_metrics = QualityMetrics(**quality_metrics_data)
        else:
            # Generate new quality assessment
            enhanced_features = request_data.get('enhanced_features')
            quality_metrics = assess_document_quality(text, enhanced_features, job_id)
        
        # Get or generate compliance result
        compliance_data = request_data.get('compliance_result')
        if compliance_data:
            # Use provided compliance result
            from quality_engine.compliance_checker import ComplianceResult
            compliance_result = ComplianceResult(**compliance_data)
        else:
            # Generate new compliance check
            enhanced_features = request_data.get('enhanced_features')
            compliance_result = check_document_compliance(text, enhanced_features, job_id)
        
        # Generate recommendations
        recommendations = generate_document_recommendations(
            quality_metrics, compliance_result, text, job_id
        )
        
        return {
            "success": True,
            "data": {
                "recommendations": {
                    "total_recommendations": recommendations.total_recommendations,
                    "estimated_improvement": recommendations.estimated_improvement,
                    "critical_recommendations": [
                        {
                            "id": rec.id,
                            "title": rec.title,
                            "description": rec.description,
                            "category": rec.category,
                            "priority": rec.priority,
                            "impact": rec.impact,
                            "effort": rec.effort,
                            "action_type": rec.action_type,
                            "specific_action": rec.specific_action,
                            "example": rec.example,
                            "affects_compliance": rec.affects_compliance
                        }
                        for rec in recommendations.critical_recommendations
                    ],
                    "high_priority_recommendations": [
                        {
                            "id": rec.id,
                            "title": rec.title,
                            "description": rec.description,
                            "category": rec.category,
                            "priority": rec.priority,
                            "impact": rec.impact,
                            "effort": rec.effort,
                            "action_type": rec.action_type,
                            "specific_action": rec.specific_action,
                            "example": rec.example,
                            "affects_compliance": rec.affects_compliance
                        }
                        for rec in recommendations.high_priority_recommendations
                    ],
                    "medium_priority_recommendations": [
                        {
                            "id": rec.id,
                            "title": rec.title,
                            "description": rec.description,
                            "category": rec.category,
                            "priority": rec.priority,
                            "impact": rec.impact,
                            "effort": rec.effort,
                            "action_type": rec.action_type,
                            "specific_action": rec.specific_action,
                            "example": rec.example,
                            "affects_compliance": rec.affects_compliance
                        }
                        for rec in recommendations.medium_priority_recommendations
                    ],
                    "quick_wins": [
                        {
                            "id": rec.id,
                            "title": rec.title,
                            "description": rec.description,
                            "impact": rec.impact,
                            "effort": rec.effort,
                            "specific_action": rec.specific_action,
                            "example": rec.example
                        }
                        for rec in recommendations.quick_wins
                    ],
                    "action_plan": {
                        "immediate_actions": recommendations.immediate_actions,
                        "short_term_actions": recommendations.short_term_actions,
                        "long_term_actions": recommendations.long_term_actions
                    },
                    "generated_at": recommendations.generated_at
                },
                "job_id": job_id
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/comprehensive")
async def comprehensive_quality_analysis(
    request_data: Dict[str, Any],
    current_user: User = Depends(get_current_user)
):
    """
    Perform comprehensive quality analysis including assessment, compliance, and recommendations
    
    Request body should contain:
    - text: Document text to analyze
    - job_id: Optional job ID
    - enhanced_features: Optional enhanced features from Week 1
    """
    try:
        text = request_data.get('text')
        if not text:
            raise HTTPException(status_code=400, detail="Text is required")
        
        job_id = request_data.get('job_id', f'comprehensive_{current_user.id}')
        enhanced_features = request_data.get('enhanced_features')
        
        # Step 1: Quality Assessment
        quality_metrics = assess_document_quality(text, enhanced_features, job_id)
        quality_insights = get_quality_insights(quality_metrics)
        
        # Step 2: Compliance Check
        compliance_result = check_document_compliance(text, enhanced_features, job_id)
        compliance_summary = get_compliance_summary(compliance_result)
        
        # Step 3: Generate Recommendations
        recommendations = generate_document_recommendations(
            quality_metrics, compliance_result, text, job_id
        )
        
        # Step 4: Overall Analysis
        overall_status = "excellent"
        if quality_metrics.overall_score >= 80 and compliance_result.is_compliant:
            overall_status = "excellent"
            status_message = "Documento atende aos padrões de alta qualidade e conformidade"
        elif quality_metrics.overall_score >= 60 and compliance_result.compliance_score >= 70:
            overall_status = "good"
            status_message = "Documento é aceitável com pequenas melhorias necessárias"
        elif quality_metrics.overall_score >= 40 or compliance_result.compliance_score >= 50:
            overall_status = "needs_work"
            status_message = "Documento requer melhorias significativas"
        else:
            overall_status = "inadequate"
            status_message = "Documento precisa de revisão importante antes do uso"
        
        return {
            "success": True,
            "data": {
                "overall_analysis": {
                    "status": overall_status,
                    "status_message": status_message,
                    "quality_score": quality_metrics.overall_score,
                    "compliance_score": compliance_result.compliance_score,
                    "is_compliant": compliance_result.is_compliant,
                    "total_recommendations": recommendations.total_recommendations,
                    "critical_issues": len(recommendations.critical_recommendations),
                    "estimated_improvement": recommendations.estimated_improvement
                },
                "quality_assessment": {
                    "overall_score": quality_metrics.overall_score,
                    "quality_level": quality_metrics.quality_level,
                    "component_scores": {
                        "completeness": quality_metrics.completeness_score,
                        "compliance": quality_metrics.compliance_score,
                        "clarity": quality_metrics.clarity_score,
                        "information": quality_metrics.information_score
                    },
                    "missing_elements": quality_metrics.missing_elements,
                    "improvement_potential": quality_metrics.improvement_potential,
                    "insights": quality_insights
                },
                "compliance_check": {
                    "is_compliant": compliance_result.is_compliant,
                    "compliance_score": compliance_result.compliance_score,
                    "compliance_level": compliance_result.compliance_level,
                    "cpc_889_status": {
                        "requirements_met": sum(1 for details in compliance_result.cpc_889_compliance.values() 
                                              if details.get('compliant', False)),
                        "total_requirements": len(compliance_result.cpc_889_compliance)
                    },
                    "violations_count": len(compliance_result.violations),
                    "warnings_count": len(compliance_result.warnings),
                    "summary": compliance_summary
                },
                "recommendations": {
                    "total_count": recommendations.total_recommendations,
                    "priority_breakdown": {
                        "critical": len(recommendations.critical_recommendations),
                        "high": len(recommendations.high_priority_recommendations),
                        "medium": len(recommendations.medium_priority_recommendations),
                        "low": len(recommendations.low_priority_recommendations)
                    },
                    "quick_wins_count": len(recommendations.quick_wins),
                    "estimated_improvement": recommendations.estimated_improvement,
                    "immediate_actions": recommendations.immediate_actions[:3],
                    "top_recommendations": [
                        {
                            "title": rec.title,
                            "priority": rec.priority,
                            "impact": rec.impact,
                            "effort": rec.effort,
                            "specific_action": rec.specific_action
                        }
                        for rec in (recommendations.critical_recommendations + 
                                  recommendations.high_priority_recommendations)[:5]
                    ]
                },
                "job_id": job_id,
                "analysis_timestamp": quality_metrics.assessment_timestamp
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in comprehensive analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def get_quality_system_status():
    """Get current status of the quality assessment system"""
    try:
        return {
            "success": True,
            "data": {
                "system_status": "operational",
                "capabilities": {
                    "quality_assessment": True,
                    "compliance_checking": True,
                    "recommendation_generation": True,
                    "cpc_889_validation": True,
                    "brazilian_legal_compliance": True
                },
                "features": {
                    "quality_scoring": "0-100 scale",
                    "compliance_levels": ["Não Conforme", "Baixa Conformidade", "Parcialmente Conforme", "Conforme", "Totalmente Conforme"],
                    "quality_levels": ["Baixa", "Média", "Boa", "Excelente"],
                    "recommendation_priorities": ["critical", "high", "medium", "low"],
                    "quick_wins_identification": True
                },
                "performance": {
                    "average_processing_time": "<100ms",
                    "supported_document_types": ["brazilian_judicial_auctions"],
                    "max_document_size": "unlimited_text_length",
                    "confidence_scoring": True
                },
                "compliance_standards": {
                    "cpc_article_889": True,
                    "brazilian_auction_regulations": True,
                    "mandatory_requirements": 7,
                    "optional_requirements": 6
                }
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting quality system status: {e}")
        raise HTTPException(status_code=500, detail=str(e))