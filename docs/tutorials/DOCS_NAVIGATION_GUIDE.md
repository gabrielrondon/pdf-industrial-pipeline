# Guia de Navegação - Documentação FastAPI

## Acessando a Documentação

1. **Abra no navegador:** http://localhost:8000/docs

2. **Interface Swagger UI:** Você verá uma interface interativa com todos os endpoints

## Localizando os Endpoints de Análise Judicial

### Na documentação, procure por:

```
🔽 JUDICIAL AUCTION ANALYSIS ENDPOINTS (ou similar)
    POST  /judicial-analysis/{job_id}    ← Executar análise
    GET   /judicial-analysis/{job_id}    ← Recuperar resultados
```

### Ou procure na lista geral por ordem alfabética:

Os endpoints devem aparecer entre outros endpoints, organizados assim:

```
📁 Endpoints da API
├── POST   /upload
├── GET    /job/{job_id}/status
├── GET    /job/{job_id}/manifest
├── DELETE /job/{job_id}
├── POST   /process-text/{job_id}
├── GET    /job/{job_id}/text-analysis
├── POST   /generate-embeddings/{job_id}
├── GET    /job/{job_id}/embeddings
├── POST   /extract-features/{job_id}
├── POST   /train-models
├── POST   /predict-leads/{job_id}
├── GET    /job/{job_id}/ml-analysis
├── POST   /judicial-analysis/{job_id}    ⭐ AQUI!
├── GET    /judicial-analysis/{job_id}    ⭐ AQUI!
├── POST   /search/semantic
├── GET    /search/leads
└── ...outros endpoints
```

## Como Testar na Documentação

### 1. Encontre o endpoint POST /judicial-analysis/{job_id}

### 2. Clique para expandir

### 3. Você verá:
- **Descrição:** "Perform comprehensive judicial auction analysis on processed documents"
- **Parâmetros:** job_id (string) - required
- **Responses:** 200, 404, 500

### 4. Para testar:
1. Clique em "Try it out"
2. Digite um job_id válido
3. Clique em "Execute"
4. Veja a resposta abaixo

## Se não encontrar os endpoints

### Possíveis causas:

1. **Servidor não foi reiniciado após as mudanças**
   - Solução: Pare (Ctrl+C) e reinicie o servidor

2. **Cache do navegador**
   - Solução: Force refresh (Ctrl+F5 ou Cmd+Shift+R)

3. **Erro na importação do módulo**
   - Verifique se não há erros no terminal onde o servidor está rodando

### Verificação rápida via terminal:

```bash
# Lista todos os endpoints disponíveis
curl http://localhost:8000/openapi.json | python3 -m json.tool | grep -A2 -B2 "judicial"
```

## Ordem dos Endpoints no Swagger

O FastAPI geralmente organiza os endpoints na ordem em que aparecem no código. Como adicionamos os endpoints de judicial-analysis após os outros, eles devem aparecer:

1. Próximo ao final da lista
2. Após os endpoints de ML
3. Antes dos endpoints de frontend/utilitários

## Screenshot do que procurar:

```
🔍 No Swagger UI você verá algo assim:

┌─────────────────────────────────────────┐
│ PDF Industrial Pipeline                  │
│ Pipeline para processamento de PDFs      │
├─────────────────────────────────────────┤
│ 🟢 POST   /judicial-analysis/{job_id}   │
│    Perform comprehensive judicial...     │
│    Parameters:                          │
│    • job_id* (path) string             │
├─────────────────────────────────────────┤
│ 🔵 GET    /judicial-analysis/{job_id}   │
│    Retrieve judicial auction analysis... │
│    Parameters:                          │
│    • job_id* (path) string             │
└─────────────────────────────────────────┘
```

## Testando Diretamente

Se preferir testar sem a interface:

```bash
# Verificar se o endpoint existe
curl -X OPTIONS http://localhost:8000/judicial-analysis/test -v

# Listar todos os endpoints
curl http://localhost:8000/openapi.json | jq '.paths | keys[]' | grep judicial
```