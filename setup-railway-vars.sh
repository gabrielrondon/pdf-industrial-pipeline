#!/bin/bash

echo "🚂 Configurando variáveis de ambiente no Railway..."
echo ""

# Verificar se está logado
if ! railway whoami &>/dev/null; then
    echo "❌ Erro: Não está logado no Railway"
    echo "Execute: railway login"
    exit 1
fi

echo "✅ Login confirmado no Railway"
echo ""

# Tentar conectar ao projeto
echo "🔗 Conectando ao projeto..."
echo "Quando aparecer a seleção, escolha 'gabriel rondon's Projects' e depois 'API (Arremate360)'"
echo ""

# O usuário precisa fazer isso manualmente pois requer seleção interativa
echo "Execute manualmente no terminal:"
echo "1. railway link"
echo "2. Selecione 'gabriel rondon's Projects'"  
echo "3. Selecione 'API (Arremate360)'"
echo ""

echo "Depois execute este script novamente ou os comandos:"
echo "railway variables set DATABASE_URL=\${{PostgreSQL.DATABASE_URL}}"
echo "railway variables set REDIS_URL=\${{Redis.REDIS_URL}}"
echo "railway variables set CELERY_BROKER_URL=\${{Redis.REDIS_URL}}"
echo "railway variables set CELERY_RESULT_BACKEND=\${{Redis.REDIS_URL}}"
echo ""

echo "Ou configure diretamente no Dashboard:"
echo "1. https://railway.app/dashboard"
echo "2. Selecione projeto 'Arremate360'"
echo "3. Clique no serviço 'API'"
echo "4. Aba 'Variables'"
echo "5. Adicione as variáveis acima"