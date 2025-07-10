# 🔗 Como Conectar Database e Redis no Railway

## Situação Atual:
- ✅ Você já tem PostgreSQL e Redis criados no Railway
- ❌ Eles não estão **conectados** ao seu app (faltam as variáveis de ambiente)

## 🎯 Solução: Conectar via Dashboard Railway

### 1. **Acesse seu projeto no Railway**
- Vá para: https://railway.app/dashboard
- Selecione o projeto `pdf-industrial-pipeline-production`

### 2. **Conectar PostgreSQL**
- Clique no seu **app principal** (não no PostgreSQL)
- Vá em **Variables** 
- Clique **+ New Variable**
- Adicione: `DATABASE_URL` = `${{Postgres.DATABASE_URL}}`
  - ⚠️ Use o nome exato do seu serviço PostgreSQL (pode ser `Postgres`, `PostgreSQL`, etc.)

### 3. **Conectar Redis**
- Ainda nas **Variables** do app principal
- Adicione: `REDIS_URL` = `${{Redis.REDIS_URL}}`
  - ⚠️ Use o nome exato do seu serviço Redis

### 4. **Deploy automático**
- Railway fará redeploy automaticamente
- Aguarde ~2 minutos

### 5. **Verificar conexão**
- Teste: https://pdf-industrial-pipeline-production.up.railway.app/test-db
- Deve retornar: `"database_configured": true` e `"redis_configured": true`

## 🔍 **Como encontrar os nomes dos serviços:**
1. No dashboard Railway, você verá os blocos dos serviços
2. O nome que aparece no bloco é o que usar na variável
3. Exemplos comuns:
   - `${{Postgres.DATABASE_URL}}`
   - `${{PostgreSQL.DATABASE_URL}}`
   - `${{Redis.REDIS_URL}}`

## 📱 **Alternativa via Railway CLI:**
```bash
railway login
railway link [seu-project-id]
railway variables set DATABASE_URL=${{Postgres.DATABASE_URL}}
railway variables set REDIS_URL=${{Redis.REDIS_URL}}
```

## ✅ **Quando funcionar:**
- API Health: OK ✅
- Database: Conectado ✅  
- Redis: Conectado ✅
- Upload funcionará com persistência completa!