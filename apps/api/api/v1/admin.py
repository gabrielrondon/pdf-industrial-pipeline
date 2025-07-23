"""
Admin Control Center API Endpoints
Comprehensive admin functionality for system management
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Request, Query, Body
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_, text
from pydantic import BaseModel, EmailStr
import io
import csv
import json

from database.connection import get_db_dependency
from database.models import (
    User, Job, AdminUser, AdminRole, AdminAuditLog, AdminInvitation,
    UserActivityLog, SystemMonitoring, AdminSession
)
from auth.admin_security import (
    AdminAuth, AdminDependency, AdminPermissions, AdminTokenService,
    AdminActivityTracker, RequireAdmin, RequireUserManagement, 
    RequireAdminManagement, RequireSystemAdmin, RequireLogsAccess,
    RequireAnalytics, RequireMonitoring, RequireSystemConfig
)
from core.monitoring import BusinessMetrics
from config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()
router = APIRouter(prefix="/admin", tags=["admin"])


# Pydantic models for requests/responses
class AdminLoginRequest(BaseModel):
    email: EmailStr
    password: str


class AdminLoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    admin_info: Dict[str, Any]
    permissions: List[str]
    expires_in: int = 28800  # 8 hours


class AdminInviteRequest(BaseModel):
    email: EmailStr
    role_id: str
    personal_message: Optional[str] = None


class UserManagementRequest(BaseModel):
    action: str  # activate, deactivate, delete, reset_password
    user_ids: List[str]
    reason: Optional[str] = None


class SystemConfigRequest(BaseModel):
    config_key: str
    config_value: Any
    category: str = "general"


# Authentication endpoints
@router.post("/login", response_model=AdminLoginResponse)
async def admin_login(
    request: Request,
    login_data: AdminLoginRequest,
    db: Session = Depends(get_db_dependency)
):
    """Admin login endpoint"""
    try:
        # Authenticate admin
        admin_data = AdminAuth.authenticate_admin(
            login_data.email, 
            login_data.password, 
            db
        )
        
        if not admin_data:
            # Log failed login attempt
            AdminActivityTracker.log_user_activity(
                activity_type="admin_login_failed",
                activity_details={"email": login_data.email, "reason": "invalid_credentials"},
                request=request,
                status_code=401,
                db=db
            )
            raise HTTPException(status_code=401, detail="Invalid admin credentials")
        
        # Create admin session
        session_token = AdminAuth.create_admin_session(
            admin_data["admin_user"],
            request.client.host if request.client else "unknown",
            request.headers.get("user-agent", "unknown"),
            db
        )
        
        # Log successful login
        AdminAuth.log_admin_action(
            admin_user_id=admin_data["admin_user"].id,
            action="admin_login",
            resource_type="session",
            details={
                "login_method": "password",
                "role": admin_data["role"].name
            },
            success=True,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            db=db
        )
        
        return AdminLoginResponse(
            access_token=session_token,
            admin_info={
                "id": str(admin_data["admin_user"].id),
                "email": admin_data["user"].email,
                "full_name": admin_data["user"].full_name,
                "role": admin_data["role"].name,
                "admin_level": admin_data["admin_user"].admin_level,
                "last_login": admin_data["admin_user"].last_login_at.isoformat() if admin_data["admin_user"].last_login_at else None
            },
            permissions=admin_data["permissions"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Admin login error: {str(e)}")
        raise HTTPException(status_code=500, detail="Login failed")


@router.post("/logout")
async def admin_logout(
    request: Request,
    admin_data: Dict[str, Any] = Depends(RequireAdmin),
    db: Session = Depends(get_db_dependency)
):
    """Admin logout endpoint"""
    try:
        # Deactivate current session
        session = admin_data.get("session")
        if session:
            session.is_active = False
            session.logout_at = datetime.utcnow()
            db.commit()
        
        # Log logout
        AdminAuth.log_admin_action(
            admin_user_id=admin_data["admin_user"].id,
            action="admin_logout",
            resource_type="session",
            resource_id=str(session.id) if session else None,
            success=True,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            db=db
        )
        
        return {"message": "Logged out successfully"}
        
    except Exception as e:
        logger.error(f"Admin logout error: {str(e)}")
        raise HTTPException(status_code=500, detail="Logout failed")


# Dashboard and overview
@router.get("/dashboard")
async def get_admin_dashboard(
    admin_data: Dict[str, Any] = Depends(RequireAdmin),
    db: Session = Depends(get_db_dependency)
):
    """Get comprehensive admin dashboard data"""
    try:
        # System overview
        total_users = db.query(User).filter(User.is_active == True).count()
        total_admins = db.query(AdminUser).filter(AdminUser.is_active == True).count()
        total_jobs = db.query(Job).count()
        recent_jobs = db.query(Job).filter(
            Job.created_at >= datetime.utcnow() - timedelta(days=7)
        ).count()
        
        # System health metrics
        failed_jobs = db.query(Job).filter(Job.status == "failed").count()
        processing_jobs = db.query(Job).filter(Job.status == "processing").count()
        
        # User activity (last 24 hours)
        recent_activity = db.query(UserActivityLog).filter(
            UserActivityLog.created_at >= datetime.utcnow() - timedelta(hours=24)
        ).count()
        
        # Admin activity
        recent_admin_actions = db.query(AdminAuditLog).filter(
            AdminAuditLog.created_at >= datetime.utcnow() - timedelta(hours=24)
        ).count()
        
        # Top active users
        top_users = db.query(
            User.email,
            User.full_name,
            func.count(Job.id).label("job_count")
        ).join(Job).group_by(User.id, User.email, User.full_name).order_by(
            desc("job_count")
        ).limit(10).all()
        
        # System status
        cache_status = "connected"  # TODO: Check actual cache status
        database_status = "connected"
        
        return {
            "overview": {
                "total_users": total_users,
                "total_admins": total_admins,
                "total_jobs": total_jobs,
                "recent_jobs": recent_jobs,
                "failed_jobs": failed_jobs,
                "processing_jobs": processing_jobs
            },
            "activity": {
                "recent_user_activity": recent_activity,
                "recent_admin_actions": recent_admin_actions
            },
            "top_users": [
                {
                    "email": user.email,
                    "name": user.full_name,
                    "job_count": user.job_count
                }
                for user in top_users
            ],
            "system_status": {
                "database": database_status,
                "cache": cache_status,
                "api": "healthy"
            },
            "admin_info": {
                "current_admin": admin_data["user"].full_name,
                "role": admin_data["role"].name,
                "permissions": admin_data["permissions"]
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting admin dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to load dashboard")


# User management
@router.get("/users")
async def get_users(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    status: Optional[str] = Query(None),  # active, inactive, all
    admin_data: Dict[str, Any] = Depends(RequireUserManagement),
    db: Session = Depends(get_db_dependency)
):
    """Get paginated list of users"""
    try:
        query = db.query(User)
        
        # Apply filters
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    User.email.ilike(search_term),
                    User.full_name.ilike(search_term),
                    User.username.ilike(search_term)
                )
            )
        
        if status == "active":
            query = query.filter(User.is_active == True)
        elif status == "inactive":
            query = query.filter(User.is_active == False)
        
        # Get total count
        total = query.count()
        
        # Get paginated results
        users = query.order_by(desc(User.created_at)).offset((page - 1) * limit).limit(limit).all()
        
        # Get user job counts
        user_data = []
        for user in users:
            job_count = db.query(Job).filter(Job.user_id == user.id).count()
            recent_activity = db.query(UserActivityLog).filter(
                and_(
                    UserActivityLog.user_id == user.id,
                    UserActivityLog.created_at >= datetime.utcnow() - timedelta(days=7)
                )
            ).count()
            
            is_admin = db.query(AdminUser).filter(AdminUser.user_id == user.id).first() is not None
            
            user_data.append({
                "id": str(user.id),
                "email": user.email,
                "username": user.username,
                "full_name": user.full_name,
                "is_active": user.is_active,
                "is_superuser": user.is_superuser,
                "is_admin": is_admin,
                "created_at": user.created_at.isoformat(),
                "job_count": job_count,
                "recent_activity": recent_activity
            })
        
        return {
            "users": user_data,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "pages": (total + limit - 1) // limit
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting users: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get users")


@router.get("/users/{user_id}")
async def get_user_details(
    user_id: str,
    admin_data: Dict[str, Any] = Depends(RequireUserManagement),
    db: Session = Depends(get_db_dependency)
):
    """Get detailed user information"""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get user jobs
        jobs = db.query(Job).filter(Job.user_id == user_id).order_by(desc(Job.created_at)).limit(10).all()
        
        # Get user activity
        activities = db.query(UserActivityLog).filter(
            UserActivityLog.user_id == user_id
        ).order_by(desc(UserActivityLog.created_at)).limit(50).all()
        
        # Check if user is admin
        admin_profile = db.query(AdminUser).filter(AdminUser.user_id == user_id).first()
        
        return {
            "user": {
                "id": str(user.id),
                "email": user.email,
                "username": user.username,
                "full_name": user.full_name,
                "is_active": user.is_active,
                "is_superuser": user.is_superuser,
                "created_at": user.created_at.isoformat(),
                "updated_at": user.updated_at.isoformat()
            },
            "admin_profile": {
                "is_admin": admin_profile is not None,
                "admin_level": admin_profile.admin_level if admin_profile else None,
                "role": admin_profile.role.name if admin_profile and admin_profile.role else None
            },
            "recent_jobs": [
                {
                    "id": str(job.id),
                    "filename": job.filename,
                    "status": job.status,
                    "created_at": job.created_at.isoformat(),
                    "file_size": job.file_size
                }
                for job in jobs
            ],
            "recent_activities": [
                {
                    "activity_type": activity.activity_type,
                    "details": activity.activity_details,
                    "timestamp": activity.created_at.isoformat(),
                    "ip_address": activity.ip_address
                }
                for activity in activities
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user details: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get user details")


@router.post("/users/manage")
async def manage_users(
    request: Request,
    management_request: UserManagementRequest,
    admin_data: Dict[str, Any] = Depends(RequireUserManagement),
    db: Session = Depends(get_db_dependency)
):
    """Bulk user management operations"""
    try:
        results = []
        
        for user_id in management_request.user_ids:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                results.append({"user_id": user_id, "success": False, "error": "User not found"})
                continue
            
            try:
                if management_request.action == "activate":
                    user.is_active = True
                elif management_request.action == "deactivate":
                    user.is_active = False
                elif management_request.action == "delete":
                    # Check permissions for delete
                    if not AdminAuth.has_permission(admin_data["permissions"], AdminPermissions.USERS_DELETE):
                        raise HTTPException(status_code=403, detail="Delete permission required")
                    db.delete(user)
                else:
                    results.append({"user_id": user_id, "success": False, "error": "Invalid action"})
                    continue
                
                db.commit()
                
                # Log the action
                AdminAuth.log_admin_action(
                    admin_user_id=admin_data["admin_user"].id,
                    action=f"user_{management_request.action}",
                    resource_type="user",
                    resource_id=user_id,
                    details={
                        "reason": management_request.reason,
                        "user_email": user.email
                    },
                    success=True,
                    ip_address=request.client.host if request.client else None,
                    user_agent=request.headers.get("user-agent"),
                    db=db
                )
                
                results.append({"user_id": user_id, "success": True})
                
            except Exception as e:
                db.rollback()
                results.append({"user_id": user_id, "success": False, "error": str(e)})
        
        return {"results": results}
        
    except Exception as e:
        logger.error(f"Error managing users: {str(e)}")
        raise HTTPException(status_code=500, detail="User management failed")


# Admin management
@router.get("/admins")
async def get_admins(
    admin_data: Dict[str, Any] = Depends(RequireAdminManagement),
    db: Session = Depends(get_db_dependency)
):
    """Get list of admin users"""
    try:
        admins = db.query(AdminUser).join(User).join(AdminRole).filter(
            AdminUser.is_active == True
        ).all()
        
        admin_list = []
        for admin in admins:
            admin_list.append({
                "id": str(admin.id),
                "user": {
                    "email": admin.user.email,
                    "full_name": admin.user.full_name,
                    "is_active": admin.user.is_active
                },
                "role": {
                    "name": admin.role.name,
                    "permissions": admin.role.permissions
                },
                "admin_level": admin.admin_level,
                "last_login": admin.last_login_at.isoformat() if admin.last_login_at else None,
                "login_count": admin.login_count,
                "created_at": admin.created_at.isoformat()
            })
        
        return {"admins": admin_list}
        
    except Exception as e:
        logger.error(f"Error getting admins: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get admins")


@router.post("/admins/invite")
async def invite_admin(
    request: Request,
    invite_request: AdminInviteRequest,
    admin_data: Dict[str, Any] = Depends(RequireAdminManagement),
    db: Session = Depends(get_db_dependency)
):
    """Invite new admin user"""
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == invite_request.email).first()
        if existing_user:
            # Check if already admin
            existing_admin = db.query(AdminUser).filter(AdminUser.user_id == existing_user.id).first()
            if existing_admin:
                raise HTTPException(status_code=400, detail="User is already an admin")
        
        # Create invitation
        invitation = AdminTokenService.create_invitation(
            email=invite_request.email,
            role_id=invite_request.role_id,
            invited_by_id=admin_data["admin_user"].id,
            personal_message=invite_request.personal_message,
            db=db
        )
        
        # Log the invitation
        AdminAuth.log_admin_action(
            admin_user_id=admin_data["admin_user"].id,
            action="admin_invite_sent",
            resource_type="admin_invitation",
            resource_id=str(invitation.id),
            details={
                "invited_email": invite_request.email,
                "role_id": invite_request.role_id
            },
            success=True,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            db=db
        )
        
        # TODO: Send invitation email
        
        return {
            "message": "Admin invitation sent successfully",
            "invitation_id": str(invitation.id),
            "expires_at": invitation.expires_at.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error inviting admin: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to send invitation")


# System monitoring and logs
@router.get("/logs/audit")
async def get_audit_logs(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    action: Optional[str] = Query(None),
    admin_id: Optional[str] = Query(None),
    admin_data: Dict[str, Any] = Depends(RequireLogsAccess),
    db: Session = Depends(get_db_dependency)
):
    """Get admin audit logs"""
    try:
        query = db.query(AdminAuditLog).join(AdminUser).join(User)
        
        if action:
            query = query.filter(AdminAuditLog.action.ilike(f"%{action}%"))
        
        if admin_id:
            query = query.filter(AdminAuditLog.admin_user_id == admin_id)
        
        total = query.count()
        logs = query.order_by(desc(AdminAuditLog.created_at)).offset((page - 1) * limit).limit(limit).all()
        
        log_data = []
        for log in logs:
            log_data.append({
                "id": str(log.id),
                "admin": {
                    "email": log.admin_user.user.email,
                    "full_name": log.admin_user.user.full_name
                },
                "action": log.action,
                "resource_type": log.resource_type,
                "resource_id": log.resource_id,
                "details": log.details,
                "success": log.success,
                "error_message": log.error_message,
                "ip_address": log.ip_address,
                "timestamp": log.created_at.isoformat()
            })
        
        return {
            "logs": log_data,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "pages": (total + limit - 1) // limit
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting audit logs: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get audit logs")


@router.get("/logs/user-activity")
async def get_user_activity_logs(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    user_id: Optional[str] = Query(None),
    activity_type: Optional[str] = Query(None),
    admin_data: Dict[str, Any] = Depends(RequireLogsAccess),
    db: Session = Depends(get_db_dependency)
):
    """Get user activity logs"""
    try:
        query = db.query(UserActivityLog)
        
        if user_id:
            query = query.filter(UserActivityLog.user_id == user_id)
            
        if activity_type:
            query = query.filter(UserActivityLog.activity_type == activity_type)
        
        total = query.count()
        logs = query.order_by(desc(UserActivityLog.created_at)).offset((page - 1) * limit).limit(limit).all()
        
        log_data = []
        for log in logs:
            user_info = None
            if log.user:
                user_info = {
                    "email": log.user.email,
                    "full_name": log.user.full_name
                }
            
            log_data.append({
                "id": str(log.id),
                "user": user_info,
                "activity_type": log.activity_type,
                "activity_details": log.activity_details,
                "endpoint": log.endpoint,
                "method": log.method,
                "ip_address": log.ip_address,
                "response_time_ms": log.response_time_ms,
                "status_code": log.status_code,
                "timestamp": log.created_at.isoformat()
            })
        
        return {
            "logs": log_data,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "pages": (total + limit - 1) // limit
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting user activity logs: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get user activity logs")


# Analytics and monitoring
@router.get("/analytics/overview")
async def get_analytics_overview(
    days: int = Query(30, ge=1, le=365),
    admin_data: Dict[str, Any] = Depends(RequireAnalytics),
    db: Session = Depends(get_db_dependency)
):
    """Get comprehensive analytics overview"""
    try:
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # User growth
        user_growth = db.query(
            func.date(User.created_at).label("date"),
            func.count(User.id).label("new_users")
        ).filter(
            User.created_at >= start_date
        ).group_by(func.date(User.created_at)).order_by("date").all()
        
        # Job statistics
        job_stats = db.query(
            func.date(Job.created_at).label("date"),
            Job.status,
            func.count(Job.id).label("count")
        ).filter(
            Job.created_at >= start_date
        ).group_by(func.date(Job.created_at), Job.status).all()
        
        # Active users (users who had activity in the period)
        active_users = db.query(
            func.date(UserActivityLog.created_at).label("date"),
            func.count(func.distinct(UserActivityLog.user_id)).label("active_users")
        ).filter(
            UserActivityLog.created_at >= start_date
        ).group_by(func.date(UserActivityLog.created_at)).order_by("date").all()
        
        # System performance metrics
        avg_response_times = db.query(
            func.date(UserActivityLog.created_at).label("date"),
            func.avg(UserActivityLog.response_time_ms).label("avg_response_time")
        ).filter(
            and_(
                UserActivityLog.created_at >= start_date,
                UserActivityLog.response_time_ms.isnot(None)
            )
        ).group_by(func.date(UserActivityLog.created_at)).order_by("date").all()
        
        return {
            "period": {"days": days, "start_date": start_date.isoformat()},
            "user_growth": [
                {"date": str(row.date), "new_users": row.new_users}
                for row in user_growth
            ],
            "job_statistics": [
                {"date": str(row.date), "status": row.status, "count": row.count}
                for row in job_stats
            ],
            "active_users": [
                {"date": str(row.date), "active_users": row.active_users}
                for row in active_users
            ],
            "performance": [
                {"date": str(row.date), "avg_response_time": float(row.avg_response_time) if row.avg_response_time else 0}
                for row in avg_response_times
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting analytics overview: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get analytics")


# System monitoring
@router.get("/monitoring/system")
async def get_system_monitoring(
    hours: int = Query(24, ge=1, le=168),  # Max 1 week
    metric_type: Optional[str] = Query(None),
    admin_data: Dict[str, Any] = Depends(RequireMonitoring),
    db: Session = Depends(get_db_dependency)
):
    """Get system monitoring metrics"""
    try:
        start_time = datetime.utcnow() - timedelta(hours=hours)
        
        query = db.query(SystemMonitoring).filter(
            SystemMonitoring.created_at >= start_time
        )
        
        if metric_type:
            query = query.filter(SystemMonitoring.metric_type == metric_type)
        
        metrics = query.order_by(SystemMonitoring.created_at).all()
        
        # Group metrics by type
        grouped_metrics = {}
        for metric in metrics:
            if metric.metric_type not in grouped_metrics:
                grouped_metrics[metric.metric_type] = []
            
            grouped_metrics[metric.metric_type].append({
                "metric_name": metric.metric_name,
                "value": metric.value,
                "unit": metric.unit,
                "source": metric.source,
                "tags": metric.tags,
                "timestamp": metric.created_at.isoformat()
            })
        
        return {
            "period": {"hours": hours, "start_time": start_time.isoformat()},
            "metrics": grouped_metrics
        }
        
    except Exception as e:
        logger.error(f"Error getting system monitoring: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get monitoring data")


# Export functionality
@router.get("/export/users")
async def export_users(
    format: str = Query("csv", regex="^(csv|json)$"),
    admin_data: Dict[str, Any] = Depends(RequireUserManagement),
    db: Session = Depends(get_db_dependency)
):
    """Export users data"""
    try:
        users = db.query(User).all()
        
        if format == "csv":
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow([
                "ID", "Email", "Username", "Full Name", "Is Active", 
                "Is Superuser", "Created At", "Job Count"
            ])
            
            # Write data
            for user in users:
                job_count = db.query(Job).filter(Job.user_id == user.id).count()
                writer.writerow([
                    str(user.id), user.email, user.username, user.full_name,
                    user.is_active, user.is_superuser, user.created_at.isoformat(),
                    job_count
                ])
            
            output.seek(0)
            return StreamingResponse(
                io.BytesIO(output.getvalue().encode()),
                media_type="text/csv",
                headers={"Content-Disposition": "attachment; filename=users_export.csv"}
            )
        
        else:  # JSON format
            users_data = []
            for user in users:
                job_count = db.query(Job).filter(Job.user_id == user.id).count()
                users_data.append({
                    "id": str(user.id),
                    "email": user.email,
                    "username": user.username,
                    "full_name": user.full_name,
                    "is_active": user.is_active,
                    "is_superuser": user.is_superuser,
                    "created_at": user.created_at.isoformat(),
                    "job_count": job_count
                })
            
            json_data = json.dumps(users_data, indent=2)
            return StreamingResponse(
                io.BytesIO(json_data.encode()),
                media_type="application/json",
                headers={"Content-Disposition": "attachment; filename=users_export.json"}
            )
        
    except Exception as e:
        logger.error(f"Error exporting users: {str(e)}")
        raise HTTPException(status_code=500, detail="Export failed")


# Testing utilities
@router.post("/test/upload")
async def test_upload(
    admin_data: Dict[str, Any] = Depends(RequireAdmin),
    db: Session = Depends(get_db_dependency)
):
    """Test document upload functionality"""
    # TODO: Implement test upload functionality
    return {"message": "Test upload endpoint - to be implemented"}


@router.get("/roles")
async def get_admin_roles(
    admin_data: Dict[str, Any] = Depends(RequireAdminManagement),
    db: Session = Depends(get_db_dependency)
):
    """Get available admin roles"""
    try:
        roles = db.query(AdminRole).filter(AdminRole.is_active == True).all()
        
        return {
            "roles": [
                {
                    "id": str(role.id),
                    "name": role.name,
                    "description": role.description,
                    "permissions": role.permissions
                }
                for role in roles
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting admin roles: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get roles")