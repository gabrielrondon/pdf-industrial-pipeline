"""
Enhanced Feedback System API Endpoints
Integrates with the shared feedback package for ML improvement
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import json
import logging

from database.connection import get_db
from database.models import User, Job, MLPrediction
from auth.middleware import get_current_user
from ml_engine.feedback_integration import FeedbackIntegrator

# Pydantic models for request/response
from pydantic import BaseModel, Field
from enum import Enum

logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(prefix="/feedback", tags=["Enhanced Feedback"])

# Enums matching the frontend package
class DocumentType(str, Enum):
    IPTU = "iptu"
    PROPERTY_VALUATION = "property_valuation"
    RISK_ASSESSMENT = "risk_assessment"
    JUDICIAL_AUCTION = "judicial_auction"
    LEGAL_DOCUMENT = "legal_document"
    FINANCIAL_STATEMENT = "financial_statement"

class FeedbackType(str, Enum):
    QUICK_QUESTION = "quick_question"
    DETAILED_INPUT = "detailed_input"
    MISSING_INFO = "missing_info"
    PEER_VALIDATION = "peer_validation"
    QUALITY_RATING = "quality_rating"

class FeedbackQuestionType(str, Enum):
    YES_NO = "yes_no"
    RATING = "rating"
    TEXT_INPUT = "text_input"
    MULTIPLE_CHOICE = "multiple_choice"
    CURRENCY = "currency"
    SELECT = "select"

# Request/Response Models
class FeedbackQuestion(BaseModel):
    id: str
    type: FeedbackQuestionType
    question: str
    required: bool = False
    creditReward: int = Field(ge=0)
    options: Optional[List[str]] = None
    placeholder: Optional[str] = None
    helpText: Optional[str] = None
    validation: Optional[Dict[str, Any]] = None

class FeedbackAnswer(BaseModel):
    questionId: str
    value: Any  # Union[str, int, float, bool]
    confidence: Optional[float] = Field(None, ge=0, le=1)
    timeSpent: Optional[int] = None  # seconds

class FeedbackSubmission(BaseModel):
    documentId: str
    documentType: DocumentType
    feedbackType: FeedbackType
    answers: List[FeedbackAnswer]
    userId: str
    sessionId: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class MissingInfoReport(BaseModel):
    documentId: str
    category: str = Field(..., regex="^(financial|legal|property_details|risk_factors|other)$")
    description: str = Field(..., min_length=10, max_length=500)
    specificField: Optional[str] = None
    suggestedValue: Optional[str] = None
    severity: str = Field("medium", regex="^(low|medium|high)$")
    userId: str

class CreditReward(BaseModel):
    baseCredits: int = Field(ge=0)
    multiplier: float = Field(ge=1)
    bonus: int = Field(ge=0, default=0)
    reason: str
    qualityScore: Optional[float] = Field(None, ge=0, le=1)

class QuestionRequest(BaseModel):
    documentId: str
    documentType: DocumentType
    mlPredictions: Optional[Dict[str, Any]] = None
    userPlan: Optional[str] = "free"

# Response Models
class FeedbackResponse(BaseModel):
    success: bool
    credits: Optional[CreditReward] = None
    error: Optional[str] = None

class QuestionsResponse(BaseModel):
    questions: List[FeedbackQuestion]
    documentContext: Dict[str, Any]

class UserFeedbackStats(BaseModel):
    userId: str
    totalSubmissions: int
    creditsEarned: int
    averageQuality: float
    streakDays: int
    badges: List[str]
    multiplierTier: int
    lastSubmission: Optional[datetime]

# Initialize feedback integrator
feedback_integrator = FeedbackIntegrator()

@router.post("/questions", response_model=QuestionsResponse)
async def get_feedback_questions(
    request: QuestionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get appropriate feedback questions for a document based on ML predictions and user context
    """
    try:
        # Get document/job information
        job = db.query(Job).filter(Job.id == request.documentId).first()
        if not job:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Get ML predictions if available
        ml_prediction = db.query(MLPrediction).filter(
            MLPrediction.job_id == request.documentId
        ).first()
        
        # Build context
        document_context = {
            "job": {
                "id": job.id,
                "status": job.status,
                "file_name": job.file_name
            },
            "mlPredictions": request.mlPredictions or {},
            "userPlan": request.userPlan,
            "confidence": ml_prediction.confidence if ml_prediction else 0.5
        }
        
        # Generate questions using the feedback integrator
        questions = await feedback_integrator.generate_questions(
            document_type=request.documentType.value,
            ml_predictions=document_context["mlPredictions"],
            confidence=document_context["confidence"],
            user_plan=request.userPlan
        )
        
        return QuestionsResponse(
            questions=questions,
            documentContext=document_context
        )
        
    except Exception as e:
        logger.error(f"Error generating feedback questions: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate questions")

@router.post("/submit", response_model=FeedbackResponse)
async def submit_feedback(
    submission: FeedbackSubmission,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Submit user feedback and calculate credit rewards
    """
    try:
        # Validate document exists
        job = db.query(Job).filter(Job.id == submission.documentId).first()
        if not job:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Check rate limiting
        can_submit = await check_submission_rate_limit(
            submission.userId, 
            submission.documentId, 
            db
        )
        if not can_submit["canSubmit"]:
            raise HTTPException(
                status_code=429, 
                detail=f"Rate limit exceeded: {can_submit['reason']}"
            )
        
        # Get user stats for credit calculation
        user_stats = await get_user_feedback_stats_internal(submission.userId, db)
        
        # Calculate credits with quality scoring
        quality_score = await calculate_feedback_quality(submission, db)
        credits = calculate_credit_reward(
            submission=submission,
            user_stats=user_stats,
            quality_score=quality_score
        )
        
        # Store feedback in database
        feedback_record = await store_feedback_submission(submission, credits, db)
        
        # Update user credits
        await update_user_credits(submission.userId, credits, db)
        
        # Process feedback for ML training (background task)
        background_tasks.add_task(
            process_feedback_for_ml,
            submission,
            feedback_record["id"]
        )
        
        # Check for achievements/badges
        background_tasks.add_task(
            check_user_achievements,
            submission.userId,
            user_stats
        )
        
        return FeedbackResponse(
            success=True,
            credits=credits
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting feedback: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to submit feedback")

@router.post("/missing-info", response_model=FeedbackResponse)
async def report_missing_info(
    report: MissingInfoReport,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Report missing information that the AI failed to capture
    """
    try:
        # Validate document exists
        job = db.query(Job).filter(Job.id == report.documentId).first()
        if not job:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Calculate credits based on severity and quality
        base_credits = {
            "low": 8,
            "medium": 12,
            "high": 18
        }.get(report.severity, 12)
        
        # Get user stats for multipliers
        user_stats = await get_user_feedback_stats_internal(report.userId, db)
        
        # Quality assessment for missing info reports
        quality_score = assess_missing_info_quality(report)
        
        credits = CreditReward(
            baseCredits=base_credits,
            multiplier=1.0 + (user_stats.multiplierTier - 1) * 0.2,
            bonus=5 if quality_score > 0.8 else 0,
            reason=f"Missing info report ({report.severity} severity)",
            qualityScore=quality_score
        )
        
        # Store missing info report
        await store_missing_info_report(report, credits, db)
        
        # Update user credits
        await update_user_credits(report.userId, credits, db)
        
        # Process for ML improvement (background task)
        background_tasks.add_task(
            process_missing_info_for_ml,
            report
        )
        
        return FeedbackResponse(
            success=True,
            credits=credits
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error reporting missing info: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to report missing information")

@router.get("/user-stats/{user_id}", response_model=UserFeedbackStats)
async def get_user_feedback_stats(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get user's feedback statistics and achievements
    """
    try:
        stats = await get_user_feedback_stats_internal(user_id, db)
        return stats
        
    except Exception as e:
        logger.error(f"Error fetching user stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch user statistics")

@router.get("/can-submit/{user_id}/{document_id}")
async def can_submit_feedback(
    user_id: str,
    document_id: str,
    db: Session = Depends(get_db)
):
    """
    Check if user can submit feedback (rate limiting, cooldowns)
    """
    try:
        result = await check_submission_rate_limit(user_id, document_id, db)
        return result
        
    except Exception as e:
        logger.error(f"Error checking submission eligibility: {str(e)}")
        return {"canSubmit": True}  # Fail open

# Helper functions
async def check_submission_rate_limit(
    user_id: str, 
    document_id: str, 
    db: Session
) -> Dict[str, Any]:
    """Check if user can submit feedback based on rate limits"""
    
    # Check if user already submitted for this document recently
    # This would typically query a feedback_submissions table
    # For now, return True (implement based on your database schema)
    
    return {
        "canSubmit": True,
        "reason": None,
        "cooldownEndsAt": None
    }

async def get_user_feedback_stats_internal(
    user_id: str, 
    db: Session
) -> UserFeedbackStats:
    """Get user feedback statistics"""
    
    # This would typically query your feedback tables
    # Return default stats for now
    return UserFeedbackStats(
        userId=user_id,
        totalSubmissions=0,
        creditsEarned=0,
        averageQuality=0.8,
        streakDays=1,
        badges=[],
        multiplierTier=1,
        lastSubmission=None
    )

def calculate_credit_reward(
    submission: FeedbackSubmission,
    user_stats: UserFeedbackStats,
    quality_score: float
) -> CreditReward:
    """Calculate credit rewards with multipliers and bonuses"""
    
    # Base credits based on feedback type and answers
    base_credits = sum(
        5 if submission.feedbackType == FeedbackType.QUICK_QUESTION else 8
        for _ in submission.answers
    )
    
    # Multiplier based on user tier and streaks
    multiplier = 1.0
    if user_stats.streakDays >= 7:
        multiplier += 0.5
    elif user_stats.streakDays >= 3:
        multiplier += 0.2
    
    # Quality bonus
    bonus = 0
    if quality_score > 0.8:
        bonus = int(base_credits * 0.3)
    
    return CreditReward(
        baseCredits=base_credits,
        multiplier=multiplier,
        bonus=bonus,
        reason=f"Feedback submission with {user_stats.streakDays}-day streak",
        qualityScore=quality_score
    )

async def calculate_feedback_quality(
    submission: FeedbackSubmission,
    db: Session
) -> float:
    """Assess the quality of feedback submission"""
    
    quality_factors = []
    
    # Time spent per question (reasonable time indicates thoughtful answers)
    for answer in submission.answers:
        if answer.timeSpent:
            # 5-60 seconds per question is reasonable
            if 5 <= answer.timeSpent <= 60:
                quality_factors.append(1.0)
            elif answer.timeSpent < 5:
                quality_factors.append(0.5)  # Too quick
            else:
                quality_factors.append(0.8)  # Very thorough
        else:
            quality_factors.append(0.7)  # No timing data
    
    # Answer completeness for text inputs
    for answer in submission.answers:
        if isinstance(answer.value, str) and len(answer.value.strip()) > 10:
            quality_factors.append(1.0)  # Detailed text responses
        else:
            quality_factors.append(0.8)
    
    return sum(quality_factors) / len(quality_factors) if quality_factors else 0.5

def assess_missing_info_quality(report: MissingInfoReport) -> float:
    """Assess quality of missing information report"""
    
    quality_score = 0.5  # Base score
    
    # Description quality
    if len(report.description) > 50:
        quality_score += 0.2
    if len(report.description) > 100:
        quality_score += 0.1
    
    # Specific field provided
    if report.specificField:
        quality_score += 0.1
    
    # Suggested value provided
    if report.suggestedValue:
        quality_score += 0.1
    
    return min(1.0, quality_score)

async def store_feedback_submission(
    submission: FeedbackSubmission,
    credits: CreditReward,
    db: Session
) -> Dict[str, Any]:
    """Store feedback submission in database"""
    
    # This would typically insert into a feedback_submissions table
    # Return a mock record for now
    return {
        "id": f"feedback_{submission.sessionId}",
        "stored_at": datetime.utcnow()
    }

async def store_missing_info_report(
    report: MissingInfoReport,
    credits: CreditReward,
    db: Session
) -> Dict[str, Any]:
    """Store missing info report in database"""
    
    # This would typically insert into a missing_info_reports table
    return {
        "id": f"missing_{report.documentId}_{int(datetime.utcnow().timestamp())}",
        "stored_at": datetime.utcnow()
    }

async def update_user_credits(
    user_id: str,
    credits: CreditReward,
    db: Session
):
    """Update user's credit balance"""
    
    total_credits = int(credits.baseCredits * credits.multiplier + credits.bonus)
    
    # This would typically update your user credits table
    # For now, just log the transaction
    logger.info(f"User {user_id} earned {total_credits} credits: {credits.reason}")

async def process_feedback_for_ml(
    submission: FeedbackSubmission,
    feedback_id: str
):
    """Process feedback for ML model improvement (background task)"""
    
    try:
        # Use the existing feedback integrator
        await feedback_integrator.process_feedback(
            document_id=submission.documentId,
            feedback_data={
                "answers": [answer.dict() for answer in submission.answers],
                "feedback_type": submission.feedbackType.value,
                "document_type": submission.documentType.value,
                "metadata": submission.metadata or {}
            }
        )
        
        logger.info(f"Processed feedback {feedback_id} for ML training")
        
    except Exception as e:
        logger.error(f"Failed to process feedback {feedback_id} for ML: {str(e)}")

async def process_missing_info_for_ml(report: MissingInfoReport):
    """Process missing info reports for ML improvement (background task)"""
    
    try:
        # This would typically update training data to include the missing information
        logger.info(f"Processing missing info report for document {report.documentId}")
        
    except Exception as e:
        logger.error(f"Failed to process missing info report: {str(e)}")

async def check_user_achievements(user_id: str, stats: UserFeedbackStats):
    """Check and award user achievements/badges (background task)"""
    
    try:
        # Implementation for achievement system
        logger.info(f"Checking achievements for user {user_id}")
        
    except Exception as e:
        logger.error(f"Failed to check achievements for user {user_id}: {str(e)}")

# Include router in main API
def include_feedback_router(app):
    """Function to include this router in the main FastAPI app"""
    app.include_router(router, prefix="/api/v1")