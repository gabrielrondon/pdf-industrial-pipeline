
import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from "https://esm.sh/@supabase/supabase-js@2"

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    const supabaseClient = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') ?? ''
    )

    // Recriar tabela de embeddings com JSONB
    const { error: dropError } = await supabaseClient.rpc('exec_sql', {
      sql: 'DROP TABLE IF EXISTS public.document_embeddings CASCADE'
    })

    const { error: createError } = await supabaseClient.rpc('exec_sql', {
      sql: `
        CREATE TABLE public.document_embeddings (
          id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
          chunk_id UUID NOT NULL,
          embedding JSONB NOT NULL,
          metadata JSONB DEFAULT '{}',
          created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
          FOREIGN KEY (chunk_id) REFERENCES public.document_chunks(id) ON DELETE CASCADE
        );
        
        ALTER TABLE public.document_embeddings ENABLE ROW LEVEL SECURITY;
        
        CREATE POLICY "Users can view embeddings of their document chunks" 
          ON public.document_embeddings 
          FOR SELECT 
          USING (
            EXISTS (
              SELECT 1 FROM public.document_chunks 
              JOIN public.documents ON documents.id = document_chunks.document_id
              WHERE document_chunks.id = document_embeddings.chunk_id 
              AND documents.user_id = auth.uid()
            )
          );

        CREATE POLICY "Users can insert embeddings for their document chunks" 
          ON public.document_embeddings 
          FOR INSERT 
          WITH CHECK (
            EXISTS (
              SELECT 1 FROM public.document_chunks 
              JOIN public.documents ON documents.id = document_chunks.document_id
              WHERE document_chunks.id = document_embeddings.chunk_id 
              AND documents.user_id = auth.uid()
            )
          );
        
        CREATE INDEX idx_document_embeddings_chunk_id ON public.document_embeddings(chunk_id);
      `
    })

    if (createError) {
      throw createError
    }

    return new Response(JSON.stringify({ success: true }), {
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    })

  } catch (error) {
    console.error('Error setting up vector tables:', error)
    return new Response(JSON.stringify({ 
      error: 'Internal server error',
      details: error.message 
    }), {
      status: 500,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    })
  }
})
