"""
Data models for judicial auction analysis
"""

from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class AuctionType(str, Enum):
    JUDICIAL = "judicial"
    EXTRAJUDICIAL = "extrajudicial"
    UNKNOWN = "unknown"


class ComplianceStatus(str, Enum):
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    CANNOT_DETERMINE = "cannot_determine"


class PropertyOccupancyStatus(str, Enum):
    VACANT = "vacant"
    OCCUPIED_TENANT = "occupied_tenant"
    OCCUPIED_OWNER = "occupied_owner"
    OCCUPIED_SQUATTER = "occupied_squatter"
    DISPUTED = "disputed"
    UNKNOWN = "unknown"


class NotificationStatus(BaseModel):
    """Status of legal notifications"""
    party_type: str
    party_identifier: Optional[str] = None
    notification_mentioned: bool = False
    notification_date: Optional[datetime] = None
    compliance_status: ComplianceStatus = ComplianceStatus.CANNOT_DETERMINE
    details: Optional[str] = None


class PublicationCompliance(BaseModel):
    """Analysis of publication compliance"""
    diario_oficial_mentioned: bool = False
    newspaper_mentioned: bool = False
    publication_dates: List[datetime] = Field(default_factory=list)
    auction_dates: List[datetime] = Field(default_factory=list)
    days_between_publication_auction: Optional[int] = None
    meets_deadline_requirement: Optional[bool] = None
    compliance_status: ComplianceStatus = ComplianceStatus.CANNOT_DETERMINE
    details: str = ""


class ValuationAnalysis(BaseModel):
    """Analysis of property valuation and auction values"""
    market_value: Optional[float] = None
    first_auction_value: Optional[float] = None
    second_auction_value: Optional[float] = None
    minimum_bid_value: Optional[float] = None
    
    first_auction_percentage: Optional[float] = None
    second_auction_percentage: Optional[float] = None
    
    below_50_percent: Optional[bool] = None
    risk_of_annulment: bool = False
    
    values_found: Dict[str, float] = Field(default_factory=dict)
    analysis_notes: str = ""


class DebtAnalysis(BaseModel):
    """Analysis of existing debts and encumbrances"""
    iptu_debt: Optional[float] = None
    condominium_debt: Optional[float] = None
    mortgage_debt: Optional[float] = None
    other_debts: Dict[str, float] = Field(default_factory=dict)
    
    total_debt: Optional[float] = None
    debt_responsibility: Optional[str] = None  # "arrematante" or "quitado_com_lance"
    
    debts_mentioned: List[str] = Field(default_factory=list)
    analysis_notes: str = ""


class PropertyStatus(BaseModel):
    """Property occupation and status analysis"""
    occupancy_status: PropertyOccupancyStatus = PropertyOccupancyStatus.UNKNOWN
    occupancy_details: str = ""
    
    has_tenants: bool = False
    has_squatters: bool = False
    has_disputes: bool = False
    
    possession_transfer_risk: str = "unknown"  # low, medium, high, unknown
    risk_factors: List[str] = Field(default_factory=list)


class LegalRestrictions(BaseModel):
    """Analysis of legal restrictions"""
    has_judicial_unavailability: bool = False
    has_liens: bool = False
    has_mortgages: bool = False
    has_seizures: bool = False
    
    restrictions_found: List[str] = Field(default_factory=list)
    transfer_viability: str = "unknown"  # viable, risky, blocked, unknown
    restriction_details: str = ""


class JudicialAnalysisResult(BaseModel):
    """Complete judicial auction analysis result"""
    # 1.1 - Auction Nature
    auction_type: AuctionType = AuctionType.UNKNOWN
    auction_type_confidence: float = 0.0
    auction_type_indicators: List[str] = Field(default_factory=list)
    
    # 1.2 - Publication Compliance
    publication_compliance: PublicationCompliance = Field(default_factory=PublicationCompliance)
    
    # 1.3 & 1.4 - Notifications (CPC Art. 889)
    executado_notification: Optional[NotificationStatus] = None
    other_notifications: List[NotificationStatus] = Field(default_factory=list)
    cpc_889_compliance: ComplianceStatus = ComplianceStatus.CANNOT_DETERMINE
    notification_analysis: str = ""
    
    # 1.5 - Valuation Analysis
    valuation: ValuationAnalysis = Field(default_factory=ValuationAnalysis)
    
    # 1.6 - Debt Analysis
    debts: DebtAnalysis = Field(default_factory=DebtAnalysis)
    
    # 1.7 - Property Status
    property_status: PropertyStatus = Field(default_factory=PropertyStatus)
    
    # 1.8 - Legal Restrictions
    legal_restrictions: LegalRestrictions = Field(default_factory=LegalRestrictions)
    
    # Overall Assessment
    overall_risk_score: float = 0.0  # 0-100, where 100 is highest risk
    investment_viability_score: float = 0.0  # 0-100, where 100 is best opportunity
    compliance_issues: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    
    # Metadata
    analysis_timestamp: datetime = Field(default_factory=datetime.now)
    analyzer_version: str = "1.0.0"
    confidence_level: float = 0.0  # Overall confidence in analysis
    
    # Raw extracted data for reference
    raw_entities: Dict[str, Any] = Field(default_factory=dict)
    raw_keywords: Dict[str, List[str]] = Field(default_factory=dict)