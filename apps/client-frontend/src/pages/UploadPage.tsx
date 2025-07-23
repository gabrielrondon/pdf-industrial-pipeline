
import { useState } from 'react';
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
    <div className="min-h-screen bg-gradient-to-br from-arremate-navy-50 to-arremate-charcoal-50">
      <div className="container py-8">        
        <div className="space-y-10">
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
              <Button 
                onClick={handleNewAnalysis}
                size="lg"
                className="bg-arremate-navy-600 hover:bg-arremate-navy-700 text-white font-semibold px-8 py-3 shadow-lg"
              >
                Analisar Outro Documento
              </Button>
            </div>
          </div>
        ) : (
          <div className="space-y-10">
            {/* Upload Component */}
            <div className="max-w-6xl mx-auto">
              <SimpleDocumentUploader 
                onAnalysisComplete={handleAnalysisComplete} 
              />
            </div>
            
            <FeaturesSection />
            
            {/* Status da API - versão discreta no rodapé */}
            <div className="mt-12">
              <div className="text-center">
                <div className="inline-flex items-center gap-2 text-xs text-arremate-charcoal-500 bg-arremate-charcoal-50 px-3 py-1 rounded-full">
                  <span>Status da API:</span>
                  <ApiTest compact={true} />
                </div>
              </div>
            </div>
          </div>
        )}
        </div>
      </div>
    </div>
  );
}
