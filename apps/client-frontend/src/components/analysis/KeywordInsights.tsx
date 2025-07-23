/**
 * Componente para exibir insights de palavras-chave baseado nas sugestões do Pedro
 * Detecta [Edital], [Laudo] e outras palavras importantes
 */

import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { analyzeDocument, KeywordMatch } from '@/utils/keywordDetection';
import { 
  FileText, 
  Clock, 
  Phone, 
  AlertTriangle, 
  CheckCircle, 
  BookOpen,
  TrendingUp
} from 'lucide-react';

interface KeywordInsightsProps {
  content: string;
  title?: string;
}

export function KeywordInsights({ content, title }: KeywordInsightsProps) {
  const analysis = analyzeDocument(content);
  
  const getRiskIcon = (level: string) => {
    switch (level) {
      case 'high':
        return <AlertTriangle className="h-4 w-4 text-red-500" />;
      case 'medium':
        return <Clock className="h-4 w-4 text-yellow-500" />;
      default:
        return <CheckCircle className="h-4 w-4 text-green-500" />;
    }
  };
  
  const getRiskColor = (level: string) => {
    switch (level) {
      case 'high':
        return 'border-red-200 bg-red-50';
      case 'medium':
        return 'border-yellow-200 bg-yellow-50';
      default:
        return 'border-green-200 bg-green-50';
    }
  };
  
  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'edital':
        return <FileText className="h-3 w-3" />;
      case 'laudo':
        return <BookOpen className="h-3 w-3" />;
      case 'prazo':
        return <Clock className="h-3 w-3" />;
      case 'contato':
        return <Phone className="h-3 w-3" />;
      default:
        return <TrendingUp className="h-3 w-3" />;
    }
  };

  return (
    <Card className={`${getRiskColor(analysis.riskLevel)} border-2`}>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          {getRiskIcon(analysis.riskLevel)}
          Análise de Palavras-Chave
          <Badge variant="outline" className="ml-auto">
            {analysis.keywords.length} encontradas
          </Badge>
        </CardTitle>
        <CardDescription>
          Detecção automática de termos importantes baseada em análise judicial
        </CardDescription>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Resumo Rápido */}
        <div className="grid grid-cols-2 gap-4">
          <div className="flex items-center gap-2">
            <FileText className="h-4 w-4 text-blue-500" />
            <span className="text-sm">
              <strong>Edital:</strong> {analysis.hasEdital ? '✅ Encontrado' : '❌ Não encontrado'}
            </span>
          </div>
          <div className="flex items-center gap-2">
            <BookOpen className="h-4 w-4 text-green-500" />
            <span className="text-sm">
              <strong>Laudo:</strong> {analysis.hasLaudo ? '✅ Encontrado' : '❌ Não encontrado'}
            </span>
          </div>
        </div>

        {/* Palavras-chave Encontradas */}
        {analysis.keywords.length > 0 && (
          <div>
            <h4 className="text-sm font-semibold mb-2">Palavras-chave Identificadas:</h4>
            <div className="flex flex-wrap gap-2">
              {analysis.keywords.map((keyword, index) => (
                <div
                  key={index}
                  className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${keyword.color}`}
                  title={keyword.description}
                >
                  {getTypeIcon(keyword.type)}
                  {keyword.word}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Sugestões Inteligentes */}
        {analysis.suggestions.length > 0 && (
          <div>
            <h4 className="text-sm font-semibold mb-2">Recomendações:</h4>
            <div className="space-y-2">
              {analysis.suggestions.map((suggestion, index) => (
                <Alert key={index} className="py-2">
                  <AlertDescription className="text-sm">
                    {suggestion}
                  </AlertDescription>
                </Alert>
              ))}
            </div>
          </div>
        )}

        {/* Alerta Especial para Documentos com Edital/Laudo */}
        {(analysis.hasEdital || analysis.hasLaudo) && (
          <Alert className="border-blue-200 bg-blue-50">
            <FileText className="h-4 w-4" />
            <AlertDescription>
              <strong>Documento Importante Detectado!</strong>
              <br />
              {analysis.hasEdital && analysis.hasLaudo 
                ? 'Este documento contém tanto edital quanto laudo - alta prioridade para análise.'
                : analysis.hasEdital 
                ? 'Edital detectado - revisar condições e prazos do leilão.'
                : 'Laudo detectado - verificar avaliação e condições do bem.'
              }
            </AlertDescription>
          </Alert>
        )}

        {/* Insights Baseados na Conversa do Pedro */}
        <div className="text-xs text-gray-600 bg-gray-50 p-3 rounded-lg">
          <p><strong>💡 Dica do Especialista:</strong></p>
          <p>
            Prazos judiciais são tipicamente de <strong>6 meses</strong>. 
            Para contatos repetidos, considere estratégia de acompanhamento sistemático.
          </p>
        </div>
      </CardContent>
    </Card>
  );
}