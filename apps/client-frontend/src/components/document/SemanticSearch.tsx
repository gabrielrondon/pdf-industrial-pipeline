
import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Search, FileText, AlertCircle } from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { supabase } from '@/integrations/supabase/client';
import { toast } from '@/components/ui/use-toast';

interface SearchResult {
  chunkId: string;
  content: string;
  similarity: number;
  wordCount: number;
  pageStart?: number;
  pageEnd?: number;
  document: {
    id: string;
    file_name: string;
    type: string;
  };
}

interface SemanticSearchProps {
  documentIds?: string[];
  onResultClick?: (result: SearchResult) => void;
}

export function SemanticSearch({ documentIds, onResultClick }: SemanticSearchProps) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [searchMethod, setSearchMethod] = useState<string>('');

  const handleSearch = async () => {
    if (!query.trim()) {
      toast({
        title: "Consulta vazia",
        description: "Por favor, digite uma pergunta para buscar.",
        variant: "destructive",
      });
      return;
    }

    setIsSearching(true);
    try {
      const { data, error } = await supabase.functions.invoke('semantic-search', {
        body: {
          query: query.trim(),
          documentIds,
          limit: 10,
          threshold: 0.6
        }
      });

      if (error) {
        throw new Error(error.message);
      }

      setResults(data.results || []);
      setSearchMethod(data.searchMethod || 'unknown');
      
      toast({
        title: "Busca concluída",
        description: `Encontrados ${data.results?.length || 0} trechos relevantes.`,
      });

    } catch (error) {
      console.error('Search error:', error);
      toast({
        title: "Erro na busca",
        description: error instanceof Error ? error.message : "Erro desconhecido na busca.",
        variant: "destructive",
      });
    } finally {
      setIsSearching(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  const getSimilarityColor = (similarity: number) => {
    if (similarity >= 0.8) return 'bg-green-100 text-green-800';
    if (similarity >= 0.7) return 'bg-yellow-100 text-yellow-800';
    return 'bg-gray-100 text-gray-800';
  };

  const getSearchMethodBadge = () => {
    if (searchMethod === 'semantic_search') {
      return <Badge variant="default">Busca Semântica (IA)</Badge>;
    } else if (searchMethod === 'text_search') {
      return <Badge variant="secondary">Busca Textual</Badge>;
    }
    return null;
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Search className="h-5 w-5" />
            Busca Semântica Inteligente
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-2">
            <Input
              placeholder="Ex: Quais são os débitos do imóvel? Há restrições ambientais?"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyPress={handleKeyPress}
              disabled={isSearching}
            />
            <Button 
              onClick={handleSearch} 
              disabled={isSearching || !query.trim()}
            >
              {isSearching ? 'Buscando...' : 'Buscar'}
            </Button>
          </div>

          {results.length === 0 && !isSearching && query && (
            <Alert>
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>
                Nenhum resultado encontrado. Tente reformular sua pergunta ou use termos diferentes.
              </AlertDescription>
            </Alert>
          )}

          {searchMethod && results.length > 0 && (
            <div className="flex items-center gap-2">
              {getSearchMethodBadge()}
              <span className="text-sm text-muted-foreground">
                {results.length} resultado(s) encontrado(s)
              </span>
            </div>
          )}
        </CardContent>
      </Card>

      <div className="space-y-4">
        {results.map((result, index) => (
          <Card 
            key={result.chunkId} 
            className="cursor-pointer hover:shadow-md transition-shadow"
            onClick={() => onResultClick?.(result)}
          >
            <CardContent className="p-4">
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-2">
                  <FileText className="h-4 w-4 text-muted-foreground" />
                  <span className="font-medium text-sm">{result.document.file_name}</span>
                  <Badge variant="outline" className="text-xs">
                    {result.document.type}
                  </Badge>
                </div>
                <div className="flex items-center gap-2">
                  {result.pageStart && (
                    <Badge variant="outline" className="text-xs">
                      Pág. {result.pageStart}
                    </Badge>
                  )}
                  <Badge className={`text-xs ${getSimilarityColor(result.similarity)}`}>
                    {Math.round(result.similarity * 100)}% relevante
                  </Badge>
                </div>
              </div>
              
              <p className="text-sm text-gray-700 leading-relaxed">
                {result.content.length > 300 
                  ? `${result.content.substring(0, 300)}...` 
                  : result.content}
              </p>
              
              <div className="flex items-center justify-between mt-3 text-xs text-muted-foreground">
                <span>{result.wordCount} palavras</span>
                <span>Resultado #{index + 1}</span>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
