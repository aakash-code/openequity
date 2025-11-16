"""
Portfolio Management Endpoints
Provides portfolio CRUD operations, transactions, and analytics
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.core.deps import get_current_user, get_db
from app.models.user import User
from app.models.portfolio import Portfolio, Transaction, TransactionType
from app.models.company import Company
from app.services.portfolio_analytics import PortfolioAnalytics

router = APIRouter()


# Pydantic models for request/response
class PortfolioCreate(BaseModel):
    name: str
    description: Optional[str] = None
    currency: str = "USD"
    strategy: Optional[str] = None
    tags: Optional[List[str]] = None
    is_public: bool = False


class PortfolioUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    strategy: Optional[str] = None
    tags: Optional[List[str]] = None
    is_public: Optional[bool] = None


class TransactionCreate(BaseModel):
    ticker: str
    transaction_type: TransactionType
    transaction_date: datetime
    quantity: float
    price: float
    commission: float = 0.0
    notes: Optional[str] = None


class TransactionUpdate(BaseModel):
    transaction_date: Optional[datetime] = None
    quantity: Optional[float] = None
    price: Optional[float] = None
    commission: Optional[float] = None
    notes: Optional[str] = None


# Portfolio endpoints
@router.post("/portfolios")
def create_portfolio(
    portfolio: PortfolioCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new portfolio

    Returns the created portfolio with ID
    """
    new_portfolio = Portfolio(
        user_id=current_user.id,
        name=portfolio.name,
        description=portfolio.description,
        currency=portfolio.currency,
        strategy=portfolio.strategy,
        tags=portfolio.tags or [],
        is_public=portfolio.is_public
    )

    db.add(new_portfolio)
    db.commit()
    db.refresh(new_portfolio)

    return {
        'id': new_portfolio.id,
        'user_id': new_portfolio.user_id,
        'name': new_portfolio.name,
        'description': new_portfolio.description,
        'currency': new_portfolio.currency,
        'strategy': new_portfolio.strategy,
        'tags': new_portfolio.tags,
        'is_public': new_portfolio.is_public,
        'created_at': new_portfolio.created_at.isoformat(),
        'updated_at': new_portfolio.updated_at.isoformat() if new_portfolio.updated_at else None
    }


@router.get("/portfolios")
def get_portfolios(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get user's portfolios

    Returns list of portfolios with basic info
    """
    portfolios = (
        db.query(Portfolio)
        .filter(Portfolio.user_id == current_user.id)
        .order_by(desc(Portfolio.created_at))
        .offset(skip)
        .limit(limit)
        .all()
    )

    total = db.query(Portfolio).filter(Portfolio.user_id == current_user.id).count()

    return {
        'portfolios': [
            {
                'id': p.id,
                'name': p.name,
                'description': p.description,
                'currency': p.currency,
                'strategy': p.strategy,
                'tags': p.tags,
                'is_public': p.is_public,
                'created_at': p.created_at.isoformat(),
                'transaction_count': len(p.transactions)
            }
            for p in portfolios
        ],
        'total': total
    }


@router.get("/portfolios/{portfolio_id}")
def get_portfolio(
    portfolio_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get portfolio details with analytics

    Returns portfolio with current positions and performance
    """
    portfolio = db.query(Portfolio).filter(
        Portfolio.id == portfolio_id,
        Portfolio.user_id == current_user.id
    ).first()

    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    # Get transactions
    transactions = (
        db.query(Transaction)
        .filter(Transaction.portfolio_id == portfolio_id)
        .order_by(Transaction.transaction_date)
        .all()
    )

    # Convert to dict format for analytics
    txn_dicts = [
        {
            'id': t.id,
            'ticker': t.ticker,
            'transaction_type': t.transaction_type.value,
            'transaction_date': t.transaction_date.isoformat(),
            'quantity': t.quantity,
            'price': t.price,
            'commission': t.commission,
            'total_amount': t.total_amount,
            'notes': t.notes
        }
        for t in transactions
    ]

    # Calculate positions
    analytics = PortfolioAnalytics()
    positions = analytics.calculate_position_summary(txn_dicts)

    # Get current prices for positions
    current_prices = {}
    for ticker in positions.keys():
        # TODO: Fetch real-time prices from API or cache
        # For now, use latest transaction price as placeholder
        latest_txn = next((t for t in reversed(txn_dicts) if t['ticker'] == ticker), None)
        current_prices[ticker] = latest_txn['price'] if latest_txn else 0.0

    # Calculate portfolio value
    portfolio_value = analytics.calculate_portfolio_value(positions, current_prices)

    # Calculate concentration
    concentration = analytics.calculate_concentration_metrics(portfolio_value['positions'])

    return {
        'id': portfolio.id,
        'name': portfolio.name,
        'description': portfolio.description,
        'currency': portfolio.currency,
        'strategy': portfolio.strategy,
        'tags': portfolio.tags,
        'is_public': portfolio.is_public,
        'created_at': portfolio.created_at.isoformat(),
        'updated_at': portfolio.updated_at.isoformat() if portfolio.updated_at else None,
        'total_value': portfolio_value['total_value'],
        'total_cost': portfolio_value['total_cost'],
        'total_gain': portfolio_value['total_gain'],
        'total_return_percent': portfolio_value['total_return_percent'],
        'position_count': portfolio_value['position_count'],
        'positions': portfolio_value['positions'],
        'concentration': concentration,
        'transaction_count': len(transactions)
    }


@router.put("/portfolios/{portfolio_id}")
def update_portfolio(
    portfolio_id: str,
    portfolio_update: PortfolioUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update portfolio metadata

    Returns updated portfolio
    """
    portfolio = db.query(Portfolio).filter(
        Portfolio.id == portfolio_id,
        Portfolio.user_id == current_user.id
    ).first()

    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    # Update fields
    if portfolio_update.name is not None:
        portfolio.name = portfolio_update.name
    if portfolio_update.description is not None:
        portfolio.description = portfolio_update.description
    if portfolio_update.strategy is not None:
        portfolio.strategy = portfolio_update.strategy
    if portfolio_update.tags is not None:
        portfolio.tags = portfolio_update.tags
    if portfolio_update.is_public is not None:
        portfolio.is_public = portfolio_update.is_public

    db.commit()
    db.refresh(portfolio)

    return {
        'id': portfolio.id,
        'name': portfolio.name,
        'description': portfolio.description,
        'currency': portfolio.currency,
        'strategy': portfolio.strategy,
        'tags': portfolio.tags,
        'is_public': portfolio.is_public,
        'updated_at': portfolio.updated_at.isoformat() if portfolio.updated_at else None
    }


@router.delete("/portfolios/{portfolio_id}")
def delete_portfolio(
    portfolio_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a portfolio and all its transactions

    Returns success message
    """
    portfolio = db.query(Portfolio).filter(
        Portfolio.id == portfolio_id,
        Portfolio.user_id == current_user.id
    ).first()

    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    db.delete(portfolio)
    db.commit()

    return {'message': 'Portfolio deleted successfully'}


# Transaction endpoints
@router.post("/portfolios/{portfolio_id}/transactions")
def add_transaction(
    portfolio_id: str,
    transaction: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Add a transaction to a portfolio

    Returns the created transaction
    """
    # Verify portfolio ownership
    portfolio = db.query(Portfolio).filter(
        Portfolio.id == portfolio_id,
        Portfolio.user_id == current_user.id
    ).first()

    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    # Verify ticker exists
    company = db.query(Company).filter(Company.ticker == transaction.ticker).first()
    if not company:
        raise HTTPException(status_code=404, detail=f"Company with ticker {transaction.ticker} not found")

    # Calculate total amount
    total_amount = (transaction.quantity * transaction.price) + transaction.commission

    new_transaction = Transaction(
        portfolio_id=portfolio_id,
        user_id=current_user.id,
        ticker=transaction.ticker,
        transaction_type=transaction.transaction_type,
        transaction_date=transaction.transaction_date,
        quantity=transaction.quantity,
        price=transaction.price,
        commission=transaction.commission,
        total_amount=total_amount,
        notes=transaction.notes,
        currency=portfolio.currency
    )

    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)

    return {
        'id': new_transaction.id,
        'portfolio_id': new_transaction.portfolio_id,
        'ticker': new_transaction.ticker,
        'transaction_type': new_transaction.transaction_type.value,
        'transaction_date': new_transaction.transaction_date.isoformat(),
        'quantity': new_transaction.quantity,
        'price': new_transaction.price,
        'commission': new_transaction.commission,
        'total_amount': new_transaction.total_amount,
        'notes': new_transaction.notes,
        'created_at': new_transaction.created_at.isoformat()
    }


@router.get("/portfolios/{portfolio_id}/transactions")
def get_transactions(
    portfolio_id: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get all transactions for a portfolio

    Returns list of transactions sorted by date
    """
    # Verify portfolio ownership
    portfolio = db.query(Portfolio).filter(
        Portfolio.id == portfolio_id,
        Portfolio.user_id == current_user.id
    ).first()

    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    transactions = (
        db.query(Transaction)
        .filter(Transaction.portfolio_id == portfolio_id)
        .order_by(desc(Transaction.transaction_date))
        .offset(skip)
        .limit(limit)
        .all()
    )

    total = db.query(Transaction).filter(Transaction.portfolio_id == portfolio_id).count()

    return {
        'transactions': [
            {
                'id': t.id,
                'ticker': t.ticker,
                'transaction_type': t.transaction_type.value,
                'transaction_date': t.transaction_date.isoformat(),
                'quantity': t.quantity,
                'price': t.price,
                'commission': t.commission,
                'total_amount': t.total_amount,
                'notes': t.notes,
                'created_at': t.created_at.isoformat()
            }
            for t in transactions
        ],
        'total': total
    }


@router.delete("/portfolios/{portfolio_id}/transactions/{transaction_id}")
def delete_transaction(
    portfolio_id: str,
    transaction_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a transaction

    Returns success message
    """
    transaction = db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.portfolio_id == portfolio_id,
        Transaction.user_id == current_user.id
    ).first()

    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    db.delete(transaction)
    db.commit()

    return {'message': 'Transaction deleted successfully'}


@router.get("/portfolios/{portfolio_id}/analytics")
def get_portfolio_analytics(
    portfolio_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get detailed portfolio analytics

    Returns performance metrics, allocation, top performers
    """
    portfolio = db.query(Portfolio).filter(
        Portfolio.id == portfolio_id,
        Portfolio.user_id == current_user.id
    ).first()

    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    # Get transactions
    transactions = (
        db.query(Transaction)
        .filter(Transaction.portfolio_id == portfolio_id)
        .order_by(Transaction.transaction_date)
        .all()
    )

    txn_dicts = [
        {
            'ticker': t.ticker,
            'transaction_type': t.transaction_type.value,
            'quantity': t.quantity,
            'price': t.price,
            'commission': t.commission
        }
        for t in transactions
    ]

    analytics = PortfolioAnalytics()
    positions = analytics.calculate_position_summary(txn_dicts)

    # Get current prices
    current_prices = {}
    for ticker in positions.keys():
        latest_txn = next((t for t in reversed(txn_dicts) if t['ticker'] == ticker), None)
        current_prices[ticker] = latest_txn['price'] if latest_txn else 0.0

    portfolio_value = analytics.calculate_portfolio_value(positions, current_prices)

    # Get company data for allocation
    tickers = list(positions.keys())
    companies = db.query(Company).filter(Company.ticker.in_(tickers)).all()
    company_data = {c.ticker: {'sector': c.sector, 'industry': c.industry, 'exchange': c.exchange} for c in companies}

    allocation = analytics.calculate_asset_allocation(portfolio_value['positions'], company_data)
    concentration = analytics.calculate_concentration_metrics(portfolio_value['positions'])
    top_performers = analytics.get_top_performers(portfolio_value['positions'], limit=5)
    worst_performers = analytics.get_worst_performers(portfolio_value['positions'], limit=5)

    return {
        'portfolio_id': portfolio_id,
        'total_value': portfolio_value['total_value'],
        'total_cost': portfolio_value['total_cost'],
        'total_return_percent': portfolio_value['total_return_percent'],
        'allocation': allocation,
        'concentration': concentration,
        'top_performers': top_performers,
        'worst_performers': worst_performers
    }
