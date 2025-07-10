# 🏛️ Judicial Analysis Documentation

Specialized functionality for Brazilian judicial auction documents analysis.

## 📋 Available Documentation

### Core Guides
- **[Judicial Analysis Usage](JUDICIAL_ANALYSIS_USAGE.md)** - Complete usage guide for judicial analysis features
- **[System Analysis](SYSTEM_ANALYSIS_JUDICIAL_AUCTIONS.md)** - Technical implementation and system details
- **[Assessment Guide](judicial_auction_assessment.md)** - Document evaluation criteria and methodology

## 🎯 What is Judicial Analysis?

The Judicial Analysis module provides specialized processing for Brazilian judicial auction documents, including:

### Key Features
- **Legal Compliance Checking** - Verification against CPC Article 889
- **Property Valuation Analysis** - Market-based property assessment
- **Risk Factor Scoring** - Comprehensive risk evaluation (50+ factors)
- **Document Classification** - Automated categorization of legal documents
- **Financial Analysis** - Debt, encumbrance, and tax analysis

### Supported Document Types
- Judicial auction notices (Editais de leilão)
- Property evaluation reports
- Legal proceedings documents
- Financial statements and debt records

## 🚀 Quick Start

### Basic Usage
```bash
# 1. Upload a judicial document
curl -X POST "http://localhost:8000/api/v1/jobs/upload" \
  -F "file=@judicial_auction.pdf"

# 2. Trigger judicial analysis
curl -X POST "http://localhost:8000/judicial-analysis/{job_id}"

# 3. Get analysis results
curl "http://localhost:8000/judicial-analysis/{job_id}"
```

### Response Structure
The judicial analysis returns structured data including:
- Property details and valuation
- Legal compliance status
- Risk assessment scores
- Financial analysis
- Market comparables

## 🏛️ Brazilian Legal Context

This system is specifically designed for the Brazilian legal system and includes:

### Legal Framework
- **CPC (Código de Processo Civil)** compliance
- **Lei de Leilões** regulations
- **Brazilian Real Estate Law** integration
- **Tax and Financial Regulations** awareness

### Regional Expertise
- Understanding of Brazilian court systems
- Regional property market knowledge
- Local legal terminology and patterns
- Brazilian Portuguese language processing

## 📖 Related Documentation
- [API Integration Guide](../integration/API_INTEGRATION_GUIDE.md) - How to integrate judicial analysis
- [Postman Examples](../postman/POSTMAN_JUDICIAL_EXAMPLE.md) - API testing examples
- [Architecture Documentation](../architecture/) - Technical implementation details