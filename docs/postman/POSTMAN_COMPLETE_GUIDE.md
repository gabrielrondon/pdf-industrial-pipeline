# Guia Completo do Postman - PDF Industrial Pipeline

## Configuração Inicial

### 1. URL Base
```
http://localhost:8000
```

### 2. Headers Padrão (para todas as requisições)
```
Content-Type: application/json
Accept: application/json
```

---

## FLUXO COMPLETO PARA ANÁLISE JUDICIAL

Para obter a análise completa do edital de leilão judicial, siga este fluxo:

### Passo 1: Upload do PDF
### Passo 2: Análise de Texto
### Passo 3: Análise Judicial
### Passo 4: Recuperar Resultados

---

## ENDPOINTS DETALHADOS

### 1. Upload de PDF

**Método:** `POST`  
**URL:** `{{base_url}}/upload`  
**Headers:**
```
Content-Type: multipart/form-data
```

**Body:**
- Tipo: `form-data`
- Key: `file`
- Value: Selecione o arquivo PDF

**Exemplo no Postman:**
1. Selecione POST
2. URL: `http://localhost:8000/upload`
3. Vá para a aba Body
4. Selecione `form-data`
5. Adicione:
   - Key: `file` (tipo File)
   - Value: Clique e selecione seu PDF

**Response Esperada:**
```json
{
    "job_id": "98ac5938-b0b8-4fc3-8546-18b65ac20115",
    "message": "PDF carregado e processado com sucesso",
    "file_info": {
        "original_name": "edital_leilao.pdf",
        "size": "1.2 MB",
        "pages": 10
    }
}
```

**Script Tests (Postman):**
```javascript
// Salvar job_id para próximas requisições
if (pm.response.code === 200) {
    var jsonData = pm.response.json();
    pm.environment.set("job_id", jsonData.job_id);
    pm.test("Job ID salvo", function () {
        pm.expect(jsonData).to.have.property('job_id');
    });
}
```

---

### 2. Verificar Status do Job

**Método:** `GET`  
**URL:** `{{base_url}}/job/{{job_id}}/status`  
**Headers:** Padrão  
**Body:** Vazio  

**Response:**
```json
{
    "job_id": "98ac5938-b0b8-4fc3-8546-18b65ac20115",
    "status": "completed",
    "progress": 100,
    "current_stage": "ready"
}
```

---

### 3. Processar Análise de Texto

**Método:** `POST`  
**URL:** `{{base_url}}/process-text/{{job_id}}`  
**Headers:** Padrão  
**Body:** Vazio  

**Response:**
```json
{
    "message": "Análise de texto concluída",
    "job_id": "98ac5938-b0b8-4fc3-8546-18b65ac20115",
    "pages_processed": 10,
    "entities_found": {
        "cnpj": 2,
        "cpf": 1,
        "money": 5,
        "dates": 4
    }
}
```

**Script Tests:**
```javascript
pm.test("Análise de texto concluída", function () {
    pm.response.to.have.status(200);
    var jsonData = pm.response.json();
    pm.expect(jsonData.message).to.include("concluída");
});
```

---

### 4. Executar Análise Judicial ⭐ NOVO

**Método:** `POST`  
**URL:** `{{base_url}}/judicial-analysis/{{job_id}}`  
**Headers:** Padrão  
**Body:** Vazio  

**Response Completa com todos os 8 pontos solicitados:**
```json
{
    "message": "Judicial auction analysis completed",
    "job_id": "98ac5938-b0b8-4fc3-8546-18b65ac20115",
    "analysis": {
        // 1.1 - Natureza do leilão
        "auction_type": "judicial",
        "auction_type_confidence": 0.9,
        "auction_type_indicators": ["leilão judicial", "hasta pública", "execução"],
        
        // 1.2 - Publicação do edital
        "publication_compliance": {
            "diario_oficial_mentioned": true,
            "newspaper_mentioned": true,
            "publication_dates": ["2024-03-08T00:00:00"],
            "auction_dates": ["2024-03-15T00:00:00", "2024-03-25T00:00:00"],
            "days_between_publication_auction": 5,
            "meets_deadline_requirement": true,
            "compliance_status": "compliant",
            "details": "Publicação em Diário Oficial e jornal mencionadas"
        },
        
        // 1.3 e 1.4 - Intimações CPC 889
        "executado_notification": {
            "party_type": "Executado",
            "notification_mentioned": true,
            "compliance_status": "compliant",
            "details": "EMPRESA EXEMPLO LTDA"
        },
        "other_notifications": [
            {
                "party_type": "cônjuge",
                "notification_mentioned": true,
                "compliance_status": "compliant"
            },
            {
                "party_type": "credor hipotecário",
                "notification_mentioned": true,
                "compliance_status": "compliant",
                "details": "BANCO EXEMPLO S.A."
            }
        ],
        "cpc_889_compliance": "compliant",
        "notification_analysis": "Artigo 889 do CPC mencionado",
        
        // 1.5 - Valores mínimos
        "valuation": {
            "market_value": 850000.00,
            "first_auction_value": 850000.00,
            "second_auction_value": 425000.00,
            "minimum_bid_value": 425000.00,
            "first_auction_percentage": 100.0,
            "second_auction_percentage": 50.0,
            "below_50_percent": false,
            "risk_of_annulment": false,
            "values_found": {
                "evaluation": 850000.00,
                "first_auction": 850000.00,
                "second_auction": 425000.00
            },
            "analysis_notes": "2ª praça no limite mínimo (50.0%)"
        },
        
        // 1.6 - Débitos existentes
        "debts": {
            "iptu_debt": 15345.67,
            "condominium_debt": 8234.50,
            "mortgage_debt": 300000.00,
            "other_debts": {},
            "total_debt": 323580.17,
            "debt_responsibility": "quitado_com_lance",
            "debts_mentioned": ["IPTU", "Condomínio", "Hipoteca"],
            "analysis_notes": "Débitos serão quitados com o produto da arrematação"
        },
        
        // 1.7 - Ocupação do imóvel
        "property_status": {
            "occupancy_status": "vacant",
            "occupancy_details": "Imóvel desocupado e livre para transferência",
            "has_tenants": false,
            "has_squatters": false,
            "has_disputes": false,
            "possession_transfer_risk": "low",
            "risk_factors": []
        },
        
        // 1.8 - Restrições legais
        "legal_restrictions": {
            "has_judicial_unavailability": false,
            "has_liens": true,
            "has_mortgages": true,
            "has_seizures": false,
            "restrictions_found": ["Penhora", "Hipoteca"],
            "transfer_viability": "viable",
            "restriction_details": "Transferência possível mas com restrições a resolver"
        },
        
        // Avaliação geral
        "overall_risk_score": 25.0,
        "investment_viability_score": 85.0,
        "compliance_issues": [],
        "recommendations": [
            "✅ BOA OPORTUNIDADE: Indicadores favoráveis para investimento",
            "Imóvel desocupado - facilita imissão na posse",
            "Débitos serão quitados com produto da arrematação"
        ],
        "confidence_level": 0.85
    }
}
```

---

### 5. Recuperar Análise Judicial

**Método:** `GET`  
**URL:** `{{base_url}}/judicial-analysis/{{job_id}}`  
**Headers:** Padrão  
**Body:** Vazio  

---

## OUTROS ENDPOINTS ÚTEIS

### 6. Pipeline Completo (Tudo em uma requisição)

**Método:** `POST`  
**URL:** `{{base_url}}/process-complete-pipeline`  
**Headers:**
```
Content-Type: multipart/form-data
```
**Body:** form-data com arquivo

---

### 7. Buscar Análise de Texto

**Método:** `GET`  
**URL:** `{{base_url}}/job/{{job_id}}/text-analysis`  

---

### 8. Gerar Embeddings

**Método:** `POST`  
**URL:** `{{base_url}}/generate-embeddings/{{job_id}}`  

---

### 9. Análise ML

**Método:** `POST`  
**URL:** `{{base_url}}/predict-leads/{{job_id}}`  

---

### 10. Busca Semântica

**Método:** `POST`  
**URL:** `{{base_url}}/search/semantic`  
**Body:**
```json
{
    "query": "imóvel desocupado leilão judicial",
    "top_k": 10,
    "threshold": 0.7
}
```

---

## CONFIGURAÇÃO DO AMBIENTE NO POSTMAN

### 1. Criar Environment
1. Clique no ícone de engrenagem (canto superior direito)
2. Add → Environment
3. Nome: "PDF Pipeline Dev"

### 2. Variáveis do Environment
```
base_url: http://localhost:8000
job_id: (deixar vazio, será preenchido automaticamente)
```

### 3. Pre-request Scripts (Global)
```javascript
// Adicionar timestamp em todas as requisições
pm.request.headers.add({
    key: 'X-Request-Time',
    value: new Date().toISOString()
});
```

### 4. Tests Scripts (Global)
```javascript
// Verificar tempo de resposta
pm.test("Resposta rápida", function () {
    pm.expect(pm.response.responseTime).to.be.below(5000);
});

// Verificar status code
pm.test("Status code válido", function () {
    pm.expect(pm.response.code).to.be.oneOf([200, 201]);
});
```

---

## COLLECTION COMPLETA - IMPORTAR NO POSTMAN

Salve o JSON abaixo como `PDF_Pipeline_Judicial.postman_collection.json`:

```json
{
    "info": {
        "name": "PDF Pipeline - Análise Judicial",
        "description": "Collection completa para análise de editais de leilão judicial",
        "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
    },
    "item": [
        {
            "name": "1. Upload PDF",
            "request": {
                "method": "POST",
                "header": [],
                "body": {
                    "mode": "formdata",
                    "formdata": [
                        {
                            "key": "file",
                            "type": "file",
                            "src": ""
                        }
                    ]
                },
                "url": {
                    "raw": "{{base_url}}/upload",
                    "host": ["{{base_url}}"],
                    "path": ["upload"]
                }
            }
        },
        {
            "name": "2. Processar Texto",
            "request": {
                "method": "POST",
                "header": [],
                "url": {
                    "raw": "{{base_url}}/process-text/{{job_id}}",
                    "host": ["{{base_url}}"],
                    "path": ["process-text", "{{job_id}}"]
                }
            }
        },
        {
            "name": "3. Análise Judicial",
            "request": {
                "method": "POST",
                "header": [],
                "url": {
                    "raw": "{{base_url}}/judicial-analysis/{{job_id}}",
                    "host": ["{{base_url}}"],
                    "path": ["judicial-analysis", "{{job_id}}"]
                }
            }
        },
        {
            "name": "4. Recuperar Análise",
            "request": {
                "method": "GET",
                "header": [],
                "url": {
                    "raw": "{{base_url}}/judicial-analysis/{{job_id}}",
                    "host": ["{{base_url}}"],
                    "path": ["judicial-analysis", "{{job_id}}"]
                }
            }
        }
    ]
}
```

---

## EXEMPLOS DE USO PARA CADA ANÁLISE

### 1.1 - Verificar Natureza do Leilão
```javascript
// No Tests do Postman
var analysis = pm.response.json().analysis;
if (analysis.auction_type === "judicial") {
    console.log("✓ Leilão Judicial confirmado");
} else {
    console.log("⚠️ Tipo de leilão: " + analysis.auction_type);
}
```

### 1.2 - Verificar Publicação
```javascript
var pub = pm.response.json().analysis.publication_compliance;
if (pub.diario_oficial_mentioned && pub.meets_deadline_requirement) {
    console.log("✓ Publicação em conformidade");
} else {
    console.log("⚠️ Problemas na publicação");
}
```

### 1.5 - Verificar Valores Mínimos
```javascript
var val = pm.response.json().analysis.valuation;
if (val.below_50_percent) {
    console.log("⚠️ ALERTA: Valor abaixo de 50% - Risco de anulação!");
} else {
    console.log("✓ Valores dentro dos limites legais");
}
```

---

## TROUBLESHOOTING

### Erro 404 - Análise não encontrada
- Certifique-se de executar a análise de texto antes da judicial
- Verifique se o job_id está correto

### Erro 500 - Erro interno
- Verifique os logs do servidor
- Certifique-se que o PDF é válido

### Timeout
- PDFs muito grandes podem demorar
- Aumente o timeout no Postman: Settings → Request timeout → 60000ms