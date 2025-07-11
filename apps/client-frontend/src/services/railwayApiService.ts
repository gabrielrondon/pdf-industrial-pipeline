/**
 * Service para usar nossa API Railway em vez do Supabase diretamente
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://pdf-industrial-pipeline-production.up.railway.app';

export interface UploadResponse {
  success: boolean;
  job_id?: string;
  message?: string;
  error?: string;
}

export interface JobStatus {
  job_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress?: number;
  results?: any;
  error?: string;
}

class RailwayApiService {
  async makeRequest(endpoint: string, options: RequestInit = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    
    try {
      const response = await fetch(url, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        ...options,
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Railway API Error:', error);
      throw error;
    }
  }

  /**
   * Faz upload de um arquivo PDF para nossa API Railway
   */
  async uploadDocument(file: File): Promise<UploadResponse> {
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/upload`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.message || `Upload failed: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Upload error:', error);
      throw error;
    }
  }

  /**
   * Verifica o status de um job de processamento
   */
  async getJobStatus(jobId: string): Promise<JobStatus> {
    return this.makeRequest(`/api/v1/jobs/${jobId}`);
  }

  /**
   * Lista todos os jobs/documentos do usuário
   */
  async getJobs(): Promise<any[]> {
    return this.makeRequest('/api/v1/jobs');
  }

  /**
   * Testa conectividade com a API
   */
  async healthCheck(): Promise<any> {
    return this.makeRequest('/health');
  }

  /**
   * Testa conexão com o banco de dados
   */
  async testDatabase(): Promise<any> {
    return this.makeRequest('/test-db');
  }
}

export const railwayApi = new RailwayApiService();
export default railwayApi;