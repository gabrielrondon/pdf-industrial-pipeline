"""
Property status and occupation analysis
"""

import re
from typing import Dict, List, Set
import logging

from .patterns import JudicialPatterns, JudicialKeywords
from .models import PropertyOccupancyStatus

logger = logging.getLogger(__name__)


class PropertyAnalyzer:
    """Analyze property status and occupation"""
    
    def __init__(self):
        self.patterns = JudicialPatterns()
        self.keywords = JudicialKeywords()
    
    def analyze_occupancy(self, text: str) -> Dict[str, any]:
        """Analyze property occupancy status"""
        result = {
            'occupancy_status': PropertyOccupancyStatus.UNKNOWN,
            'occupancy_details': '',
            'has_tenants': False,
            'has_squatters': False,
            'has_disputes': False,
            'vacant_indicators': [],
            'occupied_indicators': [],
            'risk_factors': [],
            'possession_transfer_risk': 'unknown'
        }
        
        text_lower = text.lower()
        
        # Check for vacant indicators
        for match in self.patterns.PROPERTY_PATTERNS['vacant'].finditer(text):
            result['vacant_indicators'].append(match.group(0))
        
        # Check for occupied indicators
        for match in self.patterns.PROPERTY_PATTERNS['occupied'].finditer(text):
            result['occupied_indicators'].append(match.group(0))
            result['has_tenants'] = True
        
        # Check for squatters
        for match in self.patterns.PROPERTY_PATTERNS['squatter'].finditer(text):
            result['occupied_indicators'].append(match.group(0))
            result['has_squatters'] = True
            result['risk_factors'].append('Possível ocupação irregular')
        
        # Check for disputes
        for match in self.patterns.PROPERTY_PATTERNS['dispute'].finditer(text):
            result['has_disputes'] = True
            result['risk_factors'].append('Disputa sobre a posse')
        
        # Determine occupancy status
        if result['vacant_indicators'] and not result['occupied_indicators']:
            result['occupancy_status'] = PropertyOccupancyStatus.VACANT
            result['possession_transfer_risk'] = 'low'
            result['occupancy_details'] = 'Imóvel desocupado e livre para transferência'
        
        elif result['has_squatters']:
            result['occupancy_status'] = PropertyOccupancyStatus.OCCUPIED_SQUATTER
            result['possession_transfer_risk'] = 'high'
            result['occupancy_details'] = 'Imóvel com possível ocupação irregular'
        
        elif result['has_tenants']:
            # Check if it's tenant or owner
            if 'inquilino' in text_lower or 'locatário' in text_lower:
                result['occupancy_status'] = PropertyOccupancyStatus.OCCUPIED_TENANT
                result['possession_transfer_risk'] = 'medium'
                result['occupancy_details'] = 'Imóvel ocupado por inquilino/locatário'
            else:
                result['occupancy_status'] = PropertyOccupancyStatus.OCCUPIED_OWNER
                result['possession_transfer_risk'] = 'high'
                result['occupancy_details'] = 'Imóvel possivelmente ocupado pelo executado'
        
        elif result['has_disputes']:
            result['occupancy_status'] = PropertyOccupancyStatus.DISPUTED
            result['possession_transfer_risk'] = 'high'
            result['occupancy_details'] = 'Imóvel com disputa judicial sobre a posse'
        
        # Check for possession transfer mentions
        self._analyze_possession_transfer(text, result)
        
        return result
    
    def _analyze_possession_transfer(self, text: str, result: Dict[str, any]) -> None:
        """Analyze mentions of possession transfer issues"""
        possession_patterns = [
            (r'imiss[ãa]o\s+(?:na\s+)?posse', 'Imissão na posse mencionada'),
            (r'reintegra[çc][ãa]o\s+de\s+posse', 'Possível ação de reintegração de posse'),
            (r'a[çc][ãa]o\s+possess[óo]ria', 'Ação possessória em andamento'),
            (r'desocupa[çc][ãa]o\s+(?:for[çc]ada|compuls[óo]ria)', 'Pode requerer desocupação forçada'),
            (r'resist[êe]ncia\s+[àa]\s+desocupa[çc][ãa]o', 'Resistência à desocupação prevista'),
            (r'prazo\s+para\s+desocupa[çc][ãa]o', 'Prazo para desocupação estabelecido')
        ]
        
        for pattern, risk_description in possession_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                result['risk_factors'].append(risk_description)
                
                # Increase risk level if not already high
                if result['possession_transfer_risk'] == 'low':
                    result['possession_transfer_risk'] = 'medium'
                elif result['possession_transfer_risk'] == 'unknown':
                    result['possession_transfer_risk'] = 'medium'
    
    def analyze_legal_restrictions(self, text: str) -> Dict[str, any]:
        """Analyze legal restrictions on the property"""
        result = {
            'has_judicial_unavailability': False,
            'has_liens': False,
            'has_mortgages': False,
            'has_seizures': False,
            'restrictions_found': [],
            'restriction_details': '',
            'transfer_viability': 'unknown',
            'severity_score': 0  # 0-100, higher means more severe
        }
        
        # Check for judicial unavailability
        if self.patterns.RESTRICTION_PATTERNS['unavailability'].search(text):
            result['has_judicial_unavailability'] = True
            result['restrictions_found'].append('Indisponibilidade judicial')
            result['severity_score'] += 40
        
        # Check for liens
        lien_matches = self.patterns.RESTRICTION_PATTERNS['lien'].findall(text)
        if lien_matches:
            result['has_liens'] = True
            result['restrictions_found'].extend(list(set(lien_matches)))
            result['severity_score'] += 10 * len(set(lien_matches))
        
        # Check for mortgages
        if re.search(r'hipoteca', text, re.IGNORECASE):
            result['has_mortgages'] = True
            result['restrictions_found'].append('Hipoteca')
            result['severity_score'] += 20
        
        # Check for seizures
        if re.search(r'(?:arresto|sequestro)', text, re.IGNORECASE):
            result['has_seizures'] = True
            result['restrictions_found'].append('Arresto/Sequestro')
            result['severity_score'] += 30
        
        # Check for general encumbrances
        encumbrance_matches = self.patterns.RESTRICTION_PATTERNS['encumbrance'].findall(text)
        if encumbrance_matches:
            result['restrictions_found'].extend(list(set(encumbrance_matches)))
            result['severity_score'] += 5 * len(set(encumbrance_matches))
        
        # Cap severity score at 100
        result['severity_score'] = min(result['severity_score'], 100)
        
        # Determine transfer viability
        if result['has_judicial_unavailability']:
            result['transfer_viability'] = 'blocked'
            result['restriction_details'] = 'Transferência bloqueada por indisponibilidade judicial'
        elif result['severity_score'] >= 50:
            result['transfer_viability'] = 'risky'
            result['restriction_details'] = 'Múltiplas restrições podem dificultar transferência'
        elif result['severity_score'] >= 20:
            result['transfer_viability'] = 'viable_with_conditions'
            result['restriction_details'] = 'Transferência possível mas com restrições a resolver'
        elif result['severity_score'] > 0:
            result['transfer_viability'] = 'viable'
            result['restriction_details'] = 'Restrições menores não impedem transferência'
        else:
            result['transfer_viability'] = 'clear'
            result['restriction_details'] = 'Sem restrições identificadas'
        
        # Check for positive indicators
        self._check_positive_indicators(text, result)
        
        return result
    
    def _check_positive_indicators(self, text: str, result: Dict[str, any]) -> None:
        """Check for positive indicators that property is clear"""
        positive_patterns = [
            (r'livre\s+(?:e\s+)?desembara[çc]ad[oa]', 'Livre e desembaraçado'),
            (r'sem\s+[ôo]nus', 'Sem ônus'),
            (r'sem\s+restri[çc][õo]es', 'Sem restrições'),
            (r'qu[íi]ta[çc][ãa]o\s+(?:de\s+)?hipoteca', 'Hipoteca quitada'),
            (r'baixa\s+(?:de\s+)?penhora', 'Baixa de penhora'),
            (r'cancelamento\s+(?:de\s+)?restri[çc][ãa]o', 'Cancelamento de restrição')
        ]
        
        positive_found = []
        for pattern, description in positive_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                positive_found.append(description)
        
        if positive_found:
            # Reduce severity score for positive indicators
            result['severity_score'] = max(0, result['severity_score'] - 10 * len(positive_found))
            
            # Update details if property seems clear
            if result['severity_score'] == 0:
                result['transfer_viability'] = 'clear'
                result['restriction_details'] = f"Imóvel {', '.join(positive_found).lower()}"
    
    def extract_property_details(self, text: str) -> Dict[str, any]:
        """Extract additional property details"""
        details = {
            'property_type': None,
            'area_m2': None,
            'registration_number': None,
            'location_mentions': [],
            'description_keywords': []
        }
        
        # Extract property type
        property_types = [
            ('apartamento', 'apartamento'),
            ('casa', 'casa'),
            ('terreno', 'terreno'),
            ('lote', 'lote'),
            ('sala comercial', 'sala_comercial'),
            ('loja', 'loja'),
            ('galp[ãa]o', 'galpao'),
            ('im[óo]vel rural', 'rural'),
            ('im[óo]vel urbano', 'urbano')
        ]
        
        for pattern, prop_type in property_types:
            if re.search(pattern, text, re.IGNORECASE):
                details['property_type'] = prop_type
                break
        
        # Extract area
        area_pattern = re.compile(r'(\d+(?:[.,]\d+)?)\s*m[²2]')
        area_match = area_pattern.search(text)
        if area_match:
            area_str = area_match.group(1).replace(',', '.')
            try:
                details['area_m2'] = float(area_str)
            except ValueError:
                pass
        
        # Extract registration number
        registration_patterns = [
            r'matr[íi]cula\s*(?:n[º°]?\s*)?(\d+)',
            r'registro\s*(?:n[º°]?\s*)?(\d+)',
            r'transcrição\s*(?:n[º°]?\s*)?(\d+)'
        ]
        
        for pattern in registration_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                details['registration_number'] = match.group(1)
                break
        
        # Extract location mentions
        location_patterns = [
            r'(?:rua|avenida|alameda|travessa|praça)\s+[A-Z][\w\s]+',
            r'bairro\s+[A-Z][\w\s]+',
            r'munic[íi]pio\s+(?:de\s+)?[A-Z][\w\s]+',
            r'comarca\s+(?:de\s+)?[A-Z][\w\s]+'
        ]
        
        for pattern in location_patterns:
            matches = re.findall(pattern, text)
            details['location_mentions'].extend(matches)
        
        return details