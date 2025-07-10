
import { useState } from 'react';
import { DocumentAnalysis, AnalysisStatus } from '@/types';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Switch } from '@/components/ui/switch';
import { FileText, Download, Share2, Lock, Eye, TrendingUp, AlertTriangle, DollarSign, Calendar } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { useDocuments } from '@/contexts/DocumentContext';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { cn } from '@/lib/utils';

interface AnalysisResultProps {
  analysis: DocumentAnalysis;
}

export function AnalysisResult({ analysis }: AnalysisResultProps) {
  const { user } = useAuth();
  const { toggleDocumentPrivacy, isLoading } = useDocuments();
  const [isPrivate, setIsPrivate] = useState(analysis.isPrivate);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const getDocumentTypeLabel = (type: string): string => {
    const types: Record<string, string> = {
      'edital': 'Edital de Leilão',
      'processo': 'Processo Judicial',
      'laudo': 'Laudo Técnico',
      'outro': 'Outro Documento'
    };
    return types[type] || 'Documento';
  };
  
  const getStatusColor = (status: AnalysisStatus): string => {
    const colors: Record<AnalysisStatus, string> = {
      'confirmado': 'bg-green-100 text-green-800 border-green-300',
      'alerta': 'bg-yellow-100 text-yellow-800 border-yellow-300',
      'não identificado': 'bg-gray-100 text-gray-800 border-gray-300'
    };
    return colors[status] || '';
  };
  
  const getCategoryIcon = (category: string): JSX.Element => {
    switch (category) {
      case 'leilao':
      case 'investimento':
        return <TrendingUp className="h-4 w-4" />;
      case 'prazo':
        return <Calendar className="h-4 w-4" />;
      case 'financeiro':
        return <DollarSign className="h-4 w-4" />;
      default:
        return <AlertTriangle className="h-4 w-4" />;
    }
  };
  
  const getCategoryColor = (category: string): string => {
    const colors: Record<string, string> = {
      'leilao': 'bg-blue-100 text-blue-800',
      'investimento': 'bg-green-100 text-green-800',
      'contato': 'bg-purple-100 text-purple-800',
      'prazo': 'bg-red-100 text-red-800',
      'financeiro': 'bg-yellow-100 text-yellow-800',
      'geral': 'bg-gray-100 text-gray-800'
    };
    return colors[category] || 'bg-gray-100 text-gray-800';
  };
  
  const getPriorityColor = (priority: string): string => {
    const colors: Record<string, string> = {
      'high': 'border-l-red-500 bg-red-50',
      'medium': 'border-l-yellow-500 bg-yellow-50',
      'low': 'border-l-green-500 bg-green-50'
    };
    return colors[priority] || 'border-l-gray-500 bg-gray-50';
  };
  
  const handleTogglePrivacy = async () => {
    if (user?.plan === 'free') {
      setError('Somente usuários Pro e Premium podem alterar a privacidade dos leads.');
      return;
    }
    
    setIsSaving(true);
    setError(null);
    
    try {
      const updatedDoc = await toggleDocumentPrivacy(analysis.id);
      setIsPrivate(updatedDoc.isPrivate);
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('Não foi possível alterar a privacidade do documento.');
      }
    } finally {
      setIsSaving(false);
    }
  };
  
  const canTogglePrivacy = user?.plan !== 'free';
  
  // Agrupar leads por categoria
  const leadsByCategory = analysis.points.reduce((acc, point) => {
    const category = (point as any).category || 'geral';
    if (!acc[category]) {
      acc[category] = [];
    }
    acc[category].push(point);
    return acc;
  }, {} as Record<string, typeof analysis.points>);
  
  // Estatísticas dos leads
  const totalLeads = analysis.points.length;
  const highPriorityLeads = analysis.points.filter(p => (p as any).priority === 'high').length;
  const categories = Object.keys(leadsByCategory);
  
  return (
    <Card className="w-full max-w-4xl mx-auto">
      <CardHeader>
        <div className="flex justify-between items-start">
          <div>
            <Badge className="mb-2">{getDocumentTypeLabel(analysis.type)}</Badge>
            <CardTitle className="text-2xl">{analysis.fileName}</CardTitle>
            <CardDescription>
              Analisado em {new Date(analysis.analyzedAt).toLocaleString('pt-BR')}
            </CardDescription>
          </div>
          <div className="flex items-center space-x-1 text-sm">
            {isPrivate ? (
              <>
                <Lock className="h-4 w-4 text-secondary" />
                <span className="text-secondary font-medium">Privado</span>
              </>
            ) : (
              <>
                <Share2 className="h-4 w-4 text-accent" />
                <span className="text-accent font-medium">Compartilhado</span>
              </>
            )}
          </div>
        </div>
      </CardHeader>
      
      <CardContent className="space-y-6">
        {error && (
          <Alert variant="destructive">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}
        
        {/* Estatísticas dos Leads */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-blue-50 p-4 rounded-lg">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-blue-600">Total de Leads</p>
                <p className="text-2xl font-bold text-blue-900">{totalLeads}</p>
              </div>
              <FileText className="h-8 w-8 text-blue-500" />
            </div>
          </div>
          
          <div className="bg-red-50 p-4 rounded-lg">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-red-600">Alta Prioridade</p>
                <p className="text-2xl font-bold text-red-900">{highPriorityLeads}</p>
              </div>
              <AlertTriangle className="h-8 w-8 text-red-500" />
            </div>
          </div>
          
          <div className="bg-green-50 p-4 rounded-lg">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-green-600">Categorias</p>
                <p className="text-2xl font-bold text-green-900">{categories.length}</p>
              </div>
              <TrendingUp className="h-8 w-8 text-green-500" />
            </div>
          </div>
        </div>

        {/* Leads por Categoria */}
        <div className="space-y-6">
          <h3 className="font-medium text-lg flex items-center">
            <FileText className="h-5 w-5 mr-2 text-primary" />
            Leads e Oportunidades Identificadas
          </h3>
          
          {Object.entries(leadsByCategory).map(([category, leads]) => (
            <div key={category} className="space-y-3">
              <div className="flex items-center gap-2">
                {getCategoryIcon(category)}
                <h4 className="font-medium capitalize">{category}</h4>
                <Badge variant="outline" className={getCategoryColor(category)}>
                  {leads.length} {leads.length === 1 ? 'lead' : 'leads'}
                </Badge>
              </div>
              
              <div className="space-y-3 pl-6">
                {leads.map((point) => (
                  <div 
                    key={point.id} 
                    className={cn(
                      "p-4 rounded-md border-l-4",
                      getPriorityColor((point as any).priority || 'medium'),
                      getStatusColor(point.status)
                    )}
                  >
                    <div className="flex justify-between items-start">
                      <div className="font-medium flex items-center gap-2">
                        {point.title}
                        {(point as any).value && (
                          <Badge variant="outline" className="text-green-700 bg-green-50">
                            {(point as any).value}
                          </Badge>
                        )}
                      </div>
                      <div className="flex gap-2">
                        <Badge variant="outline" className={getCategoryColor(category)}>
                          {category}
                        </Badge>
                        <Badge variant="outline">
                          {point.status}
                        </Badge>
                        {(point as any).priority && (
                          <Badge 
                            variant="outline" 
                            className={
                              (point as any).priority === 'high' ? 'border-red-500 text-red-700' :
                              (point as any).priority === 'medium' ? 'border-yellow-500 text-yellow-700' :
                              'border-green-500 text-green-700'
                            }
                          >
                            {(point as any).priority}
                          </Badge>
                        )}
                      </div>
                    </div>
                    <p className="mt-2 text-sm">{point.comment}</p>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </CardContent>
      
      <CardFooter className="flex justify-between items-center border-t p-6">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <Switch 
              id="privacy-toggle"
              checked={isPrivate}
              onCheckedChange={handleTogglePrivacy}
              disabled={!canTogglePrivacy || isSaving || isLoading}
            />
            <label 
              htmlFor="privacy-toggle" 
              className={cn(
                "text-sm cursor-pointer", 
                canTogglePrivacy ? "" : "text-muted-foreground"
              )}
            >
              Manter privado
            </label>
          </div>
          
          {!canTogglePrivacy && (
            <div className="text-xs text-muted-foreground">
              Disponível nos planos Pro e Premium
            </div>
          )}
        </div>
        
        <div className="flex space-x-2">
          <Button variant="outline" size="sm">
            <Eye className="h-4 w-4 mr-1" />
            <span>Abrir</span>
          </Button>
          <Button variant="outline" size="sm">
            <Download className="h-4 w-4 mr-1" />
            <span>Exportar Leads</span>
          </Button>
        </div>
      </CardFooter>
    </Card>
  );
}
