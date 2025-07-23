#!/usr/bin/env python3
"""
Setup Admin Control Center System
Initializes the admin system with database tables and creates initial admin user
"""

import os
import sys
import asyncio
import logging
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import bcrypt

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_database_url():
    """Get database URL from environment"""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        logger.error("DATABASE_URL environment variable not set")
        sys.exit(1)
    
    # Fix Railway's postgres:// URL to postgresql://
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    
    return database_url

def run_migration_sql(engine):
    """Run the admin system migration SQL"""
    migration_file = os.path.join(os.path.dirname(__file__), "database", "migrations", "create_admin_system.sql")
    
    if not os.path.exists(migration_file):
        logger.error(f"Migration file not found: {migration_file}")
        return False
    
    try:
        with open(migration_file, 'r') as f:
            migration_sql = f.read()
        
        # Split by individual statements and execute
        statements = migration_sql.split(';')
        
        with engine.begin() as conn:
            for statement in statements:
                statement = statement.strip()
                if statement and not statement.startswith('--'):
                    try:
                        conn.execute(text(statement))
                        logger.info(f"✅ Executed SQL statement")
                    except Exception as e:
                        if "already exists" in str(e).lower():
                            logger.info(f"⚠️ Table/constraint already exists (skipping): {str(e)[:100]}")
                        else:
                            logger.error(f"❌ Error executing statement: {str(e)}")
                            raise
        
        logger.info("🎉 Admin system migration completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {str(e)}")
        return False

def setup_initial_admin(engine, email="grondon@gmail.com", password="admin123"):
    """Set up the initial admin user"""
    try:
        # Hash the password
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        with engine.begin() as conn:
            # Check if user already exists
            result = conn.execute(
                text("SELECT id FROM users WHERE email = :email"),
                {"email": email}
            )
            user = result.first()
            
            if user:
                logger.info(f"👤 User {email} already exists")
                user_id = user[0]
            else:
                # Create user
                result = conn.execute(
                    text("""
                        INSERT INTO users (id, email, username, hashed_password, full_name, is_active, is_superuser)
                        VALUES (gen_random_uuid(), :email, :username, :password, :full_name, true, true)
                        RETURNING id
                    """),
                    {
                        "email": email,
                        "username": email.split('@')[0],
                        "password": password_hash,
                        "full_name": "Gabriel Rondon"
                    }
                )
                user_id = result.first()[0]
                logger.info(f"✅ Created user {email}")
            
            # Check if admin profile exists
            result = conn.execute(
                text("SELECT id FROM admin_users WHERE user_id = :user_id"),
                {"user_id": user_id}
            )
            admin = result.first()
            
            if admin:
                logger.info(f"👑 Admin profile for {email} already exists")
            else:
                # Get System Admin role
                result = conn.execute(
                    text("SELECT id FROM admin_roles WHERE name = 'System Admin'")
                )
                role = result.first()
                
                if not role:
                    logger.error("❌ System Admin role not found!")
                    return False
                
                role_id = role[0]
                
                # Create admin profile
                conn.execute(
                    text("""
                        INSERT INTO admin_users (
                            id, user_id, role_id, admin_level, can_manage_admins,
                            can_access_logs, can_manage_users, can_view_analytics,
                            can_system_config, is_active
                        ) VALUES (
                            gen_random_uuid(), :user_id, :role_id, 3, true,
                            true, true, true, true, true
                        )
                    """),
                    {
                        "user_id": user_id,
                        "role_id": role_id
                    }
                )
                logger.info(f"✅ Created admin profile for {email}")
        
        logger.info(f"🎉 Initial admin setup completed!")
        logger.info(f"🔑 Admin login credentials:")
        logger.info(f"   Email: {email}")
        logger.info(f"   Password: {password}")
        logger.info(f"⚠️  IMPORTANT: Change the default password after first login!")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to setup initial admin: {str(e)}")
        return False

def verify_admin_system(engine):
    """Verify the admin system is properly set up"""
    try:
        with engine.begin() as conn:
            # Check tables exist
            tables_to_check = [
                'admin_roles', 'admin_users', 'admin_invitations',
                'admin_sessions', 'admin_audit_logs', 'system_monitoring',
                'user_activity_logs'
            ]
            
            for table in tables_to_check:
                result = conn.execute(
                    text("SELECT COUNT(*) FROM information_schema.tables WHERE table_name = :table_name"),
                    {"table_name": table}
                )
                count = result.first()[0]
                if count == 0:
                    logger.error(f"❌ Table {table} not found!")
                    return False
                logger.info(f"✅ Table {table} exists")
            
            # Check roles exist
            result = conn.execute(text("SELECT COUNT(*) FROM admin_roles"))
            role_count = result.first()[0]
            logger.info(f"✅ Admin roles created: {role_count}")
            
            # Check admin user exists
            result = conn.execute(
                text("""
                    SELECT u.email, ar.name as role_name, au.admin_level
                    FROM admin_users au
                    JOIN users u ON au.user_id = u.id
                    JOIN admin_roles ar ON au.role_id = ar.id
                    WHERE u.email = 'grondon@gmail.com'
                """)
            )
            admin = result.first()
            
            if admin:
                logger.info(f"✅ Initial admin found: {admin[0]} (Role: {admin[1]}, Level: {admin[2]})")
            else:
                logger.error("❌ Initial admin not found!")
                return False
            
            logger.info("🎉 Admin system verification completed successfully!")
            return True
            
    except Exception as e:
        logger.error(f"❌ Verification failed: {str(e)}")
        return False

def main():
    """Main setup function"""
    logger.info("🚀 Starting Admin Control Center setup...")
    
    # Get database URL
    database_url = get_database_url()
    logger.info(f"📊 Connecting to database...")
    
    # Create engine
    engine = create_engine(database_url, echo=False)
    
    try:
        # Test connection
        with engine.begin() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("✅ Database connection successful")
        
        # Run migration
        logger.info("📋 Running admin system migration...")
        if not run_migration_sql(engine):
            logger.error("❌ Migration failed!")
            sys.exit(1)
        
        # Setup initial admin
        logger.info("👑 Setting up initial admin user...")
        if not setup_initial_admin(engine):
            logger.error("❌ Initial admin setup failed!")
            sys.exit(1)
        
        # Verify setup
        logger.info("🔍 Verifying admin system setup...")
        if not verify_admin_system(engine):
            logger.error("❌ System verification failed!")
            sys.exit(1)
        
        logger.info("🎉 Admin Control Center setup completed successfully!")
        logger.info("")
        logger.info("🔗 Next steps:")
        logger.info("   1. Start the API server")
        logger.info("   2. Access admin endpoints at /api/v1/admin/")
        logger.info("   3. Login with grondon@gmail.com / admin123")
        logger.info("   4. Change the default password")
        logger.info("   5. Transform the admin frontend")
        logger.info("")
        
    except Exception as e:
        logger.error(f"❌ Setup failed: {str(e)}")
        sys.exit(1)
    
    finally:
        engine.dispose()

if __name__ == "__main__":
    main()