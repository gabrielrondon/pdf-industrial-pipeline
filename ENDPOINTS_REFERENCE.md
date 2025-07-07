# Referência Completa de Endpoints - PDF Industrial Pipeline

## Índice
1. [Endpoints de Upload e Processamento](#1-upload-e-processamento)
2. [Endpoints de Análise de Texto](#2-análise-de-texto)
3. [Endpoints de Análise Judicial](#3-análise-judicial-novo)
4. [Endpoints de Embeddings](#4-embeddings)
5. [Endpoints de Machine Learning](#5-machine-learning)
6. [Endpoints de Busca](#6-busca)
7. [Endpoints de Performance](#7-performance)
8. [Endpoints Utilitários](#8-utilitários)

---

## 1. Upload e Processamento

### POST /upload
Upload de arquivo PDF para processamento.

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body: `file` (arquivo PDF)

**Response:**
```json
{
    "job_id": "uuid",
    "message": "PDF carregado e processado com sucesso",
    "file_info": {
        "original_name": "documento.pdf",
        "size": "2.5 MB",
        "pages": 15
    }
}
```

### GET /job/{job_id}/status
Verifica status do processamento.

**Response:**
```json
{
    "job_id": "uuid",
    "status": "completed",
    "progress": 100,
    "current_stage": "ready"
}
```

### GET /job/{job_id}/manifest
Obtém manifesto com detalhes do job.

**Response:**
```json
{
    "job_id": "uuid",
    "created_at": "2024-01-01T10:00:00",
    "file_info": {...},
    "pages": [...]
}
```

### DELETE /job/{job_id}
Remove arquivos do job.

---

## 2. Análise de Texto

### POST /process-text/{job_id}
Processa análise de texto (NER, keywords, lead scoring).

**Response:**
```json
{
    "message": "Análise de texto concluída",
    "job_id": "uuid",
    "pages_processed": 10,
    "entities_found": {
        "cnpj": 5,
        "cpf": 3,
        "money": 10,
        "dates": 8
    }
}
```

### GET /job/{job_id}/text-analysis
Recupera resultados da análise de texto.

**Response:**
```json
{
    "job_id": "uuid",
    "pages": {
        "page_001": {
            "text": "...",
            "entities": {...},
            "keywords": {...},
            "lead_score": 85
        }
    }
}
```

### GET /text-processing/stats
Estatísticas do processamento de texto.

---

## 3. Análise Judicial (NOVO!)

### POST /judicial-analysis/{job_id} ⭐
Executa análise completa de leilão judicial.

**Analisa:**
- 1.1 Natureza do leilão (judicial/extrajudicial)
- 1.2 Publicação (Diário Oficial, prazos)
- 1.3-1.4 Intimações CPC 889
- 1.5 Valores e avaliação
- 1.6 Débitos existentes
- 1.7 Ocupação do imóvel
- 1.8 Restrições legais

**Response:**
```json
{
    "message": "Judicial auction analysis completed",
    "job_id": "uuid",
    "analysis": {
        "auction_type": "judicial",
        "auction_type_confidence": 0.9,
        "publication_compliance": {...},
        "cpc_889_compliance": "compliant",
        "valuation": {...},
        "debts": {...},
        "property_status": {...},
        "legal_restrictions": {...},
        "overall_risk_score": 25.0,
        "investment_viability_score": 85.0,
        "recommendations": [...]
    }
}
```

### GET /judicial-analysis/{job_id} ⭐
Recupera análise judicial salva.

---

## 4. Embeddings

### POST /generate-embeddings/{job_id}
Gera embeddings semânticos do texto.

**Response:**
```json
{
    "message": "Embeddings gerados com sucesso",
    "job_id": "uuid",
    "embeddings_info": {
        "model": "bert-base-portuguese",
        "dimensions": 768,
        "chunks_processed": 25
    }
}
```

### GET /job/{job_id}/embeddings
Recupera informações dos embeddings.

### GET /embeddings/stats
Estatísticas do sistema de embeddings.

---

## 5. Machine Learning

### POST /extract-features/{job_id}
Extrai features para ML.

**Response:**
```json
{
    "message": "Features extraídas com sucesso",
    "job_id": "uuid",
    "features_count": 37
}
```

### POST /train-models
Treina modelos de ML com dados disponíveis.

**Response:**
```json
{
    "message": "Modelos treinados com sucesso",
    "models_trained": ["random_forest", "gradient_boosting"],
    "performance": {...}
}
```

### POST /predict-leads/{job_id}
Prediz qualidade do lead.

**Response:**
```json
{
    "job_id": "uuid",
    "predictions": {
        "lead_score": 87.5,
        "lead_classification": "high",
        "confidence": 0.92
    }
}
```

### GET /job/{job_id}/ml-analysis
Análise ML completa do job.

### GET /ml/lead-quality-analysis
Análise agregada de qualidade dos leads.

**Query Parameters:**
- `threshold_high`: float (default: 80.0)
- `threshold_medium`: float (default: 50.0)

### GET /ml/model-performance
Performance dos modelos treinados.

---

## 6. Busca

### POST /search/semantic
Busca semântica nos documentos.

**Request Body:**
```json
{
    "query": "imóvel desocupado leilão judicial",
    "top_k": 10,
    "threshold": 0.7
}
```

**Response:**
```json
{
    "query": "...",
    "results": [
        {
            "job_id": "uuid",
            "page_number": 3,
            "text": "...",
            "score": 0.89
        }
    ]
}
```

### GET /search/leads
Busca leads de alta qualidade.

**Query Parameters:**
- `min_score`: float (default: 70.0)
- `limit`: int (default: 10)
- `include_entities`: bool (default: true)

---

## 7. Performance

### GET /performance/cache/stats
Estatísticas do cache Redis.

**Response:**
```json
{
    "hit_rate": 0.85,
    "total_hits": 1523,
    "total_misses": 267,
    "memory_used_mb": 45.2
}
```

### GET /performance/system/health
Verifica saúde do sistema.

**Response:**
```json
{
    "system_status": "healthy",
    "uptime_seconds": 3600,
    "healthy_components": 8,
    "component_details": [...]
}
```

### GET /performance/analytics
Analytics de performance completos.

### GET /performance/benchmark/{endpoint_name}
Executa benchmark de endpoint.

**Query Parameters:**
- `iterations`: int (default: 100)

---

## 8. Utilitários

### POST /process-complete-pipeline
Executa pipeline completo em uma requisição.

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body: `file` (arquivo PDF)

**Response:**
```json
{
    "job_id": "uuid",
    "pipeline_status": "completed",
    "stages_completed": {
        "upload": true,
        "text_analysis": true,
        "embeddings": true,
        "features": true,
        "predictions": true,
        "analysis": true
    },
    "results": {...}
}
```

### GET /health
Health check básico.

**Response:**
```json
{
    "status": "healthy",
    "timestamp": "2024-01-01T10:00:00Z"
}
```

### GET /api/info
Informações da API.

**Response:**
```json
{
    "name": "PDF Industrial Pipeline",
    "version": "1.0.0",
    "description": "Pipeline para processamento industrial de arquivos PDF"
}
```

---

## Fluxo Recomendado para Análise Judicial

```
1. POST /upload
   ↓
2. POST /process-text/{job_id}
   ↓
3. POST /judicial-analysis/{job_id}  ← NOVO!
   ↓
4. GET /judicial-analysis/{job_id}   ← Resultados completos
```

---

## Códigos de Status

| Status | Descrição |
|--------|-----------|
| 200 | Sucesso |
| 201 | Criado com sucesso |
| 400 | Requisição inválida |
| 404 | Não encontrado |
| 422 | Entidade não processável |
| 500 | Erro interno do servidor |

---

## Rate Limiting

- Não implementado na versão atual
- Recomendado: max 100 requests/minuto por cliente

---

## Autenticação

- Não requerida na versão atual
- Futura implementação: Bearer Token JWT