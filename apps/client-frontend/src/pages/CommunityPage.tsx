import { useState, useEffect } from 'react';
import { useDocuments } from '@/contexts/DocumentContext';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { DocumentAnalysis } from '@/types';
import { AlertCircle, Bookmark, BookmarkCheck, FileText, Loader2, Search, Users, Star } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';

export default function CommunityPage() {
  const { getCommunityLeads, isLoading } = useDocuments();
  const [communityLeads, setCommunityLeads] = useState<DocumentAnalysis[]>([]);
  const [filteredLeads, setFilteredLeads] = useState<DocumentAnalysis[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [typeFilter, setTypeFilter] = useState('all');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [favorites, setFavorites] = useState<string[]>([]);
  const navigate = useNavigate();
  
  useEffect(() => {
    const fetchCommunityLeads = async () => {
      setLoading(true);
      setError(null);
      
      try {
        const leads = await getCommunityLeads();
        setCommunityLeads(leads);
        setFilteredLeads(leads);
      } catch (err) {
        setError('Não foi possível carregar os leads da comunidade.');
      } finally {
        setLoading(false);
      }
    };
    
    fetchCommunityLeads();
  }, [getCommunityLeads]);
  
  useEffect(() => {
    // Apply filters
    let filtered = [...communityLeads];
    
    // Apply type filter
    if (typeFilter !== 'all') {
      filtered = filtered.filter(lead => lead.type === typeFilter);
    }
    
    // Apply search filter
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(lead => 
        lead.fileName.toLowerCase().includes(query) ||
        lead.points.some(point => 
          point.title.toLowerCase().includes(query) ||
          point.comment.toLowerCase().includes(query)
        )
      );
    }
    
    setFilteredLeads(filtered);
  }, [communityLeads, typeFilter, searchQuery]);
  
  const toggleFavorite = (leadId: string) => {
    setFavorites(prev => {
      if (prev.includes(leadId)) {
        return prev.filter(id => id !== leadId);
      } else {
        return [...prev, leadId];
      }
    });
  };
  
  const getDocumentTypeLabel = (type: string): string => {
    const types: Record<string, string> = {
      'edital': 'Edital de Leilão',
      'processo': 'Processo Judicial',
      'laudo': 'Laudo Técnico',
      'outro': 'Outro Documento'
    };
    return types[type] || 'Documento';
  };
  
  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    return date.toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    });
  };
  
  return (
    <div className="container py-8">
      <div className="flex items-center gap-2 mb-8">
        <Users className="h-6 w-6 text-muted-foreground" />
        <h1 className="text-3xl font-bold tracking-tight">Leads da Comunidade</h1>
      </div>
      
      <div className="space-y-6">
        <Card className="bg-secondary/5 border-secondary/20">
          <CardContent className="pt-6">
            <div className="flex flex-col md:flex-row md:items-center gap-4 justify-between">
              <div className="flex items-center gap-2">
                <Badge className="bg-secondary">Premium</Badge>
                <p className="text-sm text-muted-foreground">
                  Acesso exclusivo a leads compartilhados por outros usuários
                </p>
              </div>
              
              <div className="flex flex-col sm:flex-row gap-2">
                <div className="relative">
                  <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                  <Input
                    type="text"
                    placeholder="Buscar leads..."
                    className="pl-8 w-full"
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
          </CardContent>
        </Card>
        
        {error && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertTitle>Erro</AlertTitle>
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}
        
        {loading || isLoading ? (
          <div className="flex flex-col items-center justify-center py-12">
            <Loader2 className="h-8 w-8 animate-spin text-primary mb-4" />
            <p className="text-muted-foreground">Carregando leads da comunidade...</p>
          </div>
        ) : filteredLeads.length === 0 ? (
          <Card>
            <CardContent className="flex flex-col items-center justify-center py-12">
              <FileText className="h-16 w-16 text-muted-foreground mb-4" />
              <h2 className="text-xl font-medium mb-2">Nenhum lead encontrado</h2>
              <p className="text-muted-foreground text-center max-w-md mb-6">
                {searchQuery || typeFilter !== 'all'
                  ? 'Nenhum lead corresponde aos seus filtros. Tente ajustar sua busca.'
                  : 'Não há leads compartilhados pela comunidade no momento.'}
              </p>
              {(searchQuery || typeFilter !== 'all') && (
                <Button 
                  variant="outline" 
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
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredLeads.map((lead) => (
              <Card key={lead.id} className="overflow-hidden">
                <CardHeader className="pb-2">
                  <div className="flex justify-between">
                    <Badge variant="outline">{getDocumentTypeLabel(lead.type)}</Badge>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-8 w-8"
                      onClick={() => toggleFavorite(lead.id)}
                    >
                      {favorites.includes(lead.id) ? (
                        <BookmarkCheck className="h-4 w-4 text-secondary" />
                      ) : (
                        <Bookmark className="h-4 w-4" />
                      )}
                    </Button>
                  </div>
                  <CardTitle className="text-lg mt-2">{lead.fileName}</CardTitle>
                  <CardDescription>
                    Compartilhado em {formatDate(lead.analyzedAt)}
                  </CardDescription>
                </CardHeader>
                
                <CardContent className="pb-3">
                  <div className="space-y-2">
                    <div className="text-sm font-medium">Pontos identificados:</div>
                    <div className="flex flex-wrap gap-2">
                      {lead.points.slice(0, 3).map((point) => (
                        <Badge key={point.id} variant="outline">
                          {point.title}
                        </Badge>
                      ))}
                      {lead.points.length > 3 && (
                        <Badge variant="outline">
                          +{lead.points.length - 3}
                        </Badge>
                      )}
                    </div>
                  </div>
                </CardContent>
                
                <CardFooter className="flex justify-between border-t pt-4">
                  <Button variant="outline" size="sm" className="w-full">
                    <FileText className="h-4 w-4 mr-2" />
                    Ver detalhes
                  </Button>
                </CardFooter>
              </Card>
            ))}
          </div>
        )}
        
        {filteredLeads.length > 0 && (
          <div className="flex justify-center mt-8">
            <div className="inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 border border-input bg-background hover:bg-accent hover:text-accent-foreground h-10 px-4 py-2">
              <span>Página 1 de 1</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
