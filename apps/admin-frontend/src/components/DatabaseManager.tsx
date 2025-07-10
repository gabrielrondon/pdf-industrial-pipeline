import React, { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card'
import { Button } from './ui/button'
import { Badge } from './ui/badge'
import { Database, RefreshCw, Settings, AlertTriangle } from 'lucide-react'

const DatabaseManager: React.FC = () => {
  const [dbStats] = useState({
    connectionStatus: 'connected',
    totalDocuments: 1247,
    totalUsers: 89,
    totalJobs: 2334,
    avgResponseTime: 45,
    uptime: '99.9%'
  })

  return (
    <div className="space-y-6">
      <h2 className="text-3xl font-bold tracking-tight">Database Manager</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Database className="h-5 w-5" />
              Connection Status
            </CardTitle>
          </CardHeader>
          <CardContent>
            <Badge className="bg-green-100 text-green-800">CONNECTED</Badge>
            <p className="text-sm text-gray-600 mt-2">Neon PostgreSQL</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Response Time</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{dbStats.avgResponseTime}ms</div>
            <p className="text-sm text-gray-600">Average query time</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Uptime</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{dbStats.uptime}</div>
            <p className="text-sm text-gray-600">Last 30 days</p>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Database Actions</CardTitle>
          <CardDescription>Administrative operations and maintenance tasks</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <Button variant="outline">
              <RefreshCw className="mr-2 h-4 w-4" />
              Refresh Stats
            </Button>
            <Button variant="outline">
              <Settings className="mr-2 h-4 w-4" />
              Run Maintenance
            </Button>
            <Button variant="outline">
              <Database className="mr-2 h-4 w-4" />
              Backup Now
            </Button>
            <Button variant="outline">
              <AlertTriangle className="mr-2 h-4 w-4" />
              Check Health
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default DatabaseManager