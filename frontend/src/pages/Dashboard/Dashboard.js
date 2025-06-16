import React, { useState, useEffect } from 'react';
import { 
  Activity, 
  FileText, 
  Zap, 
  TrendingUp, 
  Clock,
  CheckCircle,
  XCircle,
  AlertCircle,
  Users,
  Database,
  Cpu,
  HardDrive
} from 'lucide-react';
import { useApp } from '../../contexts/AppContext';
import { apiService } from '../../services/api';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';

// Sample data for charts
const performanceData = [
  { time: '00:00', cpu: 45, memory: 62, cache: 23 },
  { time: '04:00', cpu: 52, memory: 58, cache: 34 },
  { time: '08:00', cpu: 78, memory: 74, cache: 67 },
  { time: '12:00', cpu: 65, memory: 69, cache: 45 },
  { time: '16:00', cpu: 72, memory: 71, cache: 52 },
  { time: '20:00', cpu: 58, memory: 63, cache: 38 },
];

const jobStatusData = [
  { name: 'Concluídos', value: 156, color: '#10b981' },
  { name: 'Em Processamento', value: 23, color: '#3b82f6' },
  { name: 'Falharam', value: 8, color: '#ef4444' },
  { name: 'Na Fila', value: 12, color: '#f59e0b' },
];

const stageData = [
  { stage: 'PDF Split', processed: 145, errors: 2 },
  { stage: 'OCR', processed: 134, errors: 3 },
  { stage: 'Text Analysis', processed: 128, errors: 1 },
  { stage: 'Embeddings', processed: 125, errors: 0 },
  { stage: 'ML Analysis', processed: 123, errors: 2 },
];

function MetricCard({ title, value, subtitle, icon: Icon, color = 'primary', trend = null }) {
  const colorClasses = {
    primary: 'bg-primary-50 text-primary-600',
    success: 'bg-success-50 text-success-600',
    warning: 'bg-warning-50 text-warning-600',
    danger: 'bg-danger-50 text-danger-600',
  };

  return (
    <div className="card">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-2xl font-bold text-gray-900 mt-1">{value}</p>
          {subtitle && (
            <p className="text-sm text-gray-500 mt-1">{subtitle}</p>
          )}
          {trend && (
            <div className={`flex items-center mt-2 text-xs ${
              trend > 0 ? 'text-green-600' : 'text-red-600'
            }`}>
              <TrendingUp className="w-3 h-3 mr-1" />
              {trend > 0 ? '+' : ''}{trend}% vs ontem
            </div>
          )}
        </div>
        <div className={`p-3 rounded-lg ${colorClasses[color]}`}>
          <Icon className="w-6 h-6" />
        </div>
      </div>
    </div>
  );
}

function Dashboard() {
  const { state } = useApp();
  const { systemHealth, performanceStats, activeJobs, completedJobs, failedJobs } = state;
  
  const [stats, setStats] = useState({
    totalJobs: 0,
    todayJobs: 0,
    avgProcessingTime: 0,
    successRate: 0,
  });

  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setIsLoading(true);
      
      // Load various statistics
      const [systemStats, processingStats] = await Promise.all([
        apiService.getSystemStats().catch(() => ({})),
        apiService.getProcessingStats().catch(() => ({})),
      ]);

      setStats({
        totalJobs: completedJobs.length + activeJobs.length + failedJobs.length,
        todayJobs: 23, // Sample data
        avgProcessingTime: 1.2, // Sample data in minutes
        successRate: completedJobs.length > 0 ? 
          (completedJobs.length / (completedJobs.length + failedJobs.length) * 100).toFixed(1) : 
          0,
      });
    } catch (error) {
      console.error('Error loading dashboard data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="spinner w-8 h-8" />
        <span className="ml-3 text-gray-600">Carregando dashboard...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-1">Visão geral do sistema PDF Industrial Pipeline</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total de Jobs</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">156</p>
            </div>
            <div className="p-3 rounded-lg bg-primary-50 text-primary-600">
              <FileText className="w-6 h-6" />
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Jobs Ativos</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">23</p>
            </div>
            <div className="p-3 rounded-lg bg-success-50 text-success-600">
              <Activity className="w-6 h-6" />
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Tempo Médio</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">1.2min</p>
            </div>
            <div className="p-3 rounded-lg bg-warning-50 text-warning-600">
              <Clock className="w-6 h-6" />
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Taxa de Sucesso</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">94.5%</p>
            </div>
            <div className="p-3 rounded-lg bg-success-50 text-success-600">
              <CheckCircle className="w-6 h-6" />
            </div>
          </div>
        </div>
      </div>

      <div className="card">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Status do Sistema</h3>
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-gray-700">PDF Splitting</span>
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-green-400 rounded-full" />
              <span className="text-sm text-gray-600">Ativo</span>
            </div>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-gray-700">OCR Processing</span>
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-green-400 rounded-full" />
              <span className="text-sm text-gray-600">Ativo</span>
            </div>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-gray-700">Text Analysis</span>
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-green-400 rounded-full" />
              <span className="text-sm text-gray-600">Ativo</span>
            </div>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-gray-700">ML Embeddings</span>
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-green-400 rounded-full" />
              <span className="text-sm text-gray-600">Ativo</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard; 