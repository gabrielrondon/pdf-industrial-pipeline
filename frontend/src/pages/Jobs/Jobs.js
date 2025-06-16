import React from 'react';
import { Briefcase, Clock, CheckCircle, XCircle } from 'lucide-react';

function Jobs() {
  const sampleJobs = [
    { id: 'job-001', name: 'documento-contrato.pdf', status: 'completed', progress: 100, duration: '2m 15s' },
    { id: 'job-002', name: 'relatorio-vendas.pdf', status: 'processing', progress: 65, duration: '1m 30s' },
    { id: 'job-003', name: 'manual-usuario.pdf', status: 'queued', progress: 0, duration: '-' },
    { id: 'job-004', name: 'proposta-comercial.pdf', status: 'failed', progress: 0, duration: '45s' },
  ];

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-green-600" />;
      case 'processing':
        return <div className="spinner w-4 h-4" />;
      case 'failed':
        return <XCircle className="w-4 h-4 text-red-600" />;
      default:
        return <Clock className="w-4 h-4 text-gray-400" />;
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'completed':
        return 'Concluído';
      case 'processing':
        return 'Processando';
      case 'failed':
        return 'Falhou';
      default:
        return 'Na Fila';
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed':
        return 'text-green-600';
      case 'processing':
        return 'text-blue-600';
      case 'failed':
        return 'text-red-600';
      default:
        return 'text-gray-600';
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Gerenciamento de Jobs</h1>
        <p className="text-gray-600 mt-1">Monitore o progresso dos documentos no pipeline</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">{sampleJobs.length}</p>
            </div>
            <Briefcase className="w-6 h-6 text-gray-400" />
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Em Processamento</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">
                {sampleJobs.filter(j => j.status === 'processing').length}
              </p>
            </div>
            <div className="spinner w-6 h-6" />
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Concluídos</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">
                {sampleJobs.filter(j => j.status === 'completed').length}
              </p>
            </div>
            <CheckCircle className="w-6 h-6 text-green-600" />
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Falhas</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">
                {sampleJobs.filter(j => j.status === 'failed').length}
              </p>
            </div>
            <XCircle className="w-6 h-6 text-red-600" />
          </div>
        </div>
      </div>

      <div className="card">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Jobs Recentes</h3>
        <div className="space-y-3">
          {sampleJobs.map((job) => (
            <div key={job.id} className="flex items-center justify-between p-3 border border-gray-200 rounded-lg">
              <div className="flex items-center space-x-3">
                {getStatusIcon(job.status)}
                <div>
                  <p className="text-sm font-medium text-gray-900">{job.name}</p>
                  <p className="text-xs text-gray-500">ID: {job.id}</p>
                </div>
              </div>
              
              <div className="flex items-center space-x-4">
                <div className="text-right">
                  <p className={`text-sm font-medium ${getStatusColor(job.status)}`}>
                    {getStatusText(job.status)}
                  </p>
                  <p className="text-xs text-gray-500">Duração: {job.duration}</p>
                </div>
                
                {job.status === 'processing' && (
                  <div className="w-24">
                    <div className="flex items-center justify-between text-xs text-gray-500 mb-1">
                      <span>{job.progress}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${job.progress}%` }}
                      />
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default Jobs; 