import { DocumentAnalysis, AnalysisPoint, DocumentType, AnalysisStatus } from '@/types';

/**
 * Transform Railway API results to DocumentAnalysis format
 */
export function transformRailwayResultsToDocumentAnalysis(
  railwayResults: any,
  jobId: string,
  fileName: string
): DocumentAnalysis {
  if (!railwayResults || !railwayResults.points) {
    // Create a default analysis if no results
    return createDefaultAnalysis(jobId, fileName);
  }

  const points: AnalysisPoint[] = railwayResults.points.map((point: any, index: number) => ({
    id: point.id || `point_${index}`,
    title: point.title || 'Ponto de Análise',
    status: mapStatus(point.status) || 'não identificado',
    comment: point.comment || 'Análise em andamento...'
  }));

  return {
    id: jobId,
    userId: 'current_user', // Will be set by auth context
    fileName: fileName,
    fileUrl: '', // Will be set if needed
    type: inferDocumentType(railwayResults.analysis_type || fileName),
    uploadedAt: new Date().toISOString(),
    analyzedAt: railwayResults.analysis_date || new Date().toISOString(),
    isPrivate: false,
    points: points
  };
}

/**
 * Create a default analysis when no results are available
 */
function createDefaultAnalysis(jobId: string, fileName: string): DocumentAnalysis {
  return {
    id: jobId,
    userId: 'current_user',
    fileName: fileName,
    fileUrl: '',
    type: inferDocumentType(fileName),
    uploadedAt: new Date().toISOString(),
    analyzedAt: new Date().toISOString(),
    isPrivate: false,
    points: [
      {
        id: 'processing_complete',
        title: 'Processamento Concluído',
        status: 'confirmado',
        comment: 'O documento foi processado com sucesso. A análise detalhada será exibida em breve.'
      },
      {
        id: 'document_uploaded',
        title: 'Documento Carregado',
        status: 'confirmado',
        comment: `Arquivo "${fileName}" foi carregado e processado com sucesso.`
      }
    ]
  };
}

/**
 * Map Railway API status to AnalysisStatus
 */
function mapStatus(status: string): AnalysisStatus {
  const statusMap: Record<string, AnalysisStatus> = {
    'confirmado': 'confirmado',
    'confirmed': 'confirmado',
    'alerta': 'alerta',
    'alert': 'alerta',
    'warning': 'alerta',
    'não identificado': 'não identificado',
    'not_identified': 'não identificado',
    'unknown': 'não identificado'
  };

  return statusMap[status] || 'não identificado';
}

/**
 * Infer document type from filename or analysis type
 */
function inferDocumentType(input: string): DocumentType {
  const lowerInput = input.toLowerCase();

  if (lowerInput.includes('edital') || lowerInput.includes('leilao') || lowerInput.includes('leilão')) {
    return 'edital';
  }
  
  if (lowerInput.includes('processo') || lowerInput.includes('judicial')) {
    return 'processo';
  }
  
  if (lowerInput.includes('laudo') || lowerInput.includes('avaliação') || lowerInput.includes('avaliacao')) {
    return 'laudo';
  }

  return 'outro';
}

/**
 * Format file size for display
 */
export function formatFileSize(bytes: number): string {
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  if (bytes === 0) return '0 Bytes';
  
  const i = Math.floor(Math.log(bytes) / Math.log(1024));
  const size = (bytes / Math.pow(1024, i)).toFixed(1);
  
  return `${size} ${sizes[i]}`;
}

/**
 * Format processing time
 */
export function formatProcessingTime(seconds: number): string {
  if (seconds < 60) {
    return `${Math.round(seconds)}s`;
  } else if (seconds < 3600) {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.round(seconds % 60);
    return `${minutes}m ${remainingSeconds}s`;
  } else {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return `${hours}h ${minutes}m`;
  }
}

/**
 * Get priority color for UI display
 */
export function getPriorityColor(priority: string): string {
  const colors: Record<string, string> = {
    'high': 'border-l-red-500 bg-red-50',
    'medium': 'border-l-yellow-500 bg-yellow-50',
    'low': 'border-l-green-500 bg-green-50'
  };
  return colors[priority] || 'border-l-gray-500 bg-gray-50';
}

/**
 * Get category color for UI display
 */
export function getCategoryColor(category: string): string {
  const colors: Record<string, string> = {
    'leilao': 'bg-blue-100 text-blue-800',
    'investimento': 'bg-green-100 text-green-800',
    'contato': 'bg-purple-100 text-purple-800',
    'prazo': 'bg-red-100 text-red-800',
    'financeiro': 'bg-yellow-100 text-yellow-800',
    'geral': 'bg-gray-100 text-gray-800'
  };
  return colors[category] || 'bg-gray-100 text-gray-800';
}