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

from database.connection import get_db_dependency
from database.models import Job, User, JobChunk
from auth.security import get_current_active_user, PermissionChecker
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
    current_user: User = Depends(read_permission),
    db: Session = Depends(get_db_dependency)
):
    """
    List user's jobs with optional filtering
    """
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