from fastapi import FastAPI, Depends, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import HTTPBearer
from contextlib import asynccontextmanager
import time
import uuid
import logging
from typing import Dict, Any
import asyncio

# Import configuration and core modules
from config.settings import get_settings
from core.logging_config import setup_logging, request_id_var, user_id_var, api_logger
from core.monitoring import MetricsCollector, health_check, MetricsEndpoint, TracingConfig
from core.exceptions import BaseAPIException
from database.connection import init_async_db, close_async_db
from auth.security import get_current_user_optional, RateLimiter

# Import routers
from api.v1.auth import router as auth_router
from api.v1.jobs import router as jobs_router
from api.v1.analysis import router as analysis_router
from api.v1.search import router as search_router
from api.v1.admin import router as admin_router

logger = logging.getLogger(__name__)
settings = get_settings()

# Security
security = HTTPBearer(auto_error=False)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting PDF Industrial Pipeline...")
    
    # Initialize database
    try:
        await init_async_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        raise
    
    # Setup tracing
    TracingConfig.setup_tracing()
    
    # Start metrics collection
    if settings.enable_metrics:
        asyncio.create_task(MetricsCollector.start_metrics_collection())
        logger.info("Metrics collection started")
    
    # Add health checks
    health_check.add_check("database", lambda: True)  # Implement actual DB check
    health_check.add_check("redis", lambda: True)     # Implement actual Redis check
    health_check.add_check("storage", lambda: True)   # Implement actual storage check
    
    logger.info("Application startup complete")
    
    yield
    
    # Shutdown
    logger.info("Shutting down PDF Industrial Pipeline...")
    
    try:
        await close_async_db()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Error closing database: {str(e)}")
    
    logger.info("Application shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="PDF Industrial Pipeline",
    description="World-class PDF analysis system for Brazilian judicial auctions",
    version=settings.app_version,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan
)

# Middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if settings.environment == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"]  # Configure with actual allowed hosts
    )


# Request ID and logging middleware
@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    """Add request ID and logging"""
    # Generate request ID
    req_id = str(uuid.uuid4())
    request_id_var.set(req_id)
    
    # Extract user ID if available
    user_id = None
    try:
        user = await get_current_user_optional(
            credentials=request.headers.get("authorization"),
            api_key=request.headers.get("x-api-key")
        )
        if user:
            user_id = str(user.id)
            user_id_var.set(user_id)
    except Exception:
        pass
    
    # Record request start
    start_time = time.time()
    
    # Add request ID to response headers
    response = await call_next(request)
    response.headers["X-Request-ID"] = req_id
    
    # Log request
    duration = time.time() - start_time
    api_logger.log_event(
        "http_request",
        f"{request.method} {request.url.path}",
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        duration=duration,
        user_id=user_id,
        request_id=req_id,
        user_agent=request.headers.get("user-agent"),
        ip_address=request.client.host if request.client else None
    )
    
    return response


# Rate limiting middleware
rate_limiter = RateLimiter(
    requests=settings.rate_limit_requests,
    period=settings.rate_limit_period
)

if settings.rate_limit_enabled:
    @app.middleware("http")
    async def rate_limiting_middleware(request: Request, call_next):
        """Apply rate limiting"""
        try:
            await rate_limiter(request)
            return await call_next(request)
        except HTTPException as e:
            return JSONResponse(
                status_code=e.status_code,
                content={"detail": e.detail}
            )


# Exception handlers
@app.exception_handler(BaseAPIException)
async def api_exception_handler(request: Request, exc: BaseAPIException):
    """Handle custom API exceptions"""
    logger.error(
        f"API Exception: {exc.detail}",
        extra={
            "error_code": exc.error_code,
            "status_code": exc.status_code,
            "extra_data": exc.extra_data,
            "path": request.url.path,
            "method": request.method
        }
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.error_code,
                "message": exc.detail,
                "details": exc.extra_data
            }
        },
        headers=exc.headers
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions"""
    logger.error(
        f"Unexpected error: {str(exc)}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "exception_type": type(exc).__name__
        },
        exc_info=True
    )
    
    if settings.debug:
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": str(exc),
                    "type": type(exc).__name__
                }
            }
        )
    else:
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An internal error occurred"
                }
            }
        )


# Health check endpoints
@app.get("/health", tags=["System"])
async def health_check_endpoint():
    """Application health check"""
    return await health_check.run_checks()


@app.get("/health/live", tags=["System"])
async def liveness_check():
    """Kubernetes liveness probe"""
    return {"status": "alive", "timestamp": time.time()}


@app.get("/health/ready", tags=["System"])
async def readiness_check():
    """Kubernetes readiness probe"""
    checks = await health_check.run_checks()
    if checks["status"] == "healthy":
        return {"status": "ready", "timestamp": time.time()}
    else:
        raise HTTPException(status_code=503, detail="Service not ready")


# Metrics endpoint
if settings.enable_metrics:
    @app.get("/metrics", tags=["System"])
    async def metrics_endpoint():
        """Prometheus metrics endpoint"""
        return Response(
            content=MetricsEndpoint.get_metrics(),
            media_type="text/plain"
        )


# API version info
@app.get("/", tags=["System"])
async def root():
    """API root endpoint"""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "docs_url": "/docs" if settings.debug else None,
        "features": {
            "judicial_analysis": settings.enable_judicial_analysis,
            "ml_predictions": settings.enable_ml_predictions,
            "semantic_search": settings.enable_semantic_search,
            "async_processing": settings.enable_async_processing
        }
    }


# Include routers
app.include_router(
    auth_router,
    prefix=f"{settings.api_prefix}/auth",
    tags=["Authentication"]
)

app.include_router(
    jobs_router,
    prefix=f"{settings.api_prefix}/jobs",
    tags=["Jobs"]
)

app.include_router(
    analysis_router,
    prefix=f"{settings.api_prefix}/analysis",
    tags=["Analysis"]
)

app.include_router(
    search_router,
    prefix=f"{settings.api_prefix}/search",
    tags=["Search"]
)

app.include_router(
    admin_router,
    prefix=f"{settings.api_prefix}/admin",
    tags=["Administration"]
)


if __name__ == "__main__":
    uvicorn.run(
        "main_v2:app",
        host=settings.api_host,
        port=settings.api_port,
        workers=1 if settings.debug else settings.api_workers,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
        access_log=True
    )