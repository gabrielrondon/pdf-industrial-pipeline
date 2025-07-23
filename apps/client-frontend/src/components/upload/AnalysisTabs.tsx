
import React from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { FileText, Search, Loader2, BookOpen } from 'lucide-react';
import { AnalysisResult } from '@/components/document/AnalysisResult';
import { SemanticSearch } from '@/components/document/SemanticSearch';
import { ProcessingStatus } from '@/components/document/ProcessingStatus';
import { KeywordInsights } from '@/components/analysis/KeywordInsights';
import { DocumentAnalysis } from '@/types';
import { toast } from '@/components/ui/use-toast';

interface AnalysisTabsProps {
  analysis: DocumentAnalysis;
  activeTab: string;
  onTabChange: (tab: string) => void;
}

export function AnalysisTabs({ analysis, activeTab, onTabChange }: AnalysisTabsProps) {
  return (
    <Tabs value={activeTab} onValueChange={onTabChange} className="w-full">
      <TabsList className="grid w-full grid-cols-4">
        <TabsTrigger value="analysis" className="flex items-center gap-2">
          <FileText className="h-4 w-4" />
          Análise Estruturada
        </TabsTrigger>
        <TabsTrigger value="keywords" className="flex items-center gap-2">
          <BookOpen className="h-4 w-4" />
          Palavras-Chave
        </TabsTrigger>
        <TabsTrigger value="semantic" className="flex items-center gap-2">
          <Search className="h-4 w-4" />
          Busca Semântica
        </TabsTrigger>
        <TabsTrigger value="status" className="flex items-center gap-2">
          <Loader2 className="h-4 w-4" />
          Status
        </TabsTrigger>
      </TabsList>
      
      <TabsContent value="analysis" className="space-y-6">
        <AnalysisResult analysis={analysis} />
      </TabsContent>
      
      <TabsContent value="keywords" className="space-y-6">
        <KeywordInsights 
          content={analysis.extractedText || analysis.summary || ''} 
          title={analysis.fileName}
        />
      </TabsContent>
      
      <TabsContent value="semantic" className="space-y-6">
        <SemanticSearch 
          documentIds={[analysis.id]} 
          onResultClick={(result) => {
            toast({
              title: "Trecho selecionado",
              description: `Relevância: ${Math.round(result.similarity * 100)}% - ${result.document.file_name}`,
            });
          }}
        />
      </TabsContent>
      
      <TabsContent value="status" className="space-y-6">
        <ProcessingStatus 
          documentId={analysis.id}
          onProcessingComplete={() => {
            toast({
              title: "Processamento concluído!",
              description: "Agora você pode usar a busca semântica com total precisão.",
            });
          }}
        />
      </TabsContent>
    </Tabs>
  );
}
