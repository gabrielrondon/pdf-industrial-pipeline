"""
Date parsing and deadline calculation utilities
"""

import re
from datetime import datetime, timedelta
from typing import List, Optional, Tuple, Dict, Any
import logging

from .patterns import JudicialPatterns

logger = logging.getLogger(__name__)


class DateParser:
    """Parse dates from Brazilian legal documents"""
    
    def __init__(self):
        self.patterns = JudicialPatterns()
    
    def parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse a date string in various Brazilian formats"""
        try:
            # Try standard format DD/MM/YYYY or DD-MM-YYYY
            match = self.patterns.DATE_PATTERNS['standard'].match(date_str.strip())
            if match:
                day, month, year = match.groups()
                year = int(year)
                if year < 100:  # Handle 2-digit years
                    year = 2000 + year if year < 50 else 1900 + year
                return datetime(year, int(month), int(day))
            
            # Try written format "15 de janeiro de 2024"
            match = self.patterns.DATE_PATTERNS['written'].match(date_str.strip())
            if match:
                day, month_name, year = match.groups()
                month = self.patterns.MONTH_NAMES.get(month_name.lower())
                if month:
                    return datetime(int(year), month, int(day))
            
            return None
            
        except (ValueError, AttributeError) as e:
            logger.debug(f"Failed to parse date '{date_str}': {e}")
            return None
    
    def extract_dates(self, text: str, pattern_type: Optional[str] = None) -> List[Tuple[str, datetime]]:
        """Extract all dates from text, optionally using specific pattern"""
        dates = []
        
        if pattern_type and pattern_type in self.patterns.DATE_PATTERNS:
            patterns = [self.patterns.DATE_PATTERNS[pattern_type]]
        else:
            patterns = self.patterns.DATE_PATTERNS.values()
        
        for pattern in patterns:
            for match in pattern.finditer(text):
                date_str = match.group(0)
                parsed_date = self.parse_date(date_str)
                if parsed_date:
                    dates.append((date_str, parsed_date))
        
        # Remove duplicates while preserving order
        seen = set()
        unique_dates = []
        for date_tuple in dates:
            if date_tuple[1] not in seen:
                seen.add(date_tuple[1])
                unique_dates.append(date_tuple)
        
        return sorted(unique_dates, key=lambda x: x[1])
    
    def extract_auction_dates(self, text: str) -> List[datetime]:
        """Extract dates specifically related to auction events"""
        auction_dates = []
        
        # Look for dates near auction keywords
        pattern = re.compile(
            r'(?:leilão|hasta|praça|arrematação|pregão).*?'
            r'(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})',
            re.IGNORECASE | re.DOTALL
        )
        
        for match in pattern.finditer(text):
            date_str = match.group(1)
            parsed_date = self.parse_date(date_str)
            if parsed_date:
                auction_dates.append(parsed_date)
        
        return sorted(list(set(auction_dates)))
    
    def extract_publication_dates(self, text: str) -> List[datetime]:
        """Extract dates related to publication events"""
        pub_dates = []
        
        # Look for dates near publication keywords
        pattern = re.compile(
            r'(?:publicad[oa]|publicação|edital|diário\s+oficial|imprensa).*?'
            r'(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})',
            re.IGNORECASE | re.DOTALL
        )
        
        for match in pattern.finditer(text):
            date_str = match.group(1)
            parsed_date = self.parse_date(date_str)
            if parsed_date:
                pub_dates.append(parsed_date)
        
        return sorted(list(set(pub_dates)))


class DeadlineCalculator:
    """Calculate legal deadlines for judicial auctions"""
    
    # Legal requirements (in business days)
    PUBLICATION_TO_AUCTION_MIN_DAYS = 5  # CPC requirement
    NOTIFICATION_TO_AUCTION_MIN_DAYS = 10  # Typical requirement
    
    @staticmethod
    def calculate_business_days(start_date: datetime, end_date: datetime) -> int:
        """Calculate business days between two dates (excluding weekends)"""
        if start_date > end_date:
            start_date, end_date = end_date, start_date
        
        days = 0
        current = start_date
        
        while current <= end_date:
            if current.weekday() < 5:  # Monday = 0, Friday = 4
                days += 1
            current += timedelta(days=1)
        
        return days - 1  # Don't count the start date
    
    @staticmethod
    def check_publication_deadline(
        publication_date: datetime, 
        auction_date: datetime
    ) -> Tuple[bool, int]:
        """
        Check if publication meets legal deadline requirements
        Returns: (meets_requirement, days_between)
        """
        business_days = DeadlineCalculator.calculate_business_days(
            publication_date, auction_date
        )
        
        meets_requirement = business_days >= DeadlineCalculator.PUBLICATION_TO_AUCTION_MIN_DAYS
        
        return meets_requirement, business_days
    
    @staticmethod
    def find_earliest_compliant_dates(
        publication_dates: List[datetime],
        auction_dates: List[datetime]
    ) -> Optional[Tuple[datetime, datetime, int]]:
        """
        Find the earliest publication date that meets deadline for any auction date
        Returns: (publication_date, auction_date, days_between) or None
        """
        compliant_pairs = []
        
        for pub_date in publication_dates:
            for auction_date in auction_dates:
                if pub_date < auction_date:
                    meets, days = DeadlineCalculator.check_publication_deadline(
                        pub_date, auction_date
                    )
                    if meets:
                        compliant_pairs.append((pub_date, auction_date, days))
        
        if compliant_pairs:
            # Return the pair with earliest publication date
            return min(compliant_pairs, key=lambda x: x[0])
        
        return None
    
    @staticmethod
    def analyze_deadline_compliance(
        publication_dates: List[datetime],
        auction_dates: List[datetime]
    ) -> Dict[str, Any]:
        """Comprehensive deadline compliance analysis"""
        result = {
            'has_compliant_timeline': False,
            'earliest_compliant_pair': None,
            'all_combinations': [],
            'min_days_found': None,
            'max_days_found': None
        }
        
        if not publication_dates or not auction_dates:
            return result
        
        all_combos = []
        
        for pub_date in publication_dates:
            for auction_date in auction_dates:
                if pub_date < auction_date:
                    meets, days = DeadlineCalculator.check_publication_deadline(
                        pub_date, auction_date
                    )
                    all_combos.append({
                        'publication_date': pub_date,
                        'auction_date': auction_date,
                        'business_days': days,
                        'meets_requirement': meets
                    })
        
        result['all_combinations'] = all_combos
        
        if all_combos:
            days_list = [c['business_days'] for c in all_combos]
            result['min_days_found'] = min(days_list)
            result['max_days_found'] = max(days_list)
            
            compliant = [c for c in all_combos if c['meets_requirement']]
            if compliant:
                result['has_compliant_timeline'] = True
                earliest = min(compliant, key=lambda x: x['publication_date'])
                result['earliest_compliant_pair'] = earliest
        
        return result