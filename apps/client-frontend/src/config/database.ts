// Database configuration for Neon PostgreSQL
export const databaseConfig = {
  // Neon PostgreSQL connection
  neon: {
    connectionString: import.meta.env.DATABASE_URL || 
      'postgresql://neondb_owner:npg_S85VxUweMGyu@ep-icy-moon-ad3wjamy-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require',
    ssl: true,
    poolSize: 20
  },
  
  // Supabase configuration (for backward compatibility)
  supabase: {
    url: import.meta.env.VITE_SUPABASE_URL || '',
    anonKey: import.meta.env.VITE_SUPABASE_ANON_KEY || ''
  },
  
  // API configuration
  api: {
    baseUrl: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'
  }
}

export default databaseConfig