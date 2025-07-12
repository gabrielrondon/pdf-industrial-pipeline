-- Add title column to jobs table for user-editable document titles
-- This migration is safe to run multiple times

DO $$ 
BEGIN
    -- Check if title column already exists
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'jobs' 
        AND column_name = 'title'
    ) THEN
        -- Add the title column
        ALTER TABLE jobs ADD COLUMN title VARCHAR(500);
        
        -- Update existing records to use filename as initial title
        UPDATE jobs SET title = filename WHERE title IS NULL;
        
        RAISE NOTICE 'Title column added to jobs table successfully';
    ELSE
        RAISE NOTICE 'Title column already exists in jobs table';
    END IF;
END $$;

-- Add comment for documentation
COMMENT ON COLUMN jobs.title IS 'User-editable title for the document, defaults to filename';