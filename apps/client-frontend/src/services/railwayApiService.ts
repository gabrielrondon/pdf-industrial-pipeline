/**
 * Service para usar nossa API Railway em vez do Supabase diretamente
 */

import { supabase } from '@/integrations/supabase/client';

// Remove /api/v1 from VITE_API_BASE_URL as we'll add it per endpoint
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL?.replace('/api/v1', '') || 'https://pdf-industrial-pipeline-production.up.railway.app';

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
  private async getAuthHeaders(): Promise<Record<string, string>> {
    try {
      // Get current user session
      const { data: { session } } = await supabase.auth.getSession();
      
      if (session?.access_token) {
        return {
          'Authorization': `Bearer ${session.access_token}`,
        };
      }
      
      console.warn('⚠️ No authentication token available for Railway API');
      return {};
    } catch (error) {
      console.error('❌ Error getting auth headers:', error);
      return {};
    }
  }

  async makeRequest(endpoint: string, options: RequestInit = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const authHeaders = await this.getAuthHeaders();
    
    console.log(`🚀 Making request to: ${url}`);
    console.log(`🔐 Auth headers present:`, Object.keys(authHeaders));
    
    try {
      const startTime = performance.now();
      const response = await fetch(url, {
        headers: {
          'Content-Type': 'application/json',
          ...authHeaders,
          ...options.headers,
        },
        ...options,
      });
      
      const endTime = performance.now();
      console.log(`⏱️ Request completed in ${(endTime - startTime).toFixed(2)}ms`);

      if (!response.ok) {
        const errorText = await response.text().catch(() => '');
        console.error(`❌ Railway API Error ${response.status}:`, errorText);
        console.error(`❌ Full error details:`, {
          url,
          status: response.status,
          statusText: response.statusText,
          errorText
        });
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
  async uploadDocument(file: File, userId?: string): Promise<UploadResponse> {
    const formData = new FormData();
    formData.append('file', file);
    
    // Add user ID if provided
    if (userId) {
      formData.append('user_id', userId);
    }
    
    try {
      const authHeaders = await this.getAuthHeaders();
      
      const response = await fetch(`${API_BASE_URL}/api/v1/upload`, {
        method: 'POST',
        body: formData,
        headers: {
          ...authHeaders,
          // Don't set Content-Type header - let the browser set it with boundary for multipart/form-data
        },
        // Increase timeout for large files (5 minutes)
        signal: AbortSignal.timeout(300000)
      });

      if (!response.ok) {
        const errorText = await response.text().catch(() => '');
        console.error(`❌ Upload Error ${response.status}:`, errorText);
        
        try {
          const errorData = JSON.parse(errorText);
          // Handle HTTPException detail format from FastAPI
          if (errorData.detail && typeof errorData.detail === 'object') {
            throw new Error(errorData.detail.message || errorData.detail.error || `Upload failed: ${response.status}`);
          }
          throw new Error(errorData.message || errorData.error || errorData.detail || `Upload failed: ${response.status}`);
        } catch (parseError) {
          throw new Error(`Upload failed: ${response.status} ${response.statusText}${errorText ? ` - ${errorText}` : ''}`);
        }
      }

      const result = await response.json();
      console.log('✅ Upload successful:', result);
      return result;
    } catch (error) {
      console.error('❌ Upload error:', error);
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
  async getJobs(userId?: string): Promise<any[]> {
    try {
      // CRITICAL: Pass user_id as query parameter
      const url = userId ? `/api/v1/jobs?user_id=${encodeURIComponent(userId)}` : '/api/v1/jobs';
      console.log(`📡 Calling Railway API: ${url}`);
      
      const response = await this.makeRequest(url);
      console.log('📡 Railway API response for getJobs:', response);
      
      // The API returns { jobs: [...], total: number, skip: number, limit: number }
      if (response.jobs && Array.isArray(response.jobs)) {
        return response.jobs;
      }
      
      // Fallback: if it's already an array
      if (Array.isArray(response)) {
        return response;
      }
      
      console.warn('⚠️ Unexpected response format from Railway API:', response);
      return [];
    } catch (error) {
      console.error('❌ Error in getJobs:', error);
      throw error;
    }
  }

  /**
   * Atualiza o título de um job/documento
   */
  async updateJobTitle(jobId: string, title: string): Promise<any> {
    return this.makeRequest(`/api/v1/jobs/${jobId}/title`, {
      method: 'PATCH',
      body: JSON.stringify({ title }),
    });
  }

  /**
   * Deleta um job/documento
   */
  async deleteJob(jobId: string): Promise<any> {
    return this.makeRequest(`/api/v1/jobs/${jobId}`, {
      method: 'DELETE',
    });
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
    return this.makeRequest('/health');
  }

  /**
   * Busca estatísticas do dashboard
   */
  async getDashboardStats(): Promise<any> {
    try {
      const response = await this.makeRequest('/api/v1/jobs/stats/dashboard');
      console.log('📊 Dashboard stats from Railway:', response);
      return response;
    } catch (error) {
      console.error('❌ Error getting dashboard stats:', error);
      throw error;
    }
  }

  /**
   * Busca conteúdo de uma página específica do documento
   */
  async getPageContent(jobId: string, pageNumber: number): Promise<any> {
    try {
      const response = await this.makeRequest(`/api/v1/jobs/${jobId}/page/${pageNumber}`);
      console.log(`📄 Page ${pageNumber} content for job ${jobId}:`, response);
      return response;
    } catch (error) {
      console.error(`❌ Error getting page ${pageNumber} for job ${jobId}:`, error);
      throw error;
    }
  }
}

export const railwayApi = new RailwayApiService();
export default railwayApi;