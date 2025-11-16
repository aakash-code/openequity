"""
Options Chain Service
Calculate options chain data, Greeks, implied volatility, and analytics
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import random
import math


class OptionsChainService:
    """Service for options chain analysis and Greeks calculations"""

    def get_options_chain(
        self,
        ticker: str,
        expiry_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get options chain for a ticker

        Args:
            ticker: Stock ticker symbol
            expiry_date: Expiry date (YYYY-MM-DD). If None, returns nearest expiry

        Returns:
            Complete options chain with calls and puts
        """
        # In production, fetch from options data provider
        # For now, generate sample data

        spot_price = round(random.uniform(100, 5000), 2)

        # Generate expiry dates (weekly for next 4 weeks, monthly for next 3 months)
        expiry_dates = self._generate_expiry_dates()

        if not expiry_date:
            expiry_date = expiry_dates[0]

        # Generate strikes around spot price
        strikes = self._generate_strikes(spot_price)

        calls = []
        puts = []

        for strike in strikes:
            # Determine moneyness
            moneyness = self._get_moneyness(spot_price, strike, 'call')

            # Generate call option data
            call = self._generate_option_data(
                ticker, strike, expiry_date, 'call', spot_price, moneyness
            )
            calls.append(call)

            # Generate put option data
            moneyness = self._get_moneyness(spot_price, strike, 'put')
            put = self._generate_option_data(
                ticker, strike, expiry_date, 'put', spot_price, moneyness
            )
            puts.append(put)

        # Calculate max pain
        max_pain_strike = self._calculate_max_pain(calls, puts)

        # Calculate PCR (Put-Call Ratio)
        total_call_oi = sum(c['open_interest'] for c in calls)
        total_put_oi = sum(p['open_interest'] for p in puts)
        pcr = total_put_oi / total_call_oi if total_call_oi > 0 else 0

        return {
            'ticker': ticker,
            'spot_price': spot_price,
            'expiry_date': expiry_date,
            'available_expiries': expiry_dates,
            'calls': calls,
            'puts': puts,
            'analytics': {
                'max_pain': max_pain_strike,
                'pcr_oi': round(pcr, 2),
                'total_call_oi': total_call_oi,
                'total_put_oi': total_put_oi,
                'atm_strike': min(strikes, key=lambda x: abs(x - spot_price))
            },
            'last_updated': datetime.now().isoformat()
        }

    def get_option_greeks(
        self,
        spot_price: float,
        strike: float,
        time_to_expiry: float,
        volatility: float,
        risk_free_rate: float,
        option_type: str
    ) -> Dict[str, float]:
        """
        Calculate option Greeks using Black-Scholes model

        Args:
            spot_price: Current stock price
            strike: Strike price
            time_to_expiry: Time to expiry in years
            volatility: Implied volatility (annualized)
            risk_free_rate: Risk-free rate
            option_type: 'call' or 'put'

        Returns:
            Dictionary with Delta, Gamma, Theta, Vega, Rho
        """
        # Simplified Black-Scholes Greeks
        # In production, use proper implementation

        if time_to_expiry <= 0:
            return {
                'delta': 1.0 if option_type == 'call' and spot_price > strike else 0.0,
                'gamma': 0.0,
                'theta': 0.0,
                'vega': 0.0,
                'rho': 0.0
            }

        # Calculate d1 and d2
        d1 = (math.log(spot_price / strike) + (risk_free_rate + 0.5 * volatility ** 2) * time_to_expiry) / (volatility * math.sqrt(time_to_expiry))
        d2 = d1 - volatility * math.sqrt(time_to_expiry)

        # Delta
        if option_type == 'call':
            delta = self._norm_cdf(d1)
        else:
            delta = self._norm_cdf(d1) - 1

        # Gamma (same for calls and puts)
        gamma = self._norm_pdf(d1) / (spot_price * volatility * math.sqrt(time_to_expiry))

        # Theta
        if option_type == 'call':
            theta = (-spot_price * self._norm_pdf(d1) * volatility / (2 * math.sqrt(time_to_expiry))
                    - risk_free_rate * strike * math.exp(-risk_free_rate * time_to_expiry) * self._norm_cdf(d2))
        else:
            theta = (-spot_price * self._norm_pdf(d1) * volatility / (2 * math.sqrt(time_to_expiry))
                    + risk_free_rate * strike * math.exp(-risk_free_rate * time_to_expiry) * self._norm_cdf(-d2))

        # Vega (same for calls and puts)
        vega = spot_price * self._norm_pdf(d1) * math.sqrt(time_to_expiry)

        # Rho
        if option_type == 'call':
            rho = strike * time_to_expiry * math.exp(-risk_free_rate * time_to_expiry) * self._norm_cdf(d2)
        else:
            rho = -strike * time_to_expiry * math.exp(-risk_free_rate * time_to_expiry) * self._norm_cdf(-d2)

        return {
            'delta': round(delta, 4),
            'gamma': round(gamma, 4),
            'theta': round(theta / 365, 4),  # Daily theta
            'vega': round(vega / 100, 4),    # Vega per 1% change in IV
            'rho': round(rho / 100, 4)       # Rho per 1% change in rate
        }

    def analyze_strategy(
        self,
        ticker: str,
        legs: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze an options strategy (spread, straddle, etc.)

        Args:
            ticker: Stock ticker
            legs: List of strategy legs with strike, type, position, quantity

        Returns:
            Strategy analysis with P&L, Greeks, max profit/loss
        """
        spot_price = round(random.uniform(100, 5000), 2)

        total_cost = 0
        total_greeks = {'delta': 0, 'gamma': 0, 'theta': 0, 'vega': 0, 'rho': 0}

        for leg in legs:
            # In production, fetch actual option prices
            premium = round(random.uniform(1, 50), 2)
            multiplier = 1 if leg['position'] == 'buy' else -1

            cost = premium * leg['quantity'] * multiplier * 100  # 100 shares per contract
            total_cost += cost

            # Add Greeks
            greeks = self.get_option_greeks(
                spot_price,
                leg['strike'],
                leg.get('time_to_expiry', 0.1),
                leg.get('volatility', 0.3),
                0.05,
                leg['option_type']
            )

            for greek, value in greeks.items():
                total_greeks[greek] += value * leg['quantity'] * multiplier

        # Calculate P&L at different spot prices
        price_range = [spot_price * (1 + i * 0.05) for i in range(-10, 11)]
        pnl_curve = []

        for price in price_range:
            pnl = -total_cost  # Start with initial cost
            for leg in legs:
                intrinsic = self._calculate_intrinsic_value(
                    price, leg['strike'], leg['option_type']
                )
                multiplier = 1 if leg['position'] == 'buy' else -1
                pnl += intrinsic * leg['quantity'] * multiplier * 100

            pnl_curve.append({'price': round(price, 2), 'pnl': round(pnl, 2)})

        # Find max profit and max loss
        max_profit = max(p['pnl'] for p in pnl_curve)
        max_loss = min(p['pnl'] for p in pnl_curve)

        # Find breakeven points
        breakeven_points = []
        for i in range(len(pnl_curve) - 1):
            if (pnl_curve[i]['pnl'] < 0 and pnl_curve[i+1]['pnl'] >= 0) or \
               (pnl_curve[i]['pnl'] >= 0 and pnl_curve[i+1]['pnl'] < 0):
                breakeven_points.append(round((pnl_curve[i]['price'] + pnl_curve[i+1]['price']) / 2, 2))

        return {
            'ticker': ticker,
            'spot_price': spot_price,
            'total_cost': round(total_cost, 2),
            'max_profit': round(max_profit, 2),
            'max_loss': round(max_loss, 2),
            'breakeven_points': breakeven_points,
            'total_greeks': {k: round(v, 4) for k, v in total_greeks.items()},
            'pnl_curve': pnl_curve,
            'legs': legs
        }

    def _generate_expiry_dates(self) -> List[str]:
        """Generate realistic expiry dates"""
        expiries = []
        current_date = datetime.now()

        # Weekly expiries for next 4 weeks (Thursdays)
        for i in range(4):
            days_ahead = (3 - current_date.weekday()) % 7 + i * 7
            if days_ahead == 0:
                days_ahead = 7
            expiry = current_date + timedelta(days=days_ahead)
            expiries.append(expiry.strftime('%Y-%m-%d'))

        # Monthly expiries for next 3 months (last Thursday)
        for i in range(1, 4):
            month = (current_date.month + i - 1) % 12 + 1
            year = current_date.year + (current_date.month + i - 1) // 12

            # Find last Thursday
            last_day = 31
            while True:
                try:
                    last_date = datetime(year, month, last_day)
                    break
                except ValueError:
                    last_day -= 1

            # Find last Thursday
            days_back = (last_date.weekday() - 3) % 7
            last_thursday = last_date - timedelta(days=days_back)
            expiries.append(last_thursday.strftime('%Y-%m-%d'))

        return sorted(set(expiries))

    def _generate_strikes(self, spot_price: float) -> List[float]:
        """Generate strike prices around spot"""
        # Determine strike interval based on spot price
        if spot_price < 100:
            interval = 5
        elif spot_price < 500:
            interval = 10
        elif spot_price < 1000:
            interval = 25
        elif spot_price < 2000:
            interval = 50
        else:
            interval = 100

        # Generate strikes ±20% around spot
        lower = int(spot_price * 0.8 / interval) * interval
        upper = int(spot_price * 1.2 / interval) * interval

        strikes = []
        strike = lower
        while strike <= upper:
            strikes.append(float(strike))
            strike += interval

        return strikes

    def _get_moneyness(self, spot: float, strike: float, option_type: str) -> str:
        """Determine if option is ITM, ATM, or OTM"""
        diff = abs(spot - strike)
        threshold = spot * 0.02  # 2% threshold for ATM

        if diff <= threshold:
            return 'ATM'

        if option_type == 'call':
            return 'ITM' if spot > strike else 'OTM'
        else:
            return 'ITM' if spot < strike else 'OTM'

    def _generate_option_data(
        self,
        ticker: str,
        strike: float,
        expiry: str,
        option_type: str,
        spot_price: float,
        moneyness: str
    ) -> Dict[str, Any]:
        """Generate realistic option data"""
        # Calculate time to expiry
        expiry_date = datetime.strptime(expiry, '%Y-%m-%d')
        days_to_expiry = (expiry_date - datetime.now()).days
        time_to_expiry = max(days_to_expiry / 365, 0.001)

        # Generate implied volatility (higher for OTM options)
        base_iv = random.uniform(0.2, 0.5)
        if moneyness == 'OTM':
            iv = base_iv * random.uniform(1.1, 1.3)
        elif moneyness == 'ATM':
            iv = base_iv
        else:
            iv = base_iv * random.uniform(0.9, 1.0)

        # Calculate intrinsic value
        intrinsic = self._calculate_intrinsic_value(spot_price, strike, option_type)

        # Calculate time value (simplified)
        time_value = spot_price * iv * math.sqrt(time_to_expiry) * random.uniform(0.3, 0.7)

        # Option price = intrinsic + time value
        premium = max(intrinsic + time_value, 0.05)

        # Calculate Greeks
        greeks = self.get_option_greeks(
            spot_price, strike, time_to_expiry, iv, 0.05, option_type
        )

        # Generate volume and OI (higher for ATM)
        if moneyness == 'ATM':
            volume = random.randint(5000, 50000)
            oi = random.randint(10000, 100000)
        elif moneyness == 'ITM':
            volume = random.randint(1000, 20000)
            oi = random.randint(5000, 50000)
        else:
            volume = random.randint(500, 10000)
            oi = random.randint(2000, 30000)

        return {
            'ticker': ticker,
            'strike': strike,
            'expiry': expiry,
            'option_type': option_type,
            'moneyness': moneyness,
            'last_price': round(premium, 2),
            'bid': round(premium * 0.98, 2),
            'ask': round(premium * 1.02, 2),
            'change': round(random.uniform(-5, 5), 2),
            'change_percent': round(random.uniform(-20, 20), 2),
            'volume': volume,
            'open_interest': oi,
            'implied_volatility': round(iv * 100, 2),  # Convert to percentage
            'intrinsic_value': round(intrinsic, 2),
            'time_value': round(time_value, 2),
            'delta': greeks['delta'],
            'gamma': greeks['gamma'],
            'theta': greeks['theta'],
            'vega': greeks['vega'],
            'rho': greeks['rho']
        }

    def _calculate_intrinsic_value(self, spot: float, strike: float, option_type: str) -> float:
        """Calculate intrinsic value of option"""
        if option_type == 'call':
            return max(spot - strike, 0)
        else:
            return max(strike - spot, 0)

    def _calculate_max_pain(self, calls: List[Dict], puts: List[Dict]) -> float:
        """Calculate max pain strike (where option writers lose least money)"""
        # Group by strike
        strikes = set(c['strike'] for c in calls)

        min_loss = float('inf')
        max_pain_strike = 0

        for strike in strikes:
            # Calculate total loss for option writers at this strike
            total_loss = 0

            # Calls: writers lose if spot > strike
            for call in calls:
                if call['strike'] < strike:
                    total_loss += (strike - call['strike']) * call['open_interest']

            # Puts: writers lose if spot < strike
            for put in puts:
                if put['strike'] > strike:
                    total_loss += (put['strike'] - strike) * put['open_interest']

            if total_loss < min_loss:
                min_loss = total_loss
                max_pain_strike = strike

        return max_pain_strike

    def _norm_cdf(self, x: float) -> float:
        """Cumulative distribution function for standard normal distribution"""
        return (1.0 + math.erf(x / math.sqrt(2.0))) / 2.0

    def _norm_pdf(self, x: float) -> float:
        """Probability density function for standard normal distribution"""
        return math.exp(-x**2 / 2.0) / math.sqrt(2.0 * math.pi)
