const { createClient } = require('@supabase/supabase-js');

// Use your Supabase credentials
const supabaseUrl = "https://rjbiyndpxqaallhjmbwm.supabase.co";
const supabaseServiceRoleKey = process.env.SUPABASE_SERVICE_ROLE_KEY;

if (!supabaseServiceRoleKey) {
  console.error('❌ SUPABASE_SERVICE_ROLE_KEY environment variable is required');
  console.log('💡 Get your service role key from: https://supabase.com/dashboard/project/rjbiyndpxqaallhjmbwm/settings/api');
  console.log('💡 Then run: SUPABASE_SERVICE_ROLE_KEY=your_key_here node scripts/setup-db.js');
  process.exit(1);
}

const supabase = createClient(supabaseUrl, supabaseServiceRoleKey);

async function setupDatabase() {
  console.log('🚀 Setting up large document processing database...');
  
  const queries = [
    {
      name: 'processing_jobs table',
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
    },
    {
      name: 'chunk_summaries table',
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
    },
    {
      name: 'analysis_points chunk_id column',
      sql: `ALTER TABLE analysis_points ADD COLUMN IF NOT EXISTS chunk_id TEXT;`
    },
    {
      name: 'documents table large document columns',
      sql: `
        ALTER TABLE documents 
        ADD COLUMN IF NOT EXISTS total_points INTEGER DEFAULT 0,
        ADD COLUMN IF NOT EXISTS processing_method TEXT DEFAULT 'standard',
        ADD COLUMN IF NOT EXISTS file_size_mb DECIMAL,
        ADD COLUMN IF NOT EXISTS total_pages INTEGER;
      `
    },
    {
      name: 'performance indexes',
      sql: `
        CREATE INDEX IF NOT EXISTS idx_processing_jobs_document_id ON processing_jobs(document_id);
        CREATE INDEX IF NOT EXISTS idx_processing_jobs_status ON processing_jobs(status);
        CREATE INDEX IF NOT EXISTS idx_chunk_summaries_document_id ON chunk_summaries(document_id);
        CREATE INDEX IF NOT EXISTS idx_chunk_summaries_chunk_id ON chunk_summaries(chunk_id);
        CREATE INDEX IF NOT EXISTS idx_analysis_points_chunk_id ON analysis_points(chunk_id);
        CREATE INDEX IF NOT EXISTS idx_documents_processing_method ON documents(processing_method);
      `
    },
    {
      name: 'RLS policies',
      sql: `
        ALTER TABLE processing_jobs ENABLE ROW LEVEL SECURITY;
        ALTER TABLE chunk_summaries ENABLE ROW LEVEL SECURITY;

        DROP POLICY IF EXISTS "Users can view their own processing jobs" ON processing_jobs;
        CREATE POLICY "Users can view their own processing jobs" ON processing_jobs
          FOR SELECT USING (
            document_id IN (SELECT id FROM documents WHERE user_id = auth.uid())
          );

        DROP POLICY IF EXISTS "Users can update their own processing jobs" ON processing_jobs;
        CREATE POLICY "Users can update their own processing jobs" ON processing_jobs
          FOR UPDATE USING (
            document_id IN (SELECT id FROM documents WHERE user_id = auth.uid())
          );

        DROP POLICY IF EXISTS "Users can insert processing jobs for their documents" ON processing_jobs;
        CREATE POLICY "Users can insert processing jobs for their documents" ON processing_jobs
          FOR INSERT WITH CHECK (
            document_id IN (SELECT id FROM documents WHERE user_id = auth.uid())
          );

        DROP POLICY IF EXISTS "Users can view their own chunk summaries" ON chunk_summaries;
        CREATE POLICY "Users can view their own chunk summaries" ON chunk_summaries
          FOR SELECT USING (
            document_id IN (SELECT id FROM documents WHERE user_id = auth.uid())
          );

        DROP POLICY IF EXISTS "Service role can manage all processing jobs" ON processing_jobs;
        CREATE POLICY "Service role can manage all processing jobs" ON processing_jobs
          FOR ALL USING (auth.role() = 'service_role');

        DROP POLICY IF EXISTS "Service role can manage all chunk summaries" ON chunk_summaries;
        CREATE POLICY "Service role can manage all chunk summaries" ON chunk_summaries
          FOR ALL USING (auth.role() = 'service_role');
      `
    },
    {
      name: 'helper functions',
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

          UPDATE documents 
          SET processing_method = 'large_document'
          WHERE id = p_document_id;

          RETURN job_id;
        END;
        $$;

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
    }
  ];

  let success = 0;
  let errors = 0;

  for (const query of queries) {
    try {
      console.log(`📋 Creating ${query.name}...`);
      
      // Use SQL directly instead of rpc for better compatibility
      const { error } = await supabase
        .from('_dummy_')
        .select('*')
        .limit(0)
        .then(async () => {
          // Execute raw SQL using a direct query
          const { error } = await supabase.rpc('exec_sql', { sql: query.sql });
          return { error };
        })
        .catch(async () => {
          // Fallback: try using the Edge function
          const { data, error } = await supabase.functions.invoke('setup-large-document-tables');
          return { error };
        });

      if (error) {
        console.error(`❌ Error creating ${query.name}:`, error.message);
        errors++;
      } else {
        console.log(`✅ ${query.name} created successfully`);
        success++;
      }
    } catch (err) {
      console.error(`❌ Unexpected error with ${query.name}:`, err.message);
      errors++;
    }
  }

  console.log('\n🎉 Database setup completed!');
  console.log(`✅ ${success} operations successful`);
  if (errors > 0) {
    console.log(`❌ ${errors} operations failed`);
    console.log('\n💡 If you see permission errors, try running the setup-large-document-tables Edge function instead');
  }
}

setupDatabase().catch(console.error);