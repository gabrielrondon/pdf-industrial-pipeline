-- Dashboard Cache Table Migration
-- Creates a high-performance cache table for dashboard statistics

-- Create dashboard_cache table
CREATE TABLE IF NOT EXISTS dashboard_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cache_key VARCHAR(100) UNIQUE NOT NULL,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    statistics JSONB NOT NULL DEFAULT '{}',
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    calculation_time_ms INTEGER DEFAULT 0,
    record_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

-- Create indexes for optimal performance
CREATE INDEX IF NOT EXISTS idx_dashboard_cache_key_expires 
    ON dashboard_cache(cache_key, expires_at);

CREATE INDEX IF NOT EXISTS idx_dashboard_cache_user_expires 
    ON dashboard_cache(user_id, expires_at);

CREATE INDEX IF NOT EXISTS idx_dashboard_cache_expires 
    ON dashboard_cache(expires_at);

-- Create trigger to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_dashboard_cache_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_dashboard_cache_updated_at
    BEFORE UPDATE ON dashboard_cache
    FOR EACH ROW
    EXECUTE FUNCTION update_dashboard_cache_updated_at();

-- Insert initial cache entry for global stats (will be updated by background task)
INSERT INTO dashboard_cache (cache_key, statistics, expires_at)
VALUES (
    'dashboard_stats:global',
    '{
        "totalAnalyses": 0,
        "validLeads": 0,
        "sharedLeads": 0,
        "credits": 100,
        "documentTypes": [],
        "statusDistribution": [],
        "commonIssues": [],
        "monthlyAnalyses": [
            {"month": "Jan", "analyses": 0, "leads": 0},
            {"month": "Fev", "analyses": 0, "leads": 0},
            {"month": "Mar", "analyses": 0, "leads": 0},
            {"month": "Abr", "analyses": 0, "leads": 0},
            {"month": "Mai", "analyses": 0, "leads": 0},
            {"month": "Jun", "analyses": 0, "leads": 0}
        ],
        "successRate": 0,
        "averageProcessingTime": 0,
        "totalFileSize": 0,
        "averageConfidence": 0,
        "topPerformingDocumentType": "edital",
        "cacheCalculatedAt": "' || NOW()::text || '",
        "recordsProcessed": 0,
        "calculationTimeMs": 0
    }'::jsonb,
    NOW() + INTERVAL '5 minutes'
) ON CONFLICT (cache_key) DO NOTHING;

-- Add comment to table
COMMENT ON TABLE dashboard_cache IS 'High-performance cache for dashboard statistics to avoid real-time calculations';
COMMENT ON COLUMN dashboard_cache.cache_key IS 'Unique identifier for cache entries (e.g., dashboard_stats:global, dashboard_stats:user:uuid)';
COMMENT ON COLUMN dashboard_cache.statistics IS 'Pre-calculated dashboard statistics in JSONB format';
COMMENT ON COLUMN dashboard_cache.expires_at IS 'When this cache entry expires and needs refresh';
COMMENT ON COLUMN dashboard_cache.calculation_time_ms IS 'How long it took to calculate these statistics (for performance monitoring)';
COMMENT ON COLUMN dashboard_cache.record_count IS 'Number of database records processed to generate these statistics';

-- Cleanup function for old cache entries
CREATE OR REPLACE FUNCTION cleanup_expired_dashboard_cache()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM dashboard_cache 
    WHERE expires_at < NOW() - INTERVAL '1 hour';
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;