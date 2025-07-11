import React, { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card'
import { Button } from './ui/button'
import { Badge } from './ui/badge'
import { Upload, FileText, Play, Download, AlertTriangle } from 'lucide-react'

interface ProcessingResult {
  jobId: string
  status: 'processing' | 'completed' | 'failed'
  result?: any
  error?: string
  processingTime?: number
}

const DocumentTester: React.FC = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [processingResult, setProcessingResult] = useState<ProcessingResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [analysisType, setAnalysisType] = useState<'native' | 'ai'>('native')

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file && file.type === 'application/pdf') {
      setSelectedFile(file)
      setProcessingResult(null)
    }
  }

  const processDocument = async () => {
    if (!selectedFile) return

    setLoading(true)
    setProcessingResult(null)

    try {
      const formData = new FormData()
      formData.append('file', selectedFile)
      formData.append('analysis_type', analysisType)

      const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData
      })

      if (response.ok) {
        const result = await response.json()
        setProcessingResult({
          jobId: result.job_id,
          status: 'processing'
        })

        // Poll for completion
        pollJobStatus(result.job_id)
      } else {
        const errorData = await response.json().catch(() => ({ detail: 'Upload failed' }))
        console.error('Upload error:', { status: response.status, error: errorData })
        throw new Error(errorData.detail || errorData.message || `Upload failed with status ${response.status}`)
      }
    } catch (error) {
      setProcessingResult({
        jobId: '',
        status: 'failed',
        error: error instanceof Error ? error.message : 'Unknown error'
      })
    } finally {
      setLoading(false)
    }
  }

  const pollJobStatus = async (jobId: string) => {
    const maxAttempts = 60 // 5 minutes max
    let attempts = 0

    const poll = async () => {
      try {
        const response = await fetch(`/api/job/${jobId}/status`)
        if (response.ok) {
          const status = await response.json()
          
          if (status.status === 'completed') {
            setProcessingResult({
              jobId,
              status: 'completed',
              result: status.results || status.result,
              processingTime: status.processing_time
            })
            return
          } else if (status.status === 'failed') {
            setProcessingResult({
              jobId,
              status: 'failed',
              error: status.error_message || status.error
            })
            return
          }
        } else {
          const errorData = await response.json().catch(() => ({ detail: 'Status check failed' }))
          console.error('Status check error:', { status: response.status, error: errorData })
          throw new Error(errorData.detail || `Status check failed with status ${response.status}`)
        }

        attempts++
        if (attempts < maxAttempts) {
          setTimeout(poll, 5000) // Poll every 5 seconds
        } else {
          setProcessingResult({
            jobId,
            status: 'failed',
            error: 'Processing timeout'
          })
        }
      } catch (error) {
        setProcessingResult({
          jobId,
          status: 'failed',
          error: 'Failed to check status'
        })
      }
    }

    poll()
  }

  const downloadResult = () => {
    if (processingResult?.result) {
      const blob = new Blob([JSON.stringify(processingResult.result, null, 2)], {
        type: 'application/json'
      })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `analysis_result_${processingResult.jobId}.json`
      a.click()
      URL.revokeObjectURL(url)
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'bg-green-100 text-green-800'
      case 'processing': return 'bg-blue-100 text-blue-800'
      case 'failed': return 'bg-red-100 text-red-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  return (
    <div className="space-y-6">
      <h2 className="text-3xl font-bold tracking-tight">Document Tester</h2>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Upload & Process Document</CardTitle>
            <CardDescription>Test the PDF processing pipeline with real documents</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div>
              <label className="block text-sm font-medium mb-2">Analysis Type</label>
              <div className="flex space-x-4">
                <label className="flex items-center">
                  <input
                    type="radio"
                    value="native"
                    checked={analysisType === 'native'}
                    onChange={(e) => setAnalysisType(e.target.value as 'native' | 'ai')}
                    className="mr-2"
                  />
                  Native Analyzer
                </label>
                <label className="flex items-center">
                  <input
                    type="radio"
                    value="ai"
                    checked={analysisType === 'ai'}
                    onChange={(e) => setAnalysisType(e.target.value as 'native' | 'ai')}
                    className="mr-2"
                  />
                  AI Analyzer
                </label>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Select PDF File</label>
              <input
                type="file"
                accept=".pdf"
                onChange={handleFileSelect}
                className="block w-full text-sm text-gray-500
                file:mr-4 file:py-2 file:px-4
                file:rounded-full file:border-0
                file:text-sm file:font-semibold
                file:bg-blue-50 file:text-blue-700
                hover:file:bg-blue-100"
              />
            </div>

            {selectedFile && (
              <div className="flex items-center space-x-2 p-3 bg-gray-50 rounded-lg">
                <FileText className="h-5 w-5 text-gray-500" />
                <span className="text-sm">{selectedFile.name}</span>
                <span className="text-xs text-gray-500">
                  ({(selectedFile.size / 1024 / 1024).toFixed(2)} MB)
                </span>
              </div>
            )}

            <Button 
              onClick={processDocument} 
              disabled={!selectedFile || loading}
              className="w-full"
            >
              {loading ? (
                <>Processing...</>
              ) : (
                <>
                  <Play className="mr-2 h-4 w-4" />
                  Process Document
                </>
              )}
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Processing Results</CardTitle>
            <CardDescription>View analysis results and processing status</CardDescription>
          </CardHeader>
          <CardContent>
            {!processingResult ? (
              <div className="text-center text-gray-500 py-8">
                <FileText className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                <p>No results yet. Upload and process a document to see results here.</p>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Status:</span>
                  <Badge className={getStatusColor(processingResult.status)}>
                    {processingResult.status.toUpperCase()}
                  </Badge>
                </div>

                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Job ID:</span>
                  <span className="text-sm font-mono text-gray-600">
                    {processingResult.jobId}
                  </span>
                </div>

                {processingResult.processingTime && (
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">Processing Time:</span>
                    <span className="text-sm text-gray-600">
                      {processingResult.processingTime}s
                    </span>
                  </div>
                )}

                {processingResult.error && (
                  <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
                    <div className="flex items-center space-x-2">
                      <AlertTriangle className="h-4 w-4 text-red-500" />
                      <span className="text-sm font-medium text-red-800">Error</span>
                    </div>
                    <p className="text-sm text-red-700 mt-1">{processingResult.error}</p>
                  </div>
                )}

                {processingResult.result && (
                  <div className="space-y-3">
                    <div className="p-3 bg-green-50 border border-green-200 rounded-lg">
                      <p className="text-sm text-green-800">Processing completed successfully!</p>
                    </div>
                    
                    <Button 
                      onClick={downloadResult}
                      variant="outline"
                      className="w-full"
                    >
                      <Download className="mr-2 h-4 w-4" />
                      Download Results
                    </Button>

                    <div className="max-h-64 overflow-y-auto bg-gray-50 p-3 rounded-lg">
                      <pre className="text-xs">
                        {JSON.stringify(processingResult.result, null, 2)}
                      </pre>
                    </div>
                  </div>
                )}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

export default DocumentTester