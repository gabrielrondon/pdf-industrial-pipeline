# 📚 Industrial PDF Analysis Pipeline – Contexto Mestre

> **Status Atual:** 🚧 Etapa 1 - Ingestão & Particionamento (90% concluída)  
> **Última Atualização:** Janeiro 2024  
> **Desenvolvedor:** Gabriel Rondon

---

## 🎯 Objetivo Geral

Desenvolver um pipeline altamente escalável, modular e econômico para:

- ✅ Processar PDFs gigantes (milhares de páginas)
- ✅ Suportar arquivos escaneados ou mal diagramados (OCR inclusivo)
- 🔄 Extrair informações úteis como "leads" e "oportunidades"
- 🔄 Retornar resultados analisáveis para o cliente via API/frontend

---

## 🗺️ Roadmap das 7 Etapas

| # | Etapa | Status | Prioridade |
|---|-------|--------|------------|
| 1 | **Ingestão & Particionamento** | 🟢 90% | ATUAL |
| 2 | **OCR & Pré-processamento de Imagem** | ⚪ 0% | PRÓXIMA |
| 3 | **Limpeza & Estruturação do Texto** | ⚪ 0% | FUTURA |
| 4 | **Geração de Embeddings e Vetorização** | ⚪ 0% | FUTURA |
| 5 | **Identificação de Leads e Oportunidades** | ⚪ 0% | FUTURA |
| 6 | **Orquestração, Escalabilidade & Custos** | ⚪ 0% | FUTURA |
| 7 | **Interface (API + Frontend)** | ⚪ 0% | FUTURA |

**Legenda:** 🟢 Pronto | 🟡 Em Progresso | ⚪ Pendente | 🔴 Bloqueado

---

## 🔍 ETAPA 1 – Ingestão & Particionamento [ATUAL]

### 🎯 Objetivo
- [x] Receber PDFs grandes sem estourar memória
- [x] Armazenar de forma segura e rastreável
- [x] Dividir o arquivo em páginas independentes (`page-1.pdf`, `page-2.pdf`, etc.)
- [x] Marcar páginas que precisam de OCR
- [ ] Colocar os jobs na fila para processamento futuro
- [x] Gerar manifest.json com metadados completos

### 📋 Componentes e Status

#### 📥 API de Upload
- [x] FastAPI implementada (`main.py`)
- [x] Suporte a arquivos grandes
- [x] Validação de tipo MIME e extensão `.pdf`
- [x] Retorno com `job_id`, status, filename
- [x] Tratamento de erros robusto
- [x] Documentação Swagger automática

#### 🗂️ Armazenamento Inicial
- [x] Armazenamento local em `uploads/`
- [x] Estrutura organizada por job_id
- [ ] **PENDENTE:** Migração para S3 (`s3://bucket/jobs/{job_id}/orig.pdf`)
- [x] Geração de `manifest.json` com metadados

#### ✂️ Particionamento (Split PDF)
- [x] **Implementado:** `qpdf --split-pages`
- [x] Output em `/temp_splits/{job_id}/page-N.pdf`
- [x] Processamento individual de páginas
- [x] Logs estruturados de progresso
- [x] Tratamento de erros na divisão
- [x] Contagem automática de páginas

#### 🧠 Detecção de OCR Necessário
- [x] **Implementado:** `pdfminer.six` para extração de texto
- [x] Heurística: `len(text.strip()) < 100` → `needs_ocr = True`
- [x] Análise de densidade de palavras
- [x] Marcação no manifest.json

#### 🔁 Enfileiramento
- [ ] **PENDENTE:** Sistema de filas (RabbitMQ/SQS)
- [ ] **PENDENTE:** Mensagens JSON para fila `OCR`
- [x] **SIMULADO:** Estrutura preparada no manifest

#### 🛢️ Banco de Dados
- [ ] **PENDENTE:** PostgreSQL/DynamoDB
- [ ] **PENDENTE:** Tabelas `jobs`, `pages`
- [x] **ATUAL:** Armazenamento em arquivos JSON

#### 🧪 Observabilidade
- [x] Logs estruturados
- [x] Tempo de processamento por job
- [x] Contagem de páginas geradas
- [ ] **PENDENTE:** Métricas de custo
- [ ] **PENDENTE:** Monitoramento de fila

#### 🧰 Segurança
- [x] Validação robusta de arquivos
- [x] Verificação de paths seguros
- [x] Limpeza de nomes de arquivo
- [ ] **PENDENTE:** HTTPS obrigatório
- [ ] **PENDENTE:** Criptografia S3

### 📁 Arquivos Implementados
```
pdf-industrial-pipeline/
├── 📄 main.py              ✅ API FastAPI completa
├── 📄 workers/
│   └── split_worker.py     ✅ Worker de divisão completo
├── 📄 utils/
│   └── file_utils.py       ✅ Utilitários de arquivo
├── 📄 test_pipeline.py     ✅ Script de teste
├── 📄 requirements.txt     ✅ Dependências
├── 📄 README.md            ✅ Documentação
└── 📄 .gitignore           ✅ Configurado
```

### 🧪 Como Testar a Etapa 1

```bash
# 1. Testar via script
python test_pipeline.py

# 2. Testar via API
uvicorn main:app --reload
# Acesse: http://localhost:8000/docs

# 3. Verificar saúde
curl http://localhost:8000/health
```

### 📋 Exemplo de Manifest Gerado

```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "processing_info": {
    "processed_at": "2024-01-15T10:30:00.123Z",
    "processor": "qpdf",
    "status": "completed"
  },
  "original_file": {
    "filename": "documento.pdf",
    "file_size": 2621440
  },
  "output_info": {
    "total_pages": 5,
    "pages": [...]
  },
  "next_steps": {
    "ocr_required": false,
    "ready_for_processing": true
  }
}
```

### 🚧 Pendências da Etapa 1

| Item | Prioridade | Estimativa |
|------|------------|------------|
| Sistema de filas (RabbitMQ/SQS) | Alta | 2-3 dias |
| Migração para S3/MinIO | Média | 1-2 dias |
| Banco de dados (PostgreSQL) | Média | 1-2 dias |
| Métricas e monitoramento | Baixa | 1 dia |
| HTTPS obrigatório | Baixa | 0.5 dia |

---

## 🔜 ETAPAS FUTURAS (Planejamento)

### 2️⃣ OCR & Pré-processamento de Imagem
- [ ] Integração com Tesseract OCR
- [ ] Processamento de imagens (rotação, limpeza)
- [ ] Worker assíncrono para OCR
- [ ] Qualidade de texto pós-OCR

### 3️⃣ Limpeza & Estruturação do Texto
- [ ] Normalização de texto
- [ ] Detecção de estruturas (tabelas, listas)
- [ ] Segmentação semântica
- [ ] Classificação de seções

### 4️⃣ Geração de Embeddings e Vetorização
- [ ] Modelos de embedding (OpenAI/Local)
- [ ] Armazenamento vetorial (Pinecone/ChromaDB)
- [ ] Indexação semântica
- [ ] Busca por similaridade

### 5️⃣ Identificação de Leads e Oportunidades
- [ ] Regras de negócio
- [ ] Modelos de classificação
- [ ] Extração de entidades
- [ ] Scoring de oportunidades

### 6️⃣ Orquestração, Escalabilidade & Custos
- [ ] Docker/Kubernetes
- [ ] Auto-scaling
- [ ] Monitoramento de custos
- [ ] Otimização de performance

### 7️⃣ Interface (API + Frontend)
- [ ] API completa de consulta
- [ ] Dashboard web
- [ ] Upload de arquivos
- [ ] Visualização de resultados

---

## 📋 Próximos Passos Imediatos

### ✅ Para concluir Etapa 1 (100%):
1. **Implementar sistema de filas** - permitir enfileiramento real de jobs
2. **Adicionar armazenamento S3** - preparar para produção
3. **Criar testes automatizados** - garantir qualidade
4. **Documentar API completa** - facilitar integração

### 🔄 Para iniciar Etapa 2:
1. **Instalar e configurar Tesseract**
2. **Criar worker de OCR**
3. **Integrar com fila de mensagens**
4. **Implementar processamento de imagens**

---

## 🔗 Links Úteis

- **Documentação API:** http://localhost:8000/docs
- **Repositório:** (adicionar link do Git)
- **Monitoramento:** (adicionar quando implementado)
- **Deploy:** (adicionar quando implementado)

---

## 📝 Notas para Desenvolvimento

### 🎯 Princípios Arquiteturais
- **Modularidade:** Cada etapa é independente
- **Escalabilidade:** Pensado para milhares de páginas
- **Observabilidade:** Logs e métricas em tudo
- **Resilência:** Tratamento de erro robusto
- **Economia:** Otimização de custos sempre

### 🚨 Avisos Importantes
- ⚠️ **Nunca avançar etapa sem validação completa da anterior**
- ⚠️ **Sempre implementar testes antes de considerar "pronto"**
- ⚠️ **Manter backward compatibility entre versões**
- ⚠️ **Documentar todas as decisões arquiteturais**

### 💡 Decisões Técnicas Registradas
- **qpdf escolhido** para divisão de PDF (performance superior)
- **FastAPI** para API (async, docs automáticas)
- **pdfminer.six** para detecção de OCR (simplicidade)
- **JSON manifest** para metadados (flexibilidade)

---

**🏁 Fim do Contexto - Manter sempre atualizado conforme progresso**
