import React, { createContext, useContext, useReducer, useEffect } from 'react'

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

  // API Base URL
  const API_BASE_URL = import.meta.env.VITE_RAILWAY_API_URL || 'http://localhost:8000'

  // Login function
  const login = async (email: string, password: string): Promise<boolean> => {
    dispatch({ type: 'LOGIN_START' })
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/admin/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email, password })
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Login failed')
      }

      const data = await response.json()
      
      // Store token in localStorage
      localStorage.setItem('admin_token', data.access_token)
      
      dispatch({
        type: 'LOGIN_SUCCESS',
        payload: {
          user: data.admin_info,
          token: data.access_token,
          permissions: data.permissions
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

  // Logout function
  const logout = async () => {
    try {
      if (state.token) {
        await fetch(`${API_BASE_URL}/api/v1/admin/logout`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${state.token}`
          }
        })
      }
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      localStorage.removeItem('admin_token')
      dispatch({ type: 'LOGOUT' })
    }
  }

  // Check authentication status
  const checkAuth = async () => {
    const token = localStorage.getItem('admin_token')
    
    if (!token) {
      dispatch({ type: 'CHECK_AUTH_FAILURE' })
      return
    }

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/admin/dashboard`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (!response.ok) {
        throw new Error('Authentication check failed')
      }

      const data = await response.json()
      
      dispatch({
        type: 'CHECK_AUTH_SUCCESS',
        payload: {
          user: data.admin_info,
          permissions: data.admin_info.permissions || []
        }
      })
      
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