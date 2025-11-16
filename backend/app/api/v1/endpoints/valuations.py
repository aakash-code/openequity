"""
Valuation endpoints for DCF models and comparable company analysis
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.deps import get_current_user, get_db
from app.models.user import User
from app.models.dcf_valuation import DCFValuation
from app.models.peer_group import PeerGroup
from app.schemas.valuation import (
    CreateDCFRequest,
    UpdateDCFRequest,
    DCFValuationResponse,
    DCFListResponse,
    SensitivityAnalysisRequest,
    CreatePeerGroupRequest,
    UpdatePeerGroupRequest,
    PeerGroupResponse,
    PeerGroupListResponse,
    ComparableAnalysisResponse,
    WACCCalculationRequest,
    WACCCalculationResponse,
)
from app.services.dcf_calculator import DCFCalculator, WACCCalculator
from app.services.comps_calculator import CompsCalculator

router = APIRouter()
dcf_calculator = DCFCalculator()
wacc_calculator = WACCCalculator()
comps_calculator = CompsCalculator()


# WACC Calculator Endpoints


@router.post("/wacc/calculate", response_model=WACCCalculationResponse)
def calculate_wacc(
    request: WACCCalculationRequest,
    current_user: User = Depends(get_current_user),
):
    """Calculate WACC given the inputs"""
    cost_of_equity, wacc = wacc_calculator.calculate_full_wacc(
        risk_free_rate=request.risk_free_rate,
        beta=request.beta,
        equity_risk_premium=request.equity_risk_premium,
        cost_of_debt=request.cost_of_debt,
        tax_rate=request.tax_rate,
        equity_weight=request.equity_weight,
        debt_weight=request.debt_weight,
    )

    return WACCCalculationResponse(cost_of_equity=cost_of_equity, wacc=wacc)


# DCF Valuation Endpoints


@router.post("/dcf", response_model=DCFValuationResponse, status_code=status.HTTP_201_CREATED)
def create_dcf_valuation(
    request: CreateDCFRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new DCF valuation model"""

    # Calculate WACC
    cost_of_equity, wacc = wacc_calculator.calculate_full_wacc(
        risk_free_rate=request.assumptions.risk_free_rate,
        beta=request.assumptions.beta,
        equity_risk_premium=request.assumptions.equity_risk_premium,
        cost_of_debt=request.assumptions.cost_of_debt,
        tax_rate=request.assumptions.tax_rate,
        equity_weight=request.assumptions.equity_weight,
        debt_weight=request.assumptions.debt_weight,
    )

    # Perform DCF calculation
    dcf_result = dcf_calculator.calculate_dcf_valuation(
        base_revenue=request.base_revenue,
        revenue_growth_rates=request.assumptions.revenue_growth_rates,
        ebitda_margin=request.assumptions.ebitda_margin,
        depreciation_pct_revenue=request.assumptions.depreciation_pct_revenue,
        capex_pct_revenue=request.assumptions.capex_pct_revenue,
        nwc_pct_revenue=request.assumptions.nwc_pct_revenue,
        tax_rate=request.assumptions.tax_rate,
        wacc=wacc,
        terminal_growth_rate=request.assumptions.terminal_growth_rate,
        terminal_ebitda_multiple=request.assumptions.terminal_ebitda_multiple,
        net_debt=request.net_debt,
        shares_outstanding=request.shares_outstanding,
        current_price=request.current_price,
    )

    # Generate sensitivity analysis
    if request.assumptions.terminal_growth_rate:
        sensitivity = dcf_calculator.generate_sensitivity_analysis(
            base_revenue=request.base_revenue,
            revenue_growth_rates=request.assumptions.revenue_growth_rates,
            ebitda_margin=request.assumptions.ebitda_margin,
            depreciation_pct_revenue=request.assumptions.depreciation_pct_revenue,
            capex_pct_revenue=request.assumptions.capex_pct_revenue,
            nwc_pct_revenue=request.assumptions.nwc_pct_revenue,
            tax_rate=request.assumptions.tax_rate,
            base_wacc=wacc,
            base_terminal_growth=request.assumptions.terminal_growth_rate,
            net_debt=request.net_debt,
            shares_outstanding=request.shares_outstanding,
        )
    else:
        sensitivity = None

    # Create DCF valuation record
    dcf_valuation = DCFValuation(
        ticker=request.ticker,
        user_id=str(current_user.id),
        name=request.name,
        description=request.description,
        is_public=request.is_public,
        # WACC
        risk_free_rate=request.assumptions.risk_free_rate,
        equity_risk_premium=request.assumptions.equity_risk_premium,
        beta=request.assumptions.beta,
        cost_of_debt=request.assumptions.cost_of_debt,
        tax_rate=request.assumptions.tax_rate,
        debt_weight=request.assumptions.debt_weight,
        equity_weight=request.assumptions.equity_weight,
        wacc=wacc,
        # Assumptions
        projection_years=request.assumptions.projection_years,
        revenue_growth_rates=request.assumptions.revenue_growth_rates,
        ebitda_margin=request.assumptions.ebitda_margin,
        depreciation_pct_revenue=request.assumptions.depreciation_pct_revenue,
        capex_pct_revenue=request.assumptions.capex_pct_revenue,
        nwc_pct_revenue=request.assumptions.nwc_pct_revenue,
        terminal_growth_rate=request.assumptions.terminal_growth_rate,
        terminal_ebitda_multiple=request.assumptions.terminal_ebitda_multiple,
        # Results
        enterprise_value=dcf_result["valuation"]["enterprise_value"],
        equity_value=dcf_result["valuation"]["equity_value"],
        shares_outstanding=request.shares_outstanding,
        value_per_share=dcf_result["valuation"]["value_per_share"],
        current_price=request.current_price,
        upside_downside=dcf_result["valuation"]["upside_downside_pct"],
        projections=dcf_result["projections"],
        fcf_projections=dcf_result["projections"]["fcf"],
        terminal_value=dcf_result["terminal_value"]["value"],
        pv_terminal_value=dcf_result["terminal_value"]["pv"],
        pv_fcf=dcf_result["pv_fcf"]["total"],
        sensitivity_analysis=sensitivity,
    )

    db.add(dcf_valuation)
    db.commit()
    db.refresh(dcf_valuation)

    return dcf_valuation


@router.get("/dcf", response_model=DCFListResponse)
def list_dcf_valuations(
    ticker: str = None,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List DCF valuations for the current user"""
    query = db.query(DCFValuation).filter(DCFValuation.user_id == str(current_user.id))

    if ticker:
        query = query.filter(DCFValuation.ticker == ticker)

    total = query.count()
    valuations = query.order_by(DCFValuation.created_at.desc()).offset(skip).limit(limit).all()

    return DCFListResponse(valuations=valuations, total=total)


@router.get("/dcf/{valuation_id}", response_model=DCFValuationResponse)
def get_dcf_valuation(
    valuation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific DCF valuation"""
    valuation = db.query(DCFValuation).filter(DCFValuation.id == valuation_id).first()

    if not valuation:
        raise HTTPException(status_code=404, detail="DCF valuation not found")

    # Check access: user must own it or it must be public
    if valuation.user_id != str(current_user.id) and not valuation.is_public:
        raise HTTPException(status_code=403, detail="Access denied")

    return valuation


@router.put("/dcf/{valuation_id}", response_model=DCFValuationResponse)
def update_dcf_valuation(
    valuation_id: str,
    request: UpdateDCFRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a DCF valuation"""
    valuation = db.query(DCFValuation).filter(DCFValuation.id == valuation_id).first()

    if not valuation:
        raise HTTPException(status_code=404, detail="DCF valuation not found")

    if valuation.user_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="Access denied")

    # Update fields
    if request.name:
        valuation.name = request.name
    if request.description is not None:
        valuation.description = request.description
    if request.is_public is not None:
        valuation.is_public = request.is_public

    # If assumptions changed, recalculate
    needs_recalc = False
    if request.base_revenue or request.net_debt or request.shares_outstanding or request.assumptions:
        needs_recalc = True

    if needs_recalc and request.assumptions:
        # Recalculate WACC
        cost_of_equity, wacc = wacc_calculator.calculate_full_wacc(
            risk_free_rate=request.assumptions.risk_free_rate,
            beta=request.assumptions.beta,
            equity_risk_premium=request.assumptions.equity_risk_premium,
            cost_of_debt=request.assumptions.cost_of_debt,
            tax_rate=request.assumptions.tax_rate,
            equity_weight=request.assumptions.equity_weight,
            debt_weight=request.assumptions.debt_weight,
        )

        # Update assumptions
        valuation.risk_free_rate = request.assumptions.risk_free_rate
        valuation.equity_risk_premium = request.assumptions.equity_risk_premium
        valuation.beta = request.assumptions.beta
        valuation.cost_of_debt = request.assumptions.cost_of_debt
        valuation.tax_rate = request.assumptions.tax_rate
        valuation.debt_weight = request.assumptions.debt_weight
        valuation.equity_weight = request.assumptions.equity_weight
        valuation.wacc = wacc
        valuation.revenue_growth_rates = request.assumptions.revenue_growth_rates
        valuation.ebitda_margin = request.assumptions.ebitda_margin
        valuation.depreciation_pct_revenue = request.assumptions.depreciation_pct_revenue
        valuation.capex_pct_revenue = request.assumptions.capex_pct_revenue
        valuation.nwc_pct_revenue = request.assumptions.nwc_pct_revenue
        valuation.terminal_growth_rate = request.assumptions.terminal_growth_rate
        valuation.terminal_ebitda_multiple = request.assumptions.terminal_ebitda_multiple

        # Recalculate DCF
        # Note: Would need base_revenue from somewhere
        # For now, skip full recalc in update

    db.commit()
    db.refresh(valuation)

    return valuation


@router.delete("/dcf/{valuation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_dcf_valuation(
    valuation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a DCF valuation"""
    valuation = db.query(DCFValuation).filter(DCFValuation.id == valuation_id).first()

    if not valuation:
        raise HTTPException(status_code=404, detail="DCF valuation not found")

    if valuation.user_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="Access denied")

    db.delete(valuation)
    db.commit()


# Peer Group / Comps Endpoints


@router.post("/comps/peer-groups", response_model=PeerGroupResponse, status_code=status.HTTP_201_CREATED)
def create_peer_group(
    request: CreatePeerGroupRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new peer group"""
    peer_group = PeerGroup(
        ticker=request.ticker,
        user_id=str(current_user.id),
        name=request.name,
        description=request.description,
        peer_tickers=request.peer_tickers,
        is_public=request.is_public,
    )

    db.add(peer_group)
    db.commit()
    db.refresh(peer_group)

    return peer_group


@router.get("/comps/peer-groups", response_model=PeerGroupListResponse)
def list_peer_groups(
    ticker: str = None,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List peer groups for the current user"""
    query = db.query(PeerGroup).filter(PeerGroup.user_id == str(current_user.id))

    if ticker:
        query = query.filter(PeerGroup.ticker == ticker)

    total = query.count()
    peer_groups = query.order_by(PeerGroup.created_at.desc()).offset(skip).limit(limit).all()

    return PeerGroupListResponse(peer_groups=peer_groups, total=total)


@router.get("/comps/peer-groups/{group_id}", response_model=PeerGroupResponse)
def get_peer_group(
    group_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific peer group"""
    peer_group = db.query(PeerGroup).filter(PeerGroup.id == group_id).first()

    if not peer_group:
        raise HTTPException(status_code=404, detail="Peer group not found")

    if peer_group.user_id != str(current_user.id) and not peer_group.is_public:
        raise HTTPException(status_code=403, detail="Access denied")

    return peer_group


@router.put("/comps/peer-groups/{group_id}", response_model=PeerGroupResponse)
def update_peer_group(
    group_id: str,
    request: UpdatePeerGroupRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a peer group"""
    peer_group = db.query(PeerGroup).filter(PeerGroup.id == group_id).first()

    if not peer_group:
        raise HTTPException(status_code=404, detail="Peer group not found")

    if peer_group.user_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="Access denied")

    if request.name:
        peer_group.name = request.name
    if request.description is not None:
        peer_group.description = request.description
    if request.peer_tickers:
        peer_group.peer_tickers = request.peer_tickers
    if request.is_public is not None:
        peer_group.is_public = request.is_public

    db.commit()
    db.refresh(peer_group)

    return peer_group


@router.delete("/comps/peer-groups/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_peer_group(
    group_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a peer group"""
    peer_group = db.query(PeerGroup).filter(PeerGroup.id == group_id).first()

    if not peer_group:
        raise HTTPException(status_code=404, detail="Peer group not found")

    if peer_group.user_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="Access denied")

    db.delete(peer_group)
    db.commit()


@router.post("/comps/analyze/{group_id}", response_model=ComparableAnalysisResponse)
async def analyze_peer_group(
    group_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Perform comparable company analysis for a peer group"""
    peer_group = db.query(PeerGroup).filter(PeerGroup.id == group_id).first()

    if not peer_group:
        raise HTTPException(status_code=404, detail="Peer group not found")

    if peer_group.user_id != str(current_user.id) and not peer_group.is_public:
        raise HTTPException(status_code=403, detail="Access denied")

    # Perform analysis
    analysis = await comps_calculator.analyze_peer_group(
        target_ticker=peer_group.ticker, peer_tickers=peer_group.peer_tickers
    )

    if "error" in analysis:
        raise HTTPException(status_code=500, detail=analysis["error"])

    # Store analysis results in peer group
    peer_group.analysis_results = analysis
    from datetime import datetime
    peer_group.last_analyzed = datetime.utcnow()
    db.commit()

    return analysis


@router.get("/comps/analyze/ticker/{ticker}")
async def quick_comps_analysis(
    ticker: str,
    peer_tickers: str,  # Comma-separated list
    current_user: User = Depends(get_current_user),
):
    """Quick comps analysis without saving to database"""
    peers = [p.strip() for p in peer_tickers.split(",")]
    analysis = await comps_calculator.analyze_peer_group(
        target_ticker=ticker, peer_tickers=peers
    )

    if "error" in analysis:
        raise HTTPException(status_code=500, detail=analysis["error"])

    return analysis
