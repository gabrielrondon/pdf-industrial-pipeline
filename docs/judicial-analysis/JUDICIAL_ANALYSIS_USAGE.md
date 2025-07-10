# Judicial Auction Analysis - Usage Guide

## Overview

The PDF Industrial Pipeline now includes comprehensive judicial auction analysis capabilities specifically designed for Brazilian legal documents. This feature analyzes auction notices ("editais de leilão judicial") to extract critical compliance and investment information.

## Features

The judicial analysis module provides detailed analysis for:

### 1. Análise do Edital do Leilão

#### 1.1 Natureza do leilão (Auction Type)
- **Identifies**: Whether the auction is judicial or extrajudicial
- **How it works**: Analyzes keywords and legal indicators
- **Output**: `auction_type` (judicial/extrajudicial/unknown) with confidence score

#### 1.2 Publicação do edital (Publication Compliance)
- **Checks**: If published in Diário Oficial and newspaper
- **Verifies**: 5-day minimum deadline between publication and auction
- **Output**: Compliance status and specific dates found

#### 1.3 & 1.4 Intimação (CPC Art. 889 Notifications)
- **Tracks**: Notification of executado (debtor) and other required parties
- **Identifies**: Cônjuge, credores, co-proprietários, etc.
- **Output**: List of notified parties and compliance assessment

#### 1.5 Valores mínimos (Valuation Analysis)
- **Extracts**: 1st and 2nd auction values, market value
- **Calculates**: Percentage of market value
- **Alerts**: If value is below 50% (risk of annulment)

#### 1.6 Débitos existentes (Debt Analysis)
- **Identifies**: IPTU, condominium fees, mortgages
- **Determines**: Who is responsible for debts
- **Output**: Total debt amount and payment responsibility

#### 1.7 Ocupação do imóvel (Property Status)
- **Detects**: If property is vacant, occupied by tenant/owner/squatter
- **Assesses**: Risk for possession transfer
- **Output**: Occupancy status and risk factors

#### 1.8 Restrição legal (Legal Restrictions)
- **Finds**: Judicial unavailability, liens, mortgages
- **Evaluates**: Transfer viability
- **Output**: List of restrictions and severity assessment

## API Usage

### Step 1: Upload and Process Document

First, upload the PDF and run text analysis:

```bash
# Upload PDF
curl -X POST http://localhost:8000/upload \
  -F "file=@edital_leilao.pdf"

# Response:
{
  "job_id": "98ac5938-b0b8-4fc3-8546-18b65ac20115",
  "message": "PDF uploaded and processed successfully",
  ...
}

# Run text analysis
curl -X POST http://localhost:8000/process-text/{job_id}
```

### Step 2: Run Judicial Analysis

```bash
curl -X POST http://localhost:8000/judicial-analysis/{job_id}
```

### Step 3: Retrieve Results

```bash
curl -X GET http://localhost:8000/judicial-analysis/{job_id}
```

## Example Response

```json
{
  "message": "Judicial analysis retrieved",
  "job_id": "98ac5938-b0b8-4fc3-8546-18b65ac20115",
  "analysis": {
    "auction_type": "judicial",
    "auction_type_confidence": 0.9,
    "auction_type_indicators": ["leilão judicial", "execução", "juiz"],
    
    "publication_compliance": {
      "diario_oficial_mentioned": true,
      "newspaper_mentioned": true,
      "publication_dates": ["2024-03-08T00:00:00"],
      "auction_dates": ["2024-03-15T00:00:00", "2024-03-25T00:00:00"],
      "days_between_publication_auction": 5,
      "meets_deadline_requirement": true,
      "compliance_status": "compliant"
    },
    
    "cpc_889_compliance": "compliant",
    "executado_notification": {
      "party_type": "Executado",
      "notification_mentioned": true,
      "compliance_status": "compliant"
    },
    
    "valuation": {
      "market_value": 850000.0,
      "first_auction_value": 850000.0,
      "second_auction_value": 425000.0,
      "second_auction_percentage": 50.0,
      "below_50_percent": false,
      "risk_of_annulment": false
    },
    
    "debts": {
      "iptu_debt": 15345.67,
      "condominium_debt": 8234.50,
      "total_debt": 23580.17,
      "debt_responsibility": "quitado_com_lance",
      "analysis_notes": "Débitos serão quitados com o produto da arrematação"
    },
    
    "property_status": {
      "occupancy_status": "vacant",
      "occupancy_details": "Imóvel desocupado e livre para transferência",
      "possession_transfer_risk": "low"
    },
    
    "legal_restrictions": {
      "has_judicial_unavailability": false,
      "has_liens": true,
      "restrictions_found": ["Penhora", "Hipoteca"],
      "transfer_viability": "viable"
    },
    
    "overall_risk_score": 25.0,
    "investment_viability_score": 75.0,
    "confidence_level": 0.85,
    
    "recommendations": [
      "✅ BOA OPORTUNIDADE: Indicadores favoráveis para investimento",
      "Imóvel desocupado - facilita imissão na posse",
      "Débitos serão quitados com produto da arrematação"
    ],
    
    "compliance_issues": []
  }
}
```

## Risk Assessment Guide

### Overall Risk Score (0-100)
- **0-30**: Low risk - Good opportunity
- **31-50**: Moderate risk - Careful analysis needed
- **51-70**: High risk - Significant issues
- **71-100**: Very high risk - Not recommended

### Investment Viability Score (0-100)
- **0-30**: Low viability
- **31-50**: Moderate opportunity
- **51-70**: Good opportunity
- **71-100**: Excellent opportunity

## Key Compliance Alerts

The system will flag critical issues such as:

1. **Publication deadline violations**: Less than 5 business days
2. **Missing notifications**: Required parties not notified per CPC 889
3. **Below 50% valuation**: Risk of auction annulment
4. **Judicial unavailability**: Property transfer may be blocked
5. **Occupied property**: High risk for possession transfer

## Integration Example

```python
import requests
import json

# Function to analyze judicial auction
def analyze_auction_document(pdf_path):
    # 1. Upload PDF
    with open(pdf_path, 'rb') as f:
        files = {'file': f}
        upload_response = requests.post('http://localhost:8000/upload', files=files)
    
    job_id = upload_response.json()['job_id']
    
    # 2. Process text
    text_response = requests.post(f'http://localhost:8000/process-text/{job_id}')
    
    # 3. Run judicial analysis
    analysis_response = requests.post(f'http://localhost:8000/judicial-analysis/{job_id}')
    
    # 4. Get results
    results = analysis_response.json()['analysis']
    
    # 5. Make investment decision
    if results['overall_risk_score'] < 40 and results['investment_viability_score'] > 60:
        print("✅ RECOMMENDED: Good investment opportunity")
    else:
        print("⚠️ CAUTION: Review compliance issues before proceeding")
    
    return results

# Example usage
results = analyze_auction_document('edital_leilao.pdf')
print(json.dumps(results, indent=2))
```

## Best Practices

1. **Always run text analysis first**: The judicial analyzer depends on extracted text
2. **Review all compliance issues**: Even one critical issue can invalidate an auction
3. **Check confidence levels**: Lower confidence may indicate poor document quality
4. **Verify critical information manually**: Especially for high-value properties
5. **Consider all risk factors**: Combine risk score with your own due diligence

## Limitations

- Cannot verify external information (actual publications, court records)
- Date parsing assumes DD/MM/YYYY format (Brazilian standard)
- Financial values must be in R$ format
- Legal analysis is based on keyword matching, not legal reasoning
- Cannot determine if notifications were actually delivered

## Next Steps

After analysis, consider:
1. Consulting with a lawyer for high-risk properties
2. Verifying publication in actual Diário Oficial
3. Checking property registration for updated information
4. Visiting the property to confirm occupancy status
5. Calculating total investment including debts and fees