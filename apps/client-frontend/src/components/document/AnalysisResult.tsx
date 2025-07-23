
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
import { FileText, Download, Share2, Lock, Eye, TrendingUp, AlertTriangle, DollarSign, Calendar, ChevronDown, ChevronRight, ExternalLink, BookOpen, Edit, Check, X, Trash2, MoreVertical, Sparkles } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { useDocuments } from '@/contexts/DocumentContext';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { PageViewerModal } from '@/components/ui/page-viewer-modal';
import { PremiumLeadCard } from '@/components/leads/PremiumLeadCard';
import { railwayApi } from '@/services/railwayApiService';
import { toast } from 'sonner';
import { cn } from '@/lib/utils';
import { QualityDashboard } from '@/components/quality/QualityDashboard';
import { useQualityAssessment } from '@/hooks/useQualityAssessment';
import { useComplianceCheck } from '@/hooks/useComplianceCheck';
import { useRecommendations } from '@/hooks/useRecommendations';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

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
  
  // Quality hooks - Week 4 Integration
  const qualityAssessment = useQualityAssessment();
  const complianceCheck = useComplianceCheck();
  const recommendations = useRecommendations();
  const [activeTab, setActiveTab] = useState("leads");
  const [qualityData, setQualityData] = useState<any>(null);
  const [isLoadingQuality, setIsLoadingQuality] = useState(false);
  
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
  
  // Quality assessment functions - Week 4 Integration
  const generateQualityAssessment = async () => {
    if (!analysis.points || analysis.points.length === 0) {
      toast.error('Nenhuma análise disponível para avaliação de qualidade');
      return;
    }
    
    setIsLoadingQuality(true);
    try {
      // Combine analysis text from all points
      const analysisText = analysis.points
        .map(point => `${point.title}: ${point.comment}`)
        .join('\n');
      
      // Run quality assessment
      const qualityResult = await qualityAssessment.assessQuality(
        analysisText, 
        analysis.id
      );
      
      if (!qualityResult) return;
      
      // Run compliance check
      const complianceResult = await complianceCheck.checkCompliance(
        analysisText,
        analysis.id,
        analysis.type
      );
      
      if (!complianceResult) return;
      
      // Generate recommendations
      const recommendationsResult = await recommendations.generateRecommendations(
        analysisText,
        analysis.id,
        qualityResult.quality_metrics,
        complianceResult.compliance_result
      );
      
      if (!recommendationsResult) return;
      
      // Combine all data for the quality dashboard
      const combinedQualityData = {
        quality_metrics: qualityResult.quality_metrics,
        compliance_result: complianceResult.compliance_result,
        recommendations: recommendationsResult.recommendations
      };
      
      setQualityData(combinedQualityData);
      
      toast.success('Análise de qualidade inteligente concluída!');
      
    } catch (error) {
      console.error('Error generating quality assessment:', error);
      toast.error('Erro ao gerar análise de qualidade');
    } finally {
      setIsLoadingQuality(false);
    }
  };
  
  const handleRecommendationComplete = async (recommendationId: string) => {
    const success = await recommendations.markRecommendationComplete(recommendationId);
    if (success) {
      // Update local state if needed
      console.log('Recommendation completed:', recommendationId);
    }
  };
  
  const handleRefreshQuality = () => {
    generateQualityAssessment();
  };
  
  const handleExportReport = () => {
    // TODO: Implement export functionality
    toast.info('Funcionalidade de exportação em desenvolvimento');
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
    <div className="w-full max-w-6xl mx-auto space-y-6">
      <Card>
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
      </Card>

      {/* Main Content with Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <div className="flex items-center justify-between">
          <TabsList className="grid w-auto grid-cols-2">
            <TabsTrigger value="leads" className="flex items-center gap-2">
              <FileText className="h-4 w-4" />
              Leads e Oportunidades
            </TabsTrigger>
            <TabsTrigger value="quality" className="flex items-center gap-2">
              <Sparkles className="h-4 w-4" />
              Análise Inteligente
            </TabsTrigger>
          </TabsList>
          
          {activeTab === "quality" && (
            <Button 
              onClick={generateQualityAssessment}
              disabled={isLoadingQuality}
              className="flex items-center gap-2"
            >
              {isLoadingQuality ? (
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
              ) : (
                <Sparkles className="h-4 w-4" />
              )}
              {qualityData ? 'Atualizar Análise' : 'Gerar Análise Inteligente'}
            </Button>
          )}
        </div>

        <TabsContent value="leads" className="space-y-6">
          <Card>
            <CardContent className="space-y-6 pt-6">
              {error && (
                <Alert variant="destructive">
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}
        
        {/* Estatísticas dos Leads - Premium Design */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-gradient-to-r from-arremate-navy-50 to-arremate-navy-100 p-6 rounded-xl border border-arremate-navy-200 shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-semibold text-arremate-navy-700 uppercase tracking-wide">Total de Leads</p>
                <p className="text-3xl font-bold text-arremate-navy-900 mt-1">{totalLeads}</p>
                <p className="text-xs text-arremate-navy-600 mt-1">Oportunidades identificadas</p>
              </div>
              <div className="bg-arremate-navy-500 p-3 rounded-lg">
                <FileText className="h-8 w-8 text-white" />
              </div>
            </div>
          </div>
          
          <div className="bg-gradient-to-r from-red-50 to-red-100 p-6 rounded-xl border border-red-200 shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-semibold text-red-700 uppercase tracking-wide">Alta Prioridade</p>
                <p className="text-3xl font-bold text-red-900 mt-1">{highPriorityLeads}</p>
                <p className="text-xs text-red-600 mt-1">Requer atenção urgente</p>
              </div>
              <div className="bg-red-500 p-3 rounded-lg">
                <AlertTriangle className="h-8 w-8 text-white" />
              </div>
            </div>
          </div>
          
          <div className="bg-gradient-to-r from-arremate-gold-50 to-arremate-gold-100 p-6 rounded-xl border border-arremate-gold-200 shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-semibold text-arremate-gold-700 uppercase tracking-wide">Categorias</p>
                <p className="text-3xl font-bold text-arremate-gold-900 mt-1">{categories.length}</p>
                <p className="text-xs text-arremate-gold-600 mt-1">Tipos de oportunidades</p>
              </div>
              <div className="bg-arremate-gold-500 p-3 rounded-lg">
                <TrendingUp className="h-8 w-8 text-white" />
              </div>
            </div>
          </div>
        </div>

              {/* Leads por Categoria - Premium Design */}
              <div className="space-y-8">
                <div className="text-center">
                  <h3 className="text-2xl font-bold text-arremate-charcoal-900 mb-2">
                    Leads e Oportunidades Identificadas
                  </h3>
                  <p className="text-arremate-charcoal-600">
                    Análise detalhada com contexto extraído do documento original
                  </p>
                </div>
                
                {Object.entries(leadsByCategory).map(([category, leads]) => (
                  <div key={category} className="space-y-4">
                    <div className="bg-gradient-to-r from-arremate-charcoal-50 to-arremate-charcoal-100 p-4 rounded-lg border border-arremate-charcoal-200">
                      <div className="flex items-center gap-3">
                        <div className="bg-arremate-navy-500 p-2 rounded-lg">
                          {React.cloneElement(getCategoryIcon(category), { className: "h-5 w-5 text-white" })}
                        </div>
                        <div className="flex-1">
                          <h4 className="font-semibold text-lg capitalize text-arremate-charcoal-900">{category}</h4>
                          <p className="text-sm text-arremate-charcoal-600">
                            {leads.length} {leads.length === 1 ? 'oportunidade encontrada' : 'oportunidades encontradas'}
                          </p>
                        </div>
                        <Badge variant="outline" className="bg-arremate-navy-100 text-arremate-navy-800 border-arremate-navy-300 font-semibold">
                          {leads.length}
                        </Badge>
                      </div>
                    </div>
                    
                    <div className="space-y-4">
                      {leads.map((point) => {
                        const pointAny = point as any;
                        const isExpanded = expandedItems.has(point.id);
                        
                        return (
                          <PremiumLeadCard
                            key={point.id}
                            lead={{
                              id: point.id,
                              title: point.title,
                              comment: point.comment,
                              status: point.status,
                              category: category,
                              priority: pointAny.priority || 'medium',
                              page_reference: pointAny.page_reference,
                              details: pointAny.details,
                              raw_value: pointAny.raw_value,
                              value: pointAny.value
                            }}
                            isExpanded={isExpanded}
                            onToggleExpanded={() => toggleExpanded(point.id)}
                            onViewPage={handleViewPage}
                          />
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
      </Card>
    </TabsContent>

    <TabsContent value="quality" className="space-y-6">
      {qualityData ? (
        <QualityDashboard
          data={qualityData}
          isLoading={isLoadingQuality}
          onRefresh={handleRefreshQuality}
          onRecommendationComplete={handleRecommendationComplete}
          onExportReport={handleExportReport}
        />
      ) : (
        <Card className="bg-gradient-to-r from-blue-50 to-purple-50 border-blue-200">
          <CardContent className="text-center py-12">
            <Sparkles className="h-16 w-16 text-blue-500 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              Análise Inteligente Disponível
            </h3>
            <p className="text-gray-600 mb-6 max-w-2xl mx-auto">
              Obtenha insights automáticos sobre qualidade, conformidade legal e recomendações 
              inteligentes usando nossa IA especializada em documentos judiciais brasileiros.
            </p>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 max-w-3xl mx-auto mb-6">
              <div className="bg-white p-4 rounded-lg border">
                <div className="text-blue-600 font-medium mb-1">Qualidade 0-100</div>
                <div className="text-sm text-gray-600">50+ critérios avançados</div>
              </div>
              <div className="bg-white p-4 rounded-lg border">
                <div className="text-green-600 font-medium mb-1">CPC Art. 889</div>
                <div className="text-sm text-gray-600">Conformidade automática</div>
              </div>
              <div className="bg-white p-4 rounded-lg border">
                <div className="text-purple-600 font-medium mb-1">Recomendações</div>
                <div className="text-sm text-gray-600">Ações priorizadas</div>
              </div>
            </div>
            <Button 
              onClick={generateQualityAssessment}
              disabled={isLoadingQuality}
              size="lg"
              className="flex items-center gap-2"
            >
              {isLoadingQuality ? (
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
              ) : (
                <Sparkles className="h-5 w-5" />
              )}
              Gerar Análise Inteligente
            </Button>
          </CardContent>
        </Card>
      )}
    </TabsContent>
  </Tabs>

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
</div>
  );
}
