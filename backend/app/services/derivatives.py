"""
Derivatives Service
Track F&O positions, calculate margins, analyze derivative positions
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import random


class DerivativesService:
    """Service for futures and options position tracking"""

    # Margin requirements (as % of contract value)
    MARGIN_REQUIREMENTS = {
        'futures': {
            'initial': 0.15,  # 15% initial margin
            'maintenance': 0.10  # 10% maintenance margin
        },
        'options_buy': {
            'initial': 1.0,  # 100% - full premium
            'maintenance': 1.0
        },
        'options_sell': {
            'initial': 0.20,  # 20% for short options
            'maintenance': 0.15
        }
    }

    def get_futures_chain(
        self,
        ticker: str,
        expiry_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get futures chain for a ticker

        Args:
            ticker: Stock ticker symbol
            expiry_date: Expiry date. If None, returns all expiries

        Returns:
            Futures chain data
        """
        spot_price = round(random.uniform(100, 5000), 2)

        # Generate expiry dates (current month, next month, far month)
        expiries = self._generate_futures_expiries()

        futures = []
        for expiry in expiries:
            if expiry_date and expiry != expiry_date:
                continue

            # Calculate fair value with cost of carry
            days_to_expiry = (datetime.strptime(expiry, '%Y-%m-%d') - datetime.now()).days
            carry_cost = spot_price * 0.05 * (days_to_expiry / 365)  # 5% annual rate
            fair_value = spot_price + carry_cost

            # Add some random noise
            last_price = fair_value * random.uniform(0.98, 1.02)

            future = {
                'ticker': ticker,
                'expiry': expiry,
                'last_price': round(last_price, 2),
                'spot_price': spot_price,
                'basis': round(last_price - spot_price, 2),
                'basis_percent': round((last_price - spot_price) / spot_price * 100, 2),
                'change': round(random.uniform(-50, 50), 2),
                'change_percent': round(random.uniform(-3, 3), 2),
                'volume': random.randint(10000, 500000),
                'open_interest': random.randint(50000, 1000000),
                'oi_change': random.randint(-50000, 50000),
                'bid': round(last_price * 0.999, 2),
                'ask': round(last_price * 1.001, 2),
                'lot_size': self._get_lot_size(spot_price),
                'contract_value': round(last_price * self._get_lot_size(spot_price), 2)
            }
            futures.append(future)

        return {
            'ticker': ticker,
            'spot_price': spot_price,
            'futures': futures,
            'available_expiries': expiries,
            'last_updated': datetime.now().isoformat()
        }

    def calculate_position_margin(
        self,
        positions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculate margin requirements for derivative positions

        Args:
            positions: List of positions with details

        Returns:
            Margin requirements and utilization
        """
        total_initial_margin = 0
        total_maintenance_margin = 0
        total_exposure = 0

        position_margins = []

        for pos in positions:
            instrument_type = pos['instrument_type']  # 'futures', 'call_buy', 'put_buy', 'call_sell', 'put_sell'
            quantity = pos['quantity']
            price = pos['price']
            lot_size = pos.get('lot_size', 1)

            # Calculate contract value
            contract_value = price * quantity * lot_size
            total_exposure += abs(contract_value)

            # Determine margin requirement
            if instrument_type == 'futures':
                req = self.MARGIN_REQUIREMENTS['futures']
            elif instrument_type in ['call_buy', 'put_buy']:
                req = self.MARGIN_REQUIREMENTS['options_buy']
            else:  # call_sell or put_sell
                req = self.MARGIN_REQUIREMENTS['options_sell']

            initial_margin = contract_value * req['initial']
            maintenance_margin = contract_value * req['maintenance']

            total_initial_margin += initial_margin
            total_maintenance_margin += maintenance_margin

            position_margins.append({
                'position_id': pos.get('id', f"POS{len(position_margins)+1}"),
                'ticker': pos['ticker'],
                'instrument_type': instrument_type,
                'quantity': quantity,
                'contract_value': round(contract_value, 2),
                'initial_margin': round(initial_margin, 2),
                'maintenance_margin': round(maintenance_margin, 2)
            })

        # Calculate margin utilization (assume account balance)
        account_balance = total_initial_margin * 1.5  # Assume 50% buffer

        return {
            'total_exposure': round(total_exposure, 2),
            'total_initial_margin': round(total_initial_margin, 2),
            'total_maintenance_margin': round(total_maintenance_margin, 2),
            'account_balance': round(account_balance, 2),
            'available_margin': round(account_balance - total_initial_margin, 2),
            'margin_utilization_percent': round(total_initial_margin / account_balance * 100, 2),
            'positions': position_margins,
            'margin_status': 'safe' if total_initial_margin < account_balance * 0.8 else 'warning'
        }

    def analyze_fno_positions(
        self,
        positions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze F&O position portfolio

        Args:
            positions: List of F&O positions

        Returns:
            Portfolio analytics
        """
        total_value = 0
        total_pnl = 0
        delta_exposure = 0
        gamma_exposure = 0
        theta_exposure = 0
        vega_exposure = 0

        position_analytics = []

        for pos in positions:
            quantity = pos['quantity']
            entry_price = pos['entry_price']
            current_price = pos['current_price']
            lot_size = pos.get('lot_size', 1)

            # Calculate P&L
            pnl = (current_price - entry_price) * quantity * lot_size
            if pos.get('position', 'long') == 'short':
                pnl = -pnl

            total_pnl += pnl

            # Calculate position value
            position_value = current_price * quantity * lot_size
            total_value += abs(position_value)

            # Aggregate Greeks (for options)
            if 'delta' in pos:
                delta_exposure += pos['delta'] * quantity
                gamma_exposure += pos.get('gamma', 0) * quantity
                theta_exposure += pos.get('theta', 0) * quantity
                vega_exposure += pos.get('vega', 0) * quantity

            position_analytics.append({
                'ticker': pos['ticker'],
                'instrument': pos.get('instrument_type', 'futures'),
                'quantity': quantity,
                'entry_price': entry_price,
                'current_price': current_price,
                'pnl': round(pnl, 2),
                'pnl_percent': round(pnl / (entry_price * quantity * lot_size) * 100, 2),
                'position_value': round(position_value, 2)
            })

        return {
            'total_positions': len(positions),
            'total_value': round(total_value, 2),
            'total_pnl': round(total_pnl, 2),
            'total_pnl_percent': round(total_pnl / total_value * 100, 2) if total_value > 0 else 0,
            'portfolio_greeks': {
                'delta': round(delta_exposure, 2),
                'gamma': round(gamma_exposure, 4),
                'theta': round(theta_exposure, 2),
                'vega': round(vega_exposure, 2)
            },
            'positions': position_analytics,
            'risk_metrics': {
                'delta_neutral': abs(delta_exposure) < 10,
                'theta_decay': theta_exposure,
                'gamma_risk': abs(gamma_exposure)
            }
        }

    def get_oi_analysis(
        self,
        ticker: str,
        instrument_type: str = 'options'
    ) -> Dict[str, Any]:
        """
        Analyze open interest build-up

        Args:
            ticker: Stock ticker
            instrument_type: 'options' or 'futures'

        Returns:
            OI analysis with support/resistance levels
        """
        spot_price = round(random.uniform(100, 5000), 2)

        if instrument_type == 'options':
            # Generate OI data for options
            strikes = self._generate_strikes(spot_price, 20)

            call_oi = []
            put_oi = []

            max_call_oi_strike = 0
            max_call_oi = 0
            max_put_oi_strike = 0
            max_put_oi = 0

            for strike in strikes:
                # Higher OI near ATM and round numbers
                distance_from_spot = abs(strike - spot_price)
                is_round = strike % 100 == 0

                base_oi = random.randint(10000, 50000)
                if distance_from_spot < spot_price * 0.05:  # Within 5%
                    multiplier = random.uniform(2, 5)
                elif is_round:
                    multiplier = random.uniform(1.5, 3)
                else:
                    multiplier = 1

                c_oi = int(base_oi * multiplier * random.uniform(0.8, 1.2))
                p_oi = int(base_oi * multiplier * random.uniform(0.8, 1.2))

                if c_oi > max_call_oi:
                    max_call_oi = c_oi
                    max_call_oi_strike = strike

                if p_oi > max_put_oi:
                    max_put_oi = p_oi
                    max_put_oi_strike = strike

                call_oi.append({'strike': strike, 'oi': c_oi, 'oi_change': random.randint(-10000, 10000)})
                put_oi.append({'strike': strike, 'oi': p_oi, 'oi_change': random.randint(-10000, 10000)})

            # Calculate PCR
            total_call_oi = sum(c['oi'] for c in call_oi)
            total_put_oi = sum(p['oi'] for p in put_oi)
            pcr = total_put_oi / total_call_oi if total_call_oi > 0 else 0

            return {
                'ticker': ticker,
                'spot_price': spot_price,
                'call_oi': call_oi,
                'put_oi': put_oi,
                'max_call_oi': {
                    'strike': max_call_oi_strike,
                    'oi': max_call_oi,
                    'interpretation': f'Strong resistance at {max_call_oi_strike}'
                },
                'max_put_oi': {
                    'strike': max_put_oi_strike,
                    'oi': max_put_oi,
                    'interpretation': f'Strong support at {max_put_oi_strike}'
                },
                'pcr': round(pcr, 2),
                'pcr_interpretation': self._interpret_pcr(pcr),
                'last_updated': datetime.now().isoformat()
            }

        else:  # futures
            expiries = self._generate_futures_expiries()

            futures_oi = []
            for expiry in expiries:
                oi = random.randint(100000, 2000000)
                oi_change = random.randint(-100000, 100000)

                futures_oi.append({
                    'expiry': expiry,
                    'oi': oi,
                    'oi_change': oi_change,
                    'oi_change_percent': round(oi_change / oi * 100, 2) if oi > 0 else 0
                })

            total_oi = sum(f['oi'] for f in futures_oi)

            return {
                'ticker': ticker,
                'spot_price': spot_price,
                'futures_oi': futures_oi,
                'total_oi': total_oi,
                'interpretation': 'Long build-up' if futures_oi[0]['oi_change'] > 0 else 'Long unwinding',
                'last_updated': datetime.now().isoformat()
            }

    def _generate_futures_expiries(self) -> List[str]:
        """Generate futures expiry dates (current, next, far month)"""
        expiries = []
        current_date = datetime.now()

        for i in range(3):
            month = (current_date.month + i - 1) % 12 + 1
            year = current_date.year + (current_date.month + i - 1) // 12

            # Last Thursday of month
            last_day = 31
            while True:
                try:
                    last_date = datetime(year, month, last_day)
                    break
                except ValueError:
                    last_day -= 1

            days_back = (last_date.weekday() - 3) % 7
            last_thursday = last_date - timedelta(days=days_back)

            if last_thursday > current_date:
                expiries.append(last_thursday.strftime('%Y-%m-%d'))

        return expiries[:3]

    def _get_lot_size(self, price: float) -> int:
        """Determine lot size based on price (NSE convention)"""
        if price < 100:
            return 5000
        elif price < 500:
            return 1000
        elif price < 1000:
            return 500
        elif price < 2000:
            return 250
        else:
            return 125

    def _generate_strikes(self, spot: float, count: int = 20) -> List[float]:
        """Generate strike prices around spot"""
        if spot < 100:
            interval = 5
        elif spot < 500:
            interval = 10
        elif spot < 1000:
            interval = 25
        elif spot < 2000:
            interval = 50
        else:
            interval = 100

        strikes = []
        start_strike = int(spot / interval) * interval - (count // 2) * interval

        for i in range(count):
            strikes.append(float(start_strike + i * interval))

        return strikes

    def _interpret_pcr(self, pcr: float) -> str:
        """Interpret Put-Call Ratio"""
        if pcr > 1.5:
            return 'Highly Bullish - Excessive put writing'
        elif pcr > 1.2:
            return 'Bullish - More puts than calls'
        elif pcr > 0.8:
            return 'Neutral - Balanced options activity'
        elif pcr > 0.5:
            return 'Bearish - More calls than puts'
        else:
            return 'Highly Bearish - Excessive call writing'
