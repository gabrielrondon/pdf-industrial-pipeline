
import React, { useState, useRef } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Progress } from '@/components/ui/progress';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Upload, FileText, AlertCircle, CheckCircle, X, TrendingUp, Coins, Zap } from 'lucide-react';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { DocumentAnalysis, DocumentType } from '@/types';
import { useDocuments } from '@/contexts/DocumentContext';
import { useAuth } from '@/contexts/AuthContext';
import { supabase } from '@/integrations/supabase/client';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { toast } from '@/components/ui/use-toast';
import { ModelSelector, AIModel } from './ModelSelector';
import LargeDocumentService from '@/services/largeDocumentService';
import LargeDocumentProcessor from './LargeDocumentProcessor';

interface DocumentUploaderProps {
  onAnalysisComplete?: (analysis: DocumentAnalysis) => void;
}

const ANALYSIS_COST = 10; // Custo em créditos por análise

export function DocumentUploader({ onAnalysisComplete }: DocumentUploaderProps) {
  const { uploadDocument, isLoading } = useDocuments();
  const { user, refreshUser } = useAuth();
  const [file, setFile] = useState<File | null>(null);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [fileType, setFileType] = useState<DocumentType>('edital');
  const [aiModel, setAiModel] = useState<AIModel>('native');
  const [uploadedDocumentId, setUploadedDocumentId] = useState<string | null>(null);
  const [fileUrl, setFileUrl] = useState<string | null>(null);
  const [useLargeProcessing, setUseLargeProcessing] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  // Check if user has enough credits
  const hasEnoughCredits = user && user.credits >= ANALYSIS_COST;
  
  // Check if file should use large document processing
  const shouldUseLargeProcessing = file ? LargeDocumentService.shouldUseLargeProcessing(file.size) : false;
  
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (!selectedFile) return;
    
    setError(null);
    setProgress(0);
    
    if (selectedFile.type !== 'application/pdf') {
      setError('Por favor, selecione um arquivo PDF.');
      return;
    }
    
    if (selectedFile.size > 50 * 1024 * 1024) {
      setError('O arquivo é muito grande. O tamanho máximo é de 50MB.');
      return;
    }
    
    setFile(selectedFile);
    
    // Auto-detect if should use large processing
    const shouldUseLarge = LargeDocumentService.shouldUseLargeProcessing(selectedFile.size);
    setUseLargeProcessing(shouldUseLarge);
  };
  
  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
  };
  
  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    
    if (e.dataTransfer.files.length) {
      const droppedFile = e.dataTransfer.files[0];
      
      if (droppedFile.type !== 'application/pdf') {
        setError('Por favor, selecione um arquivo PDF.');
        return;
      }
      
      if (droppedFile.size > 50 * 1024 * 1024) {
        setError('O arquivo é muito grande. O tamanho máximo é de 50MB.');
        return;
      }
      
      setFile(droppedFile);
      setError(null);
      
      // Auto-detect if should use large processing
      const shouldUseLarge = LargeDocumentService.shouldUseLargeProcessing(droppedFile.size);
      setUseLargeProcessing(shouldUseLarge);
    }
  };
  
  const clearFile = () => {
    setFile(null);
    setProgress(0);
    setError(null);
    setIsUploading(false);
    setUploadedDocumentId(null);
    setFileUrl(null);
    setUseLargeProcessing(false);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleLargeDocumentProcessing = async () => {
    if (!file || !user) return;

    try {
      setProgress(10);
      console.log('Starting large document processing...');

      // Spend credits first
      const { data: creditResult, error: creditError } = await supabase.functions.invoke('manage-credits', {
        body: { 
          action: 'spend',
          amount: ANALYSIS_COST,
          reason: `Análise de documento grande: ${file.name}`
        }
      });

      if (creditError || !creditResult.success) {
        throw new Error(creditResult?.error || 'Erro ao debitar créditos');
      }

      await refreshUser();
      setProgress(25);

      // Upload file to Supabase Storage first
      const fileExt = file.name.split('.').pop();
      const fileName = `${Date.now()}_${file.name}`;
      const filePath = `documents/${user.id}/${fileName}`;

      const { data: uploadData, error: uploadError } = await supabase.storage
        .from('documents')
        .upload(filePath, file);

      if (uploadError) {
        throw new Error(`Erro ao fazer upload: ${uploadError.message}`);
      }

      setProgress(50);

      // Get public URL
      const { data: urlData } = supabase.storage
        .from('documents')
        .getPublicUrl(filePath);

      const fileUrl = urlData.publicUrl;
      setFileUrl(fileUrl);

      // Create document record
      const { data: docData, error: docError } = await supabase
        .from('documents')
        .insert({
          user_id: user.id,
          file_name: file.name,
          file_url: fileUrl,
          file_size_mb: file.size / (1024 * 1024),
          type: fileType,
          processing_method: 'large_document',
          analysis_status: 'pending'
        })
        .select()
        .single();

      if (docError) {
        throw new Error(`Erro ao criar documento: ${docError.message}`);
      }

      setUploadedDocumentId(docData.id);
      setProgress(75);

      toast({
        title: "Upload Concluído",
        description: `${file.name} foi enviado e será processado em segundo plano.`,
      });

      setProgress(100);

    } catch (error) {
      console.error('Erro no processamento de documento grande:', error);
      
      // Refund credits if upload failed
      try {
        await supabase.functions.invoke('manage-credits', {
          body: { 
            action: 'grant',
            amount: ANALYSIS_COST,
            reason: `Reembolso por falha no upload: ${file.name}`
          }
        });
        await refreshUser();
      } catch (refundError) {
        console.error('Erro ao reembolsar créditos:', refundError);
      }

      const errorMessage = error instanceof Error ? error.message : 'Erro desconhecido';
      setError(errorMessage);
      setIsUploading(false);
      setProgress(0);
      
      toast({
        title: "Erro no Upload",
        description: errorMessage,
        variant: "destructive",
      });
    }
  };
  
  const handleSubmit = async () => {
    if (!file) {
      setError('Por favor, selecione um arquivo para analisar.');
      return;
    }

    if (!user) {
      setError('Você precisa estar logado para analisar documentos.');
      return;
    }

    if (!hasEnoughCredits) {
      setError(`Créditos insuficientes. Você precisa de ${ANALYSIS_COST} créditos para esta análise.`);
      return;
    }
    
    setIsUploading(true);
    setError(null);

    // If it's a large document or user specifically chose large processing
    if (useLargeProcessing || shouldUseLargeProcessing) {
      return handleLargeDocumentProcessing();
    }
    
    try {
      setProgress(10);
      console.log('Starting document analysis...');
      
      const analysisType = aiModel === 'native' ? 'análise nativa' : 
        aiModel === 'openai' ? 'OpenAI GPT-4o' : 
        aiModel === 'mistral' ? 'Mistral Large' : 'Claude Sonnet';
      
      toast({
        title: "Análise de leads iniciada",
        description: `Usando ${analysisType} para identificar oportunidades no seu documento.`,
      });

      // Spend credits before analysis
      console.log('Spending credits...');
      setProgress(20);
      const { data: creditResult, error: creditError } = await supabase.functions.invoke('manage-credits', {
        body: { 
          action: 'spend',
          amount: ANALYSIS_COST,
          reason: `Análise de documento: ${file.name}`
        }
      });

      if (creditError || !creditResult.success) {
        throw new Error(creditResult?.error || 'Erro ao debitar créditos');
      }

      console.log('Credits spent successfully');
      setProgress(30);

      // Update user context with new credit balance
      await refreshUser();
      setProgress(40);

      // Send file directly to edge function for processing
      console.log('Sending file to analysis...');
      const formData = new FormData();
      formData.append('file', file);
      formData.append('model', aiModel);
      formData.append('documentType', fileType);

      setProgress(50);

      try {
        console.log('Calling analyze-document function...');
        const { data, error: analysisError } = await supabase.functions.invoke('analyze-document', {
          body: formData
        });

        console.log('Analysis response:', { data, error: analysisError });
        setProgress(80);

        if (analysisError) {
          throw new Error(analysisError.message || "Erro ao processar a análise do documento");
        }

        if (!data || !data.points) {
          throw new Error("Resposta inválida da análise");
        }
        
        setProgress(100);
        console.log('Analysis completed successfully');

        const analysis: DocumentAnalysis = {
          id: crypto.randomUUID(),
          userId: user.id,
          fileName: file.name,
          fileUrl: URL.createObjectURL(file),
          type: fileType,
          uploadedAt: new Date().toISOString(),
          analyzedAt: new Date().toISOString(),
          isPrivate: false,
          points: data.points
        };

        const leadCount = data.points?.length || 0;
        const highPriorityCount = data.points?.filter((p: any) => p.priority === 'high')?.length || 0;

        toast({
          title: "✨ Análise de leads concluída!",
          description: `Foram identificados ${leadCount} leads, sendo ${highPriorityCount} de alta prioridade usando ${analysisType}. ${ANALYSIS_COST} créditos debitados.`,
          variant: "default",
        });

        if (onAnalysisComplete) {
          onAnalysisComplete(analysis);
        }
      } catch (apiError: any) {
        console.error('Erro na API de análise:', apiError);
        
        // Refund credits if analysis failed
        try {
          await supabase.functions.invoke('manage-credits', {
            body: { 
              action: 'grant',
              amount: ANALYSIS_COST,
              reason: `Reembolso por falha na análise: ${file.name}`
            }
          });
          await refreshUser();
        } catch (refundError) {
          console.error('Erro ao reembolsar créditos:', refundError);
        }
        
        throw new Error("Não foi possível completar a análise do documento. Seus créditos foram reembolsados.");
      }
    } catch (err: any) {
      console.error('Erro ao analisar documento:', err);
      setError(err.message || 'Ocorreu um erro ao analisar o documento. Por favor, tente novamente.');
      setProgress(0);
      toast({
        title: "Erro na análise",
        description: err.message || "Não foi possível analisar o documento. Tente novamente.",
        variant: "destructive",
      });
    } finally {
      setIsUploading(false);
    }
  };
  
  return (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle className="text-2xl flex items-center gap-2">
          <TrendingUp className="h-6 w-6 text-primary" />
          Análise Inteligente de Documentos
        </CardTitle>
        <CardDescription>
          Use IA para identificar leads, oportunidades e informações importantes em editais e processos
        </CardDescription>
        
        {/* Credit display */}
        {user && (
          <div className="flex items-center justify-between p-3 bg-muted/50 rounded-lg">
            <div className="flex items-center gap-2">
              <Coins className="h-4 w-4 text-yellow-500" />
              <span className="text-sm font-medium">Seus créditos: {user.credits}</span>
            </div>
            <div className="text-xs text-muted-foreground">
              Custo desta análise: {ANALYSIS_COST} créditos
            </div>
          </div>
        )}
      </CardHeader>
      <CardContent>
        {error && (
          <Alert variant="destructive" className="mb-4">
            <AlertCircle className="h-4 w-4" />
            <AlertTitle>Erro</AlertTitle>
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}
        
        {!hasEnoughCredits && user && (
          <Alert className="mb-4">
            <AlertCircle className="h-4 w-4" />
            <AlertTitle>Créditos insuficientes</AlertTitle>
            <AlertDescription>
              Você precisa de pelo menos {ANALYSIS_COST} créditos para fazer uma análise. 
              Considere upgradar seu plano ou compartilhar leads para ganhar mais créditos.
            </AlertDescription>
          </Alert>
        )}
        
        {isUploading ? (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <FileText className="h-5 w-5 text-primary" />
                <div className="text-sm font-medium">{file?.name}</div>
              </div>
              <Button 
                variant="ghost" 
                size="sm" 
                className="h-8 w-8 p-0" 
                onClick={clearFile}
                disabled={progress === 100}
              >
                <X className="h-4 w-4" />
                <span className="sr-only">Cancelar</span>
              </Button>
            </div>
            
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>Progresso da Análise</span>
                <span>{Math.round(progress)}%</span>
              </div>
              <Progress value={progress} />
              {progress < 100 && progress > 10 && (
                <p className="text-xs text-muted-foreground">
                  {progress < 50 ? "Preparando análise e debitando créditos..." :
                   progress < 80 ? (aiModel === 'native' ? "Analisando com algoritmo nativo... Identificando leads e oportunidades." :
                      `Analisando com ${aiModel === 'openai' ? 'OpenAI' : aiModel === 'mistral' ? 'Mistral' : 'Claude'}... Identificando leads e oportunidades.`) :
                    "Finalizando análise..."}
                </p>
              )}
            </div>
            
            {progress === 100 && !uploadedDocumentId && (
              <Alert className="bg-accent/20 border-accent">
                <CheckCircle className="h-4 w-4 text-accent" />
                <AlertTitle>✨ Análise concluída!</AlertTitle>
                <AlertDescription>
                  Seus leads e oportunidades foram identificados com sucesso!
                </AlertDescription>
              </Alert>
            )}

            {progress === 100 && uploadedDocumentId && (
              <Alert className="bg-blue-50 border-blue-200">
                <CheckCircle className="h-4 w-4 text-blue-600" />
                <AlertTitle>Upload Concluído!</AlertTitle>
                <AlertDescription>
                  Documento enviado com sucesso. O processamento especializado está sendo preparado abaixo.
                </AlertDescription>
              </Alert>
            )}
          </div>
        ) : (
          <>
            {/* Show large document processing interface if document is uploaded */}
            {uploadedDocumentId && fileUrl && file && (
              <div className="mb-6">
                <LargeDocumentProcessor
                  documentId={uploadedDocumentId}
                  fileUrl={fileUrl}
                  fileName={file.name}
                  fileSize={file.size}
                  model={aiModel}
                  documentType={fileType}
                  onComplete={(result) => {
                    console.log('Large document processing completed:', result);
                    toast({
                      title: "Processamento Concluído",
                      description: "Documento processado com sucesso! Verifique os resultados na página de documentos.",
                    });
                  }}
                  onError={(error) => {
                    console.error('Large document processing failed:', error);
                  }}
                />
              </div>
            )}

            {/* Only show upload interface if no document is uploaded yet */}
            {!uploadedDocumentId && (
              <>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">Tipo de documento</label>
                    <Select value={fileType} onValueChange={(value: DocumentType) => setFileType(value)}>
                      <SelectTrigger>
                        <SelectValue placeholder="Selecione o tipo de documento" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="edital">Edital de Leilão</SelectItem>
                        <SelectItem value="processo">Processo Judicial</SelectItem>
                        <SelectItem value="laudo">Laudo Técnico</SelectItem>
                        <SelectItem value="outro">Outro</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  
                  <ModelSelector 
                    value={aiModel} 
                    onValueChange={setAiModel}
                    disabled={isUploading}
                  />
                </div>

                {/* Show large processing option if file is large */}
                {file && shouldUseLargeProcessing && (
                  <Alert className="mb-4">
                    <Zap className="h-4 w-4" />
                    <AlertTitle>Documento Grande Detectado</AlertTitle>
                    <AlertDescription className="mt-2">
                      <div className="space-y-2">
                        <p>
                          Este documento ({(file.size / (1024 * 1024)).toFixed(2)}MB) é considerado grande 
                          e será processado usando nosso sistema especializado para melhor performance.
                        </p>
                        <div className="flex items-center gap-2">
                          <Badge variant="secondary" className="flex items-center gap-1">
                            <Zap className="h-3 w-3" />
                            Processamento Paralelo
                          </Badge>
                          <Badge variant="secondary">
                            Análise em Lotes
                          </Badge>
                          <Badge variant="secondary">
                            Monitoramento em Tempo Real
                          </Badge>
                        </div>
                      </div>
                    </AlertDescription>
                  </Alert>
                )}
            
            <div
              className="border-2 border-dashed rounded-lg p-12 text-center hover:bg-muted/50 transition-colors cursor-pointer"
              onDragOver={handleDragOver}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
            >
              <div className="flex flex-col items-center gap-2">
                <Upload className="h-10 w-10 text-muted-foreground" />
                <h3 className="font-medium text-lg">Arraste um arquivo ou clique para selecionar</h3>
                <p className="text-sm text-muted-foreground">
                  Suportamos arquivos PDF de até 50MB e 1000 páginas
                </p>
                {file && (
                  <div className="mt-2 flex items-center gap-2 text-sm bg-secondary/10 p-2 rounded-md">
                    <FileText className="h-4 w-4 text-secondary" />
                    <span className="font-medium">{file.name}</span>
                    <Button 
                      variant="ghost" 
                      size="sm" 
                      className="h-6 w-6 p-0 ml-1" 
                      onClick={(e) => {
                        e.stopPropagation();
                        clearFile();
                      }}
                    >
                      <X className="h-3 w-3" />
                      <span className="sr-only">Remover</span>
                    </Button>
                  </div>
                )}
                
                <Input
                  ref={fileInputRef}
                  type="file"
                  accept="application/pdf"
                  className="hidden"
                  onChange={handleFileChange}
                />
              </div>
                </div>
              </>
            )}
          </>
        )}
      </CardContent>
      {!uploadedDocumentId && (
        <CardFooter className="flex justify-between">
          <Button 
            variant="ghost" 
            onClick={clearFile}
            disabled={!file || isUploading}
          >
            Limpar
          </Button>
          <Button 
            onClick={handleSubmit} 
            disabled={!file || isUploading || progress === 100 || !hasEnoughCredits}
            className="bg-primary hover:bg-primary/90"
          >
            {isUploading ? 
              (useLargeProcessing || shouldUseLargeProcessing ? 'Preparando Processamento Grande...' :
               aiModel === 'native' ? 'Analisando com Algoritmo Nativo...' : 
               `Analisando com ${aiModel === 'openai' ? 'OpenAI' : aiModel === 'mistral' ? 'Mistral' : 'Claude'}...`) : 
              `${useLargeProcessing || shouldUseLargeProcessing ? 'Iniciar Processamento Grande' : 'Iniciar Análise'} (${ANALYSIS_COST} créditos)`}
          </Button>
        </CardFooter>
      )}
    </Card>
  );
}
