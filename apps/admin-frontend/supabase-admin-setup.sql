-- Arremate360 Admin Setup Script
-- Run this in Supabase SQL Editor to create admin profile for grondon@gmail.com

-- Step 1: Check if user exists in auth.users
SELECT 
    id,
    email,
    created_at,
    email_confirmed_at,
    last_sign_in_at
FROM auth.users 
WHERE email = 'grondon@gmail.com';

-- Step 2: Check if admin profile already exists
SELECT 
    ap.*,
    u.email
FROM admin_profiles ap
JOIN auth.users u ON ap.user_id = u.id
WHERE u.email = 'grondon@gmail.com';

-- Step 3: If user exists but no admin profile, create one
-- (Only run this if Step 1 shows a user exists and Step 2 shows no admin profile)
DO $$
DECLARE
    target_user_id UUID;
    profile_exists BOOLEAN;
BEGIN
    -- Get user ID
    SELECT id INTO target_user_id 
    FROM auth.users 
    WHERE email = 'grondon@gmail.com';
    
    IF target_user_id IS NULL THEN
        RAISE NOTICE 'User grondon@gmail.com not found. Please sign up first.';
        RETURN;
    END IF;
    
    -- Check if admin profile exists
    SELECT EXISTS(
        SELECT 1 FROM admin_profiles WHERE user_id = target_user_id
    ) INTO profile_exists;
    
    IF profile_exists THEN
        RAISE NOTICE 'Admin profile already exists for grondon@gmail.com';
        RETURN;
    END IF;
    
    -- Create admin profile
    INSERT INTO admin_profiles (
        user_id, 
        admin_level, 
        role_name, 
        permissions,
        can_manage_admins, 
        can_access_logs, 
        can_manage_users, 
        can_view_analytics, 
        can_system_config,
        is_active
    ) VALUES (
        target_user_id,
        3, -- System Admin level
        'System Admin',
        '["system.manage", "users.manage", "users.delete", "admins.manage", "admins.create", "admins.delete", "logs.view", "logs.export", "analytics.view", "analytics.export", "monitoring.view", "monitoring.configure", "system.configure", "database.access"]'::jsonb,
        true, -- can_manage_admins
        true, -- can_access_logs
        true, -- can_manage_users
        true, -- can_view_analytics
        true, -- can_system_config
        true  -- is_active
    );
    
    RAISE NOTICE 'Admin profile created successfully for grondon@gmail.com';
END $$;

-- Step 4: Verify the admin profile was created
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
    ap.created_at,
    u.email,
    u.id as user_id
FROM admin_profiles ap
JOIN auth.users u ON ap.user_id = u.id
WHERE u.email = 'grondon@gmail.com';