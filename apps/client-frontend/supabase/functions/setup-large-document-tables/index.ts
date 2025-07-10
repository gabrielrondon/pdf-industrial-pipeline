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

    console.log('Setting up tables for large document processing...');

    // Create processing_jobs table if it doesn't exist
    await supabaseClient.rpc('exec_sql', {
      sql: `
        CREATE TABLE IF NOT EXISTS processing_jobs (
          id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
          document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
          status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
          progress INTEGER NOT NULL DEFAULT 0 CHECK (progress >= 0 AND progress <= 100),
          details TEXT,
          error_message TEXT,
          config JSONB,
          created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
          started_at TIMESTAMP WITH TIME ZONE,
          updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
          completed_at TIMESTAMP WITH TIME ZONE,
          UNIQUE(document_id)
        );
      `
    });

    // Create chunk_summaries table for storing chunk-level summaries
    await supabaseClient.rpc('exec_sql', {
      sql: `
        CREATE TABLE IF NOT EXISTS chunk_summaries (
          id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
          document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
          chunk_id TEXT NOT NULL,
          summary TEXT NOT NULL,
          pages INTEGER[],
          created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
      `
    });

    // Add chunk_id column to analysis_points if it doesn't exist
    await supabaseClient.rpc('exec_sql', {
      sql: `
        ALTER TABLE analysis_points 
        ADD COLUMN IF NOT EXISTS chunk_id TEXT;
      `
    });

    // Add additional columns to documents table for large document support
    await supabaseClient.rpc('exec_sql', {
      sql: `
        ALTER TABLE documents 
        ADD COLUMN IF NOT EXISTS total_points INTEGER DEFAULT 0,
        ADD COLUMN IF NOT EXISTS processing_method TEXT DEFAULT 'standard',
        ADD COLUMN IF NOT EXISTS file_size_mb DECIMAL,
        ADD COLUMN IF NOT EXISTS total_pages INTEGER;
      `
    });

    // Create indexes for performance
    await supabaseClient.rpc('exec_sql', {
      sql: `
        CREATE INDEX IF NOT EXISTS idx_processing_jobs_document_id ON processing_jobs(document_id);
        CREATE INDEX IF NOT EXISTS idx_processing_jobs_status ON processing_jobs(status);
        CREATE INDEX IF NOT EXISTS idx_chunk_summaries_document_id ON chunk_summaries(document_id);
        CREATE INDEX IF NOT EXISTS idx_chunk_summaries_chunk_id ON chunk_summaries(chunk_id);
        CREATE INDEX IF NOT EXISTS idx_analysis_points_chunk_id ON analysis_points(chunk_id);
        CREATE INDEX IF NOT EXISTS idx_documents_processing_method ON documents(processing_method);
      `
    });

    // Set up Row Level Security policies
    await supabaseClient.rpc('exec_sql', {
      sql: `
        ALTER TABLE processing_jobs ENABLE ROW LEVEL SECURITY;
        ALTER TABLE chunk_summaries ENABLE ROW LEVEL SECURITY;

        -- RLS for processing_jobs
        CREATE POLICY IF NOT EXISTS "Users can view their own processing jobs" ON processing_jobs
          FOR SELECT USING (
            document_id IN (
              SELECT id FROM documents WHERE user_id = auth.uid()
            )
          );

        CREATE POLICY IF NOT EXISTS "Users can update their own processing jobs" ON processing_jobs
          FOR UPDATE USING (
            document_id IN (
              SELECT id FROM documents WHERE user_id = auth.uid()
            )
          );

        CREATE POLICY IF NOT EXISTS "Users can insert processing jobs for their documents" ON processing_jobs
          FOR INSERT WITH CHECK (
            document_id IN (
              SELECT id FROM documents WHERE user_id = auth.uid()
            )
          );

        -- RLS for chunk_summaries
        CREATE POLICY IF NOT EXISTS "Users can view their own chunk summaries" ON chunk_summaries
          FOR SELECT USING (
            document_id IN (
              SELECT id FROM documents WHERE user_id = auth.uid()
            )
          );

        CREATE POLICY IF NOT EXISTS "Service role can manage all processing jobs" ON processing_jobs
          FOR ALL USING (auth.role() = 'service_role');

        CREATE POLICY IF NOT EXISTS "Service role can manage all chunk summaries" ON chunk_summaries
          FOR ALL USING (auth.role() = 'service_role');
      `
    });

    // Create a function to start large document processing
    await supabaseClient.rpc('exec_sql', {
      sql: `
        CREATE OR REPLACE FUNCTION start_large_document_processing(
          p_document_id UUID,
          p_config JSONB DEFAULT '{}'::jsonb
        )
        RETURNS UUID
        LANGUAGE plpgsql
        SECURITY DEFINER
        AS $$
        DECLARE
          job_id UUID;
        BEGIN
          -- Insert or update processing job
          INSERT INTO processing_jobs (document_id, status, config)
          VALUES (p_document_id, 'pending', p_config)
          ON CONFLICT (document_id) 
          DO UPDATE SET 
            status = 'pending',
            config = EXCLUDED.config,
            progress = 0,
            details = NULL,
            error_message = NULL,
            created_at = NOW(),
            started_at = NULL,
            updated_at = NOW(),
            completed_at = NULL
          RETURNING id INTO job_id;

          -- Update document processing method
          UPDATE documents 
          SET processing_method = 'large_document'
          WHERE id = p_document_id;

          RETURN job_id;
        END;
        $$;
      `
    });

    // Create function to get processing status
    await supabaseClient.rpc('exec_sql', {
      sql: `
        CREATE OR REPLACE FUNCTION get_document_processing_status(p_document_id UUID)
        RETURNS TABLE (
          status TEXT,
          progress INTEGER,
          details TEXT,
          error_message TEXT,
          created_at TIMESTAMP WITH TIME ZONE,
          started_at TIMESTAMP WITH TIME ZONE,
          completed_at TIMESTAMP WITH TIME ZONE
        )
        LANGUAGE plpgsql
        SECURITY DEFINER
        AS $$
        BEGIN
          RETURN QUERY
          SELECT 
            pj.status,
            pj.progress,
            pj.details,
            pj.error_message,
            pj.created_at,
            pj.started_at,
            pj.completed_at
          FROM processing_jobs pj
          WHERE pj.document_id = p_document_id;
        END;
        $$;
      `
    });

    console.log('Large document processing tables setup completed successfully');

    return new Response(JSON.stringify({ 
      success: true, 
      message: 'Large document processing tables setup completed'
    }), {
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    });

  } catch (error) {
    console.error('Error setting up large document tables:', error);
    
    return new Response(JSON.stringify({ 
      error: 'Failed to setup tables',
      details: error.message 
    }), {
      status: 500,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    });
  }
});