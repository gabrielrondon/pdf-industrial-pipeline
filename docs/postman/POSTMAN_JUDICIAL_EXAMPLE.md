# Exemplo Completo - Análise Judicial no Postman

## Problema: "Method Not Allowed"

Se você está recebendo `{"detail": "Method Not Allowed"}`, verifique:

1. **O servidor foi reiniciado após as mudanças?**
   ```bash
   # Pare o servidor (Ctrl+C) e reinicie:
   python main.py
   ```

2. **Está usando o método HTTP correto?**
   - ✅ POST para `/judicial-analysis/{job_id}` (executar análise)
   - ✅ GET para `/judicial-analysis/{job_id}` (recuperar resultados)

## Configuração Passo a Passo no Postman

### 1. Criar as Requisições

#### Request 1: Upload PDF
```
Method: POST
URL: http://localhost:8000/upload
Body: 
  - Tipo: form-data
  - Key: file (tipo File)
  - Value: Selecione seu PDF
```

#### Request 2: Processar Texto
```
Method: POST
URL: http://localhost:8000/process-text/{{job_id}}
Headers:
  - Content-Type: application/json
Body: (vazio)
```

#### Request 3: Análise Judicial (EXECUTAR)
```
Method: POST
URL: http://localhost:8000/judicial-analysis/{{job_id}}
Headers:
  - Content-Type: application/json
  - Accept: application/json
Body: (vazio)
```

#### Request 4: Recuperar Análise Judicial
```
Method: GET
URL: http://localhost:8000/judicial-analysis/{{job_id}}
Headers:
  - Accept: application/json
```

### 2. Scripts para Automatização

#### No Request 1 (Upload), adicione em "Tests":
```javascript
// Salvar job_id automaticamente
if (pm.response.code === 200) {
    var jsonData = pm.response.json();
    pm.environment.set("job_id", jsonData.job_id);
    console.log("Job ID salvo: " + jsonData.job_id);
    
    pm.test("Upload bem sucedido", function () {
        pm.response.to.have.status(200);
        pm.expect(jsonData).to.have.property('job_id');
    });
}
```

#### No Request 3 (Análise Judicial POST), adicione em "Tests":
```javascript
if (pm.response.code === 200) {
    var analysis = pm.response.json().analysis;
    
    // Verificar natureza do leilão
    pm.test("1.1 - Natureza do leilão identificada", function () {
        pm.expect(analysis.auction_type).to.be.oneOf(['judicial', 'extrajudicial', 'unknown']);
        console.log("Tipo: " + analysis.auction_type + " (confiança: " + (analysis.auction_type_confidence * 100) + "%)");
    });
    
    // Verificar publicação
    pm.test("1.2 - Publicação analisada", function () {
        pm.expect(analysis.publication_compliance).to.exist;
        console.log("Diário Oficial: " + (analysis.publication_compliance.diario_oficial_mentioned ? "✓" : "✗"));
        console.log("Prazo mínimo: " + (analysis.publication_compliance.meets_deadline_requirement ? "✓" : "✗"));
    });
    
    // Verificar valores
    pm.test("1.5 - Valores analisados", function () {
        pm.expect(analysis.valuation).to.exist;
        if (analysis.valuation.below_50_percent) {
            console.warn("⚠️ ALERTA: Valor abaixo de 50% - Risco de anulação!");
        }
    });
    
    // Verificar ocupação
    pm.test("1.7 - Status do imóvel", function () {
        pm.expect(analysis.property_status).to.exist;
        console.log("Ocupação: " + analysis.property_status.occupancy_status);
    });
    
    // Resumo final
    console.log("\n=== RESUMO ===");
    console.log("Risco: " + analysis.overall_risk_score + "/100");
    console.log("Viabilidade: " + analysis.investment_viability_score + "/100");
    console.log("Recomendações: " + analysis.recommendations.length);
}
```

### 3. Collection Completa para Importar

Salve como `Judicial_Analysis.postman_collection.json`:

```json
{
    "info": {
        "name": "Análise Judicial - Leilões",
        "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
    },
    "item": [
        {
            "name": "1. Upload PDF",
            "event": [
                {
                    "listen": "test",
                    "script": {
                        "exec": [
                            "if (pm.response.code === 200) {",
                            "    var jsonData = pm.response.json();",
                            "    pm.environment.set('job_id', jsonData.job_id);",
                            "    console.log('Job ID: ' + jsonData.job_id);",
                            "}"
                        ]
                    }
                }
            ],
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
                "url": "{{base_url}}/upload"
            }
        },
        {
            "name": "2. Processar Texto",
            "request": {
                "method": "POST",
                "header": [
                    {
                        "key": "Content-Type",
                        "value": "application/json"
                    }
                ],
                "url": "{{base_url}}/process-text/{{job_id}}"
            }
        },
        {
            "name": "3. Executar Análise Judicial",
            "request": {
                "method": "POST",
                "header": [
                    {
                        "key": "Content-Type",
                        "value": "application/json"
                    }
                ],
                "url": "{{base_url}}/judicial-analysis/{{job_id}}"
            }
        },
        {
            "name": "4. Recuperar Análise Judicial",
            "request": {
                "method": "GET",
                "header": [],
                "url": "{{base_url}}/judicial-analysis/{{job_id}}"
            }
        }
    ],
    "variable": [
        {
            "key": "base_url",
            "value": "http://localhost:8000"
        }
    ]
}
```

## Troubleshooting

### Se continuar com "Method Not Allowed":

1. **Verifique a documentação da API:**
   ```
   http://localhost:8000/docs
   ```
   Procure por `/judicial-analysis/{job_id}` e veja se aparece como POST

2. **Teste com cURL:**
   ```bash
   # Substitua pelo seu job_id
   curl -X POST http://localhost:8000/judicial-analysis/seu-job-id-aqui \
        -H "Content-Type: application/json"
   ```

3. **Verifique os logs do servidor:**
   O terminal onde está rodando `python main.py` mostrará os erros

4. **Teste com o script Python:**
   ```bash
   python test_judicial_endpoint.py
   ```

### Possíveis Causas do Erro:

1. **Servidor não reiniciado** após mudanças no código
2. **Job ID inválido** - o job precisa existir e ter análise de texto
3. **Ordem errada** - precisa fazer upload → processar texto → análise judicial
4. **Erro de digitação** na URL

## Exemplo de Resposta Esperada

Quando funcionar corretamente, você verá:

```json
{
    "message": "Judicial auction analysis completed",
    "job_id": "98ac5938-b0b8-4fc3-8546-18b65ac20115",
    "analysis": {
        "auction_type": "judicial",
        "auction_type_confidence": 0.9,
        "publication_compliance": {
            "diario_oficial_mentioned": true,
            "newspaper_mentioned": false,
            "compliance_status": "partially_compliant"
        },
        "valuation": {
            "second_auction_percentage": 50.0,
            "below_50_percent": false,
            "risk_of_annulment": false
        },
        "property_status": {
            "occupancy_status": "vacant",
            "possession_transfer_risk": "low"
        },
        "overall_risk_score": 25.0,
        "investment_viability_score": 75.0,
        "recommendations": [
            "✅ BOA OPORTUNIDADE: Indicadores favoráveis para investimento"
        ]
    }
}
```