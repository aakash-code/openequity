"""
Peer Group Model
Stores peer groups for comparable company analysis
"""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, JSON, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import uuid


class PeerGroup(Base):
    """Peer Group model for storing comparable company lists"""

    __tablename__ = "peer_groups"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    ticker = Column(String, ForeignKey("companies.ticker"), nullable=False, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)

    # Group metadata
    name = Column(String, nullable=False)  # e.g., "AAPL Tech Peers"
    description = Column(Text)
    is_public = Column(Boolean, default=False)  # Allow sharing peer groups

    # Peer tickers (array of ticker symbols)
    peer_tickers = Column(JSON, nullable=False)  # ["MSFT", "GOOGL", "META", ...]

    # Comparable company analysis results (cached)
    analysis_results = Column(JSON, nullable=True)  # Trading multiples, medians, etc.
    last_analyzed = Column(DateTime(timezone=True), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    company = relationship("Company", back_populates="peer_groups")
    user = relationship("User", back_populates="peer_groups")

    def __repr__(self):
        return f"<PeerGroup(id={self.id}, ticker={self.ticker}, name={self.name})>"


class ComparableAnalysis(Base):
    """Stores calculated comparable company analysis results"""

    __tablename__ = "comparable_analyses"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    peer_group_id = Column(String, ForeignKey("peer_groups.id"), nullable=False, index=True)
    ticker = Column(String, ForeignKey("companies.ticker"), nullable=False, index=True)

    # Trading multiples for each company
    company_data = Column(JSON, nullable=False)  # Name, market cap, etc.

    # Valuation multiples
    pe_ratio = Column(Float, nullable=True)
    forward_pe = Column(Float, nullable=True)
    peg_ratio = Column(Float, nullable=True)
    price_to_book = Column(Float, nullable=True)
    price_to_sales = Column(Float, nullable=True)
    ev_to_revenue = Column(Float, nullable=True)
    ev_to_ebitda = Column(Float, nullable=True)
    ev_to_ebit = Column(Float, nullable=True)
    ev_to_fcf = Column(Float, nullable=True)

    # Profitability metrics
    gross_margin = Column(Float, nullable=True)
    operating_margin = Column(Float, nullable=True)
    net_margin = Column(Float, nullable=True)
    roe = Column(Float, nullable=True)
    roa = Column(Float, nullable=True)
    roic = Column(Float, nullable=True)

    # Growth metrics
    revenue_growth = Column(Float, nullable=True)
    earnings_growth = Column(Float, nullable=True)

    # Other metrics
    market_cap = Column(Float, nullable=True)
    enterprise_value = Column(Float, nullable=True)

    # Timestamps
    calculated_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    peer_group = relationship("PeerGroup")

    def __repr__(self):
        return f"<ComparableAnalysis(ticker={self.ticker}, peer_group_id={self.peer_group_id})>"
