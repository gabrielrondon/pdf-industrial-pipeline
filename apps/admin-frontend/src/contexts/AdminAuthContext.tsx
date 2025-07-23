import React, { createContext, useContext, useReducer, useEffect } from 'react'
import { createClient } from '@supabase/supabase-js'

// Supabase client
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || 'your-supabase-url'
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY || 'your-supabase-anon-key'
const supabase = createClient(supabaseUrl, supabaseAnonKey)

// Types
interface AdminUser {
  id: string
  email: string
  full_name: string
  role: string
  admin_level: number
  last_login: string | null
}

interface AdminAuthState {
  user: AdminUser | null
  token: string | null
  permissions: string[]
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null
}

interface AdminAuthContextType extends AdminAuthState {
  login: (email: string, password: string) => Promise<boolean>
  logout: () => void
  checkAuth: () => void
  hasPermission: (permission: string) => boolean
  hasAnyPermission: (permissions: string[]) => boolean
}

// Actions
type AdminAuthAction =
  | { type: 'LOGIN_START' }
  | { type: 'LOGIN_SUCCESS'; payload: { user: AdminUser; token: string; permissions: string[] } }
  | { type: 'LOGIN_FAILURE'; payload: string }
  | { type: 'LOGOUT' }
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'CHECK_AUTH_SUCCESS'; payload: { user: AdminUser; permissions: string[] } }
  | { type: 'CHECK_AUTH_FAILURE' }

// Initial state
const initialState: AdminAuthState = {
  user: null,
  token: localStorage.getItem('admin_token'),
  permissions: [],
  isAuthenticated: false,
  isLoading: true,
  error: null
}

// Reducer
function adminAuthReducer(state: AdminAuthState, action: AdminAuthAction): AdminAuthState {
  switch (action.type) {
    case 'LOGIN_START':
      return {
        ...state,
        isLoading: true,
        error: null
      }
    
    case 'LOGIN_SUCCESS':
      return {
        ...state,
        user: action.payload.user,
        token: action.payload.token,
        permissions: action.payload.permissions,
        isAuthenticated: true,
        isLoading: false,
        error: null
      }
    
    case 'LOGIN_FAILURE':
      return {
        ...state,
        user: null,
        token: null,
        permissions: [],
        isAuthenticated: false,
        isLoading: false,
        error: action.payload
      }
    
    case 'LOGOUT':
      return {
        ...state,
        user: null,
        token: null,
        permissions: [],
        isAuthenticated: false,
        isLoading: false,
        error: null
      }
    
    case 'SET_LOADING':
      return {
        ...state,
        isLoading: action.payload
      }
    
    case 'CHECK_AUTH_SUCCESS':
      return {
        ...state,
        user: action.payload.user,
        permissions: action.payload.permissions,
        isAuthenticated: true,
        isLoading: false
      }
    
    case 'CHECK_AUTH_FAILURE':
      return {
        ...state,
        user: null,
        token: null,
        permissions: [],
        isAuthenticated: false,
        isLoading: false
      }
    
    default:
      return state
  }
}

// Context
const AdminAuthContext = createContext<AdminAuthContextType | undefined>(undefined)

// Provider
export function AdminAuthProvider({ children }: { children: React.ReactNode }) {
  const [state, dispatch] = useReducer(adminAuthReducer, initialState)

  // Login function with Supabase
  const login = async (email: string, password: string): Promise<boolean> => {
    dispatch({ type: 'LOGIN_START' })
    
    try {
      // Authenticate with Supabase
      const { data: authData, error: authError } = await supabase.auth.signInWithPassword({
        email,
        password
      })

      if (authError) {
        throw new Error(authError.message)
      }

      if (!authData.user) {
        throw new Error('Login failed - no user data')
      }

      // Debug logging to see user data
      console.log('Auth successful, checking admin profile for:', {
        userId: authData.user.id,
        email: authData.user.email,
        userMetadata: authData.user.user_metadata
      })

      // Check if user is admin
      const { data: adminProfile, error: adminError } = await supabase
        .from('admin_profiles')
        .select(`
          id,
          admin_level,
          role_name,
          permissions,
          can_manage_admins,
          can_access_logs,
          can_manage_users,
          can_view_analytics,
          can_system_config,
          is_active,
          last_login_at,
          login_count
        `)
        .eq('user_id', authData.user.id)
        .eq('is_active', true)
        .single()

      if (adminError || !adminProfile) {
        // Debug logging to understand the issue
        console.error('Admin authentication failed:', {
          userId: authData.user.id,
          email: authData.user.email,
          adminError: adminError,
          adminProfile: adminProfile,
          errorCode: adminError?.code,
          errorMessage: adminError?.message
        })
        
        // Sign out the user if they're not an admin
        await supabase.auth.signOut()
        
        // More specific error messages
        if (adminError) {
          throw new Error(`Erro na verificação de admin: ${adminError.message}`)
        } else {
          throw new Error('Acesso negado - usuário não é administrador')
        }
      }

      // Update login tracking
      await supabase
        .from('admin_profiles')
        .update({
          last_login_at: new Date().toISOString(),
          login_count: (adminProfile.login_count || 0) + 1
        })
        .eq('id', adminProfile.id)

      // Create admin session record for security tracking
      const sessionToken = authData.session?.access_token || ''
      
      if (sessionToken) {
        await supabase
          .from('admin_sessions')
          .insert({
            admin_id: adminProfile.id,
            session_token: sessionToken,
            expires_at: new Date(Date.now() + 8 * 60 * 60 * 1000).toISOString(), // 8 hours
            ip_address: null, // Will be filled by middleware if available
            user_agent: navigator.userAgent
          })
      }

      // Create user object
      const adminUser: AdminUser = {
        id: adminProfile.id,
        email: authData.user.email || '',
        full_name: authData.user.user_metadata?.full_name || authData.user.email || '',
        role: adminProfile.role_name,
        admin_level: adminProfile.admin_level,
        last_login: adminProfile.last_login_at
      }

      dispatch({
        type: 'LOGIN_SUCCESS',
        payload: {
          user: adminUser,
          token: sessionToken,
          permissions: Array.isArray(adminProfile.permissions) ? adminProfile.permissions : []
        }
      })
      
      return true
      
    } catch (error) {
      dispatch({
        type: 'LOGIN_FAILURE',
        payload: error instanceof Error ? error.message : 'Login failed'
      })
      return false
    }
  }

  // Logout function with Supabase
  const logout = async () => {
    try {
      // Mark session as inactive
      if (state.token && state.user) {
        await supabase
          .from('admin_sessions')
          .update({
            is_active: false,
            logout_at: new Date().toISOString()
          })
          .eq('session_token', state.token)
      }

      // Sign out from Supabase
      await supabase.auth.signOut()
      
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      localStorage.removeItem('admin_token')
      dispatch({ type: 'LOGOUT' })
    }
  }

  // Check authentication status with Supabase
  const checkAuth = async () => {
    try {
      // Get current session from Supabase
      const { data: { session } } = await supabase.auth.getSession()
      
      if (!session?.user) {
        dispatch({ type: 'CHECK_AUTH_FAILURE' })
        return
      }

      // Check if user is still an active admin
      const { data: adminProfile, error: adminError } = await supabase
        .from('admin_profiles')
        .select(`
          id,
          admin_level,
          role_name,
          permissions,
          is_active,
          last_login_at
        `)
        .eq('user_id', session.user.id)
        .eq('is_active', true)
        .single()

      if (adminError || !adminProfile) {
        await supabase.auth.signOut()
        dispatch({ type: 'CHECK_AUTH_FAILURE' })
        return
      }

      const adminUser: AdminUser = {
        id: adminProfile.id,
        email: session.user.email || '',
        full_name: session.user.user_metadata?.full_name || session.user.email || '',
        role: adminProfile.role_name,
        admin_level: adminProfile.admin_level,
        last_login: adminProfile.last_login_at
      }

      dispatch({
        type: 'CHECK_AUTH_SUCCESS',
        payload: {
          user: adminUser,
          permissions: Array.isArray(adminProfile.permissions) ? adminProfile.permissions : []
        }
      })

      // Store session token for future use
      if (session.access_token) {
        localStorage.setItem('admin_token', session.access_token)
      }
      
    } catch (error) {
      localStorage.removeItem('admin_token')
      dispatch({ type: 'CHECK_AUTH_FAILURE' })
    }
  }

  // Permission checking functions
  const hasPermission = (permission: string): boolean => {
    return state.permissions.includes(permission)
  }

  const hasAnyPermission = (permissions: string[]): boolean => {
    return permissions.some(permission => state.permissions.includes(permission))
  }

  // Check auth on mount
  useEffect(() => {
    checkAuth()
  }, [])

  const contextValue: AdminAuthContextType = {
    ...state,
    login,
    logout,
    checkAuth,
    hasPermission,
    hasAnyPermission
  }

  return (
    <AdminAuthContext.Provider value={contextValue}>
      {children}
    </AdminAuthContext.Provider>
  )
}

// Hook
export function useAdminAuth() {
  const context = useContext(AdminAuthContext)
  if (context === undefined) {
    throw new Error('useAdminAuth must be used within an AdminAuthProvider')
  }
  return context
}

// Permission constants
export const AdminPermissions = {
  SYSTEM_MANAGE: 'system.manage',
  USERS_MANAGE: 'users.manage',
  USERS_DELETE: 'users.delete',
  ADMINS_MANAGE: 'admins.manage',
  ADMINS_CREATE: 'admins.create',
  ADMINS_DELETE: 'admins.delete',
  LOGS_VIEW: 'logs.view',
  LOGS_EXPORT: 'logs.export',
  ANALYTICS_VIEW: 'analytics.view',
  ANALYTICS_EXPORT: 'analytics.export',
  MONITORING_VIEW: 'monitoring.view',
  MONITORING_CONFIGURE: 'monitoring.configure',
  SYSTEM_CONFIGURE: 'system.configure',
  DATABASE_ACCESS: 'database.access'
} as const