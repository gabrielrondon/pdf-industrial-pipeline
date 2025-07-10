// Simple database setup script
// Run with: node setup-database.js

console.log('🚀 Setting up large document processing database...');
console.log('');

const setupQueries = [
  {
    name: 'processing_jobs table',
    description: 'Table to track document processing jobs',
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
);`
  },
  {
    name: 'chunk_summaries table',
    description: 'Table to store chunk-level analysis summaries',
    sql: `
CREATE TABLE IF NOT EXISTS chunk_summaries (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
  chunk_id TEXT NOT NULL,
  summary TEXT NOT NULL,
  pages INTEGER[],
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);`
  },
  {
    name: 'analysis_points update',
    description: 'Add chunk_id column to analysis_points',
    sql: `ALTER TABLE analysis_points ADD COLUMN IF NOT EXISTS chunk_id TEXT;`
  },
  {
    name: 'documents table update',
    description: 'Add large document processing columns',
    sql: `
ALTER TABLE documents 
ADD COLUMN IF NOT EXISTS total_points INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS processing_method TEXT DEFAULT 'standard',
ADD COLUMN IF NOT EXISTS file_size_mb DECIMAL,
ADD COLUMN IF NOT EXISTS total_pages INTEGER;`
  },
  {
    name: 'performance indexes',
    description: 'Create indexes for better query performance',
    sql: `
CREATE INDEX IF NOT EXISTS idx_processing_jobs_document_id ON processing_jobs(document_id);
CREATE INDEX IF NOT EXISTS idx_processing_jobs_status ON processing_jobs(status);
CREATE INDEX IF NOT EXISTS idx_chunk_summaries_document_id ON chunk_summaries(document_id);
CREATE INDEX IF NOT EXISTS idx_chunk_summaries_chunk_id ON chunk_summaries(chunk_id);
CREATE INDEX IF NOT EXISTS idx_analysis_points_chunk_id ON analysis_points(chunk_id);
CREATE INDEX IF NOT EXISTS idx_documents_processing_method ON documents(processing_method);`
  },
  {
    name: 'RLS policies',
    description: 'Set up Row Level Security policies',
    sql: `
-- Enable RLS
ALTER TABLE processing_jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE chunk_summaries ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if they exist
DROP POLICY IF EXISTS "Users can view their own processing jobs" ON processing_jobs;
DROP POLICY IF EXISTS "Users can update their own processing jobs" ON processing_jobs;
DROP POLICY IF EXISTS "Users can insert processing jobs for their documents" ON processing_jobs;
DROP POLICY IF EXISTS "Users can view their own chunk summaries" ON chunk_summaries;
DROP POLICY IF EXISTS "Service role can manage all processing jobs" ON processing_jobs;
DROP POLICY IF EXISTS "Service role can manage all chunk summaries" ON chunk_summaries;

-- Create new policies
CREATE POLICY "Users can view their own processing jobs" ON processing_jobs
  FOR SELECT USING (
    document_id IN (SELECT id FROM documents WHERE user_id = auth.uid())
  );

CREATE POLICY "Users can update their own processing jobs" ON processing_jobs
  FOR UPDATE USING (
    document_id IN (SELECT id FROM documents WHERE user_id = auth.uid())
  );

CREATE POLICY "Users can insert processing jobs for their documents" ON processing_jobs
  FOR INSERT WITH CHECK (
    document_id IN (SELECT id FROM documents WHERE user_id = auth.uid())
  );

CREATE POLICY "Users can view their own chunk summaries" ON chunk_summaries
  FOR SELECT USING (
    document_id IN (SELECT id FROM documents WHERE user_id = auth.uid())
  );

CREATE POLICY "Service role can manage all processing jobs" ON processing_jobs
  FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role can manage all chunk summaries" ON chunk_summaries
  FOR ALL USING (auth.role() = 'service_role');`
  },
  {
    name: 'helper functions',
    description: 'Create helper functions for large document processing',
    sql: `
-- Function to start large document processing
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

-- Function to get processing status
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
$$;`
  }
];

console.log('📋 Database Setup Queries:');
console.log('='.repeat(50));

setupQueries.forEach((query, index) => {
  console.log(`${index + 1}. ${query.name}`);
  console.log(`   Description: ${query.description}`);
  console.log('');
});

console.log('🎯 TO SETUP THE DATABASE:');
console.log('');
console.log('1. Go to your Supabase Dashboard:');
console.log('   https://supabase.com/dashboard/project/rjbiyndpxqaallhjmbwm/sql');
console.log('');
console.log('2. Copy and run each SQL query from the queries below:');
console.log('');

setupQueries.forEach((query, index) => {
  console.log(`-- ${index + 1}. ${query.name.toUpperCase()}`);
  console.log(`-- ${query.description}`);
  console.log(query.sql.trim());
  console.log('');
  console.log('-'.repeat(80));
  console.log('');
});

console.log('✅ After running all queries, your database will be ready for large document processing!');
console.log('');
console.log('🚀 Features enabled:');
console.log('   ✅ Background job processing');
console.log('   ✅ Progress tracking');
console.log('   ✅ Chunk-based analysis');
console.log('   ✅ Real-time status updates');
console.log('   ✅ Error recovery');
console.log('   ✅ Large file support');
console.log('');