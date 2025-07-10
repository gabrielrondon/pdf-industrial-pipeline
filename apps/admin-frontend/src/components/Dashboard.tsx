import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card'
import { Badge } from './ui/badge'
import { Button } from './ui/button'
import { RefreshCw, FileText, Database, Cpu, Activity } from 'lucide-react'

interface SystemStats {
  totalDocuments: number
  activeJobs: number
  systemUptime: string
  dbConnections: number
  apiStatus: 'healthy' | 'warning' | 'error'
  lastUpdate: string
}

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<SystemStats>({
    totalDocuments: 0,
    activeJobs: 0,
    systemUptime: '0h 0m',
    dbConnections: 0,
    apiStatus: 'healthy',
    lastUpdate: new Date().toLocaleTimeString()
  })
  const [loading, setLoading] = useState(false)

  const fetchSystemStats = async () => {
    setLoading(true)
    try {
      // Replace with actual API endpoint
      const response = await fetch('/api/v1/system/stats')
      if (response.ok) {
        const data = await response.json()
        setStats({
          ...data,
          lastUpdate: new Date().toLocaleTimeString()
        })
      } else {
        // Mock data for now
        setStats({
          totalDocuments: 1247,
          activeJobs: 3,
          systemUptime: '2d 14h 32m',
          dbConnections: 8,
          apiStatus: 'healthy',
          lastUpdate: new Date().toLocaleTimeString()
        })
      }
    } catch (error) {
      console.error('Failed to fetch system stats:', error)
      // Mock data fallback
      setStats({
        totalDocuments: 1247,
        activeJobs: 3,
        systemUptime: '2d 14h 32m',
        dbConnections: 8,
        apiStatus: 'warning',
        lastUpdate: new Date().toLocaleTimeString()
      })
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchSystemStats()
    const interval = setInterval(fetchSystemStats, 30000) // Refresh every 30 seconds
    return () => clearInterval(interval)
  }, [])

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy': return 'bg-green-100 text-green-800'
      case 'warning': return 'bg-yellow-100 text-yellow-800'
      case 'error': return 'bg-red-100 text-red-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-3xl font-bold tracking-tight">Dashboard</h2>
        <Button onClick={fetchSystemStats} disabled={loading} className="flex items-center gap-2">
          <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Documents</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalDocuments.toLocaleString()}</div>
            <p className="text-xs text-muted-foreground">Processed documents</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Jobs</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.activeJobs}</div>
            <p className="text-xs text-muted-foreground">Currently processing</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">System Uptime</CardTitle>
            <Cpu className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.systemUptime}</div>
            <p className="text-xs text-muted-foreground">Since last restart</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">API Status</CardTitle>
            <Database className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="flex items-center space-x-2">
              <Badge className={getStatusColor(stats.apiStatus)}>
                {stats.apiStatus.toUpperCase()}
              </Badge>
            </div>
            <p className="text-xs text-muted-foreground">{stats.dbConnections} DB connections</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>
            <CardDescription>Latest system events and processed documents</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center space-x-4">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <div className="flex-1">
                  <p className="text-sm font-medium">Document processed successfully</p>
                  <p className="text-xs text-muted-foreground">judicial_analysis_v2.pdf - 2 minutes ago</p>
                </div>
              </div>
              <div className="flex items-center space-x-4">
                <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                <div className="flex-1">
                  <p className="text-sm font-medium">ML model training completed</p>
                  <p className="text-xs text-muted-foreground">Lead scoring model v1.2 - 15 minutes ago</p>
                </div>
              </div>
              <div className="flex items-center space-x-4">
                <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
                <div className="flex-1">
                  <p className="text-sm font-medium">High memory usage detected</p>
                  <p className="text-xs text-muted-foreground">Worker node 2 - 1 hour ago</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
            <CardDescription>Common administrative tasks</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Button variant="outline" className="w-full justify-start">
              <FileText className="mr-2 h-4 w-4" />
              Test Document Processing
            </Button>
            <Button variant="outline" className="w-full justify-start">
              <Database className="mr-2 h-4 w-4" />
              Check Database Health
            </Button>
            <Button variant="outline" className="w-full justify-start">
              <Cpu className="mr-2 h-4 w-4" />
              Monitor ML Models
            </Button>
            <Button variant="outline" className="w-full justify-start">
              <Activity className="mr-2 h-4 w-4" />
              View System Logs
            </Button>
          </CardContent>
        </Card>
      </div>

      <div className="text-xs text-muted-foreground text-center">
        Last updated: {stats.lastUpdate}
      </div>
    </div>
  )
}

export default Dashboard