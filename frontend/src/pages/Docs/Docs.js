import React, { useState } from 'react';
import { 
  Book, 
  Upload, 
  FileText, 
  Search, 
  Brain, 
  BarChart3, 
  Settings, 
  ChevronRight, 
  ChevronDown,
  Code,
  Play,
  CheckCircle,
  AlertCircle,
  Info
} from 'lucide-react';

const Docs = () => {
  const [expandedSections, setExpandedSections] = useState({
    overview: true,
    quickStart: false,
    endpoints: false,
    stages: false,
    examples: false,
    troubleshooting: false
  });

  const toggleSection = (section) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  const DocSection = ({ id, title, icon: Icon, children }) => {
    const isExpanded = expandedSections[id];
    
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 mb-6">
        <button
          onClick={() => toggleSection(id)}
          className="w-full px-6 py-4 flex items-center justify-between text-left hover:bg-gray-50 transition-colors"
        >
          <div className="flex items-center space-x-3">
            <Icon className="h-5 w-5 text-blue-600" />
            <h2 className="text-lg font-semibold text-gray-900">{title}</h2>
          </div>
          {isExpanded ? (
            <ChevronDown className="h-5 w-5 text-gray-400" />
          ) : (
            <ChevronRight className="h-5 w-5 text-gray-400" />
          )}
        </button>
        
        {isExpanded && (
          <div className="px-6 pb-6 border-t border-gray-100">
            {children}
          </div>
        )}
      </div>
    );
  };

  const CodeBlock = ({ children, language = 'bash' }) => (
    <div className="bg-gray-900 rounded-lg p-4 my-4">
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs text-gray-400 uppercase tracking-wide">{language}</span>
        <Code className="h-4 w-4 text-gray-400" />
      </div>
      <pre className="text-sm text-green-400 overflow-x-auto">
        <code>{children}</code>
      </pre>
    </div>
  );

  const EndpointCard = ({ method, path, description, example, response }) => (
    <div className="bg-gray-50 rounded-lg p-4 mb-4">
      <div className="flex items-center space-x-3 mb-2">
        <span className={`px-2 py-1 text-xs font-semibold rounded ${
          method === 'GET' ? 'bg-green-100 text-green-800' :
          method === 'POST' ? 'bg-blue-100 text-blue-800' :
          method === 'DELETE' ? 'bg-red-100 text-red-800' :
          'bg-gray-100 text-gray-800'
        }`}>
          {method}
        </span>
        <code className="text-sm font-mono bg-white px-2 py-1 rounded border">
          {path}
        </code>
      </div>
      <p className="text-gray-700 mb-3">{description}</p>
      
      {example && (
        <div>
          <h4 className="text-sm font-semibold text-gray-900 mb-2">Example:</h4>
          <CodeBlock>{example}</CodeBlock>
        </div>
      )}
      
      {response && (
        <div>
          <h4 className="text-sm font-semibold text-gray-900 mb-2">Response:</h4>
          <CodeBlock language="json">{response}</CodeBlock>
        </div>
      )}
    </div>
  );

  const StageCard = ({ number, title, description, status, features }) => (
    <div className="bg-white border border-gray-200 rounded-lg p-6 mb-4">
      <div className="flex items-center space-x-3 mb-3">
        <div className="flex items-center justify-center w-8 h-8 bg-blue-100 text-blue-600 rounded-full text-sm font-semibold">
          {number}
        </div>
        <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
        <span className={`px-2 py-1 text-xs font-semibold rounded ${
          status === 'Complete' ? 'bg-green-100 text-green-800' :
          status === 'Ready' ? 'bg-blue-100 text-blue-800' :
          'bg-gray-100 text-gray-800'
        }`}>
          {status}
        </span>
      </div>
      <p className="text-gray-600 mb-4">{description}</p>
      <ul className="space-y-1">
        {features.map((feature, index) => (
          <li key={index} className="flex items-center space-x-2 text-sm text-gray-700">
            <CheckCircle className="h-4 w-4 text-green-500" />
            <span>{feature}</span>
          </li>
        ))}
      </ul>
    </div>
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg p-8 text-white">
        <div className="flex items-center space-x-3 mb-4">
          <Book className="h-8 w-8" />
          <h1 className="text-3xl font-bold">PDF Industrial Pipeline Documentation</h1>
        </div>
        <p className="text-blue-100 text-lg">
          Complete guide to using the PDF Industrial Pipeline system for document processing, 
          text analysis, and lead generation.
        </p>
      </div>

      {/* System Overview */}
      <DocSection id="overview" title="System Overview" icon={Info}>
        <div className="prose max-w-none">
          <p className="text-gray-700 mb-4">
            The PDF Industrial Pipeline is a comprehensive document processing system that transforms 
            PDF files into actionable business intelligence. The system processes documents through 
            7 distinct stages, each adding value and extracting insights.
          </p>
          
          <div className="grid md:grid-cols-2 gap-6 mt-6">
            <div className="bg-blue-50 p-4 rounded-lg">
              <h3 className="font-semibold text-blue-900 mb-2">Key Capabilities</h3>
              <ul className="space-y-1 text-sm text-blue-800">
                <li>• PDF splitting and page extraction</li>
                <li>• OCR text recognition (Portuguese/English)</li>
                <li>• NLP text analysis and entity extraction</li>
                <li>• Vector embeddings and semantic search</li>
                <li>• Machine learning lead scoring</li>
                <li>• Performance monitoring and caching</li>
                <li>• Real-time web dashboard</li>
              </ul>
            </div>
            
            <div className="bg-green-50 p-4 rounded-lg">
              <h3 className="font-semibold text-green-900 mb-2">Use Cases</h3>
              <ul className="space-y-1 text-sm text-green-800">
                <li>• Business document analysis</li>
                <li>• Lead generation from proposals</li>
                <li>• Contract and invoice processing</li>
                <li>• Content extraction and indexing</li>
                <li>• Automated document classification</li>
                <li>• Semantic document search</li>
              </ul>
            </div>
          </div>
        </div>
      </DocSection>

      {/* Quick Start Guide */}
      <DocSection id="quickStart" title="Quick Start Guide" icon={Play}>
        <div className="space-y-6">
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <div className="flex items-center space-x-2 mb-2">
              <AlertCircle className="h-5 w-5 text-yellow-600" />
              <h3 className="font-semibold text-yellow-800">Prerequisites</h3>
            </div>
            <ul className="text-sm text-yellow-700 space-y-1">
              <li>• Python 3.8+ with virtual environment</li>
              <li>• Redis server running on localhost:6379</li>
              <li>• Tesseract OCR installed</li>
              <li>• Required Python packages (see requirements.txt)</li>
            </ul>
          </div>

          <div>
            <h3 className="font-semibold text-gray-900 mb-3">1. Start the Server</h3>
            <CodeBlock>python main.py</CodeBlock>
            <p className="text-sm text-gray-600">Server will start on http://localhost:8000</p>
          </div>

          <div>
            <h3 className="font-semibold text-gray-900 mb-3">2. Upload Your First PDF</h3>
            <CodeBlock>{`curl -X POST "http://localhost:8000/upload" \\
  -H "Content-Type: multipart/form-data" \\
  -F "file=@your-document.pdf"`}</CodeBlock>
            <p className="text-sm text-gray-600">This will return a job_id for tracking processing status</p>
          </div>

          <div>
            <h3 className="font-semibold text-gray-900 mb-3">3. Check Processing Status</h3>
            <CodeBlock>{`curl "http://localhost:8000/job/{job_id}/status"`}</CodeBlock>
          </div>

          <div>
            <h3 className="font-semibold text-gray-900 mb-3">4. Access the Web Dashboard</h3>
            <p className="text-gray-700">
              Open your browser to <code className="bg-gray-100 px-2 py-1 rounded">http://localhost:8000</code> 
              to access the interactive dashboard with real-time monitoring and analytics.
            </p>
          </div>
        </div>
      </DocSection>

      {/* API Endpoints */}
      <DocSection id="endpoints" title="API Endpoints Reference" icon={Code}>
        <div className="space-y-6">
          
          {/* Stage 1: Upload & Processing */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center space-x-2">
              <Upload className="h-5 w-5 text-blue-600" />
              <span>Stage 1: PDF Upload & Processing</span>
            </h3>
            
            <EndpointCard
              method="POST"
              path="/upload"
              description="Upload a PDF file and start processing pipeline"
              example={`curl -X POST "http://localhost:8000/upload" \\
  -H "Content-Type: multipart/form-data" \\
  -F "file=@document.pdf"`}
              response={`{
  "job_id": "uuid-string",
  "status": "processed",
  "original_filename": "document.pdf",
  "file_size": "2.5 MB",
  "page_count": 10,
  "output_directory": "temp_splits/uuid/",
  "manifest_path": "temp_splits/uuid/manifest.json"
}`}
            />

            <EndpointCard
              method="GET"
              path="/job/{job_id}/status"
              description="Check the processing status of a specific job"
              example={`curl "http://localhost:8000/job/your-job-id/status"`}
              response={`{
  "job_id": "uuid-string",
  "status": "completed",
  "pages_processed": 10,
  "ocr_completed": true,
  "text_analysis_completed": true,
  "embeddings_generated": true
}`}
            />

            <EndpointCard
              method="DELETE"
              path="/job/{job_id}"
              description="Clean up temporary files for a completed job"
              example={`curl -X DELETE "http://localhost:8000/job/your-job-id"`}
              response={`{
  "message": "Job uuid-string removed successfully"
}`}
            />
          </div>

          {/* Stage 3: Text Processing */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center space-x-2">
              <FileText className="h-5 w-5 text-green-600" />
              <span>Stage 3: Text Processing & NLP</span>
            </h3>
            
            <EndpointCard
              method="POST"
              path="/process-text/{job_id}"
              description="Process text analysis for OCR results (NLP, entity extraction, keyword analysis)"
              example={`curl -X POST "http://localhost:8000/process-text/your-job-id"`}
              response={`{
  "job_id": "uuid-string",
  "status": "text_processed",
  "result": {
    "entities_found": ["Company Name", "CNPJ", "Email"],
    "keywords": ["technology", "development", "project"],
    "lead_score": 85.5,
    "business_potential": "high"
  }
}`}
            />

            <EndpointCard
              method="GET"
              path="/job/{job_id}/text-analysis"
              description="Retrieve text analysis results for a job"
              example={`curl "http://localhost:8000/job/your-job-id/text-analysis"`}
            />

            <EndpointCard
              method="GET"
              path="/text-processing/stats"
              description="Get text processing statistics and performance metrics"
              example={`curl "http://localhost:8000/text-processing/stats"`}
            />
          </div>

          {/* Stage 4: Embeddings */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center space-x-2">
              <Search className="h-5 w-5 text-purple-600" />
              <span>Stage 4: Embeddings & Vector Search</span>
            </h3>
            
            <EndpointCard
              method="POST"
              path="/generate-embeddings/{job_id}"
              description="Generate vector embeddings for semantic search"
              example={`curl -X POST "http://localhost:8000/generate-embeddings/your-job-id"`}
            />

            <EndpointCard
              method="POST"
              path="/search/semantic"
              description="Perform semantic search across processed documents"
              example={`curl -X POST "http://localhost:8000/search/semantic" \\
  -H "Content-Type: application/json" \\
  -d '{"query": "technology companies", "k": 10, "threshold": 0.7}'`}
              response={`{
  "query": "technology companies",
  "results": [
    {
      "job_id": "uuid",
      "page_number": 1,
      "similarity_score": 0.89,
      "text_snippet": "TechSolutions Brasil...",
      "metadata": {...}
    }
  ],
  "total_results": 5
}`}
            />

            <EndpointCard
              method="GET"
              path="/search/leads"
              description="Search for high-scoring business leads"
              example={`curl "http://localhost:8000/search/leads?min_score=70.0"`}
            />
          </div>

          {/* Stage 5: Machine Learning */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center space-x-2">
              <Brain className="h-5 w-5 text-red-600" />
              <span>Stage 5: Machine Learning & Scoring</span>
            </h3>
            
            <EndpointCard
              method="POST"
              path="/extract-features/{job_id}"
              description="Extract ML features from processed text"
              example={`curl -X POST "http://localhost:8000/extract-features/your-job-id"`}
            />

            <EndpointCard
              method="POST"
              path="/train-models"
              description="Train ML models for lead scoring"
              example={`curl -X POST "http://localhost:8000/train-models" \\
  -H "Content-Type: application/json" \\
  -d '{"job_ids": ["job1", "job2"], "min_samples": 10}'`}
            />

            <EndpointCard
              method="POST"
              path="/predict-leads/{job_id}"
              description="Generate ML predictions for lead quality"
              example={`curl -X POST "http://localhost:8000/predict-leads/your-job-id"`}
            />

            <EndpointCard
              method="GET"
              path="/ml/lead-quality-analysis"
              description="Get comprehensive lead quality analysis"
              example={`curl "http://localhost:8000/ml/lead-quality-analysis?threshold_high=80.0"`}
            />
          </div>

          {/* Stage 6: Performance */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center space-x-2">
              <BarChart3 className="h-5 w-5 text-orange-600" />
              <span>Stage 6: Performance & Monitoring</span>
            </h3>
            
            <EndpointCard
              method="GET"
              path="/performance/system/health"
              description="Get comprehensive system health status"
              example={`curl "http://localhost:8000/performance/system/health"`}
              response={`{
  "system_status": "healthy",
  "uptime_seconds": 3600,
  "healthy_components": 3,
  "total_components": 4,
  "component_details": [...]
}`}
            />

            <EndpointCard
              method="GET"
              path="/performance/cache/stats"
              description="Get Redis cache statistics"
              example={`curl "http://localhost:8000/performance/cache/stats"`}
            />

            <EndpointCard
              method="GET"
              path="/performance/analytics"
              description="Get performance analytics and metrics"
              example={`curl "http://localhost:8000/performance/analytics"`}
            />
          </div>
        </div>
      </DocSection>

      {/* Usage Examples */}
      <DocSection id="examples" title="Usage Examples" icon={Play}>
        <div className="space-y-6">
          
          <div>
            <h3 className="font-semibold text-gray-900 mb-3">Complete Processing Workflow</h3>
            <p className="text-gray-600 mb-3">
              Here's a complete example of processing a business proposal document:
            </p>
            <CodeBlock>{`# 1. Upload PDF
curl -X POST "http://localhost:8000/upload" \\
  -F "file=@business-proposal.pdf"
# Returns: {"job_id": "abc-123", ...}

# 2. Check status
curl "http://localhost:8000/job/abc-123/status"

# 3. Process text analysis
curl -X POST "http://localhost:8000/process-text/abc-123"

# 4. Generate embeddings
curl -X POST "http://localhost:8000/generate-embeddings/abc-123"

# 5. Extract ML features
curl -X POST "http://localhost:8000/extract-features/abc-123"

# 6. Get lead predictions
curl -X POST "http://localhost:8000/predict-leads/abc-123"

# 7. Search similar documents
curl -X POST "http://localhost:8000/search/semantic" \\
  -H "Content-Type: application/json" \\
  -d '{"query": "software development project", "k": 5}'`}</CodeBlock>
          </div>

          <div>
            <h3 className="font-semibold text-gray-900 mb-3">System Monitoring</h3>
            <CodeBlock>{`# Check system health
curl "http://localhost:8000/performance/system/health"

# Get cache statistics
curl "http://localhost:8000/performance/cache/stats"

# View performance analytics
curl "http://localhost:8000/performance/analytics"`}</CodeBlock>
          </div>
        </div>
      </DocSection>

      {/* Troubleshooting */}
      <DocSection id="troubleshooting" title="Troubleshooting" icon={AlertCircle}>
        <div className="space-y-6">
          
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <h3 className="font-semibold text-red-800 mb-2">Common Issues</h3>
            
            <div className="space-y-4 text-sm">
              <div>
                <h4 className="font-medium text-red-700">Redis Connection Error</h4>
                <p className="text-red-600 mb-2">Error: "ConnectionError: Error connecting to Redis"</p>
                <p className="text-red-700">
                  <strong>Solution:</strong> Ensure Redis server is running on localhost:6379
                </p>
                <CodeBlock>redis-server</CodeBlock>
              </div>

              <div>
                <h4 className="font-medium text-red-700">Tesseract Not Found</h4>
                <p className="text-red-600 mb-2">Error: "TesseractNotFoundError"</p>
                <p className="text-red-700">
                  <strong>Solution:</strong> Install Tesseract OCR
                </p>
                <CodeBlock>{`# macOS
brew install tesseract tesseract-lang

# Ubuntu/Debian
sudo apt-get install tesseract-ocr tesseract-ocr-por`}</CodeBlock>
              </div>

              <div>
                <h4 className="font-medium text-red-700">Port Already in Use</h4>
                <p className="text-red-600 mb-2">Error: "Address already in use"</p>
                <p className="text-red-700">
                  <strong>Solution:</strong> Kill existing process or use different port
                </p>
                <CodeBlock>{`# Find and kill process
lsof -ti:8000 | xargs kill -9

# Or use different port
python main.py --port 8001`}</CodeBlock>
              </div>
            </div>
          </div>

          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <h3 className="font-semibold text-green-800 mb-2">Best Practices</h3>
            <ul className="space-y-2 text-sm text-green-700">
              <li>• Always check job status before proceeding to next stage</li>
              <li>• Clean up completed jobs to free disk space</li>
              <li>• Use semantic search for finding similar documents</li>
              <li>• Train ML models with sufficient data (20+ samples recommended)</li>
              <li>• Monitor system resources during heavy processing</li>
            </ul>
          </div>
        </div>
      </DocSection>
    </div>
  );
};

export default Docs; 