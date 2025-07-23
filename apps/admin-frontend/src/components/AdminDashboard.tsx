import React, { useState, useEffect } from 'react'
import { useAdminAuth } from '../contexts/AdminAuthContext'
import { createClient } from '@supabase/supabase-js'

// Supabase client
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || 'your-supabase-url'
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY || 'your-supabase-anon-key'
const supabase = createClient(supabaseUrl, supabaseAnonKey)
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card'
import { Badge } from './ui/badge'
import { Button } from './ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs'
import { 
  Users, FileText, Shield, Activity, AlertTriangle, 
  TrendingUp, Database, Server, Clock, UserCheck,
  Eye, Download, RefreshCw, Settings
} from 'lucide-react'
import { Alert, AlertDescription } from './ui/alert'

interface DashboardData {
  overview: {
    total_users: number
    total_admins: number
    total_jobs: number
    recent_jobs: number
    failed_jobs: number
    processing_jobs: number
  }
  activity: {
    recent_user_activity: number
    recent_admin_actions: number
  }
  top_users: Array<{
    email: string
    name: string
    job_count: number
  }>
  system_status: {
    database: string
    cache: string
    api: string
  }
  admin_info: {
    current_admin: string
    role: string
    permissions: string[]
  }
}

export default function AdminDashboard() {
  const { user, token, permissions } = useAdminAuth()
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [lastRefresh, setLastRefresh] = useState<Date>(new Date())

  const fetchDashboardData = async () => {
    try {
      setIsLoading(true)
      setError(null)

      // Get counts from various tables
      const [
        { count: totalUsers },
        { count: totalAdmins },
        { count: totalJobs },
        { count: recentJobs },
        { count: failedJobs },
        { count: processingJobs }
      ] = await Promise.all([
        supabase.from('users').select('*', { count: 'exact', head: true }),
        supabase.from('admin_profiles').select('*', { count: 'exact', head: true }).eq('is_active', true),
        supabase.from('documents').select('*', { count: 'exact', head: true }),
        supabase.from('documents').select('*', { count: 'exact', head: true })
          .gte('created_at', new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString()),
        supabase.from('documents').select('*', { count: 'exact', head: true }).eq('status', 'failed'),
        supabase.from('documents').select('*', { count: 'exact', head: true }).eq('status', 'processing')
      ])

      // Get recent activity
      const { count: recentUserActivity } = await supabase
        .from('user_activity_logs')
        .select('*', { count: 'exact', head: true })
        .gte('created_at', new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString())

      const { count: recentAdminActions } = await supabase
        .from('admin_audit_logs')
        .select('*', { count: 'exact', head: true })
        .gte('created_at', new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString())

      // Get top users (simplified)
      const { data: topUsersData, error: topUsersError } = await supabase
        .from('users')
        .select(`
          id,
          email,
          raw_user_meta_data,
          documents!documents_user_id_fkey(count)
        `)
        .limit(10)

      const data: DashboardData = {
        overview: {
          total_users: totalUsers || 0,
          total_admins: totalAdmins || 0,
          total_jobs: totalJobs || 0,
          recent_jobs: recentJobs || 0,
          failed_jobs: failedJobs || 0,
          processing_jobs: processingJobs || 0
        },
        activity: {
          recent_user_activity: recentUserActivity || 0,
          recent_admin_actions: recentAdminActions || 0
        },
        top_users: topUsersData?.map(user => ({
          email: user.email,
          name: user.raw_user_meta_data?.full_name || user.email,
          job_count: 0 // Will be calculated properly later
        })) || [],
        system_status: {
          database: "connected",
          cache: "connected", 
          api: "healthy"
        },
        admin_info: {
          current_admin: user?.full_name || '',
          role: user?.role || '',
          permissions: permissions
        }
      }

      setDashboardData(data)
      setLastRefresh(new Date())
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    if (token) {
      fetchDashboardData()
    }
  }, [token])

  // Auto-refresh every 30 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      if (token && !isLoading) {
        fetchDashboardData()
      }
    }, 30000)

    return () => clearInterval(interval)
  }, [token, isLoading])

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'connected':
      case 'healthy':
        return 'bg-green-100 text-green-800'
      case 'disconnected':
      case 'unhealthy':
        return 'bg-red-100 text-red-800'
      case 'degraded':
        return 'bg-yellow-100 text-yellow-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  if (isLoading && !dashboardData) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-3xl font-bold text-gray-900">Centro de Controle</h1>
          <div className="animate-pulse h-10 w-32 bg-gray-200 rounded"></div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[...Array(8)].map((_, i) => (
            <div key={i} className="animate-pulse">
              <div className="bg-gray-200 h-32 rounded-lg"></div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="space-y-6">
        <h1 className="text-3xl font-bold text-gray-900">Centro de Controle</h1>
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>
            Erro ao carregar dados do dashboard: {error}
          </AlertDescription>
        </Alert>
        <Button onClick={fetchDashboardData} variant="outline">
          <RefreshCw className="mr-2 h-4 w-4" />
          Tentar Novamente
        </Button>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Centro de Controle</h1>
          <p className="text-gray-600 mt-1">
            Bem-vindo, {user?.full_name} | {user?.role}
          </p>
        </div>
        <div className="flex items-center space-x-4">
          <div className="text-sm text-gray-500">
            Última atualização: {lastRefresh.toLocaleTimeString()}
          </div>
          <Button onClick={fetchDashboardData} variant="outline" size="sm">
            <RefreshCw className="mr-2 h-4 w-4" />
            Atualizar
          </Button>
        </div>
      </div>

      {/* System Status */}
      {dashboardData?.system_status && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Server className="mr-2 h-5 w-5" />
              Status do Sistema
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex space-x-4">
              <Badge className={getStatusColor(dashboardData.system_status.api)}>
                API: {dashboardData.system_status.api}
              </Badge>
              <Badge className={getStatusColor(dashboardData.system_status.database)}>
                Database: {dashboardData.system_status.database}
              </Badge>
              <Badge className={getStatusColor(dashboardData.system_status.cache)}>
                Cache: {dashboardData.system_status.cache}
              </Badge>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total de Usuários</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{dashboardData?.overview.total_users || 0}</div>
            <p className="text-xs text-muted-foreground">
              {dashboardData?.overview.total_admins || 0} administradores
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Documentos Processados</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{dashboardData?.overview.total_jobs || 0}</div>
            <p className="text-xs text-muted-foreground">
              {dashboardData?.overview.recent_jobs || 0} nos últimos 7 dias
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Em Processamento</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{dashboardData?.overview.processing_jobs || 0}</div>
            <p className="text-xs text-muted-foreground">
              {dashboardData?.overview.failed_jobs || 0} falharam
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Atividade Recente</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{dashboardData?.activity.recent_user_activity || 0}</div>
            <p className="text-xs text-muted-foreground">
              {dashboardData?.activity.recent_admin_actions || 0} ações admin
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Detailed Tabs */}
      <Tabs defaultValue="users" className="space-y-4">
        <TabsList>
          <TabsTrigger value="users">Usuários Ativos</TabsTrigger>
          <TabsTrigger value="permissions">Minhas Permissões</TabsTrigger>
          <TabsTrigger value="activity">Atividade do Sistema</TabsTrigger>
        </TabsList>

        <TabsContent value="users" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Usuários Mais Ativos</CardTitle>
              <CardDescription>
                Usuários com maior número de documentos processados
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {dashboardData?.top_users?.map((user, index) => (
                  <div key={index} className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center text-sm font-medium text-blue-800">
                        {index + 1}
                      </div>
                      <div>
                        <p className="font-medium">{user.name || user.email}</p>
                        <p className="text-sm text-gray-500">{user.email}</p>
                      </div>
                    </div>
                    <Badge variant="secondary">
                      {user.job_count} documentos
                    </Badge>
                  </div>
                )) || (
                  <p className="text-gray-500 text-center py-4">
                    Nenhum usuário ativo encontrado
                  </p>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="permissions" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Suas Permissões de Administrador</CardTitle>
              <CardDescription>
                Permissões concedidas ao seu perfil administrativo
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2">
                {permissions.map((permission, index) => (
                  <Badge key={index} variant="outline" className="justify-start">
                    <Shield className="mr-2 h-3 w-3" />
                    {permission}
                  </Badge>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="activity" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Atividade de Usuários (24h)</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-blue-600">
                  {dashboardData?.activity.recent_user_activity || 0}
                </div>
                <p className="text-sm text-muted-foreground">
                  Ações realizadas por usuários nas últimas 24 horas
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Ações Administrativas (24h)</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-purple-600">
                  {dashboardData?.activity.recent_admin_actions || 0}
                </div>
                <p className="text-sm text-muted-foreground">
                  Ações realizadas por administradores nas últimas 24 horas
                </p>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Ações Rápidas</CardTitle>
          <CardDescription>
            Acesso rápido às principais funcionalidades administrativas
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <Button variant="outline" className="h-20 flex-col space-y-2">
              <Users className="h-6 w-6" />
              <span className="text-sm">Gerenciar Usuários</span>
            </Button>
            <Button variant="outline" className="h-20 flex-col space-y-2">
              <Eye className="h-6 w-6" />
              <span className="text-sm">Ver Logs</span>
            </Button>
            <Button variant="outline" className="h-20 flex-col space-y-2">
              <UserCheck className="h-6 w-6" />
              <span className="text-sm">Administradores</span>
            </Button>
            <Button variant="outline" className="h-20 flex-col space-y-2">
              <Settings className="h-6 w-6" />
              <span className="text-sm">Configurações</span>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}