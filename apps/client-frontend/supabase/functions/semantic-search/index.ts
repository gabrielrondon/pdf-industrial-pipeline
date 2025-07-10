
import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from "https://esm.sh/@supabase/supabase-js@2"

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

function cosineSimilarity(a: number[], b: number[]): number {
  if (a.length !== b.length) return 0;

  let dotProduct = 0;
  let normA = 0;
  let normB = 0;

  for (let i = 0; i < a.length; i++) {
    dotProduct += a[i] * b[i];
    normA += a[i] * a[i];
    normB += b[i] * b[i];
  }

  const norm = Math.sqrt(normA) * Math.sqrt(normB);
  return norm > 0 ? dotProduct / norm : 0;
}

async function generateQueryEmbedding(query: string, apiKey: string): Promise<number[]> {
  const response = await fetch('https://api.openai.com/v1/embeddings', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${apiKey}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      model: 'text-embedding-3-small',
      input: query,
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
    const { query, documentIds, limit = 10, threshold = 0.7 } = await req.json();
    
    if (!query) {
      return new Response(JSON.stringify({ error: 'Query is required' }), {
        status: 400,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      })
    }

    const supabaseClient = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') ?? ''
    )

    const openaiApiKey = Deno.env.get('OPENAI_API_KEY');
    
    if (!openaiApiKey) {
      // Fallback to text-based search
      let searchQuery = supabaseClient
        .from('document_chunks')
        .select(`
          id,
          content,
          word_count,
          page_start,
          page_end,
          documents:document_id (
            id,
            file_name,
            type
          )
        `)
        .textSearch('content', query, { type: 'websearch' })
        .order('word_count', { ascending: false })
        .limit(limit);

      if (documentIds && documentIds.length > 0) {
        searchQuery = searchQuery.in('document_id', documentIds);
      }

      const { data: chunks, error } = await searchQuery;

      if (error) {
        throw new Error(`Search error: ${error.message}`);
      }

      return new Response(JSON.stringify({
        results: chunks?.map(chunk => ({
          chunkId: chunk.id,
          content: chunk.content,
          similarity: 0.8, // Placeholder similarity for text search
          wordCount: chunk.word_count,
          pageStart: chunk.page_start,
          pageEnd: chunk.page_end,
          document: chunk.documents
        })) || [],
        searchMethod: 'text_search'
      }), {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      })
    }

    // Generate embedding for the query
    const queryEmbedding = await generateQueryEmbedding(query, openaiApiKey);

    // Get all embeddings for specified documents
    let embeddingsQuery = supabaseClient
      .from('document_embeddings')
      .select(`
        id,
        chunk_id,
        embedding,
        metadata,
        document_chunks:chunk_id (
          id,
          content,
          word_count,
          page_start,
          page_end,
          documents:document_id (
            id,
            file_name,
            type
          )
        )
      `);

    if (documentIds && documentIds.length > 0) {
      embeddingsQuery = embeddingsQuery.in('document_chunks.document_id', documentIds);
    }

    const { data: embeddings, error: embeddingsError } = await embeddingsQuery;

    if (embeddingsError) {
      throw new Error(`Failed to fetch embeddings: ${embeddingsError.message}`);
    }

    if (!embeddings || embeddings.length === 0) {
      return new Response(JSON.stringify({
        results: [],
        message: 'No embeddings found for the specified documents'
      }), {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      })
    }

    // Calculate similarities
    const similarities = embeddings.map(embedding => {
      const embeddingVector = JSON.parse(embedding.embedding);
      const similarity = cosineSimilarity(queryEmbedding, embeddingVector);
      
      return {
        chunkId: embedding.chunk_id,
        content: embedding.document_chunks?.content || '',
        similarity,
        wordCount: embedding.document_chunks?.word_count || 0,
        pageStart: embedding.document_chunks?.page_start,
        pageEnd: embedding.document_chunks?.page_end,
        document: embedding.document_chunks?.documents,
        metadata: embedding.metadata
      };
    });

    // Filter by threshold and sort by similarity
    const results = similarities
      .filter(result => result.similarity >= threshold)
      .sort((a, b) => b.similarity - a.similarity)
      .slice(0, limit);

    console.log(`Semantic search for "${query}" found ${results.length} results`);

    return new Response(JSON.stringify({
      results,
      searchMethod: 'semantic_search',
      queryEmbedding: queryEmbedding.slice(0, 5) // First 5 dimensions for debugging
    }), {
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    })

  } catch (error) {
    console.error('Error in semantic search:', error);
    return new Response(JSON.stringify({ 
      error: 'Internal server error',
      details: error.message 
    }), {
      status: 500,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    })
  }
})
