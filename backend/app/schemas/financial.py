"""
Financial statement and ratios Pydantic schemas
"""
from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import date
from app.models.financial_statement import StatementType, PeriodType


class FinancialStatementResponse(BaseModel):
    """Financial statement response schema"""
    id: str
    ticker: str
    statement_type: StatementType
    period_type: PeriodType
    period_end: date
    fiscal_year: int
    data: Dict[str, Any]
    source: Optional[str] = None

    class Config:
        from_attributes = True


class FinancialRatiosResponse(BaseModel):
    """Financial ratios response schema"""
    ticker: str
    period_end: str
    ratios: Dict[str, Any]


class RefreshFinancialsRequest(BaseModel):
    """Request to refresh financial data"""
    market: Optional[str] = "US"
