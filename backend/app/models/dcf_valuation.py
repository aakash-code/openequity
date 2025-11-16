"""
DCF Valuation Model
Stores DCF models with assumptions, projections, and results
"""
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import uuid


class DCFValuation(Base):
    """DCF Valuation model for storing DCF analyses"""

    __tablename__ = "dcf_valuations"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    ticker = Column(String, ForeignKey("companies.ticker"), nullable=False, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)

    # Model metadata
    name = Column(String, nullable=False)  # e.g., "AAPL Base Case Q4 2024"
    description = Column(String)
    is_public = Column(Boolean, default=False)  # Allow sharing models

    # WACC assumptions
    risk_free_rate = Column(Float, nullable=False)  # e.g., 0.045 for 4.5%
    equity_risk_premium = Column(Float, nullable=False)  # e.g., 0.06 for 6%
    beta = Column(Float, nullable=False)
    cost_of_debt = Column(Float, nullable=False)
    tax_rate = Column(Float, nullable=False)
    debt_weight = Column(Float, nullable=False)  # e.g., 0.20 for 20%
    equity_weight = Column(Float, nullable=False)  # e.g., 0.80 for 80%
    wacc = Column(Float, nullable=False)  # Calculated WACC

    # Projection assumptions (5-year model typical)
    projection_years = Column(Integer, default=5)
    revenue_growth_rates = Column(JSON)  # Array of growth rates per year
    ebitda_margin = Column(Float)  # Target EBITDA margin
    depreciation_pct_revenue = Column(Float)  # D&A as % of revenue
    capex_pct_revenue = Column(Float)  # CapEx as % of revenue
    nwc_pct_revenue = Column(Float)  # Net Working Capital as % of revenue

    # Terminal value assumptions
    terminal_growth_rate = Column(Float)  # Gordon growth rate
    terminal_ebitda_multiple = Column(Float, nullable=True)  # Alternative: exit multiple

    # Results
    enterprise_value = Column(Float)
    equity_value = Column(Float)
    shares_outstanding = Column(Float)
    value_per_share = Column(Float)
    current_price = Column(Float)
    upside_downside = Column(Float)  # % upside/downside

    # Detailed projections and calculations (stored as JSON)
    projections = Column(JSON)  # Yearly projections
    fcf_projections = Column(JSON)  # Free cash flow per year
    terminal_value = Column(Float)
    pv_terminal_value = Column(Float)  # Present value of terminal value
    pv_fcf = Column(Float)  # Sum of PV of projected FCFs

    # Sensitivity analysis results
    sensitivity_analysis = Column(JSON, nullable=True)  # Grid of values

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    company = relationship("Company", back_populates="dcf_valuations")
    user = relationship("User", back_populates="dcf_valuations")

    def __repr__(self):
        return f"<DCFValuation(id={self.id}, ticker={self.ticker}, name={self.name})>"
