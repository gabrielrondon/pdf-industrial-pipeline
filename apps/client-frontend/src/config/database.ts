// Database configuration for Neon PostgreSQL
export const databaseConfig = {
  // Neon PostgreSQL connection
  neon: {
    connectionString: import.meta.env.DATABASE_URL || 
      'postgresql://user:password@localhost:5432/database',
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