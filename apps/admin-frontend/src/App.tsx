import React from 'react'
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Toaster } from 'sonner'
import './App.css'

// Contexts
import { AdminAuthProvider, useAdminAuth } from './contexts/AdminAuthContext'

// Components
import AdminLogin from './components/AdminLogin'
import AdminDashboard from './components/AdminDashboard'
import UserManagement from './components/UserManagement'
import DocumentTester from './components/DocumentTester'
import MLModelManager from './components/MLModelManager'
import DatabaseManager from './components/DatabaseManager'
import SystemHealth from './components/SystemHealth'
import APITester from './components/APITester'

// Icons
import { 
  LayoutDashboard, Users, FileText, Database, 
  Activity, Settings, LogOut, Shield, User
} from 'lucide-react'
import { Button } from './components/ui/button'
import { Badge } from './components/ui/badge'

const queryClient = new QueryClient()

function AdminLayout() {
  const { user, logout, isAuthenticated } = useAdminAuth()

  if (!isAuthenticated) {
    return <AdminLogin />
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <nav className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center space-x-8">
              <div className="flex items-center space-x-2">
                <Shield className="h-8 w-8 text-blue-600" />
                <h1 className="text-xl font-bold text-gray-900">
                  Arremate360 Admin
                </h1>
              </div>
              
              {/* Navigation Links */}
              <div className="hidden md:flex items-center space-x-8">
                <Link 
                  to="/" 
                  className="flex items-center space-x-2 text-gray-700 hover:text-gray-900 px-3 py-2 text-sm font-medium"
                >
                  <LayoutDashboard className="h-4 w-4" />
                  <span>Dashboard</span>
                </Link>
                <Link 
                  to="/users" 
                  className="flex items-center space-x-2 text-gray-700 hover:text-gray-900 px-3 py-2 text-sm font-medium"
                >
                  <Users className="h-4 w-4" />
                  <span>Usuários</span>
                </Link>
                <Link 
                  to="/documents" 
                  className="flex items-center space-x-2 text-gray-700 hover:text-gray-900 px-3 py-2 text-sm font-medium"
                >
                  <FileText className="h-4 w-4" />
                  <span>Documentos</span>
                </Link>
                <Link 
                  to="/system" 
                  className="flex items-center space-x-2 text-gray-700 hover:text-gray-900 px-3 py-2 text-sm font-medium"
                >
                  <Activity className="h-4 w-4" />
                  <span>Sistema</span>
                </Link>
                <Link 
                  to="/database" 
                  className="flex items-center space-x-2 text-gray-700 hover:text-gray-900 px-3 py-2 text-sm font-medium"
                >
                  <Database className="h-4 w-4" />
                  <span>Database</span>
                </Link>
                <Link 
                  to="/api" 
                  className="flex items-center space-x-2 text-gray-700 hover:text-gray-900 px-3 py-2 text-sm font-medium"
                >
                  <Settings className="h-4 w-4" />
                  <span>API</span>
                </Link>
              </div>
            </div>

            {/* User Info & Logout */}
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-3">
                <div className="flex items-center space-x-2">
                  <User className="h-4 w-4 text-gray-500" />
                  <div className="text-sm">
                    <div className="font-medium text-gray-900">
                      {user?.full_name}
                    </div>
                    <div className="text-gray-500 text-xs">
                      {user?.role}
                    </div>
                  </div>
                </div>
                <Badge variant="secondary" className="text-xs">
                  Nível {user?.admin_level}
                </Badge>
              </div>
              
              <Button
                variant="ghost"
                size="sm"
                onClick={logout}
                className="text-gray-700 hover:text-gray-900"
              >
                <LogOut className="h-4 w-4 mr-2" />
                Sair
              </Button>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <Routes>
          <Route path="/" element={<AdminDashboard />} />
          <Route path="/users" element={<UserManagement />} />
          <Route path="/documents" element={<DocumentTester />} />
          <Route path="/ml-models" element={<MLModelManager />} />
          <Route path="/database" element={<DatabaseManager />} />
          <Route path="/system" element={<SystemHealth />} />
          <Route path="/api" element={<APITester />} />
        </Routes>
      </main>
    </div>
  )
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AdminAuthProvider>
        <Router>
          <AdminLayout />
          <Toaster />
        </Router>
      </AdminAuthProvider>
    </QueryClientProvider>
  )
}

export default App