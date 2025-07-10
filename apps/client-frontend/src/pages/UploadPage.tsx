
import { useState } from 'react';
import { DocumentUploader } from '@/components/document/DocumentUploader';
import { SimpleDocumentUploader } from '@/components/document/SimpleDocumentUploader';
import { ApiTest } from '@/components/debug/ApiTest';
import { DocumentAnalysis } from '@/types';
import { Button } from '@/components/ui/button';
import { useAuth } from '@/contexts/AuthContext';
import { toast } from '@/components/ui/use-toast';
import { UploadHeader } from '@/components/upload/UploadHeader';
import { AuthLoader } from '@/components/upload/AuthLoader';
import { UnauthenticatedState } from '@/components/upload/UnauthenticatedState';
import { ProcessingLoader } from '@/components/upload/ProcessingLoader';
import { AnalysisTabs } from '@/components/upload/AnalysisTabs';
import { UploadIntro } from '@/components/upload/UploadIntro';
import { FeaturesSection } from '@/components/upload/FeaturesSection';
import { useBackgroundProcessing } from '@/hooks/useBackgroundProcessing';

export default function UploadPage() {
  const [analysis, setAnalysis] = useState<DocumentAnalysis | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [activeTab, setActiveTab] = useState('analysis');
  const { user, isLoading } = useAuth();
  const { startBackgroundProcessing } = useBackgroundProcessing();
  
  console.log('UploadPage render:', { user: user?.email, isLoading });
  
  const handleAnalysisComplete = (result: DocumentAnalysis) => {
    setIsProcessing(true);
    
    setTimeout(() => {
      setAnalysis(result);
      setIsProcessing(false);
      
      toast({
        title: "Análise finalizada",
        description: `Foram encontrados ${result.points.length} pontos relevantes no seu documento.`,
      });
      
      // Start background processing for chunks and embeddings
      startBackgroundProcessing(result.id, result.fileUrl);
    }, 800);
  };
  
  const handleNewAnalysis = () => {
    setAnalysis(null);
    setActiveTab('analysis');
  };

  if (isLoading) {
    return <AuthLoader />;
  }

  if (!user) {
    return <UnauthenticatedState />;
  }
  
  return (
    <div className="container py-8">
      <UploadHeader />
      
      <div className="max-w-4xl mx-auto space-y-10">
        {isProcessing ? (
          <ProcessingLoader />
        ) : analysis ? (
          <div className="space-y-6">
            <AnalysisTabs 
              analysis={analysis} 
              activeTab={activeTab} 
              onTabChange={setActiveTab} 
            />
            
            <div className="flex justify-center mt-8">
              <Button onClick={handleNewAnalysis}>
                Analisar outro documento
              </Button>
            </div>
          </div>
        ) : (
          <div className="space-y-10">
            <UploadIntro />
            
            {/* Teste de conectividade com API Railway */}
            <div className="flex justify-center">
              <ApiTest />
            </div>
            
            {/* Usando SimpleDocumentUploader que usa nossa API Railway */}
            <SimpleDocumentUploader 
              onAnalysisComplete={handleAnalysisComplete} 
            />
            
            {/* Componente original (com problemas de RLS) - mantido para referência */}
            {/* <DocumentUploader 
              onAnalysisComplete={handleAnalysisComplete} 
            /> */}
            
            <FeaturesSection />
          </div>
        )}
      </div>
    </div>
  );
}
