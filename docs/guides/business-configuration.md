# 🎯 Guia de Configuração por Tipo de Negócio

Este guia explica como configurar o sistema para diferentes tipos de negócio e objetivos específicos.

## 📋 Configuração Atual: Leilões Judiciais

O sistema está atualmente configurado para **análise de leilões judiciais brasileiros** com foco em **oportunidades de investimento imobiliário**.

### 🎯 Objetivos Atuais
- Identificar oportunidades de investimento imobiliário
- Avaliar riscos legais em leilões judiciais
- Analisar viabilidade financeira de arrematações
- Verificar conformidade processual

### 📊 Critérios de Scoring Atuais

| Critério | Pontuação | Descrição |
|----------|-----------|-----------|
| **Confirmação de Leilão Judicial** | +30 pontos | Presença de termos como "leilão judicial", "hasta pública", "arrematação" |
| **Notificações Legais** | +25 pontos | Publicações no Diário Oficial, intimações, editais |
| **Dados Financeiros** | +20 pontos | Valores de avaliação, lance mínimo, débitos |
| **Status de Ocupação** | +15 pontos | Imóvel livre vs. ocupado irregularmente |
| **Conformidade Legal** | +10 pontos | Procedimentos corretos, prazos respeitados |
| **Restrições Legais** | -15 pontos | Indisponibilidades, penhoras, gravames |

### 🔍 Keywords Configuradas

#### Leilão Judicial
```python
'judicial_auction': [
    'leilão judicial', 'hasta pública', 'arrematação', 'execução fiscal',
    'penhora', 'alienação judicial', 'hasta', 'leilão', 'arrematante',
    'adjudicação', 'execução', 'expropriação'
]
```

#### Notificações Legais
```python
'legal_notifications': [
    'edital', 'intimação', 'citação', 'diário oficial', 'publicação',
    'notificação', 'cientificação', 'comunicação', 'aviso',
    'art. 889', 'CPC', 'código de processo civil'
]
```

#### Avaliação de Propriedade
```python
'property_valuation': [
    'avaliação', 'laudo', 'perícia', 'valor de mercado', 'valor venal',
    'valor da avaliação', 'preço', 'lance mínimo', 'primeira praça',
    'segunda praça', 'valor inicial'
]
```

## 🔧 Como Personalizar para Seu Negócio

### 1. **Identificar Seus Objetivos**

Primeiro, defina claramente:
- Que tipo de documentos você processa?
- Que oportunidades você quer identificar?
- Quais são seus critérios de sucesso?
- Que riscos você quer evitar?

### 2. **Configurar Keywords Específicas**

Edite o arquivo `text_processing/text_engine.py`:

```python
LEAD_KEYWORDS = {
    'seu_objetivo_principal': [
        'palavra1', 'palavra2', 'frase específica'
    ],
    'criterio_financeiro': [
        'valor', 'preço', 'custo', 'investimento'
    ],
    'indicadores_urgencia': [
        'prazo', 'urgente', 'data limite'
    ]
    # ... adicione suas categorias
}
```

### 3. **Ajustar Critérios de Pontuação**

No método `analyze_lead_potential()`:

```python
# Exemplo: Seu critério principal (+40 pontos)
if seus_indicadores:
    score += 40
    confidence_factors.append("Critério principal identificado")

# Exemplo: Fator de risco (-20 pontos)
if fatores_de_risco:
    score -= 20
    risk_factors.append("Risco identificado")
```

### 4. **Personalizar Features de ML**

Edite `ml_engine/feature_engineering.py`:

```python
# Adicione suas features específicas
class FeatureSet:
    # ... features existentes ...
    
    # Suas features personalizadas
    seu_score_personalizado: float = 0.0
    seus_indicadores_count: int = 0
    seu_nivel_risco: str = "unknown"
```

## 📝 Exemplos de Configuração

### 🏢 **Exemplo: B2B Tech Sales**

```python
LEAD_KEYWORDS = {
    'technology_needs': [
        'sistema', 'software', 'automação', 'digital',
        'transformação digital', 'modernização'
    ],
    'decision_makers': [
        'diretor', 'gerente', 'ceo', 'cto', 'coordenador'
    ],
    'budget_indicators': [
        'orçamento', 'investimento', 'verba', 'recursos'
    ],
    'urgency': [
        'urgente', 'prazo', 'asap', 'imediato'
    ]
}

# Scoring: Technology needs (+35), Decision makers (+25), Budget (+20), Urgency (+15)
```

### 🏥 **Exemplo: Healthcare Procurement**

```python
LEAD_KEYWORDS = {
    'medical_equipment': [
        'equipamento médico', 'aparelho', 'dispositivo',
        'tecnologia médica', 'instrumental'
    ],
    'regulatory_compliance': [
        'anvisa', 'certificação', 'norma', 'regulamentação'
    ],
    'hospital_indicators': [
        'hospital', 'clínica', 'unidade de saúde', 'sus'
    ],
    'procurement_terms': [
        'licitação', 'pregão', 'concorrência', 'aquisição'
    ]
}

# Scoring: Medical equipment (+30), Compliance (+25), Hospital (+20), Procurement (+15)
```

### 🏗️ **Exemplo: Construction Contracts**

```python
LEAD_KEYWORDS = {
    'construction_projects': [
        'obra', 'construção', 'projeto', 'empreendimento',
        'edificação', 'infraestrutura'
    ],
    'engineering_terms': [
        'engenharia', 'projeto executivo', 'memorial descritivo'
    ],
    'contract_indicators': [
        'contrato', 'empreitada', 'prestação de serviços'
    ],
    'timeline_pressure': [
        'prazo', 'cronograma', 'entrega', 'conclusão'
    ]
}
```

## 🎛️ Configurações Avançadas

### **Padrões Regex Personalizados**

Adicione padrões específicos para seu domínio:

```python
PATTERNS = {
    # Padrões existentes...
    
    # Seus padrões personalizados
    'seu_codigo_especifico': r'SEU-\d{4}-\d{2}',
    'seu_valor_personalizado': r'Valor:\s*R\$\s?[\d.,]+',
    'sua_data_especifica': r'\d{2}\/\d{2}\/\d{4}'
}
```

### **Features de ML Personalizadas**

```python
def _extract_suas_features(self, features: FeatureSet, text: str) -> FeatureSet:
    """Extrai suas features específicas"""
    
    # Sua lógica personalizada
    seus_indicadores = self._count_keywords(text, suas_keywords)
    features.seu_score = min(100, seus_indicadores * 25)
    
    # Análise de risco personalizada
    if 'palavra_de_risco' in text.lower():
        features.seu_nivel_risco = 'high'
    
    return features
```

## 📊 Monitoramento e Ajustes

### **Métricas de Performance**

Monitore:
- **Precisão**: % de leads identificados que são realmente válidos
- **Recall**: % de leads válidos que foram identificados
- **Score Distribution**: Distribuição dos scores para ajustar thresholds

### **Iteração Contínua**

1. **Colete Feedback**: Analise resultados reais vs. previsões
2. **Ajuste Keywords**: Adicione/remova termos baseado na performance
3. **Refine Scoring**: Ajuste pesos baseado na importância real
4. **Teste A/B**: Compare diferentes configurações

## 🚀 Implementação

### **Passos para Implementar Sua Configuração**

1. **Backup**: Faça backup das configurações atuais
2. **Teste Gradual**: Implemente mudanças incrementalmente
3. **Validação**: Teste com documentos conhecidos
4. **Deployment**: Implante em produção com monitoramento
5. **Otimização**: Ajuste baseado em dados reais

### **Exemplo de Script de Configuração**

```python
# config/business_config.py
class BusinessConfig:
    def __init__(self, business_type: str):
        self.business_type = business_type
        self.keywords = self._load_keywords()
        self.scoring_weights = self._load_scoring_weights()
        
    def _load_keywords(self):
        if self.business_type == "judicial_auction":
            return JUDICIAL_AUCTION_KEYWORDS
        elif self.business_type == "b2b_tech":
            return B2B_TECH_KEYWORDS
        # ... outras configurações
        
    def apply_configuration(self):
        # Aplicar configuração ao sistema
        pass
```

## 📞 Suporte

Para configurações específicas do seu negócio:
- 📖 **Documentação Técnica**: [docs/architecture/](../architecture/)
- 🔧 **Guia de Desenvolvimento**: [developer-guide.md](developer-guide.md)
- 🐛 **Issues**: Reporte problemas no GitHub
- 💬 **Discussões**: Compartilhe casos de uso

---

**💡 Dica**: Comece com configurações simples e evolua gradualmente baseado nos resultados reais do seu negócio. 