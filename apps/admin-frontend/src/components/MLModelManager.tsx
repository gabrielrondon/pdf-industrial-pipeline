import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card'
import { Button } from './ui/button'
import { Badge } from './ui/badge'
import { Brain, Play, Pause, Download, Upload, RefreshCw } from 'lucide-react'

interface ModelInfo {
  name: string
  version: string
  status: 'active' | 'training' | 'idle' | 'error'
  accuracy?: number
  lastTrained?: string
  size: string
}

const MLModelManager: React.FC = () => {
  const [models, setModels] = useState<ModelInfo[]>([
    {
      name: 'Lead Scoring Model',
      version: 'v1.2.3',
      status: 'active',
      accuracy: 0.94,
      lastTrained: '2024-01-15',
      size: '45.2 MB'
    },
    {
      name: 'Document Classifier',
      version: 'v2.1.0',
      status: 'active',
      accuracy: 0.89,
      lastTrained: '2024-01-10',
      size: '23.8 MB'
    },
    {
      name: 'Feature Engineering Pipeline',
      version: 'v1.0.8',
      status: 'idle',
      lastTrained: '2024-01-05',
      size: '12.1 MB'
    }
  ])
  const [loading, setLoading] = useState(false)

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800'
      case 'training': return 'bg-blue-100 text-blue-800'
      case 'idle': return 'bg-gray-100 text-gray-800'
      case 'error': return 'bg-red-100 text-red-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const retrainModel = async (modelName: string) => {
    setLoading(true)
    try {
      const response = await fetch(`/api/v1/models/${modelName}/retrain`, {
        method: 'POST'
      })
      if (response.ok) {
        // Update model status to training
        setModels(prev => prev.map(model => 
          model.name === modelName 
            ? { ...model, status: 'training' as const }
            : model
        ))
      }
    } catch (error) {
      console.error('Failed to retrain model:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-3xl font-bold tracking-tight">ML Model Manager</h2>
        <Button className="flex items-center gap-2">
          <RefreshCw className="h-4 w-4" />
          Refresh Models
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {models.map((model, index) => (
          <Card key={index}>
            <CardHeader>
              <div className="flex items-center justify-between">
                <Brain className="h-5 w-5 text-blue-500" />
                <Badge className={getStatusColor(model.status)}>
                  {model.status.toUpperCase()}
                </Badge>
              </div>
              <CardTitle className="text-lg">{model.name}</CardTitle>
              <CardDescription>Version {model.version}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {model.accuracy && (
                <div className="flex justify-between">
                  <span className="text-sm font-medium">Accuracy:</span>
                  <span className="text-sm">{(model.accuracy * 100).toFixed(1)}%</span>
                </div>
              )}
              <div className="flex justify-between">
                <span className="text-sm font-medium">Size:</span>
                <span className="text-sm">{model.size}</span>
              </div>
              {model.lastTrained && (
                <div className="flex justify-between">
                  <span className="text-sm font-medium">Last Trained:</span>
                  <span className="text-sm">{model.lastTrained}</span>
                </div>
              )}
              
              <div className="flex space-x-2 pt-2">
                <Button 
                  size="sm" 
                  variant="outline"
                  onClick={() => retrainModel(model.name)}
                  disabled={loading || model.status === 'training'}
                >
                  <Play className="h-3 w-3 mr-1" />
                  Retrain
                </Button>
                <Button size="sm" variant="outline">
                  <Download className="h-3 w-3 mr-1" />
                  Export
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Training History</CardTitle>
          <CardDescription>Recent model training sessions and performance metrics</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center justify-between p-3 border rounded-lg">
              <div>
                <p className="font-medium">Lead Scoring Model v1.2.3</p>
                <p className="text-sm text-gray-600">Training completed successfully</p>
              </div>
              <div className="text-right">
                <p className="text-sm font-medium">94.2% accuracy</p>
                <p className="text-xs text-gray-500">2 hours ago</p>
              </div>
            </div>
            <div className="flex items-center justify-between p-3 border rounded-lg">
              <div>
                <p className="font-medium">Document Classifier v2.1.0</p>
                <p className="text-sm text-gray-600">Training completed successfully</p>
              </div>
              <div className="text-right">
                <p className="text-sm font-medium">89.7% accuracy</p>
                <p className="text-xs text-gray-500">1 day ago</p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default MLModelManager