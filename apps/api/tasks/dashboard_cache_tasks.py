"""
Background tasks for maintaining dashboard cache

These tasks run periodically to keep the dashboard statistics cache fresh
and ensure fast response times for users.
"""

import time
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any

from celery import Celery
from sqlalchemy.orm import Session

from database.connection import get_db_dependency
from services.dashboard_cache_service import DashboardCacheService
from database.models import User, DashboardCache

logger = logging.getLogger(__name__)

# Initialize Celery app (this would normally be imported from celery_app.py)
try:
    from celery_app import app as celery_app
    CELERY_AVAILABLE = True
except ImportError:
    logger.warning("⚠️ Celery not available, cache tasks will not be scheduled")
    CELERY_AVAILABLE = False
    celery_app = None


def refresh_dashboard_cache_sync():
    """
    Synchronous version of cache refresh for non-Celery environments.
    Can be called directly or from a background thread.
    """
    try:
        logger.info("🔄 Starting dashboard cache refresh (sync)")
        start_time = time.time()
        
        # Get database session
        db_dependency = get_db_dependency()
        db_session = next(db_dependency)
        
        try:
            # Refresh global statistics
            logger.info("📊 Refreshing global dashboard statistics")
            global_stats = DashboardCacheService.update_cache(db_session, user_id=None, force_refresh=True)
            logger.info(f"✅ Global stats refreshed: {global_stats.get('totalAnalyses', 0)} analyses")
            
            # Get active users who might need individual cache refresh
            active_users = db_session.query(User).filter(
                User.is_active == True,
                User.created_at > datetime.utcnow() - timedelta(days=30)  # Active in last 30 days
            ).limit(50).all()  # Limit to prevent overwhelming the system
            
            logger.info(f"👥 Found {len(active_users)} active users for cache refresh")
            
            # Refresh cache for active users
            refreshed_users = 0
            for user in active_users:
                try:
                    user_stats = DashboardCacheService.update_cache(db_session, user_id=str(user.id), force_refresh=True)
                    refreshed_users += 1
                    logger.debug(f"✅ Refreshed cache for user {user.id}")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to refresh cache for user {user.id}: {e}")
            
            # Clean up expired cache entries
            DashboardCacheService.cleanup_expired_cache(db_session)
            
            total_time = time.time() - start_time
            logger.info(f"🎉 Cache refresh completed in {total_time:.2f}s - Global + {refreshed_users} users")
            
            return {
                "success": True,
                "global_refreshed": True,
                "users_refreshed": refreshed_users,
                "total_time_seconds": total_time,
                "completed_at": datetime.utcnow().isoformat()
            }
            
        finally:
            db_session.close()
            
    except Exception as e:
        logger.error(f"❌ Error in cache refresh: {e}")
        return {
            "success": False,
            "error": str(e),
            "completed_at": datetime.utcnow().isoformat()
        }


if CELERY_AVAILABLE:
    @celery_app.task(bind=True, name="refresh_dashboard_cache")
    def refresh_dashboard_cache(self):
        """
        Celery task to refresh dashboard cache.
        Runs periodically to keep statistics fresh.
        """
        try:
            logger.info("🔄 Starting dashboard cache refresh task")
            
            # Use the synchronous function
            result = refresh_dashboard_cache_sync()
            
            if result["success"]:
                logger.info(f"✅ Cache refresh task completed: {result['users_refreshed']} users refreshed")
            else:
                logger.error(f"❌ Cache refresh task failed: {result['error']}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Cache refresh task error: {e}")
            return {
                "success": False,
                "error": str(e),
                "completed_at": datetime.utcnow().isoformat()
            }

    @celery_app.task(bind=True, name="cleanup_expired_cache")
    def cleanup_expired_cache(self):
        """
        Celery task to clean up expired cache entries.
        Runs daily to keep the cache table clean.
        """
        try:
            logger.info("🧹 Starting cache cleanup task")
            
            db_dependency = get_db_dependency()
            db_session = next(db_dependency)
            
            try:
                DashboardCacheService.cleanup_expired_cache(db_session)
                logger.info("✅ Cache cleanup completed")
                return {"success": True, "completed_at": datetime.utcnow().isoformat()}
            finally:
                db_session.close()
                
        except Exception as e:
            logger.error(f"❌ Cache cleanup error: {e}")
            return {
                "success": False,
                "error": str(e),
                "completed_at": datetime.utcnow().isoformat()
            }

    @celery_app.task(bind=True, name="warm_dashboard_cache")
    def warm_dashboard_cache(self, user_ids: List[str] = None):
        """
        Celery task to warm up cache for specific users.
        Useful for ensuring VIP users have immediate dashboard access.
        """
        try:
            logger.info(f"🔥 Warming cache for {len(user_ids) if user_ids else 'all'} users")
            
            db_dependency = get_db_dependency()
            db_session = next(db_dependency)
            
            try:
                warmed_users = 0
                
                if user_ids:
                    # Warm specific users
                    for user_id in user_ids:
                        try:
                            DashboardCacheService.update_cache(db_session, user_id=user_id, force_refresh=True)
                            warmed_users += 1
                            logger.debug(f"🔥 Warmed cache for user {user_id}")
                        except Exception as e:
                            logger.warning(f"⚠️ Failed to warm cache for user {user_id}: {e}")
                else:
                    # Warm global cache
                    DashboardCacheService.update_cache(db_session, user_id=None, force_refresh=True)
                    warmed_users = 1
                    logger.info("🔥 Warmed global cache")
                
                logger.info(f"✅ Cache warming completed: {warmed_users} caches warmed")
                return {
                    "success": True,
                    "users_warmed": warmed_users,
                    "completed_at": datetime.utcnow().isoformat()
                }
                
            finally:
                db_session.close()
                
        except Exception as e:
            logger.error(f"❌ Cache warming error: {e}")
            return {
                "success": False,
                "error": str(e),
                "completed_at": datetime.utcnow().isoformat()
            }


# Background task scheduler (for non-Celery environments)
import threading
import time as time_module

class BackgroundCacheRefresher:
    """
    Simple background thread-based cache refresher for environments without Celery.
    """
    
    def __init__(self, refresh_interval_minutes: int = 5):
        self.refresh_interval_minutes = refresh_interval_minutes
        self.is_running = False
        self.thread = None
    
    def start(self):
        """Start the background cache refresher"""
        if self.is_running:
            logger.warning("⚠️ Background cache refresher already running")
            return
        
        self.is_running = True
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
        logger.info(f"🚀 Background cache refresher started (interval: {self.refresh_interval_minutes}m)")
    
    def stop(self):
        """Stop the background cache refresher"""
        self.is_running = False
        if self.thread:
            self.thread.join()
        logger.info("🛑 Background cache refresher stopped")
    
    def _run_loop(self):
        """Main loop for background cache refreshing"""
        while self.is_running:
            try:
                logger.info("🔄 Background cache refresh triggered")
                result = refresh_dashboard_cache_sync()
                
                if result["success"]:
                    logger.info(f"✅ Background refresh completed: {result['users_refreshed']} users")
                else:
                    logger.error(f"❌ Background refresh failed: {result['error']}")
                
            except Exception as e:
                logger.error(f"❌ Background refresh loop error: {e}")
            
            # Wait for next interval
            time_module.sleep(self.refresh_interval_minutes * 60)

# Global instance for non-Celery environments
background_refresher = BackgroundCacheRefresher()


def start_background_cache_refresh():
    """
    Start cache refresh based on available task system.
    Use Celery if available, otherwise use background thread.
    """
    if CELERY_AVAILABLE:
        logger.info("🔧 Scheduling Celery-based cache refresh tasks")
        # Note: In production, these would be configured in celery beat schedule
        # For now, we'll document the recommended schedule:
        # refresh_dashboard_cache.apply_async(countdown=60)  # First refresh after 1 minute
        logger.info("📝 Recommended Celery beat schedule:")
        logger.info("   - refresh_dashboard_cache: every 5 minutes")
        logger.info("   - cleanup_expired_cache: daily at 2 AM")
    else:
        logger.info("🔧 Starting thread-based background cache refresh")
        background_refresher.start()


def stop_background_cache_refresh():
    """Stop background cache refresh"""
    if not CELERY_AVAILABLE:
        background_refresher.stop()