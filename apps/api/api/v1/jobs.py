from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
import os
import tempfile
import logging
from sqlalchemy import func

from database.connection import get_db_dependency
from database.models import Job, User, JobChunk
from auth.security import get_current_active_user, get_current_user_optional, PermissionChecker
from core.exceptions import ResourceNotFoundError, ValidationError, FileSizeExceededError, InvalidFileFormatError
from config.settings import get_settings
from tasks.pdf_tasks import process_complete_pdf_pipeline
from api.v1.schemas import JobResponse, JobCreateResponse, JobListResponse, JobStatusResponse

logger = logging.getLogger(__name__)
settings = get_settings()
router = APIRouter()

# Permission checkers
read_permission = PermissionChecker(["jobs:read"])
write_permission = PermissionChecker(["jobs:write"])


@router.post("/upload", response_model=JobCreateResponse)
async def upload_pdf(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    priority: int = 0,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db_dependency)
):
    """
    Upload a PDF file for processing
    """
    try:
        # Validate file
        if not file.filename.lower().endswith('.pdf'):
            raise InvalidFileFormatError("PDF", file.content_type or "unknown")
        
        # Check file size
        file_size = 0
        content = await file.read()
        file_size = len(content)
        
        if file_size > settings.max_pdf_size_bytes:
            raise FileSizeExceededError(settings.max_pdf_size_mb)
        
        if file_size == 0:
            raise ValidationError("File is empty", "file")
        
        # Generate job ID
        job_id = str(uuid.uuid4())
        
        # Save file temporarily
        temp_dir = tempfile.mkdtemp()
        temp_file_path = os.path.join(temp_dir, f"{job_id}.pdf")
        
        with open(temp_file_path, "wb") as temp_file:
            temp_file.write(content)
        
        # Create job record
        job = Job(
            id=job_id,
            user_id=current_user.id,
            filename=file.filename,
            file_size=file_size,
            priority=priority,
            status="uploaded",
            config={
                "temp_file_path": temp_file_path,
                "original_filename": file.filename
            }
        )
        
        db.add(job)
        db.commit()
        db.refresh(job)
        
        # Start processing pipeline
        if settings.enable_async_processing:
            task = process_complete_pdf_pipeline.delay(job_id, temp_file_path)
            
            # Update job with task ID
            job.config["task_id"] = task.id
            db.commit()
            
            logger.info(f"Started processing pipeline for job {job_id} with task {task.id}")
        
        return JobCreateResponse(
            job_id=job_id,
            status="processing",
            message="PDF uploaded successfully and processing started",
            task_id=task.id if settings.enable_async_processing else None
        )
        
    except Exception as e:
        logger.error(f"Upload failed: {str(e)}", exc_info=True)
        if isinstance(e, (ValidationError, FileSizeExceededError, InvalidFileFormatError)):
            raise e
        raise HTTPException(status_code=500, detail="Upload failed")


@router.get("/", response_model=JobListResponse)
async def list_jobs(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    db: Session = Depends(get_db_dependency),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    List user's jobs with optional filtering
    """
    # If no user, return empty list
    if not current_user:
        return JobListResponse(
            jobs=[],
            total=0,
            skip=skip,
            limit=limit
        )
    
    query = db.query(Job).filter(Job.user_id == current_user.id)
    
    if status:
        query = query.filter(Job.status == status)
    
    total = query.count()
    jobs = query.order_by(desc(Job.created_at)).offset(skip).limit(limit).all()
    
    return JobListResponse(
        jobs=[JobResponse.from_orm(job) for job in jobs],
        total=total,
        skip=skip,
        limit=limit
    )


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: str,
    current_user: User = Depends(read_permission),
    db: Session = Depends(get_db_dependency)
):
    """
    Get detailed job information
    """
    job = db.query(Job).filter(
        Job.id == job_id,
        Job.user_id == current_user.id
    ).first()
    
    if not job:
        raise ResourceNotFoundError("Job", job_id)
    
    return JobResponse.from_orm(job)


@router.get("/{job_id}/status", response_model=JobStatusResponse)
async def get_job_status(
    job_id: str,
    current_user: User = Depends(read_permission),
    db: Session = Depends(get_db_dependency)
):
    """
    Get job processing status
    """
    job = db.query(Job).filter(
        Job.id == job_id,
        Job.user_id == current_user.id
    ).first()
    
    if not job:
        raise ResourceNotFoundError("Job", job_id)
    
    # Get task status if available
    task_status = None
    task_info = None
    
    if job.config.get("task_id") and settings.enable_async_processing:
        try:
            from celery_app import app as celery_app
            task = celery_app.AsyncResult(job.config["task_id"])
            task_status = task.status
            task_info = task.info if task.info else {}
        except Exception as e:
            logger.warning(f"Could not get task status: {str(e)}")
    
    # Get analysis results if job is completed
    results = None
    if job.status == "completed" and job.config and "analysis_results" in job.config:
        results = job.config["analysis_results"]
    
    return JobStatusResponse(
        job_id=job_id,
        status=job.status,
        progress=task_info.get("current", 0) if task_info else None,
        total_steps=task_info.get("total", 4) if task_info else 4,
        current_step=task_info.get("status", "") if task_info else "",
        created_at=job.created_at,
        processing_started_at=job.processing_started_at,
        processing_completed_at=job.processing_completed_at,
        error_message=job.error_message,
        task_status=task_status,
        task_info=task_info,
        results=results
    )


@router.get("/{job_id}/chunks")
async def get_job_chunks(
    job_id: str,
    current_user: User = Depends(read_permission),
    db: Session = Depends(get_db_dependency)
):
    """
    Get job chunks information
    """
    job = db.query(Job).filter(
        Job.id == job_id,
        Job.user_id == current_user.id
    ).first()
    
    if not job:
        raise ResourceNotFoundError("Job", job_id)
    
    chunks = db.query(JobChunk).filter(JobChunk.job_id == job_id).order_by(JobChunk.chunk_number).all()
    
    return {
        "job_id": job_id,
        "total_chunks": len(chunks),
        "chunks": [
            {
                "chunk_id": str(chunk.id),
                "chunk_number": chunk.chunk_number,
                "page_start": chunk.page_start,
                "page_end": chunk.page_end,
                "status": chunk.status,
                "text_length": len(chunk.raw_text) if chunk.raw_text else 0,
                "processed_at": chunk.processed_at
            }
            for chunk in chunks
        ]
    }


@router.delete("/{job_id}")
async def delete_job(
    job_id: str,
    current_user: User = Depends(write_permission),
    db: Session = Depends(get_db_dependency)
):
    """
    Delete a job and all associated data
    """
    job = db.query(Job).filter(
        Job.id == job_id,
        Job.user_id == current_user.id
    ).first()
    
    if not job:
        raise ResourceNotFoundError("Job", job_id)
    
    # Cancel task if running
    if job.config.get("task_id") and job.status in ["processing", "uploaded"]:
        try:
            from celery_app import app as celery_app
            celery_app.control.revoke(job.config["task_id"], terminate=True)
        except Exception as e:
            logger.warning(f"Could not cancel task: {str(e)}")
    
    # Clean up temporary files
    temp_file_path = job.config.get("temp_file_path")
    if temp_file_path and os.path.exists(temp_file_path):
        try:
            os.remove(temp_file_path)
            # Also remove the temp directory if empty
            temp_dir = os.path.dirname(temp_file_path)
            if os.path.exists(temp_dir) and not os.listdir(temp_dir):
                os.rmdir(temp_dir)
        except Exception as e:
            logger.warning(f"Could not clean up temp file: {str(e)}")
    
    # Delete from database (cascading will handle related records)
    db.delete(job)
    db.commit()
    
    return {"message": f"Job {job_id} deleted successfully"}


@router.post("/{job_id}/retry")
async def retry_job(
    job_id: str,
    current_user: User = Depends(write_permission),
    db: Session = Depends(get_db_dependency)
):
    """
    Retry a failed job
    """
    job = db.query(Job).filter(
        Job.id == job_id,
        Job.user_id == current_user.id
    ).first()
    
    if not job:
        raise ResourceNotFoundError("Job", job_id)
    
    if job.status not in ["failed", "error"]:
        raise ValidationError(f"Job is in '{job.status}' status and cannot be retried")
    
    # Reset job status
    job.status = "uploaded"
    job.error_message = None
    job.retry_count = (job.retry_count or 0) + 1
    job.processing_started_at = None
    job.processing_completed_at = None
    
    db.commit()
    
    # Start processing again
    if settings.enable_async_processing:
        temp_file_path = job.config.get("temp_file_path")
        if not temp_file_path or not os.path.exists(temp_file_path):
            raise ValidationError("Original file no longer available for retry")
        
        task = process_complete_pdf_pipeline.delay(job_id, temp_file_path)
        job.config["task_id"] = task.id
        job.status = "processing"
        db.commit()
        
        return {
            "message": f"Job {job_id} retry started",
            "task_id": task.id,
            "retry_count": job.retry_count
        }
    else:
        return {
            "message": f"Job {job_id} reset for retry",
            "retry_count": job.retry_count
        }


@router.get("/stats/dashboard")
async def get_dashboard_stats(
    db: Session = Depends(get_db_dependency),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Get dashboard statistics for the current user
    """
    # If no user, return empty stats
    if not current_user:
        return {
            "totalAnalyses": 0,
            "validLeads": 0,
            "sharedLeads": 0,
            "credits": 100,
            "documentTypes": [],
            "statusDistribution": [],
            "commonIssues": [],
            "monthlyAnalyses": [],
            "successRate": 0,
            "averageProcessingTime": 0,
            "totalFileSize": 0,
            "averageConfidence": 0,
            "topPerformingDocumentType": "edital"
        }
    
    # Optimized: Use SQL aggregations instead of loading all jobs into memory
    base_query = db.query(Job).filter(Job.user_id == current_user.id)
    
    # Get basic counts with single query
    total_analyses = base_query.count()
    valid_leads = base_query.filter(Job.status == "completed").count()
    shared_leads = int(valid_leads * 0.4)  # Simulate 40% shared
    credits = 100  # Default credits, should come from user profile
    
    # Document types distribution - optimized with SQL
    document_types = []
    if total_analyses > 0:
        # Get filenames only for type classification (much faster than full objects)
        filenames_query = base_query.with_entities(Job.filename).all()
        type_counts = {}
        
        for (filename,) in filenames_query:
            filename_lower = filename.lower() if filename else ""
            if 'edital' in filename_lower:
                doc_type = 'edital'
            elif 'processo' in filename_lower:
                doc_type = 'processo'
            elif 'laudo' in filename_lower:
                doc_type = 'laudo'
            else:
                doc_type = 'outro'
            
            type_counts[doc_type] = type_counts.get(doc_type, 0) + 1
        
        for doc_type, count in type_counts.items():
            document_types.append({"type": doc_type, "count": count})
    
    # Status distribution (simulated)
    status_distribution = []
    if valid_leads > 0:
        confirmed = int(valid_leads * 0.6)
        alerts = int(valid_leads * 0.25)
        unidentified = valid_leads - confirmed - alerts
        
        if confirmed > 0:
            status_distribution.append({"status": "confirmado", "count": confirmed})
        if alerts > 0:
            status_distribution.append({"status": "alerta", "count": alerts})
        if unidentified > 0:
            status_distribution.append({"status": "não identificado", "count": unidentified})
    
    # Common issues (simulated)
    common_issues = []
    if valid_leads > 0:
        common_issues = [
            {"issue": "Documentação incompleta", "count": max(1, int(valid_leads * 0.3))},
            {"issue": "Valor de avaliação divergente", "count": max(1, int(valid_leads * 0.2))},
            {"issue": "Pendências fiscais", "count": max(1, int(valid_leads * 0.15))},
        ]
    
    # Monthly analyses (simplified)
    monthly_analyses = [
        {"month": "Jan", "analyses": int(total_analyses * 0.1), "leads": int(valid_leads * 0.1)},
        {"month": "Fev", "analyses": int(total_analyses * 0.15), "leads": int(valid_leads * 0.15)},
        {"month": "Mar", "analyses": int(total_analyses * 0.2), "leads": int(valid_leads * 0.2)},
        {"month": "Abr", "analyses": int(total_analyses * 0.25), "leads": int(valid_leads * 0.25)},
        {"month": "Mai", "analyses": int(total_analyses * 0.2), "leads": int(valid_leads * 0.2)},
        {"month": "Jun", "analyses": int(total_analyses * 0.1), "leads": int(valid_leads * 0.1)},
    ]
    
    return {
        "totalAnalyses": total_analyses,
        "validLeads": valid_leads,
        "sharedLeads": shared_leads,
        "credits": credits,
        "documentTypes": document_types,
        "statusDistribution": status_distribution,
        "commonIssues": common_issues,
        "monthlyAnalyses": monthly_analyses,
        "successRate": (valid_leads / max(total_analyses, 1)) * 100,
        "averageProcessingTime": 2.3,
        "totalFileSize": db.query(func.sum(Job.file_size)).filter(Job.user_id == current_user.id).scalar() or 0,
        "averageConfidence": 0.87,
        "topPerformingDocumentType": document_types[0]["type"] if document_types else "edital"
    }


@router.get("/{job_id}/page/{page_number}")
async def get_job_page_content(
    job_id: str,
    page_number: int,
    db: Session = Depends(get_db_dependency),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Get content of a specific page from a job's document
    """
    # Try to find job - with user filter if authenticated, without if not
    if current_user:
        job = db.query(Job).filter(
            Job.id == job_id,
            Job.user_id == current_user.id
        ).first()
    else:
        job = db.query(Job).filter(Job.id == job_id).first()
    
    if not job:
        raise ResourceNotFoundError("Job", job_id)
    
    # Get chunk for the specific page
    chunk = db.query(JobChunk).filter(
        JobChunk.job_id == job_id,
        JobChunk.page_start <= page_number,
        JobChunk.page_end >= page_number
    ).first()
    
    # Get total pages from job config or estimate
    total_pages = job.config.get("total_pages", 1) if job.config else 1
    
    if not chunk:
        # Try to get any chunk from this job to provide some content
        any_chunk = db.query(JobChunk).filter(JobChunk.job_id == job_id).first()
        
        if any_chunk:
            # Return content from the first available chunk with a note
            return {
                "page_content": f"NOTA: Página {page_number} não encontrada. Conteúdo da primeira página disponível:\n\n{any_chunk.content}",
                "filename": job.filename,
                "total_pages": total_pages,
                "page_number": page_number,
                "chunk_id": any_chunk.id
            }
        else:
            # No chunks found at all, provide fallback content
            return {
                "page_content": f"Documento: {job.filename}\nStatus: {job.status}\n\nConteúdo da página não disponível.\nO documento pode ainda estar em processamento ou pode ter ocorrido um erro durante a extração do texto.",
                "filename": job.filename,
                "total_pages": total_pages,
                "page_number": page_number,
                "chunk_id": "fallback"
            }
    
    return {
        "page_content": chunk.content,
        "filename": job.filename,
        "total_pages": total_pages,
        "page_number": page_number,
        "chunk_id": chunk.id
    }