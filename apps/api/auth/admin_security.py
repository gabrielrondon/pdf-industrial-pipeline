"""
Admin Authentication and Authorization System
Comprehensive security module for admin control center
"""

import logging
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from fastapi import HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from database.connection import get_db_dependency
from database.models import (
    User, AdminUser, AdminRole, AdminSession, AdminAuditLog, 
    AdminInvitation, UserActivityLog
)
from auth.security import verify_password, create_access_token
from config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()
security = HTTPBearer()


class AdminPermissions:
    """Admin permission constants"""
    SYSTEM_MANAGE = "system.manage"
    USERS_MANAGE = "users.manage"
    USERS_DELETE = "users.delete"
    ADMINS_MANAGE = "admins.manage"
    ADMINS_CREATE = "admins.create"
    ADMINS_DELETE = "admins.delete"
    LOGS_VIEW = "logs.view"
    LOGS_EXPORT = "logs.export"
    ANALYTICS_VIEW = "analytics.view"
    ANALYTICS_EXPORT = "analytics.export"
    MONITORING_VIEW = "monitoring.view"
    MONITORING_CONFIGURE = "monitoring.configure"
    SYSTEM_CONFIGURE = "system.configure"
    DATABASE_ACCESS = "database.access"


class AdminAuth:
    """Admin authentication and authorization handler"""
    
    @staticmethod
    def authenticate_admin(email: str, password: str, db: Session) -> Optional[Dict[str, Any]]:
        """Authenticate admin user and return admin details"""
        try:
            # Find user
            user = db.query(User).filter(
                and_(User.email == email, User.is_active == True)
            ).first()
            
            if not user or not verify_password(password, user.hashed_password):
                return None
            
            # Check if user is admin
            admin_user = db.query(AdminUser).filter(
                and_(
                    AdminUser.user_id == user.id,
                    AdminUser.is_active == True
                )
            ).first()
            
            if not admin_user:
                return None
            
            # Get admin role and permissions
            role = db.query(AdminRole).filter(AdminRole.id == admin_user.role_id).first()
            if not role or not role.is_active:
                return None
            
            # Update login tracking
            admin_user.last_login_at = datetime.utcnow()
            admin_user.login_count += 1
            db.commit()
            
            return {
                "user": user,
                "admin_user": admin_user,
                "role": role,
                "permissions": role.permissions
            }
            
        except Exception as e:
            logger.error(f"Admin authentication error: {str(e)}")
            return None
    
    @staticmethod
    def create_admin_session(admin_user: AdminUser, ip_address: str, user_agent: str, db: Session) -> str:
        """Create secure admin session"""
        try:
            # Generate secure session token
            session_token = secrets.token_urlsafe(32)
            
            # Create session record
            session = AdminSession(
                admin_user_id=admin_user.id,
                session_token=session_token,
                ip_address=ip_address,
                user_agent=user_agent,
                expires_at=datetime.utcnow() + timedelta(hours=8)  # 8 hour sessions
            )
            
            db.add(session)
            db.commit()
            
            return session_token
            
        except Exception as e:
            logger.error(f"Error creating admin session: {str(e)}")
            raise HTTPException(status_code=500, detail="Session creation failed")
    
    @staticmethod
    def validate_admin_session(session_token: str, db: Session) -> Optional[Dict[str, Any]]:
        """Validate admin session and return admin details"""
        try:
            session = db.query(AdminSession).filter(
                and_(
                    AdminSession.session_token == session_token,
                    AdminSession.is_active == True,
                    AdminSession.expires_at > datetime.utcnow()
                )
            ).first()
            
            if not session:
                return None
            
            # Update last activity
            session.last_activity_at = datetime.utcnow()
            
            # Get admin user and role
            admin_user = db.query(AdminUser).filter(
                and_(
                    AdminUser.id == session.admin_user_id,
                    AdminUser.is_active == True
                )
            ).first()
            
            if not admin_user:
                return None
            
            user = db.query(User).filter(User.id == admin_user.user_id).first()
            role = db.query(AdminRole).filter(AdminRole.id == admin_user.role_id).first()
            
            db.commit()
            
            return {
                "user": user,
                "admin_user": admin_user,
                "role": role,
                "session": session,
                "permissions": role.permissions if role else []
            }
            
        except Exception as e:
            logger.error(f"Error validating admin session: {str(e)}")
            return None
    
    @staticmethod
    def has_permission(permissions: List[str], required_permission: str) -> bool:
        """Check if admin has required permission"""
        return required_permission in permissions
    
    @staticmethod
    def has_any_permission(permissions: List[str], required_permissions: List[str]) -> bool:
        """Check if admin has any of the required permissions"""
        return any(perm in permissions for perm in required_permissions)
    
    @staticmethod
    def log_admin_action(
        admin_user_id: str,
        action: str,
        resource_type: str,
        resource_id: str = None,
        details: Dict[str, Any] = None,
        success: bool = True,
        error_message: str = None,
        ip_address: str = None,
        user_agent: str = None,
        db: Session = None
    ):
        """Log admin action for audit trail"""
        try:
            if not db:
                return
                
            audit_log = AdminAuditLog(
                admin_user_id=admin_user_id,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                details=details or {},
                success=success,
                error_message=error_message,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            db.add(audit_log)
            db.commit()
            
            logger.info(f"Admin action logged: {action} on {resource_type} by {admin_user_id}")
            
        except Exception as e:
            logger.error(f"Error logging admin action: {str(e)}")


class AdminDependency:
    """Admin dependency injection classes"""
    
    def __init__(self, required_permissions: List[str] = None, require_any: bool = False):
        self.required_permissions = required_permissions or []
        self.require_any = require_any
    
    def __call__(
        self,
        request: Request,
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db: Session = Depends(get_db_dependency)
    ) -> Dict[str, Any]:
        """Verify admin authentication and permissions"""
        
        if not credentials:
            raise HTTPException(status_code=401, detail="Admin authentication required")
        
        # Validate session
        admin_data = AdminAuth.validate_admin_session(credentials.credentials, db)
        if not admin_data:
            raise HTTPException(status_code=401, detail="Invalid or expired admin session")
        
        # Check permissions if required
        if self.required_permissions:
            user_permissions = admin_data.get("permissions", [])
            
            if self.require_any:
                has_permission = AdminAuth.has_any_permission(user_permissions, self.required_permissions)
            else:
                has_permission = all(
                    AdminAuth.has_permission(user_permissions, perm) 
                    for perm in self.required_permissions
                )
            
            if not has_permission:
                # Log unauthorized access attempt
                AdminAuth.log_admin_action(
                    admin_user_id=admin_data["admin_user"].id,
                    action="unauthorized_access_attempt",
                    resource_type="permission",
                    details={
                        "required_permissions": self.required_permissions,
                        "user_permissions": user_permissions,
                        "endpoint": str(request.url)
                    },
                    success=False,
                    error_message="Insufficient permissions",
                    ip_address=request.client.host if request.client else None,
                    user_agent=request.headers.get("user-agent"),
                    db=db
                )
                
                raise HTTPException(
                    status_code=403, 
                    detail=f"Admin permission required: {', '.join(self.required_permissions)}"
                )
        
        # Log successful admin access
        AdminAuth.log_admin_action(
            admin_user_id=admin_data["admin_user"].id,
            action="admin_access",
            resource_type="endpoint",
            resource_id=str(request.url.path),
            details={
                "method": request.method,
                "permissions_checked": self.required_permissions
            },
            success=True,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            db=db
        )
        
        return admin_data


# Dependency instances for common permission levels
RequireAdmin = AdminDependency()
RequireUserManagement = AdminDependency([AdminPermissions.USERS_MANAGE])
RequireUserDelete = AdminDependency([AdminPermissions.USERS_DELETE])
RequireAdminManagement = AdminDependency([AdminPermissions.ADMINS_MANAGE])
RequireSystemAdmin = AdminDependency([AdminPermissions.SYSTEM_MANAGE])
RequireLogsAccess = AdminDependency([AdminPermissions.LOGS_VIEW])
RequireAnalytics = AdminDependency([AdminPermissions.ANALYTICS_VIEW])
RequireMonitoring = AdminDependency([AdminPermissions.MONITORING_VIEW])
RequireSystemConfig = AdminDependency([AdminPermissions.SYSTEM_CONFIGURE])


class AdminTokenService:
    """Service for managing admin invitation tokens"""
    
    @staticmethod
    def generate_invitation_token() -> str:
        """Generate secure invitation token"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def create_invitation(
        email: str,
        role_id: str,
        invited_by_id: str,
        personal_message: str = None,
        expires_hours: int = 72,
        db: Session = None
    ) -> AdminInvitation:
        """Create admin invitation"""
        try:
            # Check if invitation already exists and is active
            existing = db.query(AdminInvitation).filter(
                and_(
                    AdminInvitation.email == email,
                    AdminInvitation.status == "pending",
                    AdminInvitation.expires_at > datetime.utcnow()
                )
            ).first()
            
            if existing:
                raise HTTPException(
                    status_code=400, 
                    detail="Active invitation already exists for this email"
                )
            
            # Get role for permissions preview
            role = db.query(AdminRole).filter(AdminRole.id == role_id).first()
            if not role:
                raise HTTPException(status_code=404, detail="Admin role not found")
            
            invitation = AdminInvitation(
                email=email,
                token=AdminTokenService.generate_invitation_token(),
                invited_by_id=invited_by_id,
                role_id=role_id,
                expires_at=datetime.utcnow() + timedelta(hours=expires_hours),
                personal_message=personal_message,
                permissions_preview={
                    "role_name": role.name,
                    "permissions": role.permissions
                }
            )
            
            db.add(invitation)
            db.commit()
            db.refresh(invitation)
            
            return invitation
            
        except Exception as e:
            logger.error(f"Error creating admin invitation: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to create invitation")
    
    @staticmethod
    def validate_invitation_token(token: str, db: Session) -> Optional[AdminInvitation]:
        """Validate invitation token"""
        invitation = db.query(AdminInvitation).filter(
            AdminInvitation.token == token
        ).first()
        
        if not invitation:
            return None
        
        return invitation if invitation.is_valid() else None


class AdminActivityTracker:
    """Track user activities for admin monitoring"""
    
    @staticmethod
    def log_user_activity(
        user_id: str = None,
        activity_type: str = "unknown",
        activity_details: Dict[str, Any] = None,
        request: Request = None,
        response_time_ms: int = None,
        status_code: int = 200,
        db: Session = None
    ):
        """Log user activity for admin monitoring"""
        try:
            if not db:
                return
            
            activity_log = UserActivityLog(
                user_id=user_id,
                activity_type=activity_type,
                activity_details=activity_details or {},
                ip_address=request.client.host if request and request.client else None,
                user_agent=request.headers.get("user-agent") if request else None,
                endpoint=str(request.url.path) if request else None,
                method=request.method if request else None,
                response_time_ms=response_time_ms,
                status_code=status_code
            )
            
            db.add(activity_log)
            db.commit()
            
        except Exception as e:
            logger.error(f"Error logging user activity: {str(e)}")


# Utility functions for admin operations
def get_admin_by_email(email: str, db: Session) -> Optional[Dict[str, Any]]:
    """Get admin user by email"""
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    
    admin_user = db.query(AdminUser).filter(AdminUser.user_id == user.id).first()
    if not admin_user:
        return None
    
    role = db.query(AdminRole).filter(AdminRole.id == admin_user.role_id).first()
    
    return {
        "user": user,
        "admin_user": admin_user,
        "role": role
    }


def is_super_admin(admin_data: Dict[str, Any]) -> bool:
    """Check if admin is super admin (level 2+)"""
    return admin_data.get("admin_user", {}).admin_level >= 2


def can_manage_admin(current_admin: Dict[str, Any], target_admin: Dict[str, Any]) -> bool:
    """Check if current admin can manage target admin"""
    current_level = current_admin.get("admin_user", {}).admin_level
    target_level = target_admin.get("admin_user", {}).admin_level
    
    # Can only manage admins of lower level
    return current_level > target_level and current_admin.get("admin_user", {}).can_manage_admins