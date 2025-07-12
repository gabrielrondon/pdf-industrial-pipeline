
import { useState } from 'react';
import { DocumentAnalysis, AnalysisStatus } from '@/types';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Switch } from '@/components/ui/switch';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible';
import { Input } from '@/components/ui/input';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger, DropdownMenuSeparator } from '@/components/ui/dropdown-menu';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { FileText, Download, Share2, Lock, Eye, TrendingUp, AlertTriangle, DollarSign, Calendar, ChevronDown, ChevronRight, ExternalLink, BookOpen, Edit, Check, X, Trash2, MoreVertical } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { useDocuments } from '@/contexts/DocumentContext';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { PageViewerModal } from '@/components/ui/page-viewer-modal';
import { railwayApi } from '@/services/railwayApiService';
import { toast } from 'sonner';
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
  const [expandedItems, setExpandedItems] = useState<Set<string>>(new Set());
  const [modalPageNumber, setModalPageNumber] = useState<number | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  
  // Title editing state
  const [isEditingTitle, setIsEditingTitle] = useState(false);
  const [editedTitle, setEditedTitle] = useState(analysis.fileName);
  const [isSavingTitle, setIsSavingTitle] = useState(false);
  
  // Delete confirmation state
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  
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
  
  const toggleExpanded = (pointId: string) => {
    const newExpanded = new Set(expandedItems);
    if (newExpanded.has(pointId)) {
      newExpanded.delete(pointId);
    } else {
      newExpanded.add(pointId);
    }
    setExpandedItems(newExpanded);
  };

  const handleViewPage = (pageNum: number) => {
    setModalPageNumber(pageNum);
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setModalPageNumber(null);
  };

  const getDetailedExplanation = (point: any) => {
    const category = point.category;
    const title = point.title.toLowerCase();
    
    if (category === 'financeiro' || title.includes('lance') || title.includes('avaliação') || title.includes('valor')) {
      return {
        icon: '💰',
        tips: [
          'Compare com avaliações de mercado da região',
          'Verifique se há ônus ou dívidas associadas',
          'Calcule custos adicionais (ITBI, cartório, etc.)',
          'Considere o potencial de valorização'
        ]
      };
    }
    
    if (category === 'prazo' || title.includes('data') || title.includes('prazo')) {
      return {
        icon: '⏰',
        tips: [
          'Marque na agenda com antecedência',
          'Prepare documentação necessária',
          'Organize recursos financeiros',
          'Verifique requisitos para participação'
        ]
      };
    }
    
    if (category === 'contato' || title.includes('contato') || title.includes('telefone')) {
      return {
        icon: '📞',
        tips: [
          'Entre em contato para esclarecimentos',
          'Tire dúvidas sobre o processo',
          'Confirme informações importantes',
          'Solicite visita ao imóvel se possível'
        ]
      };
    }
    
    if (category === 'leilao' || title.includes('leilão') || title.includes('hasta')) {
      return {
        icon: '🏛️',
        tips: [
          'Estude o edital completo',
          'Verifique condições de pagamento',
          'Confirme documentação exigida',
          'Analise histórico do processo'
        ]
      };
    }
    
    return {
      icon: '📋',
      tips: [
        'Analise com atenção os detalhes',
        'Consulte um advogado se necessário',
        'Verifique documentação relacionada',
        'Considere riscos e oportunidades'
      ]
    };
  };
  
  // Title editing functions
  const handleTitleEdit = () => {
    setIsEditingTitle(true);
    setEditedTitle(analysis.fileName);
  };
  
  const handleTitleSave = async () => {
    if (!editedTitle.trim()) {
      toast.error('O título não pode estar vazio');
      return;
    }
    
    setIsSavingTitle(true);
    try {
      await railwayApi.updateJobTitle(analysis.id, editedTitle.trim());
      
      // Update local state
      analysis.fileName = editedTitle.trim();
      
      setIsEditingTitle(false);
      toast.success('Título atualizado com sucesso!');
    } catch (error) {
      console.error('Error updating title:', error);
      toast.error('Erro ao atualizar título. Tente novamente.');
    } finally {
      setIsSavingTitle(false);
    }
  };
  
  const handleTitleCancel = () => {
    setEditedTitle(analysis.fileName);
    setIsEditingTitle(false);
  };
  
  const handleTitleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleTitleSave();
    } else if (e.key === 'Escape') {
      handleTitleCancel();
    }
  };
  
  // Delete functions
  const handleDeleteClick = () => {
    setShowDeleteDialog(true);
  };
  
  const handleDeleteConfirm = async () => {
    setIsDeleting(true);
    try {
      await railwayApi.deleteJob(analysis.id);
      
      toast.success('Documento removido com sucesso!');
      
      // Refresh the document list by navigating back or triggering a refresh
      // This will depend on how the parent component handles state
      window.location.href = '/dashboard'; // Simple navigation back to dashboard
      
    } catch (error) {
      console.error('Error deleting document:', error);
      toast.error('Erro ao remover documento. Tente novamente.');
    } finally {
      setIsDeleting(false);
      setShowDeleteDialog(false);
    }
  };
  
  const handleDeleteCancel = () => {
    setShowDeleteDialog(false);
  };
  
  // Agrupar leads por categoria - with null safety
  const leadsByCategory = (analysis.points || []).reduce((acc, point) => {
    const category = (point as any).category || 'geral';
    if (!acc[category]) {
      acc[category] = [];
    }
    acc[category].push(point);
    return acc;
  }, {} as Record<string, typeof analysis.points>);
  
  // Estatísticas dos leads - with null safety
  const totalLeads = (analysis.points || []).length;
  const highPriorityLeads = (analysis.points || []).filter(p => (p as any).priority === 'high').length;
  const categories = Object.keys(leadsByCategory);
  
  return (
    <Card className="w-full max-w-4xl mx-auto">
      <CardHeader>
        <div className="flex justify-between items-start">
          <div className="flex-1">
            <Badge className="mb-2">{getDocumentTypeLabel(analysis.type)}</Badge>
            
            {/* Editable Title */}
            <div className="flex items-center gap-2 mb-2">
              {isEditingTitle ? (
                <div className="flex items-center gap-2 flex-1">
                  <Input
                    value={editedTitle}
                    onChange={(e) => setEditedTitle(e.target.value)}
                    onKeyDown={handleTitleKeyPress}
                    className="text-2xl font-semibold h-auto py-1 border-2 border-primary"
                    placeholder="Título do documento"
                    autoFocus
                    disabled={isSavingTitle}
                  />
                  <Button
                    size="sm"
                    onClick={handleTitleSave}
                    disabled={isSavingTitle || !editedTitle.trim()}
                    className="shrink-0"
                  >
                    {isSavingTitle ? (
                      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    ) : (
                      <Check className="h-4 w-4" />
                    )}
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={handleTitleCancel}
                    disabled={isSavingTitle}
                    className="shrink-0"
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>
              ) : (
                <div className="flex items-center gap-2 flex-1 group">
                  <CardTitle className="text-2xl flex-1">{analysis.fileName}</CardTitle>
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={handleTitleEdit}
                    className="opacity-0 group-hover:opacity-100 transition-opacity shrink-0"
                  >
                    <Edit className="h-4 w-4" />
                  </Button>
                </div>
              )}
            </div>
            
            <CardDescription>
              Analisado em {new Date(analysis.analyzedAt).toLocaleString('pt-BR')}
            </CardDescription>
          </div>
          <div className="flex items-center gap-3">
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
            
            {/* Actions Dropdown */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                  <MoreVertical className="h-4 w-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem onClick={handleTitleEdit}>
                  <Edit className="h-4 w-4 mr-2" />
                  Editar título
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem 
                  onClick={handleDeleteClick}
                  className="text-destructive focus:text-destructive"
                >
                  <Trash2 className="h-4 w-4 mr-2" />
                  Excluir documento
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
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
                {leads.map((point) => {
                  const pointAny = point as any;
                  const isExpanded = expandedItems.has(point.id);
                  const hasDetails = pointAny.details || pointAny.page_reference;
                  
                  return (
                    <Collapsible key={point.id} open={isExpanded} onOpenChange={() => toggleExpanded(point.id)}>
                      <CollapsibleTrigger asChild>
                        <div 
                          className={cn(
                            "p-4 rounded-md border-l-4 cursor-pointer hover:bg-gray-50 transition-colors",
                            getPriorityColor(pointAny.priority || 'medium'),
                            getStatusColor(point.status)
                          )}
                        >
                          <div className="flex justify-between items-start">
                            <div className="font-medium flex items-center gap-2">
                              {point.title}
                              {pointAny.value && (
                                <Badge variant="outline" className="text-green-700 bg-green-50">
                                  {pointAny.value}
                                </Badge>
                              )}
                              {pointAny.page_reference && (
                                <Badge variant="outline" className="text-blue-700 bg-blue-50">
                                  <BookOpen className="h-3 w-3 mr-1" />
                                  Pág. {pointAny.page_reference}
                                </Badge>
                              )}
                            </div>
                            <div className="flex gap-2 items-center">
                              <Badge variant="outline" className={getCategoryColor(category)}>
                                {category}
                              </Badge>
                              <Badge variant="outline">
                                {point.status}
                              </Badge>
                              {pointAny.priority && (
                                <Badge 
                                  variant="outline" 
                                  className={
                                    pointAny.priority === 'high' ? 'border-red-500 text-red-700' :
                                    pointAny.priority === 'medium' ? 'border-yellow-500 text-yellow-700' :
                                    'border-green-500 text-green-700'
                                  }
                                >
                                  {pointAny.priority}
                                </Badge>
                              )}
                              {hasDetails && (
                                <div className="h-6 w-6 flex items-center justify-center">
                                  {isExpanded ? (
                                    <ChevronDown className="h-4 w-4" />
                                  ) : (
                                    <ChevronRight className="h-4 w-4" />
                                  )}
                                </div>
                              )}
                            </div>
                          </div>
                          
                          <p className="mt-2 text-sm">{point.comment}</p>
                        </div>
                      </CollapsibleTrigger>
                        
                        {hasDetails && (
                          <CollapsibleContent className="mt-3">
                            <div className="bg-gray-50 p-4 rounded-md border space-y-3">
                              <h5 className="font-medium text-sm mb-2 flex items-center">
                                <Eye className="h-4 w-4 mr-1" />
                                Detalhes Específicos
                              </h5>
                              
                              {pointAny.page_reference && (
                                <div className="bg-blue-50 p-3 rounded border-l-4 border-blue-400">
                                  <div className="flex items-center justify-between mb-2">
                                    <span className="text-sm font-medium text-blue-800">
                                      📄 Localização no Documento
                                    </span>
                                    <Button 
                                      variant="outline" 
                                      size="sm" 
                                      onClick={(e) => {
                                        e.stopPropagation(); // Prevent triggering the collapsible
                                        handleViewPage(pointAny.page_reference);
                                      }}
                                      className="h-7 text-xs bg-blue-100 hover:bg-blue-200 border-blue-300"
                                    >
                                      <ExternalLink className="h-3 w-3 mr-1" />
                                      Ver Página {pointAny.page_reference}
                                    </Button>
                                  </div>
                                  <span className="text-xs text-blue-600">
                                    Esta informação foi encontrada na página {pointAny.page_reference} do documento original
                                  </span>
                                </div>
                              )}
                              
                              {pointAny.details && (
                                <div className="bg-white p-3 rounded border">
                                  <h6 className="font-medium text-xs text-gray-700 mb-2">INFORMAÇÕES TÉCNICAS</h6>
                                  <div className="space-y-2">
                                    {Object.entries(pointAny.details).map(([key, value]) => (
                                      <div key={key} className="flex justify-between text-sm">
                                        <span className="text-gray-600 capitalize">
                                          {key.replace(/_/g, ' ')}:
                                        </span>
                                        <span className="font-medium text-gray-900">{String(value)}</span>
                                      </div>
                                    ))}
                                  </div>
                                </div>
                              )}
                              
                              {pointAny.raw_value && (
                                <div className="bg-yellow-50 p-2 rounded border-l-4 border-yellow-400">
                                  <div className="text-xs font-medium text-yellow-800 mb-1">TEXTO ORIGINAL</div>
                                  <div className="text-xs text-yellow-700 italic">
                                    "{pointAny.raw_value}"
                                  </div>
                                </div>
                              )}

                              {(() => {
                                const explanation = getDetailedExplanation(pointAny);
                                return (
                                  <div className="bg-green-50 p-3 rounded border-l-4 border-green-400">
                                    <h6 className="font-medium text-sm text-green-800 mb-2 flex items-center">
                                      <span className="mr-1">{explanation.icon}</span>
                                      DICAS PARA AÇÃO
                                    </h6>
                                    <ul className="space-y-1">
                                      {explanation.tips.map((tip, index) => (
                                        <li key={index} className="text-xs text-green-700 flex items-start">
                                          <span className="text-green-500 mr-1 mt-0.5">▸</span>
                                          {tip}
                                        </li>
                                      ))}
                                    </ul>
                                  </div>
                                );
                              })()}
                            </div>
                          </CollapsibleContent>
                        )}
                    </Collapsible>
                  );
                })}
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

      <PageViewerModal
        isOpen={isModalOpen}
        onClose={handleCloseModal}
        pageNumber={modalPageNumber || 1}
        jobId={analysis.id}
        documentName={analysis.fileName}
      />

      {/* Delete Confirmation Dialog */}
      <Dialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Trash2 className="h-5 w-5 text-destructive" />
              Excluir Documento
            </DialogTitle>
            <DialogDescription>
              Você tem certeza que deseja excluir permanentemente o documento "{analysis.fileName}"?
              Esta ação não pode ser desfeita e todos os dados de análise serão perdidos.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button 
              variant="outline" 
              onClick={handleDeleteCancel}
              disabled={isDeleting}
            >
              Cancelar
            </Button>
            <Button 
              variant="destructive" 
              onClick={handleDeleteConfirm}
              disabled={isDeleting}
            >
              {isDeleting ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                  Excluindo...
                </>
              ) : (
                <>
                  <Trash2 className="h-4 w-4 mr-2" />
                  Excluir Permanentemente
                </>
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </Card>
  );
}
