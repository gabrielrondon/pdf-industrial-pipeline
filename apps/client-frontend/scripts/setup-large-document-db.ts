import { createClient } from '@supabase/supabase-js';

// Use your Supabase credentials
const supabaseUrl = "https://rjbiyndpxqaallhjmbwm.supabase.co";
const supabaseServiceRoleKey = process.env.SUPABASE_SERVICE_ROLE_KEY;

if (!supabaseServiceRoleKey) {
  console.error('❌ SUPABASE_SERVICE_ROLE_KEY environment variable is required');
  process.exit(1);
}

const supabase = createClient(supabaseUrl, supabaseServiceRoleKey);

async function setupLargeDocumentTables() {
  console.log('🚀 Setting up large document processing tables...');

  try {
    // Create processing_jobs table
    console.log('📋 Creating processing_jobs table...');
    const { error: jobsError } = await supabase.rpc('exec_sql', {
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

    if (jobsError) {
      console.error('❌ Error creating processing_jobs table:', jobsError);
      throw jobsError;
    }
    console.log('✅ processing_jobs table created');

    // Create chunk_summaries table
    console.log('📋 Creating chunk_summaries table...');
    const { error: summariesError } = await supabase.rpc('exec_sql', {
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

    if (summariesError) {
      console.error('❌ Error creating chunk_summaries table:', summariesError);
      throw summariesError;
    }
    console.log('✅ chunk_summaries table created');

    // Add chunk_id column to analysis_points
    console.log('📋 Adding chunk_id to analysis_points...');
    const { error: chunkIdError } = await supabase.rpc('exec_sql', {
      sql: `
        ALTER TABLE analysis_points 
        ADD COLUMN IF NOT EXISTS chunk_id TEXT;
      `
    });

    if (chunkIdError) {
      console.error('❌ Error adding chunk_id to analysis_points:', chunkIdError);
      throw chunkIdError;
    }
    console.log('✅ chunk_id column added to analysis_points');

    // Add additional columns to documents table
    console.log('📋 Adding large document columns to documents table...');
    const { error: documentsError } = await supabase.rpc('exec_sql', {
      sql: `
        ALTER TABLE documents 
        ADD COLUMN IF NOT EXISTS total_points INTEGER DEFAULT 0,
        ADD COLUMN IF NOT EXISTS processing_method TEXT DEFAULT 'standard',
        ADD COLUMN IF NOT EXISTS file_size_mb DECIMAL,
        ADD COLUMN IF NOT EXISTS total_pages INTEGER;
      `
    });

    if (documentsError) {
      console.error('❌ Error updating documents table:', documentsError);
      throw documentsError;
    }
    console.log('✅ documents table updated');

    // Create indexes
    console.log('📋 Creating indexes...');
    const { error: indexesError } = await supabase.rpc('exec_sql', {
      sql: `
        CREATE INDEX IF NOT EXISTS idx_processing_jobs_document_id ON processing_jobs(document_id);
        CREATE INDEX IF NOT EXISTS idx_processing_jobs_status ON processing_jobs(status);
        CREATE INDEX IF NOT EXISTS idx_chunk_summaries_document_id ON chunk_summaries(document_id);
        CREATE INDEX IF NOT EXISTS idx_chunk_summaries_chunk_id ON chunk_summaries(chunk_id);
        CREATE INDEX IF NOT EXISTS idx_analysis_points_chunk_id ON analysis_points(chunk_id);
        CREATE INDEX IF NOT EXISTS idx_documents_processing_method ON documents(processing_method);
      `
    });

    if (indexesError) {
      console.error('❌ Error creating indexes:', indexesError);
      throw indexesError;
    }
    console.log('✅ Indexes created');

    // Set up RLS policies
    console.log('📋 Setting up Row Level Security policies...');
    const { error: rlsError } = await supabase.rpc('exec_sql', {
      sql: `
        ALTER TABLE processing_jobs ENABLE ROW LEVEL SECURITY;
        ALTER TABLE chunk_summaries ENABLE ROW LEVEL SECURITY;

        -- RLS for processing_jobs
        DROP POLICY IF EXISTS "Users can view their own processing jobs" ON processing_jobs;
        CREATE POLICY "Users can view their own processing jobs" ON processing_jobs
          FOR SELECT USING (
            document_id IN (
              SELECT id FROM documents WHERE user_id = auth.uid()
            )
          );

        DROP POLICY IF EXISTS "Users can update their own processing jobs" ON processing_jobs;
        CREATE POLICY "Users can update their own processing jobs" ON processing_jobs
          FOR UPDATE USING (
            document_id IN (
              SELECT id FROM documents WHERE user_id = auth.uid()
            )
          );

        DROP POLICY IF EXISTS "Users can insert processing jobs for their documents" ON processing_jobs;
        CREATE POLICY "Users can insert processing jobs for their documents" ON processing_jobs
          FOR INSERT WITH CHECK (
            document_id IN (
              SELECT id FROM documents WHERE user_id = auth.uid()
            )
          );

        -- RLS for chunk_summaries
        DROP POLICY IF EXISTS "Users can view their own chunk summaries" ON chunk_summaries;
        CREATE POLICY "Users can view their own chunk summaries" ON chunk_summaries
          FOR SELECT USING (
            document_id IN (
              SELECT id FROM documents WHERE user_id = auth.uid()
            )
          );

        DROP POLICY IF EXISTS "Service role can manage all processing jobs" ON processing_jobs;
        CREATE POLICY "Service role can manage all processing jobs" ON processing_jobs
          FOR ALL USING (auth.role() = 'service_role');

        DROP POLICY IF EXISTS "Service role can manage all chunk summaries" ON chunk_summaries;
        CREATE POLICY "Service role can manage all chunk summaries" ON chunk_summaries
          FOR ALL USING (auth.role() = 'service_role');
      `
    });

    if (rlsError) {
      console.error('❌ Error setting up RLS policies:', rlsError);
      throw rlsError;
    }
    console.log('✅ RLS policies created');

    // Create helper functions
    console.log('📋 Creating helper functions...');
    const { error: functionsError } = await supabase.rpc('exec_sql', {
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

    if (functionsError) {
      console.error('❌ Error creating helper functions:', functionsError);
      throw functionsError;
    }
    console.log('✅ Helper functions created');

    console.log('🎉 Large document processing database setup completed successfully!');
    console.log('\n📊 Summary:');
    console.log('  ✅ processing_jobs table created');
    console.log('  ✅ chunk_summaries table created');
    console.log('  ✅ analysis_points table updated');
    console.log('  ✅ documents table updated');
    console.log('  ✅ Indexes created for performance');
    console.log('  ✅ Row Level Security policies set up');
    console.log('  ✅ Helper functions created');
    console.log('\n🚀 You can now process large documents!');

  } catch (error) {
    console.error('❌ Database setup failed:', error);
    process.exit(1);
  }
}

// Run the setup
setupLargeDocumentTables();