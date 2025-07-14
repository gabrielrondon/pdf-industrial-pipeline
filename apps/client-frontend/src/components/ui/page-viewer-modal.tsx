import React, { useState } from 'react';
import { 
  Dialog, 
  DialogContent, 
  DialogDescription, 
  DialogHeader, 
  DialogTitle,
  DialogFooter
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import { 
  FileText, 
  Copy, 
  Download, 
  ExternalLink, 
  Loader2, 
  AlertCircle,
  BookOpen,
  Eye,
  X
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { toast } from 'sonner';
import { railwayApi } from '@/services/railwayApiService';

interface PageViewerModalProps {
  isOpen: boolean;
  onClose: () => void;
  pageNumber: number;
  jobId?: string;
  documentName?: string;
}

interface PageData {
  page_content: string;
  filename: string;
  total_pages: number;
  page_number: number;
}

export function PageViewerModal({ 
  isOpen, 
  onClose, 
  pageNumber, 
  jobId, 
  documentName 
}: PageViewerModalProps) {
  const [pageData, setPageData] = useState<PageData | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchPageContent = async () => {
    if (!jobId) {
      setError('ID do job não encontrado. Esta funcionalidade precisa do ID do processamento para acessar o conteúdo da página.');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      // Use the Railway API service instead of direct fetch
      
      console.log(`📄 Fetching page ${pageNumber} for job ${jobId}`);
      const data = await railwayApi.getPageContent(jobId, pageNumber);
      
      console.log('📄 Page data received:', data);
      setPageData(data);
    } catch (err) {
      console.error('Erro ao buscar conteúdo da página:', err);
      
      // More specific error handling
      if (err instanceof Error) {
        if (err.message.includes('404')) {
          setError(`Página ${pageNumber} não encontrada neste documento. O documento pode não ter páginas suficientes ou o processamento ainda não foi concluído.`);
        } else if (err.message.includes('401') || err.message.includes('403')) {
          setError('Acesso negado. Você pode não ter permissão para visualizar este documento.');
        } else {
          setError(`Erro ao carregar conteúdo da página: ${err.message}`);
        }
      } else {
        setError('Erro desconhecido ao carregar o conteúdo da página.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleCopyContent = () => {
    if (pageData?.page_content) {
      navigator.clipboard.writeText(pageData.page_content);
      toast.success('Conteúdo copiado para a área de transferência!');
    }
  };

  const handleDownloadContent = () => {
    if (pageData?.page_content && pageData?.filename) {
      const blob = new Blob([pageData.page_content], { type: 'text/plain' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${pageData.filename}_pagina_${pageNumber}.txt`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      toast.success('Conteúdo baixado com sucesso!');
    }
  };

  // Fetch content when modal opens
  React.useEffect(() => {
    if (isOpen && !pageData && !isLoading && !error) {
      fetchPageContent();
    }
  }, [isOpen, pageData, isLoading, error]);

  // Reset state when modal closes
  React.useEffect(() => {
    if (!isOpen) {
      setPageData(null);
      setError(null);
    }
  }, [isOpen]);

  const contentLines = pageData?.page_content?.split('\n') || [];
  const wordCount = pageData?.page_content?.split(/\s+/).length || 0;
  const charCount = pageData?.page_content?.length || 0;

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[85vh] flex flex-col">
        <DialogHeader className="flex-shrink-0">
          <div className="flex items-start justify-between">
            <div className="space-y-2">
              <DialogTitle className="text-xl font-semibold flex items-center gap-2">
                <BookOpen className="h-5 w-5 text-primary" />
                Visualizar Página {pageNumber}
              </DialogTitle>
              <DialogDescription className="text-sm text-muted-foreground">
                {documentName ? `Documento: ${documentName}` : 'Conteúdo extraído da página do documento'}
              </DialogDescription>
            </div>
            {/* Remove duplicate close button - Dialog already has one */}
          </div>
          
          {pageData && (
            <div className="flex flex-wrap gap-2 pt-2">
              <Badge variant="outline" className="bg-blue-50 text-blue-700 border-blue-200">
                <FileText className="h-3 w-3 mr-1" />
                Página {pageData.page_number} de {pageData.total_pages}
              </Badge>
              <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">
                {wordCount} palavras
              </Badge>
              <Badge variant="outline" className="bg-purple-50 text-purple-700 border-purple-200">
                {charCount} caracteres
              </Badge>
            </div>
          )}
        </DialogHeader>

        <Separator className="my-4" />

        <div className="flex-1 min-h-0">
          {isLoading && (
            <div className="flex items-center justify-center h-48">
              <div className="text-center space-y-3">
                <Loader2 className="h-8 w-8 animate-spin mx-auto text-primary" />
                <p className="text-sm text-muted-foreground">Carregando conteúdo da página...</p>
              </div>
            </div>
          )}

          {error && (
            <div className="flex items-center justify-center h-48">
              <div className="text-center space-y-3 max-w-md">
                <AlertCircle className="h-8 w-8 mx-auto text-destructive" />
                <div>
                  <p className="font-medium text-destructive">Erro ao carregar conteúdo</p>
                  <p className="text-sm text-muted-foreground mt-1">{error}</p>
                </div>
                <Button 
                  variant="outline" 
                  size="sm" 
                  onClick={fetchPageContent}
                  className="mt-3"
                >
                  Tentar Novamente
                </Button>
              </div>
            </div>
          )}

          {pageData && (
            <div className="space-y-4 h-full">
              {/* Document Info Header */}
              <div className="bg-slate-50 p-4 rounded-lg border">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-medium text-slate-900">{pageData.filename}</h4>
                    <p className="text-sm text-slate-600 mt-1">
                      Página {pageData.page_number} de {pageData.total_pages} • {contentLines.length} linhas de texto
                    </p>
                  </div>
                  <div className="flex gap-2">
                    <Button 
                      variant="outline" 
                      size="sm" 
                      onClick={handleCopyContent}
                      className="h-8"
                    >
                      <Copy className="h-3 w-3 mr-1" />
                      Copiar
                    </Button>
                    <Button 
                      variant="outline" 
                      size="sm" 
                      onClick={handleDownloadContent}
                      className="h-8"
                    >
                      <Download className="h-3 w-3 mr-1" />
                      Baixar
                    </Button>
                  </div>
                </div>
              </div>

              {/* Content Display */}
              <div className="flex-1 border rounded-lg overflow-hidden">
                <div className="bg-slate-100 px-4 py-2 border-b">
                  <div className="flex items-center gap-2">
                    <Eye className="h-4 w-4 text-slate-600" />
                    <span className="text-sm font-medium text-slate-700">Conteúdo Extraído</span>
                  </div>
                </div>
                
                <ScrollArea className="h-64">
                  <div className="p-4">
                    {pageData.page_content ? (
                      <pre className="whitespace-pre-wrap text-sm font-mono leading-relaxed text-slate-800 break-words">
                        {pageData.page_content}
                      </pre>
                    ) : (
                      <div className="text-center py-8">
                        <FileText className="h-8 w-8 mx-auto text-slate-400 mb-2" />
                        <p className="text-sm text-slate-500">Nenhum conteúdo de texto encontrado nesta página</p>
                      </div>
                    )}
                  </div>
                </ScrollArea>
              </div>
            </div>
          )}
        </div>

        <DialogFooter className="flex-shrink-0 flex justify-between items-center pt-4">
          <div className="text-xs text-muted-foreground">
            💡 Este é o texto extraído exatamente desta página do documento original
          </div>
          <div className="flex gap-2">
            <Button variant="outline" onClick={onClose}>
              Fechar
            </Button>
            {pageData && (
              <Button onClick={handleCopyContent}>
                <Copy className="h-4 w-4 mr-1" />
                Copiar Conteúdo
              </Button>
            )}
          </div>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}