
import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from "https://esm.sh/@supabase/supabase-js@2"
import pdfParse from "https://esm.sh/pdf-parse@1.1.1"

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

interface ChunkResult {
  content: string;
  wordCount: number;
  startIndex: number;
  endIndex: string;
  pageStart?: number;
  pageEnd?: number;
}

class TextChunker {
  private readonly targetWords: number;
  private readonly overlapWords: number;

  constructor(targetWords = 450, overlapWords = 50) {
    this.targetWords = targetWords;
    this.overlapWords = overlapWords;
  }

  chunkText(text: string, pageNumber?: number): ChunkResult[] {
    const words = text.split(/\s+/).filter(word => word.length > 0);
    const chunks: ChunkResult[] = [];
    
    let startIdx = 0;

    while (startIdx < words.length) {
      const endIdx = Math.min(startIdx + this.targetWords, words.length);
      const chunkWords = words.slice(startIdx, endIdx);
      const content = chunkWords.join(' ');
      
      chunks.push({
        content,
        wordCount: chunkWords.length,
        startIndex: startIdx,
        endIndex: `${endIdx - 1}`,
        pageStart: pageNumber,
        pageEnd: pageNumber
      });

      if (endIdx >= words.length) break;
      startIdx = endIdx - this.overlapWords;
    }

    return chunks;
  }

  chunkPages(pages: { content: string; pageNumber: number }[]): ChunkResult[] {
    const allChunks: ChunkResult[] = [];
    
    for (let i = 0; i < pages.length; i++) {
      const page = pages[i];
      const pageChunks = this.chunkText(page.content, page.pageNumber);
      allChunks.push(...pageChunks);
    }

    return allChunks;
  }
}

async function extractTextByPage(arrayBuffer: ArrayBuffer): Promise<{ content: string; pageNumber: number }[]> {
  const pages: { content: string; pageNumber: number }[] = [];
  let currentPage = 0;

  await pdfParse(new Uint8Array(arrayBuffer), {
    pagerender: async (pageData: any) => {
      currentPage++;
      const textContent = await pageData.getTextContent();
      const text = textContent.items
        .map((item: any) => item.str)
        .join(' ')
        .replace(/\s+/g, ' ')
        .trim();
      
      if (text && text.length > 50) { // Filter out pages with minimal content
        pages.push({
          content: text,
          pageNumber: currentPage
        });
      }
      return '';
    }
  });

  return pages;
}

async function generateEmbedding(text: string, apiKey: string): Promise<number[]> {
  const response = await fetch('https://api.openai.com/v1/embeddings', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${apiKey}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      model: 'text-embedding-3-small',
      input: text,
      encoding_format: 'float'
    }),
  });

  if (!response.ok) {
    throw new Error(`OpenAI API error: ${response.statusText}`);
  }

  const data = await response.json();
  return data.data[0].embedding;
}

serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    const { documentId, fileUrl } = await req.json();
    
    if (!documentId || !fileUrl) {
      return new Response(JSON.stringify({ error: 'Missing documentId or fileUrl' }), {
        status: 400,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      })
    }

    const supabaseClient = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') ?? ''
    )

    const openaiApiKey = Deno.env.get('OPENAI_API_KEY');

    // Update job status to processing
    await supabaseClient
      .from('processing_jobs')
      .update({ 
        status: 'processing', 
        started_at: new Date().toISOString(),
        progress: 10
      })
      .eq('document_id', documentId);

    console.log(`Starting processing for document ${documentId}`);

    // Download and process PDF
    const fileResponse = await fetch(fileUrl);
    if (!fileResponse.ok) {
      throw new Error(`Failed to download file: ${fileResponse.statusText}`);
    }

    const arrayBuffer = await fileResponse.arrayBuffer();
    console.log(`Downloaded file, size: ${arrayBuffer.byteLength} bytes`);

    // Update progress
    await supabaseClient
      .from('processing_jobs')
      .update({ progress: 30 })
      .eq('document_id', documentId);

    // Extract text by pages
    const pages = await extractTextByPage(arrayBuffer);
    console.log(`Extracted ${pages.length} pages`);

    // Update progress
    await supabaseClient
      .from('processing_jobs')
      .update({ progress: 50 })
      .eq('document_id', documentId);

    // Chunk text
    const chunker = new TextChunker();
    const chunks = chunker.chunkPages(pages);
    console.log(`Created ${chunks.length} chunks`);

    // Save chunks to database
    const chunksToInsert = chunks.map((chunk, index) => ({
      document_id: documentId,
      chunk_index: index,
      content: chunk.content,
      word_count: chunk.wordCount,
      page_start: chunk.pageStart,
      page_end: chunk.pageEnd
    }));

    const { data: insertedChunks, error: chunkError } = await supabaseClient
      .from('document_chunks')
      .insert(chunksToInsert)
      .select('id, content');

    if (chunkError) {
      throw new Error(`Failed to save chunks: ${chunkError.message}`);
    }

    console.log(`Saved ${insertedChunks.length} chunks`);

    // Update progress
    await supabaseClient
      .from('processing_jobs')
      .update({ progress: 70 })
      .eq('document_id', documentId);

    // Generate embeddings if OpenAI API key is available
    if (openaiApiKey && insertedChunks) {
      console.log('Generating embeddings...');
      
      const embeddingsToInsert = [];
      
      for (let i = 0; i < insertedChunks.length; i++) {
        const chunk = insertedChunks[i];
        
        try {
          const embedding = await generateEmbedding(chunk.content, openaiApiKey);
          
          embeddingsToInsert.push({
            chunk_id: chunk.id,
            embedding: JSON.stringify(embedding),
            metadata: {
              word_count: chunks[i].wordCount,
              page_start: chunks[i].pageStart,
              page_end: chunks[i].pageEnd
            }
          });

          // Update progress
          const progressValue = 70 + Math.floor((i / insertedChunks.length) * 20);
          await supabaseClient
            .from('processing_jobs')
            .update({ progress: progressValue })
            .eq('document_id', documentId);

          // Rate limiting
          await new Promise(resolve => setTimeout(resolve, 100));
          
        } catch (embeddingError) {
          console.error(`Failed to generate embedding for chunk ${i}:`, embeddingError);
          // Continue with other chunks
        }
      }

      if (embeddingsToInsert.length > 0) {
        const { error: embeddingError } = await supabaseClient
          .from('document_embeddings')
          .insert(embeddingsToInsert);

        if (embeddingError) {
          console.error('Failed to save embeddings:', embeddingError);
        } else {
          console.log(`Saved ${embeddingsToInsert.length} embeddings`);
        }
      }
    } else {
      console.log('Skipping embeddings - no OpenAI API key provided');
    }

    // Complete the job
    await supabaseClient
      .from('processing_jobs')
      .update({ 
        status: 'completed', 
        progress: 100,
        completed_at: new Date().toISOString()
      })
      .eq('document_id', documentId);

    console.log(`Processing completed for document ${documentId}`);

    return new Response(JSON.stringify({ 
      success: true, 
      chunksCount: chunks.length,
      embeddingsGenerated: openaiApiKey ? true : false
    }), {
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    })

  } catch (error) {
    console.error('Error processing document:', error);
    
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
          error_message: error.message,
          completed_at: new Date().toISOString()
        })
        .eq('document_id', documentId);
    }

    return new Response(JSON.stringify({ 
      error: 'Internal server error',
      details: error.message 
    }), {
      status: 500,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    })
  }
})
