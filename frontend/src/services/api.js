import axios from 'axios';

// Create axios instance with default config
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response.data;
  },
  (error) => {
    // Handle common error scenarios
    if (error.response?.status === 401) {
      // Unauthorized - clear token and redirect to login
      localStorage.removeItem('auth_token');
      window.location.href = '/login';
    } else if (error.response?.status >= 500) {
      // Server error
      console.error('Server error:', error.response?.data);
    } else if (error.code === 'ECONNABORTED') {
      // Request timeout
      console.error('Request timeout');
    } else if (!error.response) {
      // Network error
      console.error('Network error:', error.message);
    }
    
    return Promise.reject(error);
  }
);

// API Service methods
export const apiService = {
  // Health & Status
  async getHealth() {
    return api.get('/health');
  },

  async getSystemHealth() {
    return api.get('/performance/system/health');
  },

  // Performance & Analytics
  async getCacheStats() {
    return api.get('/performance/cache/stats');
  },

  async clearCache() {
    return api.delete('/performance/cache/clear');
  },

  async getParallelStats() {
    return api.get('/performance/parallel/stats');
  },

  async getMetricsStats() {
    return api.get('/performance/metrics/stats');
  },

  async getAnalytics() {
    return api.get('/performance/analytics');
  },

  async benchmarkEndpoint(endpointName, iterations = 10) {
    return api.get(`/performance/benchmark/${endpointName}`, {
      params: { iterations }
    });
  },

  // Job Management
  async uploadFile(file, onUploadProgress) {
    const formData = new FormData();
    formData.append('file', file);

    return api.post('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress,
    });
  },

  async getJobStatus(jobId) {
    return api.get(`/job-status/${jobId}`);
  },

  async getJobResults(jobId) {
    return api.get(`/job-results/${jobId}`);
  },

  async cancelJob(jobId) {
    return api.post(`/jobs/${jobId}/cancel`);
  },

  async deleteJob(jobId) {
    return api.delete(`/jobs/${jobId}`);
  },

  async retryJob(jobId) {
    return api.post(`/jobs/${jobId}/retry`);
  },

  // Stage-specific operations
  async processOcr(jobId) {
    return api.post(`/process-ocr/${jobId}`);
  },

  async processText(jobId) {
    return api.post(`/process-text/${jobId}`);
  },

  async generateEmbeddings(jobId) {
    return api.post(`/generate-embeddings/${jobId}`);
  },

  async runMlAnalysis(jobId) {
    return api.post(`/ml-analysis/${jobId}`);
  },

  // Search & Query
  async searchEmbeddings(query, limit = 10) {
    return api.post('/search-embeddings', { query, limit });
  },

  async searchSimilar(jobId, threshold = 0.8) {
    return api.post('/search-similar', { job_id: jobId, threshold });
  },

  // ML & Predictions
  async predictLead(features) {
    return api.post('/ml/predict-lead', { features });
  },

  async getModelPerformance() {
    return api.get('/ml/model-performance');
  },

  async retrainModel(modelType = 'lead_scoring') {
    return api.post('/ml/retrain', { model_type: modelType });
  },

  // Statistics & Reports
  async getEmbeddingStats() {
    return api.get('/embeddings/stats');
  },

  async getTextStats() {
    return api.get('/text/stats');
  },

  async getProcessingStats() {
    return api.get('/processing/stats');
  },

  async getSystemStats() {
    return api.get('/stats');
  },

  // Bulk Operations
  async bulkUpload(files, onUploadProgress) {
    const formData = new FormData();
    files.forEach((file, index) => {
      formData.append(`files`, file);
    });

    return api.post('/bulk-upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress,
    });
  },

  async bulkProcess(jobIds, operation) {
    return api.post('/bulk-process', {
      job_ids: jobIds,
      operation,
    });
  },

  // Export & Download
  async exportResults(jobId, format = 'json') {
    return api.get(`/export/${jobId}`, {
      params: { format },
      responseType: format === 'pdf' ? 'blob' : 'json',
    });
  },

  async downloadFile(jobId, fileType) {
    return api.get(`/download/${jobId}/${fileType}`, {
      responseType: 'blob',
    });
  },

  // Configuration
  async getConfig() {
    return api.get('/config');
  },

  async updateConfig(config) {
    return api.put('/config', config);
  },

  // User Management (Basic)
  async login(credentials) {
    const response = await api.post('/auth/login', credentials);
    if (response.token) {
      localStorage.setItem('auth_token', response.token);
    }
    return response;
  },

  async logout() {
    localStorage.removeItem('auth_token');
    return api.post('/auth/logout');
  },

  async getCurrentUser() {
    return api.get('/auth/me');
  },

  // Notifications
  async getNotifications() {
    return api.get('/notifications');
  },

  async markNotificationRead(notificationId) {
    return api.put(`/notifications/${notificationId}/read`);
  },

  async clearNotifications() {
    return api.delete('/notifications');
  },
};

// Utility functions
export const apiUtils = {
  // Handle file download
  downloadBlob(blob, filename) {
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  },

  // Format file size
  formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  },

  // Format duration
  formatDuration(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);
    
    if (hours > 0) {
      return `${hours}h ${minutes}m ${secs}s`;
    } else if (minutes > 0) {
      return `${minutes}m ${secs}s`;
    } else {
      return `${secs}s`;
    }
  },

  // Check if error is network related
  isNetworkError(error) {
    return !error.response && error.code !== 'ECONNABORTED';
  },

  // Get error message
  getErrorMessage(error) {
    if (error.response?.data?.message) {
      return error.response.data.message;
    } else if (error.response?.data?.detail) {
      return error.response.data.detail;
    } else if (error.message) {
      return error.message;
    } else {
      return 'Erro desconhecido';
    }
  },
};

export default api; 