# Railway Environment Variables Setup

Para configurar as variáveis de ambiente no Railway, você precisa:

## 1. Instalar Railway CLI
```bash
npm install -g @railway/cli
railway login
```

## 2. Conectar ao projeto
```bash
railway link pdf-industrial-pipeline-production
```

## 3. Adicionar PostgreSQL
```bash
railway add postgresql
```

## 4. Adicionar Redis
```bash
railway add redis
```

## 5. Configurar Variáveis de Ambiente
```bash
# Essas serão configuradas automaticamente pelo Railway
railway variables set DATABASE_URL=$DATABASE_URL
railway variables set REDIS_URL=$REDIS_URL

# Variáveis adicionais da nossa aplicação
railway variables set ENVIRONMENT=production
railway variables set SECRET_KEY="abca14e8ad3982ae93c07c42b01daf57886355ca0702a58b6d94717942f78d09"
railway variables set DEBUG=false
railway variables set API_VERSION=v2
```

## 6. Verificar Variáveis
```bash
railway variables
```

## 7. Redeploy para aplicar mudanças
```bash
railway redeploy
```

## Variáveis que o Railway deve configurar automaticamente:
- `DATABASE_URL` - URL de conexão com PostgreSQL
- `REDIS_URL` - URL de conexão com Redis
- `PGUSER`, `POSTGRES_PASSWORD`, `PGDATABASE`, `RAILWAY_PRIVATE_DOMAIN` - Configurações do PostgreSQL

## Como verificar se funcionou:
1. Acesse: https://pdf-industrial-pipeline-production.up.railway.app/test-db
2. Deve retornar: `{"database_configured": true, "redis_configured": true, "environment": "production"}`