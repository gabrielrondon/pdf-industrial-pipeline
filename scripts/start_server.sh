#!/bin/bash
# Script para iniciar o servidor do PDF Industrial Pipeline

echo "🚀 Iniciando PDF Industrial Pipeline..."
echo "📍 Diretório: $(pwd)"
echo "🐍 Python: $(which python3)"
echo ""

# Verificar se já existe um processo rodando
if lsof -ti:8000 > /dev/null 2>&1; then
    echo "⚠️  Porta 8000 já está em uso!"
    echo "Matando processo anterior..."
    kill -9 $(lsof -ti:8000) 2>/dev/null
    sleep 2
fi

# Verificar dependências
echo "📦 Verificando dependências..."
if ! python3 -c "import fastapi" 2>/dev/null; then
    echo "❌ FastAPI não encontrado. Instale com: pip install -r requirements.txt"
    exit 1
fi

# Iniciar servidor
echo "✅ Iniciando servidor na porta 8000..."
echo "📄 Documentação disponível em: http://localhost:8000/docs"
echo ""
echo "Para parar o servidor, pressione Ctrl+C"
echo "----------------------------------------"
echo ""

# Executar o servidor
python3 main.py