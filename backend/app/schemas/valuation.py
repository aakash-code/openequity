"""
Pydantic schemas for valuation endpoints
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime


# DCF Valuation Schemas


class DCFAssumptions(BaseModel):
    """DCF model assumptions"""

    # WACC components
    risk_free_rate: float = Field(..., ge=0, le=1, description="Risk-free rate (decimal)")
    equity_risk_premium: float = Field(..., ge=0, le=1, description="Equity risk premium (decimal)")
    beta: float = Field(..., description="Stock beta")
    cost_of_debt: float = Field(..., ge=0, le=1, description="Cost of debt (decimal)")
    tax_rate: float = Field(..., ge=0, le=1, description="Tax rate (decimal)")
    debt_weight: float = Field(..., ge=0, le=1, description="Debt weight (decimal)")
    equity_weight: float = Field(..., ge=0, le=1, description="Equity weight (decimal)")

    # Projection assumptions
    projection_years: int = Field(5, ge=1, le=10, description="Number of projection years")
    revenue_growth_rates: List[float] = Field(..., description="Annual revenue growth rates")
    ebitda_margin: float = Field(..., ge=-1, le=1, description="Target EBITDA margin (decimal)")
    depreciation_pct_revenue: float = Field(..., ge=0, le=1, description="D&A as % of revenue")
    capex_pct_revenue: float = Field(..., ge=0, le=1, description="CapEx as % of revenue")
    nwc_pct_revenue: float = Field(..., ge=-1, le=1, description="NWC change as % of revenue")

    # Terminal value
    terminal_growth_rate: Optional[float] = Field(None, ge=0, le=0.1, description="Terminal growth rate")
    terminal_ebitda_multiple: Optional[float] = Field(None, ge=0, description="Terminal EBITDA multiple")


class CreateDCFRequest(BaseModel):
    """Request to create a new DCF valuation"""

    ticker: str
    name: str
    description: Optional[str] = None
    is_public: bool = False

    # Base data
    base_revenue: float = Field(..., gt=0)
    net_debt: float = Field(0, description="Net debt (Total Debt - Cash)")
    shares_outstanding: float = Field(..., gt=0)
    current_price: Optional[float] = Field(None, gt=0)

    # Assumptions
    assumptions: DCFAssumptions


class UpdateDCFRequest(BaseModel):
    """Request to update a DCF valuation"""

    name: Optional[str] = None
    description: Optional[str] = None
    is_public: Optional[bool] = None
    base_revenue: Optional[float] = Field(None, gt=0)
    net_debt: Optional[float] = None
    shares_outstanding: Optional[float] = Field(None, gt=0)
    current_price: Optional[float] = Field(None, gt=0)
    assumptions: Optional[DCFAssumptions] = None


class DCFValuationResponse(BaseModel):
    """DCF valuation response"""

    id: str
    ticker: str
    user_id: str
    name: str
    description: Optional[str]
    is_public: bool

    # WACC
    risk_free_rate: float
    equity_risk_premium: float
    beta: float
    cost_of_debt: float
    tax_rate: float
    debt_weight: float
    equity_weight: float
    wacc: float

    # Projection assumptions
    projection_years: int
    revenue_growth_rates: List[float]
    ebitda_margin: float
    depreciation_pct_revenue: float
    capex_pct_revenue: float
    nwc_pct_revenue: float

    # Terminal value
    terminal_growth_rate: Optional[float]
    terminal_ebitda_multiple: Optional[float]

    # Results
    enterprise_value: float
    equity_value: float
    shares_outstanding: float
    value_per_share: float
    current_price: Optional[float]
    upside_downside: Optional[float]

    # Detailed results
    projections: Dict
    fcf_projections: List[float]
    terminal_value: float
    pv_terminal_value: float
    pv_fcf: float

    # Sensitivity analysis
    sensitivity_analysis: Optional[Dict]

    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class DCFListResponse(BaseModel):
    """List of DCF valuations"""

    valuations: List[DCFValuationResponse]
    total: int


class SensitivityAnalysisRequest(BaseModel):
    """Request for sensitivity analysis"""

    wacc_range: Optional[List[float]] = None
    terminal_growth_range: Optional[List[float]] = None


# Peer Group / Comps Schemas


class CreatePeerGroupRequest(BaseModel):
    """Request to create a peer group"""

    ticker: str
    name: str
    description: Optional[str] = None
    peer_tickers: List[str] = Field(..., min_length=1, description="List of peer ticker symbols")
    is_public: bool = False


class UpdatePeerGroupRequest(BaseModel):
    """Request to update a peer group"""

    name: Optional[str] = None
    description: Optional[str] = None
    peer_tickers: Optional[List[str]] = Field(None, min_length=1)
    is_public: Optional[bool] = None


class PeerGroupResponse(BaseModel):
    """Peer group response"""

    id: str
    ticker: str
    user_id: str
    name: str
    description: Optional[str]
    peer_tickers: List[str]
    is_public: bool
    analysis_results: Optional[Dict]
    last_analyzed: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class PeerGroupListResponse(BaseModel):
    """List of peer groups"""

    peer_groups: List[PeerGroupResponse]
    total: int


class CompanyMetrics(BaseModel):
    """Company metrics for comps analysis"""

    ticker: str
    company_name: str
    market_cap: float
    enterprise_value: float
    current_price: float
    currency: str

    # Valuation multiples
    pe_ratio: Optional[float]
    forward_pe: Optional[float]
    peg_ratio: Optional[float]
    price_to_book: Optional[float]
    price_to_sales: Optional[float]
    ev_to_revenue: Optional[float]
    ev_to_ebitda: Optional[float]
    ev_to_ebit: Optional[float]

    # Profitability
    gross_margin: Optional[float]
    operating_margin: Optional[float]
    net_margin: Optional[float]
    roe: Optional[float]
    roa: Optional[float]

    # Growth
    revenue_growth: Optional[float]
    earnings_growth: Optional[float]


class MultipleStatistics(BaseModel):
    """Statistics for a trading multiple across peer group"""

    median: Optional[float]
    mean: Optional[float]
    min: Optional[float]
    max: Optional[float]
    count: int


class ComparableAnalysisResponse(BaseModel):
    """Comparable company analysis response"""

    target: CompanyMetrics
    peers: List[CompanyMetrics]
    peer_statistics: Dict[str, MultipleStatistics]
    implied_valuations: Dict


class WACCCalculationRequest(BaseModel):
    """Request to calculate WACC"""

    risk_free_rate: float = Field(..., ge=0, le=1)
    beta: float
    equity_risk_premium: float = Field(..., ge=0, le=1)
    cost_of_debt: float = Field(..., ge=0, le=1)
    tax_rate: float = Field(..., ge=0, le=1)
    equity_weight: float = Field(..., ge=0, le=1)
    debt_weight: float = Field(..., ge=0, le=1)


class WACCCalculationResponse(BaseModel):
    """WACC calculation response"""

    cost_of_equity: float
    wacc: float
