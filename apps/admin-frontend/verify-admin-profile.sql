-- Verify Admin Profile Setup for grondon@gmail.com
-- Run this in Supabase SQL Editor to check what's happening

-- 1. Check if user exists in auth.users
SELECT 
    'AUTH USER CHECK' as check_type,
    id,
    email,
    created_at,
    email_confirmed_at,
    last_sign_in_at,
    email_confirmed_at IS NOT NULL as email_confirmed
FROM auth.users 
WHERE email = 'grondon@gmail.com';

-- 2. Check if admin_profiles table exists and has correct structure
SELECT 
    'ADMIN_PROFILES TABLE' as check_type,
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns 
WHERE table_name = 'admin_profiles' 
ORDER BY ordinal_position;

-- 3. Check if admin profile exists for grondon@gmail.com
SELECT 
    'ADMIN PROFILE CHECK' as check_type,
    ap.id as profile_id,
    ap.user_id,
    ap.admin_level,
    ap.role_name,
    ap.permissions,
    ap.can_manage_admins,
    ap.can_access_logs,
    ap.can_manage_users,
    ap.can_view_analytics,
    ap.can_system_config,
    ap.is_active,
    ap.created_at as profile_created,
    u.email,
    u.id as auth_user_id
FROM admin_profiles ap
FULL OUTER JOIN auth.users u ON ap.user_id = u.id
WHERE u.email = 'grondon@gmail.com' OR ap.user_id IS NULL;

-- 4. Check RLS policies on admin_profiles table
SELECT 
    'RLS POLICIES' as check_type,
    schemaname,
    tablename,
    policyname,
    permissive,
    cmd,
    qual,
    with_check
FROM pg_policies 
WHERE tablename = 'admin_profiles';

-- 5. If no admin profile found, let's see what users exist in admin_profiles
SELECT 
    'ALL ADMIN PROFILES' as check_type,
    ap.id,
    ap.admin_level,
    ap.role_name,
    ap.is_active,
    u.email
FROM admin_profiles ap
JOIN auth.users u ON ap.user_id = u.id
ORDER BY ap.created_at DESC
LIMIT 5;