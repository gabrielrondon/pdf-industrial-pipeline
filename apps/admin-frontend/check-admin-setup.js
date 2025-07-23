/**
 * Admin Setup Checker for Arremate360
 * 
 * This script checks if grondon@gmail.com exists in Supabase Auth
 * and creates the admin profile if needed.
 * 
 * Run with: node check-admin-setup.js
 */

import { createClient } from '@supabase/supabase-js'

const supabaseUrl = 'https://rjbiyndpxqaallhjmbwm.supabase.co'
const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY

if (!supabaseServiceKey) {
  console.error('❌ SUPABASE_SERVICE_ROLE_KEY environment variable is required')
  console.log('Set it with: export SUPABASE_SERVICE_ROLE_KEY="your-service-role-key"')
  process.exit(1)
}

// Create Supabase client with service role key for admin operations
const supabase = createClient(supabaseUrl, supabaseServiceKey, {
  auth: {
    autoRefreshToken: false,
    persistSession: false
  }
})

async function checkAndSetupAdmin() {
  try {
    console.log('🔍 Checking if grondon@gmail.com exists in Supabase Auth...')
    
    // Check if user exists in auth.users
    const { data: authUsers, error: authError } = await supabase.auth.admin.listUsers()
    
    if (authError) {
      console.error('❌ Error fetching users:', authError.message)
      return
    }
    
    const grontronUser = authUsers.users?.find(user => user.email === 'grondon@gmail.com')
    
    if (!grontronUser) {
      console.log('❌ User grondon@gmail.com not found in Supabase Auth')
      console.log('📝 Next steps:')
      console.log('1. Go to your client app and sign up with grondon@gmail.com')
      console.log('2. Or use Supabase dashboard to create the user')
      console.log('3. Then run this script again')
      return
    }
    
    console.log('✅ User grondon@gmail.com found in Supabase Auth')
    console.log(`   User ID: ${grontronUser.id}`)
    console.log(`   Created: ${grontronUser.created_at}`)
    
    // Check if admin profile already exists
    console.log('🔍 Checking if admin profile exists...')
    
    const { data: adminProfile, error: profileError } = await supabase
      .from('admin_profiles')
      .select('*')
      .eq('user_id', grontronUser.id)
      .single()
    
    if (profileError && profileError.code !== 'PGRST116') {
      console.error('❌ Error checking admin profile:', profileError.message)
      return
    }
    
    if (adminProfile) {
      console.log('✅ Admin profile already exists!')
      console.log(`   Admin Level: ${adminProfile.admin_level}`)
      console.log(`   Role: ${adminProfile.role_name}`)
      console.log(`   Active: ${adminProfile.is_active}`)
      console.log(`   Can Manage Admins: ${adminProfile.can_manage_admins}`)
      return
    }
    
    // Create admin profile using the function
    console.log('🛠️  Creating admin profile for grondon@gmail.com...')
    
    const { data: result, error: createError } = await supabase.rpc('create_admin_profile', {
      user_email: 'grondon@gmail.com',
      admin_level: 3,
      role_name: 'System Admin'
    })
    
    if (createError) {
      console.error('❌ Error creating admin profile:', createError.message)
      return
    }
    
    console.log('✅ Admin profile created successfully!')
    console.log(`   Profile ID: ${result}`)
    
    // Verify the creation
    const { data: newProfile, error: verifyError } = await supabase
      .from('admin_profiles')
      .select('*')
      .eq('user_id', grontronUser.id)
      .single()
    
    if (verifyError) {
      console.error('❌ Error verifying admin profile:', verifyError.message)
      return
    }
    
    console.log('🎉 Admin setup complete!')
    console.log('📊 Admin Profile Details:')
    console.log(`   Admin Level: ${newProfile.admin_level} (System Admin)`)
    console.log(`   Role: ${newProfile.role_name}`)
    console.log(`   Can Manage Admins: ${newProfile.can_manage_admins}`)
    console.log(`   Can Access Logs: ${newProfile.can_access_logs}`)
    console.log(`   Can Manage Users: ${newProfile.can_manage_users}`)
    console.log(`   Can View Analytics: ${newProfile.can_view_analytics}`)
    console.log(`   Can System Config: ${newProfile.can_system_config}`)
    console.log(`   Permissions: ${JSON.stringify(newProfile.permissions, null, 2)}`)
    
  } catch (error) {
    console.error('❌ Unexpected error:', error.message)
  }
}

// Run the check
checkAndSetupAdmin()