"""
Company model
"""
from sqlalchemy import Boolean, Column, String, Integer, Numeric, DateTime
from sqlalchemy.sql import func

from app.db.base import Base


class Company(Base):
    """Company model for equity research"""
    __tablename__ = "companies"

    ticker = Column(String(10), primary_key=True)
    name = Column(String(255), nullable=False, index=True)
    sector = Column(String(100), index=True)
    industry = Column(String(100), index=True)
    market_cap = Column(Numeric(20, 2))
    employees = Column(Integer)
    founded_year = Column(Integer)
    headquarters = Column(String(255))
    website = Column(String(255))
    description = Column(String)
    sic_code = Column(String(10))
    cik = Column(String(10), unique=True, index=True)
    exchange = Column(String(20))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Company {self.ticker}: {self.name}>"
