import { Pool, PoolConfig } from 'pg'
import { DatabaseConfig } from '@pdf-pipeline/types'

export class DatabaseConnection {
  private pool: Pool
  
  constructor(config?: DatabaseConfig) {
    const dbConfig: PoolConfig = {
      connectionString: config ? 
        `postgresql://${config.username}:${config.password}@${config.host}:${config.port}/${config.database}?sslmode=require&channel_binding=require` :
        process.env.DATABASE_URL || 'postgresql://neondb_owner:npg_S85VxUweMGyu@ep-icy-moon-ad3wjamy-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require',
      ssl: config?.ssl !== false,
      max: config?.poolSize || 20,
      idleTimeoutMillis: 30000,
      connectionTimeoutMillis: 2000,
    }
    
    this.pool = new Pool(dbConfig)
  }

  async query(text: string, params?: any[]) {
    const client = await this.pool.connect()
    try {
      const result = await client.query(text, params)
      return result
    } finally {
      client.release()
    }
  }

  async getSystemStats() {
    const result = await this.query(`
      SELECT 
        (SELECT COUNT(*) FROM documents) as total_documents,
        (SELECT COUNT(*) FROM processing_jobs WHERE status = 'processing') as active_jobs,
        (SELECT COUNT(*) FROM profiles) as total_users
    `)
    return result.rows[0]
  }

  async close() {
    await this.pool.end()
  }
}

export const createDatabase = (config?: DatabaseConfig) => {
  return new DatabaseConnection(config)
}

export * from '@pdf-pipeline/types'