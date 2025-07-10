
import { createClient } from '@supabase/supabase-js'
import type { Database } from './types'

const supabaseUrl = "https://rjbiyndpxqaallhjmbwm.supabase.co"
const supabaseAnonKey = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJqYml5bmRweHFhYWxsaGptYndtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDU2NjEwNzUsImV4cCI6MjA2MTIzNzA3NX0.h3hviSaTY6fJLUrRbl2X6LHfQlxAhHishQ-jVur09-A"

export const supabase = createClient<Database>(supabaseUrl, supabaseAnonKey, {
  auth: {
    autoRefreshToken: true,
    persistSession: true,
    detectSessionInUrl: true
  }
})
