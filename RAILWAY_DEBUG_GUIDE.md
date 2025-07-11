# 🔍 Railway Database Connection Debug

## Problema:
Configurou conforme `docs/setup/RAILWAY_DEPLOYMENT.md` mas ainda:
```json
{"database_configured": false, "redis_configured": false}
```

## 🕵️ Debug Steps:

### 1. **Verificar quais variáveis estão chegando na API**
Aguarde 2 minutos (deploy) e acesse:
- https://pdf-industrial-pipeline-production.up.railway.app/debug-env

### 2. **Possíveis problemas comuns:**

#### A. **Nome do serviço diferente**
Você pode ter usado:
```bash
DATABASE_URL=${{PostgreSQL.DATABASE_URL}}
REDIS_URL=${{Redis.REDIS_URL}}
```

Mas talvez os nomes sejam diferentes, como:
- `${{Postgres.DATABASE_URL}}`
- `${{postgres.DATABASE_URL}}`
- `${{RedisService.REDIS_URL}}`

#### B. **Variáveis não foram salvas**
- Clicou em "Save" depois de adicionar as variáveis?
- Fez redeploy depois de configurar?

#### C. **Sintaxe incorreta**
```bash
# ✅ Correto
DATABASE_URL=${{PostgreSQL.DATABASE_URL}}

# ❌ Incorreto  
DATABASE_URL=${{PostgreSQL.URL}}
DATABASE_URL=${PostgreSQL.DATABASE_URL}
```

## 🔧 **Soluções baseadas no debug:**

### Se `/debug-env` mostrar:
1. **`railway_vars` vazio** → Variáveis não foram configuradas
2. **`POSTGRES_*` variáveis existem** → Use nomes corretos
3. **`DATABASE_URL_EXISTS: false`** → Variável não foi referenciada corretamente

## 🎯 **Próximo passo:**
1. Acesse `/debug-env` (aguarde deploy)
2. Me mostre o resultado
3. Vou identificar exatamente o que ajustar

## 🚀 **Solução rápida alternativa:**
Se continuar com problemas, podemos usar diretamente as URLs que o Railway gera:

1. Vá no serviço PostgreSQL → Variables
2. Copie a URL completa do `DATABASE_URL`
3. Cole diretamente no app (sem `${{...}}`)
4. Faça o mesmo com Redis