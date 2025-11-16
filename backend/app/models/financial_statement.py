"""
Financial Statement model
"""
from sqlalchemy import Column, String, Date, Integer, DateTime, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
import uuid
import enum

from app.db.base import Base


class StatementType(str, enum.Enum):
    """Financial statement type"""
    INCOME = "income"
    BALANCE = "balance"
    CASHFLOW = "cashflow"


class PeriodType(str, enum.Enum):
    """Reporting period type"""
    ANNUAL = "annual"
    QUARTERLY = "quarterly"


class FinancialStatement(Base):
    """Financial statement model"""
    __tablename__ = "financial_statements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ticker = Column(String(10), ForeignKey("companies.ticker", ondelete="CASCADE"), nullable=False, index=True)
    statement_type = Column(Enum(StatementType), nullable=False, index=True)
    period_type = Column(Enum(PeriodType), nullable=False)
    period_end = Column(Date, nullable=False, index=True)
    fiscal_year = Column(Integer, nullable=False)
    fiscal_period = Column(String(10))
    data = Column(JSONB, nullable=False)
    source = Column(String(50))
    filing_url = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<FinancialStatement {self.ticker} {self.statement_type} {self.period_end}>"
