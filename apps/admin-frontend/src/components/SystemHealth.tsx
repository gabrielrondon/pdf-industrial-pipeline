import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card'
import { Badge } from './ui/badge'
import { Button } from './ui/button'
import { Activity, Cpu, HardDrive, Wifi, RefreshCw, Database, Server } from 'lucide-react'

interface SystemMetrics {
  api_status: 'healthy' | 'warning' | 'error'
  database_status: 'connected' | 'disconnected' | 'error' 
  uptime: string
  active_connections: number
  total_jobs: number
  failed_jobs: number
  last_updated: string
}

const SystemHealth: React.FC = () => {
  const [metrics, setMetrics] = useState<SystemMetrics>({
    api_status: 'error',
    database_status: 'error',
    uptime: 'Unknown',
    active_connections: 0,
    total_jobs: 0,
    failed_jobs: 0,
    last_updated: 'Never'
  })
  const [loading, setLoading] = useState(false)

  const fetchSystemHealth = async () => {
    setLoading(true)
    try {
      const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'https://pdf-industrial-pipeline-production.up.railway.app'
      
      // Try to get health data from Railway API
      const healthResponse = await fetch(`${apiBaseUrl}/health`)
      
      if (healthResponse.ok) {
        const healthData = await healthResponse.json()
        
        // Try to get job statistics
        let jobStats = { total_jobs: 0, active_jobs: 0, failed_jobs: 0 }
        try {
          const statsResponse = await fetch(`${apiBaseUrl}/api/v1/jobs/stats`)
          if (statsResponse.ok) {
            jobStats = await statsResponse.json()
          }
        } catch (e) {
          console.log('Could not fetch job stats:', e)
        }

        setMetrics({
          api_status: 'healthy',
          database_status: healthData.database ? 'connected' : 'error',
          uptime: healthData.uptime || 'Unknown',
          active_connections: healthData.database_connections || 0,
          total_jobs: jobStats.total_jobs || 0,
          failed_jobs: jobStats.failed_jobs || 0,
          last_updated: new Date().toLocaleTimeString()
        })
      } else {
        setMetrics(prev => ({
          ...prev,
          api_status: 'error',
          database_status: 'error',
          last_updated: new Date().toLocaleTimeString()
        }))
      }
    } catch (error) {
      console.error('Failed to fetch system health:', error)
      setMetrics(prev => ({
        ...prev,
        api_status: 'error',
        database_status: 'error',
        last_updated: new Date().toLocaleTimeString()
      }))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchSystemHealth()
    const interval = setInterval(fetchSystemHealth, 30000) // Refresh every 30 seconds
    return () => clearInterval(interval)
  }, [])

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'healthy':
      case 'connected':
        return <Badge className="bg-green-100 text-green-800">HEALTHY</Badge>
      case 'warning':
        return <Badge className="bg-yellow-100 text-yellow-800">WARNING</Badge>
      case 'error':
      case 'disconnected':
        return <Badge className="bg-red-100 text-red-800">ERROR</Badge>
      default:
        return <Badge className="bg-gray-100 text-gray-800">UNKNOWN</Badge>
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-3xl font-bold tracking-tight">System Health</h2>
        <Button onClick={fetchSystemHealth} disabled={loading} className="flex items-center gap-2">
          <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Server className="h-5 w-5" />
              API Status
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">Railway API</div>
            {getStatusBadge(metrics.api_status)}
            <p className="text-xs text-muted-foreground mt-2">
              Last checked: {metrics.last_updated}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Database className="h-5 w-5" />
              Database
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{metrics.active_connections}</div>
            {getStatusBadge(metrics.database_status)}
            <p className="text-xs text-muted-foreground mt-2">
              Active connections
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="h-5 w-5" />
              System Uptime
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{metrics.uptime}</div>
            {getStatusBadge(metrics.api_status)}
            <p className="text-xs text-muted-foreground mt-2">
              Since last restart
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Cpu className="h-5 w-5" />
              Job Processing
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{metrics.total_jobs}</div>
            {metrics.failed_jobs > 0 ? 
              <Badge className="bg-yellow-100 text-yellow-800">
                {metrics.failed_jobs} FAILED
              </Badge> :
              <Badge className="bg-green-100 text-green-800">ALL OK</Badge>
            }
            <p className="text-xs text-muted-foreground mt-2">
              Total jobs processed
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

export default SystemHealth