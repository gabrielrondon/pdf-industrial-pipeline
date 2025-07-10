import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from "https://esm.sh/@supabase/supabase-js@2"
import pdfParse from "https://esm.sh/pdf-parse@1.1.1"

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

interface ProcessingConfig {
  maxPagesPerBatch: number;
  chunkSize: number; // words per chunk
  chunkOverlap: number; // words overlap
  maxConcurrentAnalysis: number;
  analysisTimeout: number; // ms
}

interface AnalysisPoint {
  id: string;
  title: string;
  comment: string;
  status: 'confirmado' | 'alerta' | 'não identificado';
  type: string;
  category: string;
  value?: string | null;
  priority: 'high' | 'medium' | 'low';
  legal_reference?: string | null;
  page?: number;
  chunk_id?: string;
}

interface ChunkAnalysisResult {
  points: AnalysisPoint[];
  summary?: string;
  chunk_id: string;
  pages: number[];
}

interface DocumentBatch {
  batchId: string;
  pages: { content: string; pageNumber: number }[];
  startPage: number;
  endPage: number;
}

const DEFAULT_CONFIG: ProcessingConfig = {
  maxPagesPerBatch: 50, // Process 50 pages at a time
  chunkSize: 800, // Larger chunks for better context
  chunkOverlap: 100, // Meaningful overlap
  maxConcurrentAnalysis: 3, // Parallel AI analysis
  analysisTimeout: 120000 // 2 minutes per chunk
};

class LargeDocumentProcessor {
  private config: ProcessingConfig;
  private supabase: any;
  private documentId: string;

  constructor(supabase: any, documentId: string, config: ProcessingConfig = DEFAULT_CONFIG) {
    this.supabase = supabase;
    this.documentId = documentId;
    this.config = config;
  }

  async updateProgress(progress: number, status?: string, details?: string) {
    await this.supabase
      .from('processing_jobs')
      .update({ 
        progress,
        status: status || 'processing',
        details,
        updated_at: new Date().toISOString()
      })
      .eq('document_id', this.documentId);
  }

  async extractPagesInBatches(arrayBuffer: ArrayBuffer): Promise<DocumentBatch[]> {
    const allPages: { content: string; pageNumber: number }[] = [];
    let currentPage = 0;

    console.log('Starting page extraction...');
    
    await pdfParse(new Uint8Array(arrayBuffer), {
      pagerender: async (pageData: any) => {
        currentPage++;
        try {
          const textContent = await pageData.getTextContent();
          const text = textContent.items
            .map((item: any) => item.str)
            .join(' ')
            .replace(/\s+/g, ' ')
            .trim();
          
          if (text && text.length > 50) {
            allPages.push({
              content: text,
              pageNumber: currentPage
            });
          }
        } catch (error) {
          console.error(`Error processing page ${currentPage}:`, error);
        }
        return '';
      }
    });

    console.log(`Extracted ${allPages.length} pages from ${currentPage} total pages`);

    // Create batches
    const batches: DocumentBatch[] = [];
    const { maxPagesPerBatch } = this.config;

    for (let i = 0; i < allPages.length; i += maxPagesPerBatch) {
      const batchPages = allPages.slice(i, i + maxPagesPerBatch);
      const startPage = batchPages[0].pageNumber;
      const endPage = batchPages[batchPages.length - 1].pageNumber;
      
      batches.push({
        batchId: `batch_${startPage}_${endPage}`,
        pages: batchPages,
        startPage,
        endPage
      });
    }

    console.log(`Created ${batches.length} batches for processing`);
    return batches;
  }

  createChunksFromBatch(batch: DocumentBatch): Array<{
    content: string;
    wordCount: number;
    pages: number[];
    chunkId: string;
    batchId: string;
  }> {
    const chunks = [];
    const { chunkSize, chunkOverlap } = this.config;
    
    // Combine all pages in batch into single text with page markers
    const combinedText = batch.pages
      .map(page => `[PAGE_${page.pageNumber}] ${page.content}`)
      .join(' ');
    
    const words = combinedText.split(/\s+/).filter(word => word.length > 0);
    let chunkIndex = 0;
    
    for (let startIdx = 0; startIdx < words.length; startIdx += chunkSize - chunkOverlap) {
      const endIdx = Math.min(startIdx + chunkSize, words.length);
      const chunkWords = words.slice(startIdx, endIdx);
      const content = chunkWords.join(' ');
      
      // Extract page numbers from this chunk
      const pageMatches = content.match(/\[PAGE_(\d+)\]/g) || [];
      const pages = [...new Set(pageMatches.map(match => 
        parseInt(match.replace(/\[PAGE_(\d+)\]/, '$1'))
      ))].sort((a, b) => a - b);
      
      // Clean content by removing page markers
      const cleanContent = content.replace(/\[PAGE_\d+\]\s*/g, '').trim();
      
      if (cleanContent.length > 100) { // Only keep substantial chunks
        chunks.push({
          content: cleanContent,
          wordCount: chunkWords.length,
          pages,
          chunkId: `${batch.batchId}_chunk_${chunkIndex}`,
          batchId: batch.batchId
        });
        chunkIndex++;
      }
      
      if (endIdx >= words.length) break;
    }
    
    return chunks;
  }

  async analyzeChunkWithAI(chunk: any, model: string, documentType: string): Promise<ChunkAnalysisResult> {
    const apiKey = Deno.env.get('OPENAI_API_KEY') || Deno.env.get('ANTHROPIC_API_KEY') || Deno.env.get('MISTRAL_API_KEY');
    
    if (!apiKey) {
      return this.analyzeChunkNative(chunk);
    }

    const prompt = `Analise este trecho de ${documentType} e identifique:
1. Informações sobre licitações e editais
2. Dados de avaliação de imóveis
3. Condições especiais ou restrições
4. Oportunidades de investimento

Trecho para análise (páginas ${chunk.pages.join('-')}):
${chunk.content}

Responda em JSON com formato:
{
  "points": [
    {
      "id": "único_id",
      "title": "Título do achado",
      "comment": "Descrição detalhada",
      "status": "confirmado|alerta|não identificado",
      "type": "tipo_da_informacao",
      "category": "categoria",
      "value": "valor_se_aplicavel",
      "priority": "high|medium|low",
      "legal_reference": "referencia_legal_se_aplicavel"
    }
  ],
  "summary": "Resumo dos principais achados deste trecho"
}`;

    try {
      const timeoutPromise = new Promise((_, reject) =>
        setTimeout(() => reject(new Error('Analysis timeout')), this.config.analysisTimeout)
      );

      const analysisPromise = this.callAI(prompt, model);
      const result = await Promise.race([analysisPromise, timeoutPromise]) as any;
      
      // Add chunk and page info to each point
      const points = result.points?.map((point: any) => ({
        ...point,
        id: point.id || `${chunk.chunkId}_${Date.now()}`,
        chunk_id: chunk.chunkId,
        page: chunk.pages.length === 1 ? chunk.pages[0] : undefined
      })) || [];

      return {
        points,
        summary: result.summary,
        chunk_id: chunk.chunkId,
        pages: chunk.pages
      };
    } catch (error) {
      console.error(`AI analysis failed for chunk ${chunk.chunkId}:`, error);
      return this.analyzeChunkNative(chunk);
    }
  }

  async callAI(prompt: string, model: string): Promise<any> {
    const openaiKey = Deno.env.get('OPENAI_API_KEY');
    const anthropicKey = Deno.env.get('ANTHROPIC_API_KEY');
    const mistralKey = Deno.env.get('MISTRAL_API_KEY');

    let apiKey: string;
    let url: string;
    let body: any;

    if (model === 'openai' && openaiKey) {
      apiKey = openaiKey;
      url = 'https://api.openai.com/v1/chat/completions';
      body = {
        model: 'gpt-4o',
        messages: [{ role: 'user', content: prompt }],
        max_tokens: 2000,
        temperature: 0.1
      };
    } else if (model === 'anthropic' && anthropicKey) {
      apiKey = anthropicKey;
      url = 'https://api.anthropic.com/v1/messages';
      body = {
        model: 'claude-3-sonnet-20240229',
        max_tokens: 2000,
        messages: [{ role: 'user', content: prompt }]
      };
    } else if (model === 'mistral' && mistralKey) {
      apiKey = mistralKey;
      url = 'https://api.mistral.ai/v1/chat/completions';
      body = {
        model: 'mistral-large-latest',
        messages: [{ role: 'user', content: prompt }],
        max_tokens: 2000
      };
    } else {
      throw new Error(`No API key available for model: ${model}`);
    }

    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiKey}`,
        'anthropic-version': model === 'anthropic' ? '2023-06-01' : undefined
      },
      body: JSON.stringify(body)
    });

    if (!response.ok) {
      throw new Error(`API request failed: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    const content = data.choices ? data.choices[0].message.content : data.content;
    
    try {
      return JSON.parse(content);
    } catch {
      throw new Error('Invalid JSON response from AI');
    }
  }

  analyzeChunkNative(chunk: any): ChunkAnalysisResult {
    const points: AnalysisPoint[] = [];
    const content = chunk.content.toLowerCase();
    
    // Native analysis rules for Brazilian auction documents
    const patterns = [
      {
        pattern: /leil[ãa]o|hasta\s+p[úu]blica|aliena[çc][ãa]o/gi,
        category: 'Licitação',
        type: 'Tipo de Procedimento',
        title: 'Procedimento Licitatório Identificado'
      },
      {
        pattern: /r\$\s*[\d.,]+|valor\s+de\s+avalia[çc][ãa]o/gi,
        category: 'Financeiro',
        type: 'Valor',
        title: 'Valor Monetário Identificado'
      },
      {
        pattern: /imovel|im[óo]vel|terreno|casa|apartamento|lote/gi,
        category: 'Bem',
        type: 'Imóvel',
        title: 'Imóvel para Leilão'
      }
    ];

    patterns.forEach((rule, index) => {
      const matches = content.match(rule.pattern);
      if (matches) {
        points.push({
          id: `${chunk.chunkId}_native_${index}`,
          title: rule.title,
          comment: `Identificado: ${matches.slice(0, 3).join(', ')}${matches.length > 3 ? '...' : ''}`,
          status: 'confirmado',
          type: rule.type,
          category: rule.category,
          priority: 'medium',
          chunk_id: chunk.chunkId,
          page: chunk.pages.length === 1 ? chunk.pages[0] : undefined
        });
      }
    });

    return {
      points,
      summary: `Análise nativa encontrou ${points.length} pontos relevantes.`,
      chunk_id: chunk.chunkId,
      pages: chunk.pages
    };
  }

  async processBatch(batch: DocumentBatch, model: string, documentType: string): Promise<ChunkAnalysisResult[]> {
    console.log(`Processing batch ${batch.batchId} (pages ${batch.startPage}-${batch.endPage})`);
    
    const chunks = this.createChunksFromBatch(batch);
    console.log(`Created ${chunks.length} chunks for batch ${batch.batchId}`);
    
    const results: ChunkAnalysisResult[] = [];
    const { maxConcurrentAnalysis } = this.config;
    
    // Process chunks in parallel batches
    for (let i = 0; i < chunks.length; i += maxConcurrentAnalysis) {
      const chunkBatch = chunks.slice(i, i + maxConcurrentAnalysis);
      
      const batchPromises = chunkBatch.map(chunk => 
        model === 'native' 
          ? Promise.resolve(this.analyzeChunkNative(chunk))
          : this.analyzeChunkWithAI(chunk, model, documentType)
      );
      
      try {
        const batchResults = await Promise.allSettled(batchPromises);
        
        batchResults.forEach((result, index) => {
          if (result.status === 'fulfilled') {
            results.push(result.value);
          } else {
            console.error(`Chunk analysis failed:`, result.reason);
            // Add fallback native analysis
            results.push(this.analyzeChunkNative(chunkBatch[index]));
          }
        });
        
        // Rate limiting between batch requests
        if (model !== 'native' && i + maxConcurrentAnalysis < chunks.length) {
          await new Promise(resolve => setTimeout(resolve, 1000));
        }
        
      } catch (error) {
        console.error(`Batch processing failed:`, error);
        // Fallback to native analysis for remaining chunks
        chunkBatch.forEach(chunk => {
          results.push(this.analyzeChunkNative(chunk));
        });
      }
    }
    
    return results;
  }

  async saveResults(allResults: ChunkAnalysisResult[]): Promise<void> {
    // Aggregate all analysis points
    const allPoints = allResults.flatMap(result => result.points);
    
    // Save analysis points to database
    if (allPoints.length > 0) {
      const pointsToInsert = allPoints.map(point => ({
        document_id: this.documentId,
        title: point.title,
        comment: point.comment,
        status: point.status,
        type: point.type,
        category: point.category,
        value: point.value,
        priority: point.priority,
        legal_reference: point.legal_reference,
        page: point.page,
        chunk_id: point.chunk_id,
        created_at: new Date().toISOString()
      }));

      const { error: pointsError } = await this.supabase
        .from('analysis_points')
        .insert(pointsToInsert);

      if (pointsError) {
        console.error('Failed to save analysis points:', pointsError);
        throw new Error(`Failed to save analysis: ${pointsError.message}`);
      }
    }

    // Save chunk summaries
    const summariesToInsert = allResults
      .filter(result => result.summary)
      .map(result => ({
        document_id: this.documentId,
        chunk_id: result.chunk_id,
        summary: result.summary,
        pages: result.pages,
        created_at: new Date().toISOString()
      }));

    if (summariesToInsert.length > 0) {
      const { error: summaryError } = await this.supabase
        .from('chunk_summaries')
        .insert(summariesToInsert);

      if (summaryError) {
        console.error('Failed to save summaries:', summaryError);
        // Don't throw error for summaries, they're optional
      }
    }

    // Update document analysis status
    const categories = [...new Set(allPoints.map(p => p.category))];
    const totalLeads = allPoints.filter(p => p.status === 'confirmado').length;

    await this.supabase
      .from('documents')
      .update({
        analysis_status: 'completed',
        total_leads: totalLeads,
        categories: categories,
        analyzed_at: new Date().toISOString(),
        total_points: allPoints.length
      })
      .eq('id', this.documentId);
  }
}

serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    const { documentId, fileUrl, model = 'native', documentType = 'edital', config } = await req.json();
    
    if (!documentId || !fileUrl) {
      return new Response(JSON.stringify({ error: 'Missing documentId or fileUrl' }), {
        status: 400,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      })
    }

    const supabaseClient = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') ?? ''
    );

    const processingConfig = { ...DEFAULT_CONFIG, ...config };
    const processor = new LargeDocumentProcessor(supabaseClient, documentId, processingConfig);

    // Initialize processing job
    await processor.updateProgress(5, 'starting', 'Initializing large document processing');
    
    console.log(`Starting large document processing for ${documentId} with model ${model}`);

    // Download file
    const fileResponse = await fetch(fileUrl);
    if (!fileResponse.ok) {
      throw new Error(`Failed to download file: ${fileResponse.statusText}`);
    }

    const arrayBuffer = await fileResponse.arrayBuffer();
    const fileSizeMB = arrayBuffer.byteLength / (1024 * 1024);
    console.log(`Downloaded file: ${fileSizeMB.toFixed(2)}MB`);
    
    await processor.updateProgress(15, 'processing', `Downloaded ${fileSizeMB.toFixed(2)}MB file`);

    // Extract pages in batches
    const batches = await processor.extractPagesInBatches(arrayBuffer);
    const totalPages = batches.reduce((sum, batch) => sum + batch.pages.length, 0);
    
    await processor.updateProgress(30, 'processing', `Extracted ${totalPages} pages in ${batches.length} batches`);

    // Process each batch
    const allResults: ChunkAnalysisResult[] = [];
    const progressPerBatch = 50 / batches.length; // 30% to 80% for batch processing
    
    for (let i = 0; i < batches.length; i++) {
      const batch = batches[i];
      console.log(`Processing batch ${i + 1}/${batches.length}: ${batch.batchId}`);
      
      try {
        const batchResults = await processor.processBatch(batch, model, documentType);
        allResults.push(...batchResults);
        
        const progress = 30 + Math.floor((i + 1) * progressPerBatch);
        const pointsFound = batchResults.reduce((sum, result) => sum + result.points.length, 0);
        
        await processor.updateProgress(
          progress, 
          'processing', 
          `Processed batch ${i + 1}/${batches.length}, found ${pointsFound} points`
        );
        
      } catch (error) {
        console.error(`Failed to process batch ${batch.batchId}:`, error);
        await processor.updateProgress(
          30 + Math.floor((i + 1) * progressPerBatch), 
          'processing', 
          `Warning: Batch ${i + 1} failed, continuing with next batch`
        );
      }
    }

    await processor.updateProgress(80, 'processing', 'Saving analysis results');

    // Save all results
    await processor.saveResults(allResults);

    const totalPoints = allResults.reduce((sum, result) => sum + result.points.length, 0);
    const confirmedLeads = allResults.reduce((sum, result) => 
      sum + result.points.filter(p => p.status === 'confirmado').length, 0
    );

    await processor.updateProgress(100, 'completed', 
      `Analysis complete: ${totalPoints} points found, ${confirmedLeads} confirmed leads`
    );

    console.log(`Large document processing completed for ${documentId}: ${totalPoints} points, ${confirmedLeads} leads`);

    return new Response(JSON.stringify({
      success: true,
      documentId,
      model,
      batches: batches.length,
      totalPages,
      totalPoints,
      confirmedLeads,
      processingTime: 'completed'
    }), {
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    });

  } catch (error) {
    console.error('Error in large document processing:', error);
    
    // Update job status to failed
    const { documentId } = await req.json().catch(() => ({}));
    if (documentId) {
      const supabaseClient = createClient(
        Deno.env.get('SUPABASE_URL') ?? '',
        Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') ?? ''
      );
      
      await supabaseClient
        .from('processing_jobs')
        .update({ 
          status: 'failed', 
          progress: 0,
          error_message: error.message,
          completed_at: new Date().toISOString()
        })
        .eq('document_id', documentId);
    }

    return new Response(JSON.stringify({ 
      error: 'Large document processing failed',
      details: error.message 
    }), {
      status: 500,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    });
  }
});