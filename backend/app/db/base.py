"""
Base class for SQLAlchemy models
"""
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Import all models here so Alembic can detect them
from app.models.user import User
from app.models.company import Company
from app.models.financial_statement import FinancialStatement
from app.models.watchlist import Watchlist, WatchlistItem
