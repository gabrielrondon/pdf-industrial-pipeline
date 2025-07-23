-- Migration: Create Admin System
-- Date: 2025-01-23
-- Description: Complete admin control center with roles, permissions, invitations, and monitoring

-- Create admin roles table
CREATE TABLE IF NOT EXISTS admin_roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    permissions JSONB DEFAULT '[]'::jsonb,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create admin users table
CREATE TABLE IF NOT EXISTS admin_users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    role_id UUID NOT NULL REFERENCES admin_roles(id) ON DELETE RESTRICT,
    admin_level INTEGER NOT NULL DEFAULT 1,
    can_manage_admins BOOLEAN NOT NULL DEFAULT false,
    can_access_logs BOOLEAN NOT NULL DEFAULT true,
    can_manage_users BOOLEAN NOT NULL DEFAULT true,
    can_view_analytics BOOLEAN NOT NULL DEFAULT true,
    can_system_config BOOLEAN NOT NULL DEFAULT false,
    last_login_at TIMESTAMP WITH TIME ZONE,
    login_count INTEGER NOT NULL DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create admin invitations table
CREATE TABLE IF NOT EXISTS admin_invitations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL,
    token VARCHAR(255) UNIQUE NOT NULL,
    invited_by_id UUID NOT NULL REFERENCES admin_users(id) ON DELETE CASCADE,
    role_id UUID NOT NULL REFERENCES admin_roles(id) ON DELETE RESTRICT,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    accepted_at TIMESTAMP WITH TIME ZONE,
    cancelled_at TIMESTAMP WITH TIME ZONE,
    personal_message TEXT,
    permissions_preview JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create admin sessions table
CREATE TABLE IF NOT EXISTS admin_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    admin_user_id UUID NOT NULL REFERENCES admin_users(id) ON DELETE CASCADE,
    session_token VARCHAR(255) UNIQUE NOT NULL,
    ip_address VARCHAR(45),
    user_agent TEXT,
    login_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    logout_at TIMESTAMP WITH TIME ZONE,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT true,
    last_activity_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create admin audit logs table
CREATE TABLE IF NOT EXISTS admin_audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    admin_user_id UUID NOT NULL REFERENCES admin_users(id) ON DELETE CASCADE,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    resource_id VARCHAR(255),
    details JSONB DEFAULT '{}'::jsonb,
    ip_address VARCHAR(45),
    user_agent TEXT,
    success BOOLEAN NOT NULL,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create system monitoring table
CREATE TABLE IF NOT EXISTS system_monitoring (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    metric_type VARCHAR(50) NOT NULL,
    metric_name VARCHAR(100) NOT NULL,
    value DOUBLE PRECISION NOT NULL,
    unit VARCHAR(20),
    source VARCHAR(50) DEFAULT 'system',
    tags JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create user activity logs table
CREATE TABLE IF NOT EXISTS user_activity_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    activity_type VARCHAR(50) NOT NULL,
    activity_details JSONB DEFAULT '{}'::jsonb,
    ip_address VARCHAR(45),
    user_agent TEXT,
    endpoint VARCHAR(255),
    method VARCHAR(10),
    response_time_ms INTEGER,
    status_code INTEGER,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_admin_roles_name_active ON admin_roles(name, is_active);
CREATE INDEX IF NOT EXISTS idx_admin_users_user_active ON admin_users(user_id, is_active);
CREATE INDEX IF NOT EXISTS idx_admin_users_level ON admin_users(admin_level);
CREATE INDEX IF NOT EXISTS idx_admin_invitations_email_status ON admin_invitations(email, status);
CREATE INDEX IF NOT EXISTS idx_admin_invitations_token ON admin_invitations(token);
CREATE INDEX IF NOT EXISTS idx_admin_invitations_expires ON admin_invitations(expires_at);
CREATE INDEX IF NOT EXISTS idx_admin_sessions_token_active ON admin_sessions(session_token, is_active);
CREATE INDEX IF NOT EXISTS idx_admin_sessions_user_active ON admin_sessions(admin_user_id, is_active);
CREATE INDEX IF NOT EXISTS idx_admin_sessions_expires ON admin_sessions(expires_at);
CREATE INDEX IF NOT EXISTS idx_admin_audit_action_date ON admin_audit_logs(action, created_at);
CREATE INDEX IF NOT EXISTS idx_admin_audit_resource ON admin_audit_logs(resource_type, resource_id);
CREATE INDEX IF NOT EXISTS idx_admin_audit_admin_date ON admin_audit_logs(admin_user_id, created_at);
CREATE INDEX IF NOT EXISTS idx_admin_audit_success_date ON admin_audit_logs(success, created_at);
CREATE INDEX IF NOT EXISTS idx_system_monitoring_type_date ON system_monitoring(metric_type, created_at);
CREATE INDEX IF NOT EXISTS idx_system_monitoring_name_date ON system_monitoring(metric_name, created_at);
CREATE INDEX IF NOT EXISTS idx_system_monitoring_source_date ON system_monitoring(source, created_at);
CREATE INDEX IF NOT EXISTS idx_user_activity_type_date ON user_activity_logs(activity_type, created_at);
CREATE INDEX IF NOT EXISTS idx_user_activity_user_date ON user_activity_logs(user_id, created_at);
CREATE INDEX IF NOT EXISTS idx_user_activity_status_date ON user_activity_logs(status_code, created_at);

-- Insert default admin roles
INSERT INTO admin_roles (name, description, permissions) VALUES
('System Admin', 'Full system access with all permissions', '[
    "system.manage",
    "users.manage", 
    "users.delete",
    "admins.manage",
    "admins.create",
    "admins.delete",
    "logs.view",
    "logs.export", 
    "analytics.view",
    "analytics.export",
    "monitoring.view",
    "monitoring.configure",
    "system.configure",
    "database.access"
]'::jsonb),

('Super Admin', 'Advanced admin with most permissions except system config', '[
    "users.manage",
    "users.delete", 
    "admins.manage",
    "admins.create",
    "logs.view",
    "logs.export",
    "analytics.view",
    "analytics.export",
    "monitoring.view"
]'::jsonb),

('Admin', 'Standard admin with basic management permissions', '[
    "users.manage",
    "logs.view", 
    "analytics.view",
    "monitoring.view"
]'::jsonb),

('Read Only Admin', 'View-only access for monitoring and analytics', '[
    "logs.view",
    "analytics.view", 
    "monitoring.view"
]'::jsonb)
ON CONFLICT (name) DO NOTHING;

-- Create or update grondon@gmail.com as initial System Admin
-- First ensure the user exists
INSERT INTO users (id, email, username, hashed_password, full_name, is_active, is_superuser)
VALUES (
    gen_random_uuid(),
    'grondon@gmail.com', 
    'grondon',
    '$2b$12$dummy.hash.for.initial.setup.replace.with.real.password',
    'Gabriel Rondon',
    true,
    true
) ON CONFLICT (email) DO UPDATE SET
    is_superuser = true,
    is_active = true,
    full_name = COALESCE(EXCLUDED.full_name, users.full_name);

-- Create admin profile for grondon@gmail.com
INSERT INTO admin_users (
    user_id,
    role_id, 
    admin_level,
    can_manage_admins,
    can_access_logs,
    can_manage_users,
    can_view_analytics,
    can_system_config,
    is_active
)
SELECT 
    u.id,
    r.id,
    3, -- System Admin level
    true,
    true,
    true,
    true,
    true,
    true
FROM users u
CROSS JOIN admin_roles r
WHERE u.email = 'grondon@gmail.com' 
AND r.name = 'System Admin'
ON CONFLICT (user_id) DO UPDATE SET
    role_id = EXCLUDED.role_id,
    admin_level = 3,
    can_manage_admins = true,
    can_access_logs = true,
    can_manage_users = true,
    can_view_analytics = true,
    can_system_config = true,
    is_active = true;

-- Add update triggers for updated_at timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply triggers to all admin tables
DROP TRIGGER IF EXISTS update_admin_roles_updated_at ON admin_roles;
CREATE TRIGGER update_admin_roles_updated_at BEFORE UPDATE ON admin_roles FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_admin_users_updated_at ON admin_users;
CREATE TRIGGER update_admin_users_updated_at BEFORE UPDATE ON admin_users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_admin_invitations_updated_at ON admin_invitations;
CREATE TRIGGER update_admin_invitations_updated_at BEFORE UPDATE ON admin_invitations FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_admin_sessions_updated_at ON admin_sessions;
CREATE TRIGGER update_admin_sessions_updated_at BEFORE UPDATE ON admin_sessions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_admin_audit_logs_updated_at ON admin_audit_logs;
CREATE TRIGGER update_admin_audit_logs_updated_at BEFORE UPDATE ON admin_audit_logs FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_system_monitoring_updated_at ON system_monitoring;
CREATE TRIGGER update_system_monitoring_updated_at BEFORE UPDATE ON system_monitoring FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_user_activity_logs_updated_at ON user_activity_logs;
CREATE TRIGGER update_user_activity_logs_updated_at BEFORE UPDATE ON user_activity_logs FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert initial system monitoring metrics
INSERT INTO system_monitoring (metric_type, metric_name, value, unit, source, tags) VALUES
('system', 'admin_system_initialized', 1, 'boolean', 'migration', '{"version": "1.0", "migration_date": "2025-01-23"}'::jsonb),
('database', 'admin_tables_created', 7, 'count', 'migration', '{"tables": ["admin_roles", "admin_users", "admin_invitations", "admin_sessions", "admin_audit_logs", "system_monitoring", "user_activity_logs"]}'::jsonb);

-- Log the admin system setup
INSERT INTO admin_audit_logs (
    admin_user_id,
    action,
    resource_type, 
    resource_id,
    details,
    success
)
SELECT 
    au.id,
    'system_initialized',
    'system',
    'admin_control_center',
    '{"description": "Admin control center system initialized", "initial_admin": "grondon@gmail.com", "roles_created": 4, "migration_date": "2025-01-23"}'::jsonb,
    true
FROM admin_users au
JOIN users u ON au.user_id = u.id
WHERE u.email = 'grondon@gmail.com';

COMMIT;