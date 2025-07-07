"""
Enhanced regex patterns and keywords for judicial auction analysis
"""

import re
from typing import Dict, List, Pattern


class JudicialPatterns:
    """Regex patterns for judicial document analysis"""
    
    # Enhanced date patterns
    DATE_PATTERNS = {
        'standard': re.compile(r'\b(\d{1,2})[\/\-](\d{1,2})[\/\-](\d{2,4})\b'),
        'written': re.compile(r'\b(\d{1,2})\s+de\s+(\w+)\s+de\s+(\d{4})\b', re.IGNORECASE),
        'auction_date': re.compile(
            r'(?:leilão|hasta|praça|arrematação).*?(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})', 
            re.IGNORECASE | re.DOTALL
        ),
        'publication_date': re.compile(
            r'(?:publicad[oa]|publicação|edital).*?(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})', 
            re.IGNORECASE | re.DOTALL
        ),
    }
    
    # Month names for date parsing
    MONTH_NAMES = {
        'janeiro': 1, 'jan': 1, 'fevereiro': 2, 'fev': 2, 'março': 3, 'mar': 3,
        'abril': 4, 'abr': 4, 'maio': 5, 'mai': 5, 'junho': 6, 'jun': 6,
        'julho': 7, 'jul': 7, 'agosto': 8, 'ago': 8, 'setembro': 9, 'set': 9,
        'outubro': 10, 'out': 10, 'novembro': 11, 'nov': 11, 'dezembro': 12, 'dez': 12
    }
    
    # Enhanced financial patterns
    FINANCIAL_PATTERNS = {
        'monetary': re.compile(
            r'R\$\s*([0-9]{1,3}(?:\.[0-9]{3})*(?:,[0-9]{2})?)', 
            re.IGNORECASE
        ),
        'percentage': re.compile(r'(\d+(?:,\d+)?)\s*%'),
        'iptu': re.compile(
            r'IPTU.*?R\$\s*([0-9]{1,3}(?:\.[0-9]{3})*(?:,[0-9]{2})?)',
            re.IGNORECASE | re.DOTALL
        ),
        'condominium': re.compile(
            r'condom[íi]nio.*?R\$\s*([0-9]{1,3}(?:\.[0-9]{3})*(?:,[0-9]{2})?)',
            re.IGNORECASE | re.DOTALL
        ),
        'evaluation': re.compile(
            r'avalia[çc][ãa]o.*?R\$\s*([0-9]{1,3}(?:\.[0-9]{3})*(?:,[0-9]{2})?)',
            re.IGNORECASE | re.DOTALL
        ),
        'minimum_bid': re.compile(
            r'(?:lance\s*m[íi]nimo|valor\s*m[íi]nimo).*?R\$\s*([0-9]{1,3}(?:\.[0-9]{3})*(?:,[0-9]{2})?)',
            re.IGNORECASE | re.DOTALL
        ),
    }
    
    # CPC Article 889 related patterns
    CPC_889_PATTERNS = {
        'article_mention': re.compile(
            r'(?:art(?:igo)?\.?\s*889|CPC.*?889)',
            re.IGNORECASE
        ),
        'notification_verb': re.compile(
            r'(?:intimad[oa]s?|notificad[oa]s?|citad[oa]s?|cientificad[oa]s?)',
            re.IGNORECASE
        ),
        'required_parties': re.compile(
            r'(?:executad[oa]|c[ôo]njuge|copropriet[áa]rio|titular\s+de\s+direito|'
            r'credor\s+hipotec[áa]rio|usufrutu[áa]rio|credor\s+pignorat[íi]cio|'
            r'promitente\s+comprador|Union|Estado|Munic[íi]pio)',
            re.IGNORECASE
        ),
    }
    
    # Legal restriction patterns
    RESTRICTION_PATTERNS = {
        'unavailability': re.compile(
            r'(?:indisponibilidade|bloqueio\s+judicial|penhora\s+de\s+rosto)',
            re.IGNORECASE
        ),
        'lien': re.compile(
            r'(?:penhora|arresto|sequestro|hipoteca|aliena[çc][ãa]o\s+fiduci[áa]ria)',
            re.IGNORECASE
        ),
        'encumbrance': re.compile(
            r'(?:[ôo]nus|grava[çc][ãa]o|restri[çc][ãa]o|impedimento)',
            re.IGNORECASE
        ),
    }
    
    # Property status patterns
    PROPERTY_PATTERNS = {
        'vacant': re.compile(
            r'(?:desocupad[oa]|vag[oa]|livre\s+de\s+pessoas|sem\s+ocupantes?|'
            r'livre\s+e\s+desembaraçad[oa])',
            re.IGNORECASE
        ),
        'occupied': re.compile(
            r'(?:ocupad[oa]|inquilin[oa]|locat[áa]rio|arrendat[áa]rio|comodat[áa]rio)',
            re.IGNORECASE
        ),
        'squatter': re.compile(
            r'(?:posseir[oa]|invas[ãa]o|ocupa[çc][ãa]o\s+irregular)',
            re.IGNORECASE
        ),
        'dispute': re.compile(
            r'(?:lit[íi]gio|disputa|controv[ée]rsia|conflito\s+de\s+posse)',
            re.IGNORECASE
        ),
    }


class JudicialKeywords:
    """Enhanced keyword sets for judicial analysis"""
    
    # Auction type indicators
    AUCTION_TYPE = {
        'judicial': [
            'leilão judicial', 'hasta pública', 'praça judicial',
            'alienação judicial', 'arrematação judicial', 'execução',
            'processo judicial', 'determinação judicial', 'ordem judicial',
            'juiz', 'magistrado', 'vara', 'tribunal', 'fórum',
            'processo de execução', 'cumprimento de sentença'
        ],
        'extrajudicial': [
            'leilão extrajudicial', 'leilão particular', 'leilão privado',
            'alienação fiduciária', 'consolidação da propriedade',
            'lei 9.514', 'decreto-lei 70/66', 'credor fiduciário',
            'agente fiduciário', 'sem intervenção judicial'
        ]
    }
    
    # Publication compliance keywords
    PUBLICATION_COMPLIANCE = {
        'official_gazette': [
            'diário oficial', 'diário da justiça', 'DJE', 'DOE',
            'publicação oficial', 'imprensa oficial'
        ],
        'newspaper': [
            'jornal de grande circulação', 'jornal local',
            'periódico', 'publicado em jornal', 'veículo de comunicação'
        ],
        'compliance': [
            'prazo legal', 'antecedência mínima', '5 dias',
            'cinco dias', 'tempestivamente', 'regularmente publicado'
        ]
    }
    
    # Notification compliance keywords
    NOTIFICATION_KEYWORDS = {
        'notification_verbs': [
            'intimado', 'intimada', 'notificado', 'notificada',
            'citado', 'citada', 'cientificado', 'cientificada'
        ],
        'notification_methods': [
            'pessoalmente', 'por mandado', 'por oficial de justiça',
            'por carta', 'AR', 'aviso de recebimento', 'edital',
            'publicação', 'presumida', 'ficta'
        ],
        'cpc_889_parties': {
            'I': ['executado', 'devedor', 'ex-proprietário'],
            'II': ['cônjuge', 'esposo', 'esposa', 'companheiro', 'companheira'],
            'III': ['coproprietário', 'condômino'],
            'IV': ['titular de direito real', 'usufrutuário', 'superficiário'],
            'V': ['credor hipotecário', 'credor com garantia real'],
            'VI': ['credor fiduciário', 'agente fiduciário'],
            'VII': ['promitente comprador', 'promissário comprador'],
            'VIII': ['União', 'Estado', 'Município', 'ente público']
        }
    }
    
    # Financial indicators
    FINANCIAL_KEYWORDS = {
        'debt_types': [
            'débito', 'dívida', 'inadimplência', 'pendência',
            'IPTU', 'imposto predial', 'contribuição', 'taxa',
            'condomínio', 'despesa condominial', 'cota condominial',
            'hipoteca', 'financiamento', 'empréstimo', 'mútuo'
        ],
        'payment_responsibility': [
            'sub-rogação', 'quitado com o produto', 'responsabilidade do arrematante',
            'livre de débitos', 'débitos inclusos', 'ônus do arrematante'
        ],
        'valuation': [
            'avaliação', 'valor de mercado', 'laudo de avaliação',
            'primeira praça', 'segunda praça', '1ª praça', '2ª praça',
            'lance mínimo', 'valor mínimo', '50%', 'cinquenta por cento',
            'vil preço', 'abaixo da avaliação'
        ]
    }
    
    # Risk indicators
    RISK_KEYWORDS = {
        'high_risk': [
            'indisponibilidade', 'bloqueio judicial', 'sequestro',
            'arresto', 'ocupação irregular', 'invasão', 'litígio',
            'ação possessória', 'reintegração de posse', 'imissão na posse',
            'recurso pendente', 'agravo', 'apelação', 'embargos'
        ],
        'low_risk': [
            'livre e desembaraçado', 'sem ônus', 'desocupado',
            'regular', 'em ordem', 'sem pendências', 'quitado',
            'sem restrições', 'disponível', 'transmissível'
        ]
    }