import { useEffect, useState } from 'react';
import { useDocuments } from '@/contexts/DocumentContext';
import { useAuth } from '@/contexts/AuthContext';
import { DashboardStats as StatsType } from '@/types';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { 
  BarChart, 
  PieChart, 
  FileText, 
  TrendingUp, 
  Users, 
  Database,
  RefreshCw,
  Target,
  Award,
  Calendar,
  AlertTriangle,
  CheckCircle,
  DollarSign,
  Activity
} from 'lucide-react';
import { 
  BarChart as RechartsBarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend,
  ResponsiveContainer,
  PieChart as RechartsPieChart,
  Pie,
  Cell,
  LineChart,
  Line,
  Area,
  AreaChart
} from 'recharts';

export default function StatsPage() {
  const { getStats, isLoading, documents } = useDocuments();
  const { user } = useAuth();
  const [stats, setStats] = useState<StatsType | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);
  
  const loadStats = async () => {
    if (!user?.id) return;
    
    setRefreshing(true);
    try {
      const data = await getStats();
      setStats(data);
      setError(null);
    } catch (err) {
      setError('Não foi possível carregar as estatísticas.');
      console.error(err);
    } finally {
      setRefreshing(false);
    }
  };
  
  useEffect(() => {
    loadStats();
  }, [getStats, user?.id]);

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

  // Calculate additional metrics
  const successRate = stats ? (stats.validLeads / Math.max(stats.totalAnalyses, 1)) * 100 : 0;
  const shareRate = stats ? (stats.sharedLeads / Math.max(stats.totalAnalyses, 1)) * 100 : 0;
  
  // Calculate recent activity (last 7 days)
  const recentDocuments = documents.filter(doc => {
    const docDate = new Date(doc.analyzedAt);
    const weekAgo = new Date();
    weekAgo.setDate(weekAgo.getDate() - 7);
    return docDate >= weekAgo;
  });

  const getDocumentTypeLabel = (type: string): string => {
    const types: Record<string, string> = {
      'edital': 'Editais de Leilão',
      'processo': 'Processos Judiciais',
      'laudo': 'Laudos Técnicos',
      'outro': 'Outros Documentos'
    };
    return types[type] || 'Outros';
  };

  const getStatusLabel = (status: string): string => {
    const statuses: Record<string, string> = {
      'confirmado': 'Leads Confirmados',
      'alerta': 'Leads com Alerta',
      'não identificado': 'Não Identificados'
    };
    return statuses[status] || status;
  };

  if (isLoading && !stats) {
    return (
      <div className="container mx-auto p-6 space-y-6">
        <div className="flex items-center justify-between">
          <div className="space-y-1">
            <h1 className="text-3xl font-bold">Estatísticas</h1>
            <p className="text-muted-foreground">
              Análise detalhada do seu desempenho e atividade
            </p>
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {Array.from({ length: 8 }).map((_, i) => (
            <Card key={i} className="animate-pulse">
              <CardContent className="p-6">
                <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                <div className="h-8 bg-gray-200 rounded w-1/2"></div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto p-6">
        <Card>
          <CardContent className="p-6 text-center">
            <AlertTriangle className="h-12 w-12 text-red-500 mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">Erro ao carregar estatísticas</h3>
            <p className="text-muted-foreground mb-4">{error}</p>
            <Button onClick={loadStats} disabled={refreshing}>
              <RefreshCw className={`h-4 w-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
              Tentar novamente
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="space-y-1">
          <h1 className="text-3xl font-bold">Estatísticas</h1>
          <p className="text-muted-foreground">
            Análise detalhada do seu desempenho e atividade
          </p>
        </div>
        <Button onClick={loadStats} disabled={refreshing} variant="outline">
          <RefreshCw className={`h-4 w-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
          Atualizar
        </Button>
      </div>

      {/* Main Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Total de Análises</p>
                <p className="text-2xl font-bold">{stats?.totalAnalyses || 0}</p>
              </div>
              <FileText className="h-8 w-8 text-blue-500" />
            </div>
            <div className="mt-4">
              <p className="text-xs text-muted-foreground">
                {recentDocuments.length} nos últimos 7 dias
              </p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Leads Válidos</p>
                <p className="text-2xl font-bold text-green-600">{stats?.validLeads || 0}</p>
              </div>
              <CheckCircle className="h-8 w-8 text-green-500" />
            </div>
            <div className="mt-4">
              <Progress value={successRate} className="h-2" />
              <p className="text-xs text-muted-foreground mt-1">
                {successRate.toFixed(1)}% taxa de sucesso
              </p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Leads Compartilhados</p>
                <p className="text-2xl font-bold text-purple-600">{stats?.sharedLeads || 0}</p>
              </div>
              <Users className="h-8 w-8 text-purple-500" />
            </div>
            <div className="mt-4">
              <Progress value={shareRate} className="h-2" />
              <p className="text-xs text-muted-foreground mt-1">
                {shareRate.toFixed(1)}% taxa de compartilhamento
              </p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Créditos Disponíveis</p>
                <p className="text-2xl font-bold text-orange-600">{stats?.credits || 0}</p>
              </div>
              <DollarSign className="h-8 w-8 text-orange-500" />
            </div>
            <div className="mt-4">
              <Badge variant="outline" className="text-xs">
                {user?.plan || 'free'} plan
              </Badge>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Document Types Chart */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <BarChart className="h-5 w-5 mr-2" />
              Tipos de Documentos
            </CardTitle>
            <CardDescription>
              Distribuição dos documentos analisados por categoria
            </CardDescription>
          </CardHeader>
          <CardContent>
            {stats?.documentTypes && stats.documentTypes.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <RechartsBarChart data={stats.documentTypes}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="type" 
                    tickFormatter={getDocumentTypeLabel}
                    angle={-45}
                    textAnchor="end"
                    height={80}
                  />
                  <YAxis />
                  <Tooltip 
                    labelFormatter={getDocumentTypeLabel}
                    formatter={(value) => [value, 'Quantidade']}
                  />
                  <Bar dataKey="count" fill="#0088FE" />
                </RechartsBarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-[300px] flex items-center justify-center text-muted-foreground">
                Nenhum dado disponível
              </div>
            )}
          </CardContent>
        </Card>

        {/* Status Distribution Chart */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <PieChart className="h-5 w-5 mr-2" />
              Status dos Leads
            </CardTitle>
            <CardDescription>
              Distribuição dos leads por status de validação
            </CardDescription>
          </CardHeader>
          <CardContent>
            {stats?.statusDistribution && stats.statusDistribution.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <RechartsPieChart>
                  <Pie
                    data={stats.statusDistribution}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ status, count, percent }) => 
                      `${getStatusLabel(status)}: ${count} (${(percent * 100).toFixed(0)}%)`
                    }
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="count"
                  >
                    {stats.statusDistribution.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip 
                    formatter={(value, name) => [value, getStatusLabel(name as string)]}
                  />
                </RechartsPieChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-[300px] flex items-center justify-center text-muted-foreground">
                Nenhum dado disponível
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Additional Insights */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Common Issues */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <AlertTriangle className="h-5 w-5 mr-2" />
              Principais Problemas Identificados
            </CardTitle>
            <CardDescription>
              Os pontos de atenção mais comuns nos documentos analisados
            </CardDescription>
          </CardHeader>
          <CardContent>
            {stats?.commonIssues && stats.commonIssues.length > 0 ? (
              <div className="space-y-3">
                {stats.commonIssues.slice(0, 5).map((issue, index) => (
                  <div key={index} className="flex items-center justify-between p-3 bg-muted/50 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <Badge variant="outline">{index + 1}</Badge>
                      <span className="text-sm font-medium">{issue.issue}</span>
                    </div>
                    <Badge variant="secondary">{issue.count} ocorrências</Badge>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-muted-foreground">
                <AlertTriangle className="h-8 w-8 mx-auto mb-2 opacity-50" />
                <p>Nenhum problema identificado ainda</p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Performance Summary */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Activity className="h-5 w-5 mr-2" />
              Resumo de Performance
            </CardTitle>
            <CardDescription>
              Indicadores-chave do seu desempenho na plataforma
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Taxa de Sucesso</span>
                <div className="flex items-center space-x-2">
                  <Progress value={successRate} className="w-20 h-2" />
                  <span className="text-sm font-bold">{successRate.toFixed(1)}%</span>
                </div>
              </div>
              
              <Separator />
              
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Taxa de Compartilhamento</span>
                <div className="flex items-center space-x-2">
                  <Progress value={shareRate} className="w-20 h-2" />
                  <span className="text-sm font-bold">{shareRate.toFixed(1)}%</span>
                </div>
              </div>
              
              <Separator />
              
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Atividade Recente</span>
                <Badge variant={recentDocuments.length > 0 ? "default" : "secondary"}>
                  {recentDocuments.length > 0 ? `${recentDocuments.length} análises` : 'Nenhuma atividade'}
                </Badge>
              </div>
              
              <Separator />
              
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Plano Atual</span>
                <Badge variant="outline" className="capitalize">
                  {user?.plan || 'free'}
                </Badge>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}