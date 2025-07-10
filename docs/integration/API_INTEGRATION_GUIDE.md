# Guia de Integração da API - Análise Judicial de Leilões

## Visão Geral

Esta API permite análise automatizada de editais de leilão judicial, extraindo informações críticas para tomada de decisão em investimentos imobiliários.

## Informações da API

- **Base URL**: `http://localhost:8000` (desenvolvimento) 
- **Formato**: JSON
- **Encoding**: UTF-8
- **Autenticação**: Não requerida (versão atual)

---

## Fluxo de Análise Judicial

```mermaid
graph LR
    A[Upload PDF] --> B[Processar Texto]
    B --> C[Análise Judicial]
    C --> D[Resultados Completos]
```

---

## Endpoints Principais

### 1. Upload de Documento

Faz upload do PDF do edital de leilão.

```http
POST /upload
Content-Type: multipart/form-data

file: [arquivo PDF]
```

**Exemplo cURL:**
```bash
curl -X POST http://localhost:8000/upload \
  -F "file=@edital_leilao.pdf"
```

**Exemplo Python:**
```python
import requests

with open('edital_leilao.pdf', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/upload',
        files={'file': f}
    )
    job_id = response.json()['job_id']
```

**Exemplo JavaScript (Node.js):**
```javascript
const FormData = require('form-data');
const fs = require('fs');
const axios = require('axios');

const form = new FormData();
form.append('file', fs.createReadStream('edital_leilao.pdf'));

const response = await axios.post('http://localhost:8000/upload', form, {
    headers: form.getHeaders()
});
const jobId = response.data.job_id;
```

**Response:**
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

---

### 2. Processar Texto

Extrai e analisa o texto do documento.

```http
POST /process-text/{job_id}
```

**Exemplo Python:**
```python
response = requests.post(f'http://localhost:8000/process-text/{job_id}')
```

---

### 3. Análise Judicial Completa

Realiza análise completa dos 8 pontos críticos do edital.

```http
POST /judicial-analysis/{job_id}
```

**Response Detalhada:**

```json
{
    "message": "Judicial auction analysis completed",
    "job_id": "98ac5938-b0b8-4fc3-8546-18b65ac20115",
    "analysis": {
        // Estrutura completa descrita abaixo
    }
}
```

---

## Estrutura de Resposta da Análise Judicial

### 1.1 Natureza do Leilão

```json
{
    "auction_type": "judicial",              // "judicial", "extrajudicial", "unknown"
    "auction_type_confidence": 0.9,          // 0.0 a 1.0
    "auction_type_indicators": [             // Palavras-chave encontradas
        "leilão judicial",
        "hasta pública",
        "execução"
    ]
}
```

### 1.2 Publicação do Edital

```json
{
    "publication_compliance": {
        "diario_oficial_mentioned": true,     // Menção ao Diário Oficial
        "newspaper_mentioned": true,          // Menção a jornal
        "publication_dates": [                // Datas de publicação encontradas
            "2024-03-08T00:00:00"
        ],
        "auction_dates": [                    // Datas dos leilões
            "2024-03-15T00:00:00",
            "2024-03-25T00:00:00"
        ],
        "days_between_publication_auction": 5, // Dias úteis
        "meets_deadline_requirement": true,    // Cumpre prazo mínimo de 5 dias
        "compliance_status": "compliant",      // "compliant", "non_compliant", "partially_compliant", "cannot_determine"
        "details": "Publicação em Diário Oficial e jornal mencionadas"
    }
}
```

### 1.3 e 1.4 Intimações (CPC Art. 889)

```json
{
    "executado_notification": {
        "party_type": "Executado",
        "party_identifier": "EMPRESA EXEMPLO LTDA",
        "notification_mentioned": true,
        "compliance_status": "compliant"
    },
    "other_notifications": [
        {
            "party_type": "cônjuge",
            "notification_mentioned": true,
            "compliance_status": "compliant"
        },
        {
            "party_type": "credor hipotecário",
            "party_identifier": "BANCO EXEMPLO S.A.",
            "notification_mentioned": true,
            "compliance_status": "compliant"
        }
    ],
    "cpc_889_compliance": "compliant",
    "notification_analysis": "Artigo 889 do CPC mencionado. Principais partes notificadas."
}
```

### 1.5 Valores Mínimos de Arrematação

```json
{
    "valuation": {
        "market_value": 850000.00,           // Valor de mercado/avaliação
        "first_auction_value": 850000.00,    // Valor 1ª praça
        "second_auction_value": 425000.00,   // Valor 2ª praça
        "minimum_bid_value": 425000.00,      // Lance mínimo
        "first_auction_percentage": 100.0,   // % em relação à avaliação
        "second_auction_percentage": 50.0,   // % em relação à avaliação
        "below_50_percent": false,           // Abaixo de 50%?
        "risk_of_annulment": false,          // Risco de anulação
        "analysis_notes": "2ª praça no limite mínimo (50.0%)"
    }
}
```

### 1.6 Débitos Existentes

```json
{
    "debts": {
        "iptu_debt": 15345.67,               // IPTU
        "condominium_debt": 8234.50,         // Condomínio
        "mortgage_debt": 300000.00,          // Hipoteca
        "other_debts": {},                   // Outros débitos
        "total_debt": 323580.17,             // Total
        "debt_responsibility": "quitado_com_lance", // "arrematante" ou "quitado_com_lance"
        "debts_mentioned": ["IPTU", "Condomínio", "Hipoteca"],
        "analysis_notes": "Débitos serão quitados com o produto da arrematação"
    }
}
```

### 1.7 Ocupação do Imóvel

```json
{
    "property_status": {
        "occupancy_status": "vacant",         // "vacant", "occupied_tenant", "occupied_owner", "occupied_squatter", "disputed", "unknown"
        "occupancy_details": "Imóvel desocupado e livre para transferência",
        "has_tenants": false,                // Tem inquilinos?
        "has_squatters": false,              // Tem posseiros?
        "has_disputes": false,               // Tem disputas?
        "possession_transfer_risk": "low",   // "low", "medium", "high", "unknown"
        "risk_factors": []                   // Fatores de risco específicos
    }
}
```

### 1.8 Restrições Legais

```json
{
    "legal_restrictions": {
        "has_judicial_unavailability": false, // Indisponibilidade judicial
        "has_liens": true,                   // Penhoras
        "has_mortgages": true,               // Hipotecas
        "has_seizures": false,               // Arrestos/Sequestros
        "restrictions_found": [              // Lista de restrições
            "Penhora",
            "Hipoteca"
        ],
        "transfer_viability": "viable",      // "clear", "viable", "viable_with_conditions", "risky", "blocked"
        "restriction_details": "Transferência possível mas com restrições a resolver"
    }
}
```

### Avaliação Final

```json
{
    "overall_risk_score": 25.0,              // 0-100 (100 = maior risco)
    "investment_viability_score": 85.0,      // 0-100 (100 = melhor oportunidade)
    "confidence_level": 0.85,                // 0-1 (confiança na análise)
    "compliance_issues": [],                 // Lista de problemas encontrados
    "recommendations": [                     // Recomendações
        "✅ BOA OPORTUNIDADE: Indicadores favoráveis para investimento",
        "Imóvel desocupado - facilita imissão na posse"
    ]
}
```

---

## Exemplos de Integração

### Python - Cliente Completo

```python
import requests
import json
from typing import Dict, Any

class JudicialAuctionAnalyzer:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
    
    def analyze_auction(self, pdf_path: str) -> Dict[str, Any]:
        """
        Analisa um edital de leilão judicial
        
        Args:
            pdf_path: Caminho para o arquivo PDF
            
        Returns:
            Dict com análise completa
        """
        # 1. Upload do PDF
        with open(pdf_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(f"{self.base_url}/upload", files=files)
            response.raise_for_status()
            job_id = response.json()['job_id']
        
        # 2. Processar texto
        response = requests.post(f"{self.base_url}/process-text/{job_id}")
        response.raise_for_status()
        
        # 3. Análise judicial
        response = requests.post(f"{self.base_url}/judicial-analysis/{job_id}")
        response.raise_for_status()
        
        return response.json()['analysis']
    
    def evaluate_investment(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Avalia se é um bom investimento baseado na análise
        """
        risk_score = analysis['overall_risk_score']
        viability_score = analysis['investment_viability_score']
        
        # Critérios de decisão
        is_recommended = (
            risk_score < 40 and 
            viability_score > 60 and
            not analysis['valuation']['below_50_percent'] and
            analysis['property_status']['occupancy_status'] == 'vacant'
        )
        
        return {
            'recommended': is_recommended,
            'risk_level': 'low' if risk_score < 30 else 'medium' if risk_score < 60 else 'high',
            'opportunity_level': 'excellent' if viability_score > 80 else 'good' if viability_score > 60 else 'fair',
            'key_concerns': analysis['compliance_issues'],
            'positive_factors': self._extract_positive_factors(analysis)
        }
    
    def _extract_positive_factors(self, analysis: Dict[str, Any]) -> list:
        factors = []
        
        if analysis['property_status']['occupancy_status'] == 'vacant':
            factors.append("Imóvel desocupado")
        
        if analysis['publication_compliance']['compliance_status'] == 'compliant':
            factors.append("Publicação em conformidade")
        
        if analysis['cpc_889_compliance'] == 'compliant':
            factors.append("Notificações legais cumpridas")
        
        if analysis['debts']['debt_responsibility'] == 'quitado_com_lance':
            factors.append("Débitos serão quitados")
        
        return factors

# Exemplo de uso
analyzer = JudicialAuctionAnalyzer()
result = analyzer.analyze_auction('edital_leilao.pdf')
evaluation = analyzer.evaluate_investment(result)

print(f"Recomendado: {'SIM' if evaluation['recommended'] else 'NÃO'}")
print(f"Nível de risco: {evaluation['risk_level']}")
print(f"Nível de oportunidade: {evaluation['opportunity_level']}")
```

### JavaScript/TypeScript - Cliente

```typescript
interface JudicialAnalysis {
    auction_type: 'judicial' | 'extrajudicial' | 'unknown';
    auction_type_confidence: number;
    publication_compliance: PublicationCompliance;
    valuation: ValuationAnalysis;
    debts: DebtAnalysis;
    property_status: PropertyStatus;
    legal_restrictions: LegalRestrictions;
    overall_risk_score: number;
    investment_viability_score: number;
    recommendations: string[];
}

class JudicialAuctionClient {
    constructor(private baseUrl: string = 'http://localhost:8000') {}
    
    async analyzeAuction(pdfFile: File): Promise<JudicialAnalysis> {
        // 1. Upload
        const formData = new FormData();
        formData.append('file', pdfFile);
        
        const uploadResponse = await fetch(`${this.baseUrl}/upload`, {
            method: 'POST',
            body: formData
        });
        
        const { job_id } = await uploadResponse.json();
        
        // 2. Process text
        await fetch(`${this.baseUrl}/process-text/${job_id}`, {
            method: 'POST'
        });
        
        // 3. Judicial analysis
        const analysisResponse = await fetch(`${this.baseUrl}/judicial-analysis/${job_id}`, {
            method: 'POST'
        });
        
        const { analysis } = await analysisResponse.json();
        return analysis;
    }
    
    evaluateRisk(analysis: JudicialAnalysis): string {
        if (analysis.overall_risk_score < 30) return 'BAIXO';
        if (analysis.overall_risk_score < 60) return 'MÉDIO';
        return 'ALTO';
    }
}
```

### C# - Cliente .NET

```csharp
using System;
using System.Net.Http;
using System.Threading.Tasks;
using Newtonsoft.Json;

public class JudicialAuctionClient
{
    private readonly HttpClient _httpClient;
    private readonly string _baseUrl;
    
    public JudicialAuctionClient(string baseUrl = "http://localhost:8000")
    {
        _baseUrl = baseUrl;
        _httpClient = new HttpClient();
    }
    
    public async Task<JudicialAnalysis> AnalyzeAuctionAsync(string pdfPath)
    {
        // 1. Upload
        using var form = new MultipartFormDataContent();
        using var fileStream = File.OpenRead(pdfPath);
        form.Add(new StreamContent(fileStream), "file", Path.GetFileName(pdfPath));
        
        var uploadResponse = await _httpClient.PostAsync($"{_baseUrl}/upload", form);
        var uploadResult = JsonConvert.DeserializeObject<UploadResponse>(
            await uploadResponse.Content.ReadAsStringAsync()
        );
        
        // 2. Process text
        await _httpClient.PostAsync($"{_baseUrl}/process-text/{uploadResult.JobId}", null);
        
        // 3. Judicial analysis
        var analysisResponse = await _httpClient.PostAsync(
            $"{_baseUrl}/judicial-analysis/{uploadResult.JobId}", null
        );
        
        var result = JsonConvert.DeserializeObject<AnalysisResponse>(
            await analysisResponse.Content.ReadAsStringAsync()
        );
        
        return result.Analysis;
    }
}
```

---

## Códigos de Status HTTP

| Código | Significado |
|--------|-------------|
| 200 | Sucesso |
| 400 | Requisição inválida (ex: arquivo não é PDF) |
| 404 | Recurso não encontrado (ex: job_id inválido) |
| 422 | Entidade não processável |
| 500 | Erro interno do servidor |

---

## Melhores Práticas

1. **Sempre processar texto antes da análise judicial**
   ```python
   # Correto
   upload() -> process_text() -> judicial_analysis()
   
   # Incorreto
   upload() -> judicial_analysis()  # Erro 404
   ```

2. **Implementar retry para requisições**
   ```python
   import time
   
   def retry_request(func, max_attempts=3):
       for i in range(max_attempts):
           try:
               return func()
           except Exception as e:
               if i == max_attempts - 1:
                   raise
               time.sleep(2 ** i)  # Backoff exponencial
   ```

3. **Validar respostas**
   ```python
   if analysis['confidence_level'] < 0.5:
       print("⚠️ Baixa confiança na análise - verificar manualmente")
   ```

4. **Monitorar indicadores críticos**
   ```python
   # Alertas críticos
   if analysis['valuation']['below_50_percent']:
       alert("RISCO: Valor abaixo de 50% - possível anulação")
   
   if analysis['legal_restrictions']['has_judicial_unavailability']:
       alert("BLOQUEIO: Indisponibilidade judicial detectada")
   ```

---

## Limitações da API

1. **Tamanho máximo do arquivo**: 50MB
2. **Timeout de processamento**: 5 minutos
3. **Formatos aceitos**: Apenas PDF
4. **Idioma**: Otimizado para português brasileiro
5. **Análise baseada em texto**: Não processa imagens dentro do PDF

---

## Suporte e Contato

- **Documentação**: [GitHub Wiki](https://github.com/seu-repo/wiki)
- **Issues**: [GitHub Issues](https://github.com/seu-repo/issues)
- **Email**: suporte@exemplo.com

---

## Changelog

### v1.0.0 (2024-01-04)
- Lançamento inicial
- Análise completa dos 8 pontos do edital judicial
- Suporte para CPC Art. 889
- Cálculo de prazos e valores