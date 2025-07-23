
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
        {/* Premium Upload Header */}
        <div className="text-center mb-12">
          <div className="bg-gradient-to-r from-arremate-navy-600 to-arremate-navy-700 p-12 rounded-xl border border-arremate-navy-800 shadow-lg">
            <div className="bg-arremate-gold-500 p-4 rounded-full w-fit mx-auto mb-6">
              <svg className="h-12 w-12 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
            </div>
            <h1 className="text-4xl font-bold text-white mb-4">
              Análise Inteligente de Documentos
            </h1>
            <p className="text-xl text-arremate-navy-200 max-w-3xl mx-auto leading-relaxed">
              Descubra oportunidades valiosas em editais de leilão e processos judiciais com nossa IA especializada em documentação brasileira
            </p>
          </div>
        </div>
        
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
            <SimpleDocumentUploader 
              onAnalysisComplete={handleAnalysisComplete} 
            />
            
            <FeaturesSection />
            
            {/* Railway Status no rodé */}
            <div className="mt-16 pt-8 border-t border-arremate-charcoal-200">
              <div className="flex justify-center">
                <div className="bg-arremate-charcoal-50 p-4 rounded-lg">
                  <h3 className="text-sm font-semibold text-arremate-charcoal-700 mb-3 text-center">
                    Status da API Railway
                  </h3>
                  <ApiTest />
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
