-- Setup Initial Admin for Arremate360 Admin System
-- Run this after grondon@gmail.com has signed up in Supabase Auth

-- Create admin profile for grondon@gmail.com as System Admin (level 3)
SELECT create_admin_profile('grondon@gmail.com', 3, 'System Admin');

-- Verify the admin profile was created
SELECT 
    ap.id,
    ap.admin_level,
    ap.role_name,
    ap.permissions,
    ap.can_manage_admins,
    ap.can_access_logs,
    ap.can_manage_users,
    ap.can_view_analytics,
    ap.can_system_config,
    ap.is_active,
    u.email,
    u.created_at as user_created_at
FROM admin_profiles ap
JOIN auth.users u ON ap.user_id = u.id
WHERE u.email = 'grondon@gmail.com';