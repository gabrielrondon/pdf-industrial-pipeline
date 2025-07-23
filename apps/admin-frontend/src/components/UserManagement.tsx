import React, { useState, useEffect } from 'react'
import { useAdminAuth, AdminPermissions } from '../contexts/AdminAuthContext'
import { createClient } from '@supabase/supabase-js'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card'
import { Button } from './ui/button'
import { Input } from './ui/input'
import { Badge } from './ui/badge'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from './ui/dialog'
import { Alert, AlertDescription } from './ui/alert'
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs'
import { 
  Search, Filter, MoreHorizontal, Eye, Edit, Trash2, 
  UserCheck, UserX, RefreshCw, Download, Plus,
  Calendar, Activity, FileText, Shield
} from 'lucide-react'
import { Checkbox } from './ui/checkbox'

// Supabase client
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || 'https://rjbiyndpxqaallhjmbwm.supabase.co'
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY || 'your-supabase-anon-key'
const supabase = createClient(supabaseUrl, supabaseAnonKey)

interface User {
  id: string
  email: string
  username: string
  full_name: string
  is_active: boolean
  is_superuser: boolean
  is_admin: boolean
  created_at: string
  job_count: number
  recent_activity: number
}

interface UserDetails {
  user: {
    id: string
    email: string
    username: string
    full_name: string
    is_active: boolean
    is_superuser: boolean
    created_at: string
    updated_at: string
  }
  admin_profile: {
    is_admin: boolean
    admin_level: number | null
    role: string | null
  }
  recent_jobs: Array<{
    id: string
    filename: string
    status: string
    created_at: string
    file_size: number
  }>
  recent_activities: Array<{
    activity_type: string
    details: any
    timestamp: string
    ip_address: string
  }>
}

export default function UserManagement() {
  const { token, hasPermission } = useAdminAuth()
  const [users, setUsers] = useState<User[]>([])
  const [filteredUsers, setFilteredUsers] = useState<User[]>([])
  const [selectedUsers, setSelectedUsers] = useState<Set<string>>(new Set())
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [currentPage, setCurrentPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedUserDetails, setSelectedUserDetails] = useState<UserDetails | null>(null)
  const [isDetailsLoading, setIsDetailsLoading] = useState(false)

  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://pdf-industrial-pipeline-production.up.railway.app'
  const usersPerPage = 20

  const fetchUsers = async (page = 1, search = '', status = 'all') => {
    try {
      setIsLoading(true)
      setError(null)

      // First try to get users from Supabase profiles (which we know exist)
      const { data: profilesData, error: profilesError } = await supabase
        .from('profiles')
        .select(`
          id,
          email,
          full_name,
          credits,
          plan,
          created_at,
          last_active_at
        `)
        .order('created_at', { ascending: false })
        .range((page - 1) * usersPerPage, page * usersPerPage - 1)

      if (profilesError) {
        console.error('Supabase profiles error:', profilesError)
        throw new Error('Failed to fetch user profiles')
      }

      // Transform Supabase profiles data to match User interface
      const transformedUsers: User[] = profilesData?.map(profile => ({
        id: profile.id,
        email: profile.email || '',
        username: profile.email?.split('@')[0] || '',
        full_name: profile.full_name || profile.email || '',
        is_active: true,
        is_superuser: false,
        is_admin: false,
        created_at: profile.created_at,
        job_count: 0, // We'll try to get this from Railway API
        recent_activity: profile.last_active_at ? 
          Math.floor((new Date().getTime() - new Date(profile.last_active_at).getTime()) / (1000 * 60 * 60 * 24)) : 
          0
      })) || []

      // Try to enrich with Railway API data (job counts)
      try {
        const response = await fetch(`${API_BASE_URL}/api/v1/jobs/stats`, {
          headers: {
            'Content-Type': 'application/json'
          }
        })

        if (response.ok) {
          const railwayStats = await response.json()
          // If we get Railway data, we could enrich user job counts here
          console.log('Railway stats available:', railwayStats)
        }
      } catch (railwayError) {
        console.log('Railway API not available for enrichment:', railwayError)
      }

      // Apply client-side filtering
      let filtered = transformedUsers
      if (search) {
        filtered = filtered.filter(user => 
          user.email.toLowerCase().includes(search.toLowerCase()) ||
          user.full_name.toLowerCase().includes(search.toLowerCase())
        )
      }
      if (status !== 'all') {
        filtered = filtered.filter(user => 
          status === 'active' ? user.is_active : !user.is_active
        )
      }

      setUsers(transformedUsers)
      setFilteredUsers(filtered)
      
      // Get total count for pagination
      const { count } = await supabase
        .from('profiles')
        .select('*', { count: 'exact', head: true })
      
      setTotalPages(Math.ceil((count || 0) / usersPerPage))
      
    } catch (err) {
      console.error('Error fetching users:', err)
      setError(err instanceof Error ? err.message : 'Unknown error')
    } finally {
      setIsLoading(false)
    }
  }

  const fetchUserDetails = async (userId: string) => {
    try {
      setIsDetailsLoading(true)
      const response = await fetch(`${API_BASE_URL}/api/v1/admin/users/${userId}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (!response.ok) {
        throw new Error('Failed to fetch user details')
      }

      const data = await response.json()
      setSelectedUserDetails(data)
      
    } catch (err) {
      console.error('Error fetching user details:', err)
    } finally {
      setIsDetailsLoading(false)
    }
  }

  const handleBulkAction = async (action: string, reason?: string) => {
    if (selectedUsers.size === 0) return

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/admin/users/manage`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          action,
          user_ids: Array.from(selectedUsers),
          reason
        })
      })

      if (!response.ok) {
        throw new Error('Bulk action failed')
      }

      // Refresh users list
      await fetchUsers(currentPage, searchTerm, statusFilter)
      setSelectedUsers(new Set())
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Bulk action failed')
    }
  }

  const exportUsers = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/admin/export/users?format=csv`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (!response.ok) {
        throw new Error('Export failed')
      }

      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `users_export_${new Date().toISOString().split('T')[0]}.csv`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Export failed')
    }
  }

  useEffect(() => {
    if (token) {
      fetchUsers(currentPage, searchTerm, statusFilter)
    }
  }, [token, currentPage, searchTerm, statusFilter])

  const handleSelectAll = (checked: boolean) => {
    if (checked) {
      setSelectedUsers(new Set(users.map(user => user.id)))
    } else {
      setSelectedUsers(new Set())
    }
  }

  const handleSelectUser = (userId: string, checked: boolean) => {
    const newSelected = new Set(selectedUsers)
    if (checked) {
      newSelected.add(userId)
    } else {
      newSelected.delete(userId)
    }
    setSelectedUsers(newSelected)
  }

  const canManageUsers = hasPermission(AdminPermissions.USERS_MANAGE)
  const canDeleteUsers = hasPermission(AdminPermissions.USERS_DELETE)

  if (!canManageUsers) {
    return (
      <div className="flex items-center justify-center min-h-64">
        <Alert>
          <Shield className="h-4 w-4" />
          <AlertDescription>
            Você não tem permissão para gerenciar usuários.
          </AlertDescription>
        </Alert>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Gerenciamento de Usuários</h1>
          <p className="text-gray-600 mt-1">
            Visualize e gerencie todos os usuários da plataforma
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Button onClick={exportUsers} variant="outline">
            <Download className="mr-2 h-4 w-4" />
            Exportar
          </Button>
          <Button onClick={() => fetchUsers(currentPage, searchTerm, statusFilter)}>
            <RefreshCw className="mr-2 h-4 w-4" />
            Atualizar
          </Button>
        </div>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                <Input
                  placeholder="Buscar usuários por email, nome ou username..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-48">
                <SelectValue placeholder="Filtrar por status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Todos os usuários</SelectItem>
                <SelectItem value="active">Usuários ativos</SelectItem>
                <SelectItem value="inactive">Usuários inativos</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Bulk Actions */}
      {selectedUsers.size > 0 && (
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div className="text-sm text-gray-600">
                {selectedUsers.size} usuário(s) selecionado(s)
              </div>
              <div className="flex space-x-2">
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => handleBulkAction('activate')}
                >
                  <UserCheck className="mr-2 h-4 w-4" />
                  Ativar
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => handleBulkAction('deactivate')}
                >
                  <UserX className="mr-2 h-4 w-4" />
                  Desativar
                </Button>
                {canDeleteUsers && (
                  <Button
                    size="sm"
                    variant="destructive"
                    onClick={() => handleBulkAction('delete')}
                  >
                    <Trash2 className="mr-2 h-4 w-4" />
                    Excluir
                  </Button>
                )}
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Error Alert */}
      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Users Table */}
      <Card>
        <CardHeader>
          <CardTitle>Lista de Usuários</CardTitle>
          <CardDescription>
            Total: {users.length} usuários
          </CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-4">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="animate-pulse flex items-center space-x-4">
                  <div className="w-4 h-4 bg-gray-200 rounded"></div>
                  <div className="flex-1 space-y-2">
                    <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                    <div className="h-3 bg-gray-200 rounded w-1/2"></div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="space-y-4">
              {/* Table Header */}
              <div className="flex items-center space-x-4 py-2 border-b font-medium text-sm text-gray-700">
                <Checkbox
                  checked={selectedUsers.size === users.length && users.length > 0}
                  onCheckedChange={handleSelectAll}
                />
                <div className="flex-1">Usuário</div>
                <div className="w-24">Status</div>
                <div className="w-20">Docs</div>
                <div className="w-20">Atividade</div>
                <div className="w-32">Criado em</div>
                <div className="w-20">Ações</div>
              </div>

              {/* Table Rows */}
              {users.map((user) => (
                <div key={user.id} className="flex items-center space-x-4 py-3 border-b hover:bg-gray-50">
                  <Checkbox
                    checked={selectedUsers.has(user.id)}
                    onCheckedChange={(checked) => handleSelectUser(user.id, checked as boolean)}
                  />
                  <div className="flex-1">
                    <div className="font-medium">{user.full_name || user.username}</div>
                    <div className="text-sm text-gray-500">{user.email}</div>
                    <div className="flex items-center space-x-2 mt-1">
                      {user.is_admin && (
                        <Badge variant="secondary" className="text-xs">Admin</Badge>
                      )}
                      {user.is_superuser && (
                        <Badge variant="default" className="text-xs">Super</Badge>
                      )}
                    </div>
                  </div>
                  <div className="w-24">
                    <Badge variant={user.is_active ? "default" : "secondary"}>
                      {user.is_active ? 'Ativo' : 'Inativo'}
                    </Badge>
                  </div>
                  <div className="w-20 text-center font-medium">
                    {user.job_count}
                  </div>
                  <div className="w-20 text-center">
                    <Badge variant="outline" className="text-xs">
                      {user.recent_activity}
                    </Badge>
                  </div>
                  <div className="w-32 text-sm text-gray-500">
                    {new Date(user.created_at).toLocaleDateString()}
                  </div>
                  <div className="w-20">
                    <Dialog>
                      <DialogTrigger asChild>
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => fetchUserDetails(user.id)}
                        >
                          <Eye className="h-4 w-4" />
                        </Button>
                      </DialogTrigger>
                      <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
                        <DialogHeader>
                          <DialogTitle>Detalhes do Usuário</DialogTitle>
                          <DialogDescription>
                            Informações detalhadas e atividade do usuário
                          </DialogDescription>
                        </DialogHeader>
                        
                        {isDetailsLoading ? (
                          <div className="flex items-center justify-center py-8">
                            <RefreshCw className="h-6 w-6 animate-spin" />
                          </div>
                        ) : selectedUserDetails ? (
                          <Tabs defaultValue="info" className="mt-4">
                            <TabsList>
                              <TabsTrigger value="info">Informações Gerais</TabsTrigger>
                              <TabsTrigger value="jobs">Documentos</TabsTrigger>
                              <TabsTrigger value="activity">Atividade</TabsTrigger>
                            </TabsList>
                            
                            <TabsContent value="info" className="space-y-4">
                              <div className="grid grid-cols-2 gap-4">
                                <div>
                                  <h4 className="font-medium">Informações Básicas</h4>
                                  <div className="space-y-2 mt-2 text-sm">
                                    <div><strong>Nome:</strong> {selectedUserDetails.user.full_name}</div>
                                    <div><strong>Email:</strong> {selectedUserDetails.user.email}</div>
                                    <div><strong>Username:</strong> {selectedUserDetails.user.username}</div>
                                    <div><strong>Status:</strong> {selectedUserDetails.user.is_active ? 'Ativo' : 'Inativo'}</div>
                                  </div>
                                </div>
                                <div>
                                  <h4 className="font-medium">Permissões</h4>
                                  <div className="space-y-2 mt-2 text-sm">
                                    <div><strong>Admin:</strong> {selectedUserDetails.admin_profile.is_admin ? 'Sim' : 'Não'}</div>
                                    {selectedUserDetails.admin_profile.is_admin && (
                                      <>
                                        <div><strong>Nível:</strong> {selectedUserDetails.admin_profile.admin_level}</div>
                                        <div><strong>Cargo:</strong> {selectedUserDetails.admin_profile.role}</div>
                                      </>
                                    )}
                                    <div><strong>Superusuário:</strong> {selectedUserDetails.user.is_superuser ? 'Sim' : 'Não'}</div>
                                  </div>
                                </div>
                              </div>
                            </TabsContent>
                            
                            <TabsContent value="jobs" className="space-y-4">
                              <div>
                                <h4 className="font-medium mb-3">Documentos Recentes</h4>
                                <div className="space-y-2">
                                  {selectedUserDetails.recent_jobs.map((job) => (
                                    <div key={job.id} className="flex items-center justify-between p-3 border rounded">
                                      <div>
                                        <div className="font-medium">{job.filename}</div>
                                        <div className="text-sm text-gray-500">
                                          {new Date(job.created_at).toLocaleString()}
                                        </div>
                                      </div>
                                      <div className="flex items-center space-x-2">
                                        <Badge variant={job.status === 'completed' ? 'default' : 'secondary'}>
                                          {job.status}
                                        </Badge>
                                        <span className="text-sm text-gray-500">
                                          {(job.file_size / 1024 / 1024).toFixed(1)} MB
                                        </span>
                                      </div>
                                    </div>
                                  ))}
                                </div>
                              </div>
                            </TabsContent>
                            
                            <TabsContent value="activity" className="space-y-4">
                              <div>
                                <h4 className="font-medium mb-3">Atividade Recente</h4>
                                <div className="space-y-2">
                                  {selectedUserDetails.recent_activities.map((activity, index) => (
                                    <div key={index} className="flex items-center justify-between p-3 border rounded">
                                      <div>
                                        <div className="font-medium">{activity.activity_type}</div>
                                        <div className="text-sm text-gray-500">
                                          {new Date(activity.timestamp).toLocaleString()}
                                        </div>
                                      </div>
                                      <div className="text-sm text-gray-500">
                                        {activity.ip_address}
                                      </div>
                                    </div>
                                  ))}
                                </div>
                              </div>
                            </TabsContent>
                          </Tabs>
                        ) : null}
                      </DialogContent>
                    </Dialog>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-between mt-6">
              <div className="text-sm text-gray-500">
                Página {currentPage} de {totalPages}
              </div>
              <div className="flex space-x-2">
                <Button
                  variant="outline"
                  size="sm"
                  disabled={currentPage <= 1}
                  onClick={() => setCurrentPage(currentPage - 1)}
                >
                  Anterior
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  disabled={currentPage >= totalPages}
                  onClick={() => setCurrentPage(currentPage + 1)}
                >
                  Próxima
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}