import React, { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card'
import { Button } from './ui/button'
import { Badge } from './ui/badge'
import { Send, Code, Clock } from 'lucide-react'

interface APIResponse {
  status: number
  data: any
  responseTime: number
}

const APITester: React.FC = () => {
  const [response, setResponse] = useState<APIResponse | null>(null)
  const [loading, setLoading] = useState(false)

  const testEndpoint = async (endpoint: string, method = 'GET') => {
    setLoading(true)
    const startTime = Date.now()
    
    try {
      const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'https://pdf-industrial-pipeline-production.up.railway.app'
      const fullUrl = endpoint.startsWith('http') ? endpoint : `${apiBaseUrl}${endpoint}`
      
      const res = await fetch(fullUrl, { 
        method,
        headers: {
          'Content-Type': 'application/json'
        }
      })
      
      let data
      try {
        data = await res.json()
      } catch {
        data = { message: await res.text() }
      }
      
      const responseTime = Date.now() - startTime
      
      setResponse({
        status: res.status,
        data,
        responseTime
      })
    } catch (error) {
      setResponse({
        status: 0,
        data: { error: error instanceof Error ? error.message : 'Network error' },
        responseTime: Date.now() - startTime
      })
    } finally {
      setLoading(false)
    }
  }

  const endpoints = [
    { name: 'Health Check', path: '/health', method: 'GET' },
    { name: 'Jobs Stats', path: '/api/v1/jobs/stats', method: 'GET' },
    { name: 'Jobs List', path: '/api/v1/jobs', method: 'GET' },
    { name: 'System Info', path: '/api/v1/system/info', method: 'GET' },
  ]

  const getStatusColor = (status: number) => {
    if (status >= 200 && status < 300) return 'bg-green-100 text-green-800'
    if (status >= 400) return 'bg-red-100 text-red-800'
    return 'bg-gray-100 text-gray-800'
  }

  return (
    <div className="space-y-6">
      <h2 className="text-3xl font-bold tracking-tight">API Tester</h2>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Quick Tests</CardTitle>
            <CardDescription>Test common API endpoints</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {endpoints.map((endpoint, index) => (
              <Button
                key={index}
                variant="outline"
                className="w-full justify-between"
                onClick={() => testEndpoint(endpoint.path, endpoint.method)}
                disabled={loading}
              >
                <span>{endpoint.name}</span>
                <Code className="h-4 w-4" />
              </Button>
            ))}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Response</CardTitle>
            <CardDescription>API response details</CardDescription>
          </CardHeader>
          <CardContent>
            {!response ? (
              <div className="text-center text-gray-500 py-8">
                <Send className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                <p>Select an endpoint to test</p>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Status:</span>
                  <Badge className={getStatusColor(response.status)}>
                    {response.status}
                  </Badge>
                </div>
                
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Response Time:</span>
                  <span className="text-sm flex items-center gap-1">
                    <Clock className="h-3 w-3" />
                    {response.responseTime}ms
                  </span>
                </div>

                <div>
                  <span className="text-sm font-medium mb-2 block">Response Data:</span>
                  <div className="max-h-64 overflow-y-auto bg-gray-50 p-3 rounded-lg">
                    <pre className="text-xs">
                      {JSON.stringify(response.data, null, 2)}
                    </pre>
                  </div>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

export default APITester