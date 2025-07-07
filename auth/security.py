from datetime import datetime, timedelta
from typing import Optional, Dict, List
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader
from sqlalchemy.orm import Session
import secrets
import logging

from config.settings import get_settings
from database.models import User, APIKey
from database.connection import get_db_dependency

logger = logging.getLogger(__name__)
settings = get_settings()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Security schemes
bearer_scheme = HTTPBearer()
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


class AuthService:
    """Authentication and authorization service"""
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """Generate password hash"""
        return pwd_context.hash(password)
    
    @staticmethod
    def create_access_token(data: Dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
        
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
        return encoded_jwt
    
    @staticmethod
    def create_refresh_token(data: Dict) -> str:
        """Create JWT refresh token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
        return encoded_jwt
    
    @staticmethod
    def decode_token(token: str) -> Dict:
        """Decode and validate JWT token"""
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
            return payload
        except JWTError:
            return None
    
    @staticmethod
    def generate_api_key() -> str:
        """Generate a secure API key"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
        """Authenticate user with username and password"""
        user = db.query(User).filter(
            (User.username == username) | (User.email == username)
        ).first()
        
        if not user or not AuthService.verify_password(password, user.hashed_password):
            return None
        
        if not user.is_active:
            return None
            
        return user
    
    @staticmethod
    def get_user_by_api_key(db: Session, api_key: str) -> Optional[User]:
        """Get user by API key"""
        key = db.query(APIKey).filter(
            APIKey.key == api_key,
            APIKey.is_active == True
        ).first()
        
        if not key:
            return None
            
        # Check expiration
        if key.expires_at and key.expires_at < datetime.utcnow():
            return None
            
        return key.user if key.user.is_active else None


# Dependency functions
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
    db: Session = Depends(get_db_dependency)
) -> User:
    """Get current user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = AuthService.decode_token(credentials.credentials)
        if payload is None or payload.get("type") != "access":
            raise credentials_exception
            
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None or not user.is_active:
        raise credentials_exception
        
    return user


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(bearer_scheme),
    api_key: Optional[str] = Security(api_key_header),
    db: Session = Depends(get_db_dependency)
) -> Optional[User]:
    """Get current user from JWT token or API key (optional)"""
    # Try JWT first
    if credentials:
        try:
            return await get_current_user(credentials, db)
        except HTTPException:
            pass
    
    # Try API key
    if api_key:
        user = AuthService.get_user_by_api_key(db, api_key)
        if user:
            return user
    
    return None


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Ensure user is active"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


async def get_current_superuser(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Ensure user is superuser"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user


class PermissionChecker:
    """Check specific permissions"""
    
    def __init__(self, required_scopes: List[str]):
        self.required_scopes = required_scopes
    
    async def __call__(
        self,
        api_key: Optional[str] = Security(api_key_header),
        current_user: Optional[User] = Depends(get_current_user_optional),
        db: Session = Depends(get_db_dependency)
    ) -> User:
        if current_user:
            # JWT users have all permissions
            return current_user
        
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
        
        # Check API key scopes
        key = db.query(APIKey).filter(
            APIKey.key == api_key,
            APIKey.is_active == True
        ).first()
        
        if not key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key"
            )
        
        # Check scopes
        if self.required_scopes:
            for scope in self.required_scopes:
                if scope not in key.scopes:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Missing required scope: {scope}"
                    )
        
        return key.user


# Rate limiting decorator
class RateLimiter:
    """Rate limiting implementation"""
    
    def __init__(self, requests: int = 100, period: int = 60):
        self.requests = requests
        self.period = period
        self.cache = {}  # In production, use Redis
    
    async def __call__(self, current_user: User = Depends(get_current_user_optional)):
        if not settings.rate_limit_enabled:
            return
            
        user_id = str(current_user.id) if current_user else "anonymous"
        now = datetime.utcnow()
        
        # Clean old entries
        self.cache = {
            k: v for k, v in self.cache.items()
            if (now - v['first']).total_seconds() < self.period
        }
        
        if user_id in self.cache:
            user_data = self.cache[user_id]
            if user_data['count'] >= self.requests:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded"
                )
            user_data['count'] += 1
        else:
            self.cache[user_id] = {
                'first': now,
                'count': 1
            }


# Utility functions
def create_user(
    db: Session,
    email: str,
    username: str,
    password: str,
    full_name: Optional[str] = None,
    is_superuser: bool = False
) -> User:
    """Create a new user"""
    user = User(
        email=email,
        username=username,
        hashed_password=AuthService.get_password_hash(password),
        full_name=full_name,
        is_superuser=is_superuser
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_api_key_for_user(
    db: Session,
    user: User,
    name: str,
    scopes: List[str] = None,
    expires_in_days: Optional[int] = None
) -> APIKey:
    """Create API key for user"""
    expires_at = None
    if expires_in_days:
        expires_at = datetime.utcnow() + timedelta(days=expires_in_days)
    
    api_key = APIKey(
        key=AuthService.generate_api_key(),
        name=name,
        user_id=user.id,
        scopes=scopes or [],
        expires_at=expires_at
    )
    db.add(api_key)
    db.commit()
    db.refresh(api_key)
    return api_key