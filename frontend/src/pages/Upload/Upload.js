import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload as UploadIcon, FileText, X, Check, AlertCircle } from 'lucide-react';
import { apiService, apiUtils } from '../../services/api';
import toast from 'react-hot-toast';

function Upload() {
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState({});

  const onDrop = useCallback((acceptedFiles, rejectedFiles) => {
    // Handle rejected files
    rejectedFiles.forEach(({ file, errors }) => {
      errors.forEach(error => {
        if (error.code === 'file-too-large') {
          toast.error(`Arquivo ${file.name} é muito grande. Máximo 50MB.`);
        } else if (error.code === 'file-invalid-type') {
          toast.error(`Arquivo ${file.name} não é um PDF válido.`);
        }
      });
    });

    // Add accepted files
    const newFiles = acceptedFiles.map(file => ({
      id: Date.now() + Math.random(),
      file,
      status: 'pending',
      progress: 0,
      jobId: null,
      error: null,
    }));

    setFiles(prev => [...prev, ...newFiles]);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf']
    },
    maxSize: 50 * 1024 * 1024, // 50MB
    multiple: true
  });

  const removeFile = (fileId) => {
    setFiles(prev => prev.filter(f => f.id !== fileId));
  };

  const uploadFile = async (fileData) => {
    try {
      setFiles(prev => prev.map(f => 
        f.id === fileData.id 
          ? { ...f, status: 'uploading', progress: 0 }
          : f
      ));

      const response = await apiService.uploadFile(fileData.file, (progressEvent) => {
        const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        setUploadProgress(prev => ({ ...prev, [fileData.id]: progress }));
        setFiles(prev => prev.map(f => 
          f.id === fileData.id 
            ? { ...f, progress }
            : f
        ));
      });

      setFiles(prev => prev.map(f => 
        f.id === fileData.id 
          ? { 
              ...f, 
              status: 'completed', 
              progress: 100,
              jobId: response.job_id 
            }
          : f
      ));

      toast.success(`${fileData.file.name} carregado com sucesso!`);
      
    } catch (error) {
      console.error('Upload error:', error);
      const errorMessage = apiUtils.getErrorMessage(error);
      
      setFiles(prev => prev.map(f => 
        f.id === fileData.id 
          ? { 
              ...f, 
              status: 'error', 
              error: errorMessage 
            }
          : f
      ));

      toast.error(`Erro ao carregar ${fileData.file.name}: ${errorMessage}`);
    }
  };

  const uploadAll = async () => {
    const pendingFiles = files.filter(f => f.status === 'pending');
    if (pendingFiles.length === 0) return;

    setUploading(true);
    
    try {
      // Upload files in parallel (but limit concurrency)
      const uploadPromises = pendingFiles.map(file => uploadFile(file));
      await Promise.all(uploadPromises);
      
      toast.success(`${pendingFiles.length} arquivo(s) carregado(s) com sucesso!`);
    } catch (error) {
      console.error('Batch upload error:', error);
    } finally {
      setUploading(false);
    }
  };

  const clearCompleted = () => {
    setFiles(prev => prev.filter(f => f.status !== 'completed'));
  };

  const retryFailed = () => {
    const failedFiles = files.filter(f => f.status === 'error');
    failedFiles.forEach(file => {
      uploadFile(file);
    });
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <Check className="w-4 h-4 text-green-600" />;
      case 'error':
        return <AlertCircle className="w-4 h-4 text-red-600" />;
      case 'uploading':
        return <div className="spinner w-4 h-4" />;
      default:
        return <FileText className="w-4 h-4 text-gray-400" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed':
        return 'text-green-600';
      case 'error':
        return 'text-red-600';
      case 'uploading':
        return 'text-blue-600';
      default:
        return 'text-gray-600';
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'completed':
        return 'Concluído';
      case 'error':
        return 'Erro';
      case 'uploading':
        return 'Carregando...';
      default:
        return 'Pendente';
    }
  };

  const pendingCount = files.filter(f => f.status === 'pending').length;
  const completedCount = files.filter(f => f.status === 'completed').length;
  const errorCount = files.filter(f => f.status === 'error').length;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Upload de Documentos</h1>
        <p className="text-gray-600 mt-1">
          Envie seus arquivos PDF para processamento no pipeline
        </p>
      </div>

      {/* Upload Area */}
      <div className="card">
        <div
          {...getRootProps()}
          className={`dropzone ${
            isDragActive ? 'dropzone-active' : ''
          } cursor-pointer`}
        >
          <input {...getInputProps()} />
          
          <div className="text-center">
            <UploadIcon className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            
            {isDragActive ? (
              <div>
                <p className="text-lg font-medium text-primary-600">
                  Solte os arquivos aqui
                </p>
                <p className="text-sm text-gray-500 mt-1">
                  Os arquivos serão adicionados à fila de upload
                </p>
              </div>
            ) : (
              <div>
                <p className="text-lg font-medium text-gray-900">
                  Arraste e solte seus arquivos PDF aqui
                </p>
                <p className="text-sm text-gray-500 mt-1">
                  ou <span className="text-primary-600 font-medium">clique para selecionar</span>
                </p>
                <p className="text-xs text-gray-400 mt-2">
                  Máximo 50MB por arquivo • Apenas arquivos PDF
                </p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Upload Controls */}
      {files.length > 0 && (
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-lg font-medium text-gray-900">
                Fila de Upload ({files.length})
              </h3>
              <div className="flex items-center space-x-4 text-sm text-gray-500 mt-1">
                {pendingCount > 0 && <span>{pendingCount} pendente(s)</span>}
                {completedCount > 0 && <span>{completedCount} concluído(s)</span>}
                {errorCount > 0 && <span>{errorCount} com erro</span>}
              </div>
            </div>
            
            <div className="flex items-center space-x-2">
              {errorCount > 0 && (
                <button
                  onClick={retryFailed}
                  className="btn-secondary text-sm"
                  disabled={uploading}
                >
                  Tentar Novamente
                </button>
              )}
              
              {completedCount > 0 && (
                <button
                  onClick={clearCompleted}
                  className="btn-secondary text-sm"
                  disabled={uploading}
                >
                  Limpar Concluídos
                </button>
              )}
              
              {pendingCount > 0 && (
                <button
                  onClick={uploadAll}
                  className="btn-primary text-sm"
                  disabled={uploading}
                >
                  {uploading ? 'Carregando...' : `Carregar ${pendingCount} arquivo(s)`}
                </button>
              )}
            </div>
          </div>

          {/* File List */}
          <div className="space-y-3">
            {files.map((fileData) => (
              <div key={fileData.id} className="flex items-center space-x-4 p-3 border border-gray-200 rounded-lg">
                <div className="flex-shrink-0">
                  {getStatusIcon(fileData.status)}
                </div>
                
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-900 truncate">
                        {fileData.file.name}
                      </p>
                      <div className="flex items-center space-x-2 text-xs text-gray-500">
                        <span>{apiUtils.formatFileSize(fileData.file.size)}</span>
                        <span>•</span>
                        <span className={getStatusColor(fileData.status)}>
                          {getStatusText(fileData.status)}
                        </span>
                        {fileData.jobId && (
                          <>
                            <span>•</span>
                            <span>Job: {fileData.jobId.slice(0, 8)}...</span>
                          </>
                        )}
                      </div>
                    </div>
                    
                    <div className="flex items-center space-x-2">
                      {fileData.status === 'uploading' && (
                        <span className="text-xs text-gray-500">
                          {fileData.progress}%
                        </span>
                      )}
                      
                      {fileData.status !== 'uploading' && (
                        <button
                          onClick={() => removeFile(fileData.id)}
                          className="p-1 text-gray-400 hover:text-gray-600"
                        >
                          <X className="w-4 h-4" />
                        </button>
                      )}
                    </div>
                  </div>
                  
                  {/* Progress Bar */}
                  {fileData.status === 'uploading' && (
                    <div className="w-full bg-gray-200 rounded-full h-1.5 mt-2">
                      <div 
                        className="bg-primary-500 h-1.5 rounded-full transition-all duration-300"
                        style={{ width: `${fileData.progress}%` }}
                      />
                    </div>
                  )}
                  
                  {/* Error Message */}
                  {fileData.status === 'error' && fileData.error && (
                    <p className="text-xs text-red-600 mt-1">
                      {fileData.error}
                    </p>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Upload Tips */}
      <div className="card bg-blue-50 border-blue-200">
        <h3 className="text-sm font-medium text-blue-900 mb-2">
          Dicas para um upload bem-sucedido:
        </h3>
        <ul className="text-sm text-blue-800 space-y-1">
          <li>• Certifique-se de que os arquivos são PDFs válidos</li>
          <li>• Arquivos com OCR já aplicado processam mais rapidamente</li>
          <li>• Evite PDFs protegidos por senha</li>
          <li>• Para melhor performance, limite uploads a 10 arquivos por vez</li>
        </ul>
      </div>
    </div>
  );
}

export default Upload; 