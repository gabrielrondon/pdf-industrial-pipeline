
import { useEffect, useState } from 'react';
import { useDocuments } from '@/contexts/DocumentContext';
import { useAuth } from '@/contexts/AuthContext';
import { DashboardStats as StatsType } from '@/types';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { BarChart, PieChart, FileText, TrendingUp, Users, Database } from 'lucide-react';
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
  Cell
} from 'recharts';

export function DashboardStats() {
  const { getStats, isLoading } = useDocuments();
  const { user } = useAuth();
  const [stats, setStats] = useState<StatsType | null>(null);
  const [error, setError] = useState<string | null>(null);
  
  useEffect(() => {
    const loadStats = async () => {
      if (!user?.id) {
        console.log('👤 DashboardStats: aguardando user.id...');
        return;
      }
      
      console.log('📊 DashboardStats: carregando stats para user:', user.id);
      
      try {
        const data = await getStats();
        console.log('📊 DashboardStats: stats carregadas:', data);
        setStats(data);
        setError(null);
      } catch (err) {
        console.error('❌ DashboardStats: erro ao carregar stats:', err);
        setError('Não foi possível carregar as estatísticas.');
        
        // Fallback para stats mínimas para não deixar vazio
        setStats({
          totalAnalyses: 0,
          validLeads: 0,
          sharedLeads: 0,
          credits: 100,
          documentTypes: [],
          statusDistribution: [],
          commonIssues: [],
          monthlyAnalyses: [],
          successRate: 0,
          averageProcessingTime: 0,
          totalFileSize: 0,
          averageConfidence: 0,
          topPerformingDocumentType: 'edital'
        });
      }
    };
    
    loadStats();
  }, [getStats, user?.id]);
  
  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {Array.from({ length: 4 }).map((_, i) => (
          <Card key={i} className="animate-pulse">
            <CardHeader className="pb-2">
              <div className="h-4 w-24 bg-muted rounded"></div>
            </CardHeader>
            <CardContent>
              <div className="h-7 w-16 bg-muted rounded"></div>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }
  
  if (!stats) {
    return (
      <div className="text-center p-12">
        <Database className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
        <p className="text-muted-foreground">
          {error || 'Nenhuma estatística disponível. Faça sua primeira análise para ver os dados aqui.'}
        </p>
      </div>
    );
  }
  
  // Format document type data for pie chart
  const documentTypeData = stats.documentTypes.map(item => ({
    name: item.type === 'edital' ? 'Editais' : 
          item.type === 'processo' ? 'Processos' : 
          item.type === 'laudo' ? 'Laudos' : 'Outros',
    value: item.count
  }));
  
  // Format status data for bar chart
  const statusData = stats.statusDistribution.map(item => ({
    name: item.status === 'confirmado' ? 'Confirmados' : 
          item.status === 'alerta' ? 'Alertas' : 'Não identificados',
    value: item.count
  }));
  
  // Colors for charts
  const COLORS = ['#3730a3', '#8b5cf6', '#c084fc', '#ddd6fe'];
  const STATUS_COLORS = {
    'Confirmados': '#22c55e',
    'Alertas': '#f59e0b',
    'Não identificados': '#6b7280'
  };
  
  const conversionRate = stats.totalAnalyses > 0 ? (stats.validLeads / stats.totalAnalyses) * 100 : 0;
  const shareRate = stats.validLeads > 0 ? (stats.sharedLeads / stats.validLeads) * 100 : 0;
  
  return (
    <div className="space-y-8">
      {/* Stat cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
              <FileText className="h-4 w-4" />
              Total de análises
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalAnalyses}</div>
            <p className="text-xs text-muted-foreground mt-1">
              documentos processados
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
              <TrendingUp className="h-4 w-4" />
              Leads válidos
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.validLeads}</div>
            <div className="mt-2">
              <Progress value={conversionRate} />
              <p className="text-xs text-muted-foreground mt-1">
                {conversionRate.toFixed(1)}% de conversão
              </p>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
              <Users className="h-4 w-4" />
              Leads compartilhados
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.sharedLeads}</div>
            <div className="mt-2">
              <Progress value={shareRate} />
              <p className="text-xs text-muted-foreground mt-1">
                {shareRate.toFixed(1)}% dos leads válidos
              </p>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
              <Database className="h-4 w-4" />
              Créditos disponíveis
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.credits}</div>
            <p className="text-xs text-muted-foreground mt-1">
              {user?.plan === 'free' ? 'Upgrade para usar IA' : 'créditos para análises IA'}
            </p>
          </CardContent>
        </Card>
      </div>
      
      {/* Charts - only show if there's data */}
      {(documentTypeData.length > 0 || statusData.length > 0) && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {documentTypeData.length > 0 && (
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>Tipos de documento</CardTitle>
                    <CardDescription>
                      Distribuição por tipo de documento
                    </CardDescription>
                  </div>
                  <PieChart className="h-4 w-4 text-muted-foreground" />
                </div>
              </CardHeader>
              <CardContent>
                <div className="h-80">
                  <ResponsiveContainer width="100%" height="100%">
                    <RechartsPieChart>
                      <Pie
                        data={documentTypeData}
                        cx="50%"
                        cy="50%"
                        labelLine={true}
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="value"
                        label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                      >
                        {documentTypeData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip />
                      <Legend />
                    </RechartsPieChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>
          )}
          
          {statusData.length > 0 && (
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>Distribuição de status</CardTitle>
                    <CardDescription>
                      Pontos por status de identificação
                    </CardDescription>
                  </div>
                  <BarChart className="h-4 w-4 text-muted-foreground" />
                </div>
              </CardHeader>
              <CardContent>
                <div className="h-80">
                  <ResponsiveContainer width="100%" height="100%">
                    <RechartsBarChart
                      data={statusData}
                      margin={{
                        top: 20,
                        right: 30,
                        left: 20,
                        bottom: 5,
                      }}
                    >
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="name" />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      <Bar dataKey="value" name="Quantidade">
                        {statusData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={STATUS_COLORS[entry.name] || COLORS[index % COLORS.length]} />
                        ))}
                      </Bar>
                    </RechartsBarChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      )}
      
      {/* Common issues - only show if there are issues */}
      {stats.commonIssues.length > 0 && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Pontos jurídicos mais comuns</CardTitle>
                <CardDescription>
                  Problemas frequentemente identificados nas análises
                </CardDescription>
              </div>
              <FileText className="h-4 w-4 text-muted-foreground" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-6">
              {stats.commonIssues.map((issue, index) => {
                const percentage = stats.totalAnalyses > 0 ? (issue.count / stats.totalAnalyses) * 100 : 0;
                return (
                  <div key={index} className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="font-medium capitalize">{issue.issue}</span>
                      <span className="text-sm text-muted-foreground">
                        {issue.count} ocorrência{issue.count !== 1 ? 's' : ''}
                      </span>
                    </div>
                    <Progress value={percentage} />
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
