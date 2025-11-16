"""
Portfolio and Transaction Models
Stores user portfolios and trading transactions
"""
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, JSON, Boolean, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import uuid
import enum


class TransactionType(str, enum.Enum):
    """Transaction types"""
    BUY = "buy"
    SELL = "sell"
    DIVIDEND = "dividend"
    SPLIT = "split"


class Portfolio(Base):
    """Portfolio model for tracking investment portfolios"""

    __tablename__ = "portfolios"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)

    # Portfolio metadata
    name = Column(String, nullable=False)  # e.g., "Growth Portfolio", "Retirement Account"
    description = Column(String)
    currency = Column(String, default="USD")  # USD, INR
    is_public = Column(Boolean, default=False)  # Allow sharing portfolios

    # Portfolio strategy/tags
    strategy = Column(String)  # e.g., "Value", "Growth", "Dividend", "Index"
    tags = Column(JSON)  # Array of custom tags

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    transactions = relationship("Transaction", back_populates="portfolio", cascade="all, delete-orphan")
    user = relationship("app.models.user.User", foreign_keys=[user_id])


class Transaction(Base):
    """Transaction model for portfolio trades and activities"""

    __tablename__ = "transactions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    portfolio_id = Column(String, ForeignKey("portfolios.id"), nullable=False, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    ticker = Column(String, ForeignKey("companies.ticker"), nullable=False, index=True)

    # Transaction details
    transaction_type = Column(Enum(TransactionType), nullable=False)  # buy, sell, dividend, split
    transaction_date = Column(DateTime(timezone=True), nullable=False)

    # Trade details (for buy/sell)
    quantity = Column(Float, nullable=False)  # Number of shares
    price = Column(Float, nullable=False)  # Price per share
    commission = Column(Float, default=0.0)  # Trading commission/fees
    total_amount = Column(Float, nullable=False)  # Total transaction value (quantity * price + fees)

    # Additional details
    notes = Column(String)  # User notes about the transaction
    currency = Column(String, default="USD")

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    portfolio = relationship("Portfolio", back_populates="transactions")
    user = relationship("app.models.user.User", foreign_keys=[user_id])
    company = relationship("app.models.company.Company", foreign_keys=[ticker])
