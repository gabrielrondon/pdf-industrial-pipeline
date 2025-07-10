
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
import { FileText, Lock, Search, Share2, Trash2 } from 'lucide-react';
import { cn } from '@/lib/utils';

export function DocumentList() {
  const { documents, toggleDocumentPrivacy, isLoading } = useDocuments();
  const { user } = useAuth();
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
          {filteredDocuments.map((doc) => (
            <Card key={doc.id} className="overflow-hidden">
              <div className="flex flex-col md:flex-row">
                <div className="flex-1 p-6">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                    <div>
                      <Badge className="mb-2">
                        {getDocumentTypeLabel(doc.type)}
                      </Badge>
                      <h3 className="font-medium text-lg">{doc.fileName}</h3>
                      <p className="text-sm text-muted-foreground">
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
                  
                  <div className="mt-4">
                    <div className="text-sm font-medium mb-2">Pontos identificados:</div>
                    <div className="flex flex-wrap gap-2">
                      {doc.points.slice(0, 3).map((point) => (
                        <Badge key={point.id} variant="outline">
                          {point.title}
                        </Badge>
                      ))}
                      {doc.points.length > 3 && (
                        <Badge variant="outline">
                          +{doc.points.length - 3}
                        </Badge>
                      )}
                    </div>
                  </div>
                </div>
                
                <div className={cn(
                  "border-t md:border-t-0 md:border-l",
                  "flex flex-row md:flex-col justify-between",
                  "p-4 bg-muted/20"
                )}>
                  <div className="flex items-center">
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
                        "text-xs", 
                        canTogglePrivacy 
                          ? "cursor-pointer" 
                          : "text-muted-foreground"
                      )}
                    >
                      Privado
                    </label>
                  </div>
                  
                  <div className="flex flex-col gap-2 mt-4">
                    <Button size="sm" asChild>
                      <Link to={`/documents/${doc.id}`}>Ver detalhes</Link>
                    </Button>
                    <Button size="sm" variant="outline">
                      <Trash2 className="h-4 w-4 mr-1" />
                      <span>Remover</span>
                    </Button>
                  </div>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
