
import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useDocuments } from '@/contexts/DocumentContext';
import { useAuth } from '@/contexts/AuthContext';
import { DocumentAnalysis, DocumentType } from '@/types';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Input } from '@/components/ui/input';
import { Switch } from '@/components/ui/switch';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { FileText, Lock, Search, Share2, Trash2, TrendingUp, Calendar, DollarSign, Eye, StickyNote, Download } from 'lucide-react';
import { cn } from '@/lib/utils';

export function DocumentList() {
  const { documents, toggleDocumentPrivacy, isLoading } = useDocuments();
  const { user } = useAuth();
  
  console.log('📋 DocumentList render - documents:', documents.length, 'isLoading:', isLoading);
  const [searchQuery, setSearchQuery] = useState('');
  const [typeFilter, setTypeFilter] = useState<string>('all');
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const canTogglePrivacy = user?.plan !== 'free';
  
  const getDocumentTypeLabel = (type: DocumentType): string => {
    const types: Record<DocumentType, string> = {
      'edital': 'Edital de Leilão',
      'processo': 'Processo Judicial',
      'laudo': 'Laudo Técnico',
      'outro': 'Outro Documento'
    };
    return types[type] || 'Documento';
  };
  
  const handleTogglePrivacy = async (id: string) => {
    if (!canTogglePrivacy) {
      setError('Somente usuários Pro e Premium podem alterar a privacidade dos leads.');
      return;
    }
    
    setIsSaving(true);
    setError(null);
    
    try {
      await toggleDocumentPrivacy(id);
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
  
  // Filter documents
  const filteredDocuments = documents.filter((doc) => {
    // Apply type filter
    if (typeFilter !== 'all' && doc.type !== typeFilter) {
      return false;
    }
    
    // Apply search filter
    const searchLower = searchQuery.toLowerCase();
    return (
      doc.fileName.toLowerCase().includes(searchLower) ||
      getDocumentTypeLabel(doc.type).toLowerCase().includes(searchLower) ||
      doc.points.some(
        (point) =>
          point.title.toLowerCase().includes(searchLower) ||
          point.comment.toLowerCase().includes(searchLower)
      )
    );
  });
  
  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    return date.toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    });
  };

  const getDocumentStats = (doc: DocumentAnalysis) => {
    const confirmedLeads = doc.points.filter(p => p.status === 'confirmado').length;
    const alertLeads = doc.points.filter(p => p.status === 'alerta').length;
    const hasNotes = localStorage.getItem(`document_notes_${doc.id}`)?.length > 0;
    
    // Try to extract financial info
    const financialPoints = doc.points.filter(point => 
      (point as any).category === 'financeiro' || 
      point.title.includes('R$') ||
      point.title.includes('Lance') ||
      point.title.includes('Avaliação')
    );

    const hasFinancialData = financialPoints.length > 0;
    
    return {
      confirmedLeads,
      alertLeads,
      hasNotes,
      hasFinancialData,
      totalPoints: doc.points.length
    };
  };
  
  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row gap-4 items-start md:items-center justify-between">
        <div className="text-lg font-medium">Documentos analisados</div>
        
        <div className="flex flex-col sm:flex-row w-full md:w-auto gap-2">
          <div className="relative w-full sm:w-64">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              type="text"
              placeholder="Buscar documentos..."
              className="pl-8"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
          
          <Select value={typeFilter} onValueChange={setTypeFilter}>
            <SelectTrigger className="w-full sm:w-40">
              <SelectValue placeholder="Filtrar por tipo" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Todos os tipos</SelectItem>
              <SelectItem value="edital">Editais</SelectItem>
              <SelectItem value="processo">Processos</SelectItem>
              <SelectItem value="laudo">Laudos</SelectItem>
              <SelectItem value="outro">Outros</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>
      
      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}
      
      {isLoading ? (
        <div className="text-center p-12">
          <div className="animate-pulse">Carregando documentos...</div>
        </div>
      ) : filteredDocuments.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center p-8">
            <FileText className="h-12 w-12 text-muted-foreground mb-3" />
            <h3 className="text-lg font-medium">Nenhum documento encontrado</h3>
            <p className="text-muted-foreground text-sm mt-1">
              {searchQuery || typeFilter !== 'all'
                ? 'Tente ajustar seus filtros de busca'
                : 'Faça upload de documentos para começar a análise'}
            </p>
            {(searchQuery || typeFilter !== 'all') && (
              <Button 
                variant="outline" 
                className="mt-4"
                onClick={() => {
                  setSearchQuery('');
                  setTypeFilter('all');
                }}
              >
                Limpar filtros
              </Button>
            )}
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {(filteredDocuments || []).map((doc) => {
            const stats = getDocumentStats(doc);
            
            return (
              <Card key={doc.id} className="overflow-hidden hover:shadow-md transition-shadow">
                <div className="flex flex-col lg:flex-row">
                  <div className="flex-1 p-6">
                    {/* Header */}
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-4">
                      <div>
                        <div className="flex items-center gap-2 mb-2">
                          <Badge className="bg-blue-100 text-blue-800">
                            {getDocumentTypeLabel(doc.type)}
                          </Badge>
                          {stats.hasNotes && (
                            <Badge variant="outline" className="text-purple-700 bg-purple-50">
                              <StickyNote className="h-3 w-3 mr-1" />
                              Com anotações
                            </Badge>
                          )}
                        </div>
                        <h3 className="font-semibold text-lg">{doc.fileName}</h3>
                        <p className="text-sm text-muted-foreground flex items-center">
                          <Calendar className="h-4 w-4 mr-1" />
                          Analisado em {formatDate(doc.analyzedAt)}
                        </p>
                      </div>
                      
                      <div className="mt-2 sm:mt-0">
                        <div className="flex items-center space-x-1 text-sm">
                          {doc.isPrivate ? (
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
                    </div>
                    
                    {/* Stats Grid */}
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
                      <div className="text-center p-3 bg-green-50 rounded-lg">
                        <div className="flex items-center justify-center mb-1">
                          <Eye className="h-4 w-4 text-green-600" />
                        </div>
                        <div className="text-lg font-bold text-green-700">{stats.confirmedLeads}</div>
                        <div className="text-xs text-green-600">Confirmados</div>
                      </div>
                      
                      <div className="text-center p-3 bg-yellow-50 rounded-lg">
                        <div className="flex items-center justify-center mb-1">
                          <TrendingUp className="h-4 w-4 text-yellow-600" />
                        </div>
                        <div className="text-lg font-bold text-yellow-700">{stats.alertLeads}</div>
                        <div className="text-xs text-yellow-600">Alertas</div>
                      </div>
                      
                      <div className="text-center p-3 bg-blue-50 rounded-lg">
                        <div className="flex items-center justify-center mb-1">
                          <FileText className="h-4 w-4 text-blue-600" />
                        </div>
                        <div className="text-lg font-bold text-blue-700">{stats.totalPoints}</div>
                        <div className="text-xs text-blue-600">Total Leads</div>
                      </div>
                      
                      <div className="text-center p-3 bg-purple-50 rounded-lg">
                        <div className="flex items-center justify-center mb-1">
                          <DollarSign className="h-4 w-4 text-purple-600" />
                        </div>
                        <div className="text-lg font-bold text-purple-700">
                          {stats.hasFinancialData ? 'Sim' : 'Não'}
                        </div>
                        <div className="text-xs text-purple-600">Dados Financeiros</div>
                      </div>
                    </div>
                    
                    {/* Top Leads Preview */}
                    <div className="mt-4">
                      <div className="text-sm font-medium mb-2 flex items-center">
                        <TrendingUp className="h-4 w-4 mr-1" />
                        Principais oportunidades:
                      </div>
                      <div className="flex flex-wrap gap-2">
                        {(doc.points || []).slice(0, 3).map((point) => (
                          <Badge 
                            key={point.id} 
                            variant="outline"
                            className={
                              point.status === 'confirmado' ? 'border-green-500 text-green-700' :
                              point.status === 'alerta' ? 'border-yellow-500 text-yellow-700' :
                              'border-gray-500 text-gray-700'
                            }
                          >
                            {point.title.length > 30 ? point.title.substring(0, 30) + '...' : point.title}
                          </Badge>
                        ))}
                        {doc.points.length > 3 && (
                          <Badge variant="outline" className="bg-gray-50">
                            +{doc.points.length - 3} outros
                          </Badge>
                        )}
                      </div>
                    </div>
                  </div>
                  
                  {/* Actions Panel */}
                  <div className={cn(
                    "border-t lg:border-t-0 lg:border-l",
                    "flex flex-row lg:flex-col justify-between",
                    "p-6 bg-muted/20 lg:min-w-64"
                  )}>
                    {/* Privacy Toggle */}
                    <div className="flex items-center mb-4">
                      <Switch 
                        id={`privacy-toggle-${doc.id}`}
                        checked={doc.isPrivate}
                        onCheckedChange={() => handleTogglePrivacy(doc.id)}
                        disabled={!canTogglePrivacy || isSaving || isLoading}
                        className="mr-2"
                      />
                      <label 
                        htmlFor={`privacy-toggle-${doc.id}`}
                        className={cn(
                          "text-sm", 
                          canTogglePrivacy 
                            ? "cursor-pointer" 
                            : "text-muted-foreground"
                        )}
                      >
                        Manter privado
                      </label>
                    </div>
                    
                    {/* Action Buttons */}
                    <div className="flex flex-col gap-2 w-full">
                      <Button size="sm" asChild className="w-full">
                        <Link to={`/documents/${doc.id}`}>
                          <Eye className="h-4 w-4 mr-2" />
                          Ver análise completa
                        </Link>
                      </Button>
                      
                      <Button size="sm" variant="outline" className="w-full">
                        <Download className="h-4 w-4 mr-2" />
                        Exportar leads
                      </Button>
                      
                      <Button size="sm" variant="outline" className="w-full text-red-600 hover:text-red-700">
                        <Trash2 className="h-4 w-4 mr-2" />
                        Remover
                      </Button>
                    </div>
                  </div>
                </div>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}
