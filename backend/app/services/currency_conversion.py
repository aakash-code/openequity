"""
Currency Conversion Service
Handles currency conversions between USD, INR, and other currencies
"""

from typing import Dict, Optional
from datetime import datetime, timedelta
import random


class CurrencyConversionService:
    """Service for currency conversion"""

    # Sample exchange rates (in production, fetch from forex API)
    # Base currency: USD
    EXCHANGE_RATES = {
        'USD': 1.0,
        'INR': 83.12,  # 1 USD = 83.12 INR (approximate)
        'EUR': 0.92,
        'GBP': 0.79,
        'JPY': 149.50,
        'CNY': 7.24
    }

    CURRENCY_SYMBOLS = {
        'USD': '$',
        'INR': '₹',
        'EUR': '€',
        'GBP': '£',
        'JPY': '¥',
        'CNY': '¥'
    }

    CURRENCY_NAMES = {
        'USD': 'US Dollar',
        'INR': 'Indian Rupee',
        'EUR': 'Euro',
        'GBP': 'British Pound',
        'JPY': 'Japanese Yen',
        'CNY': 'Chinese Yuan'
    }

    def get_exchange_rate(
        self,
        from_currency: str,
        to_currency: str
    ) -> float:
        """
        Get exchange rate between two currencies

        Args:
            from_currency: Source currency code (USD, INR, etc.)
            to_currency: Target currency code

        Returns:
            Exchange rate
        """
        from_currency = from_currency.upper()
        to_currency = to_currency.upper()

        if from_currency not in self.EXCHANGE_RATES or to_currency not in self.EXCHANGE_RATES:
            raise ValueError(f"Unsupported currency: {from_currency} or {to_currency}")

        # Convert to USD first, then to target currency
        usd_rate = 1 / self.EXCHANGE_RATES[from_currency]
        return usd_rate * self.EXCHANGE_RATES[to_currency]

    def convert_amount(
        self,
        amount: float,
        from_currency: str,
        to_currency: str
    ) -> float:
        """
        Convert amount from one currency to another

        Args:
            amount: Amount to convert
            from_currency: Source currency
            to_currency: Target currency

        Returns:
            Converted amount
        """
        rate = self.get_exchange_rate(from_currency, to_currency)
        return round(amount * rate, 2)

    def get_currency_symbol(self, currency: str) -> str:
        """Get currency symbol"""
        return self.CURRENCY_SYMBOLS.get(currency.upper(), currency.upper())

    def get_currency_name(self, currency: str) -> str:
        """Get currency full name"""
        return self.CURRENCY_NAMES.get(currency.upper(), currency.upper())

    def get_supported_currencies(self) -> Dict[str, Dict[str, any]]:
        """Get all supported currencies with their info"""
        return {
            code: {
                'name': self.CURRENCY_NAMES[code],
                'symbol': self.CURRENCY_SYMBOLS[code],
                'rate_to_usd': 1 / self.EXCHANGE_RATES[code]
            }
            for code in self.EXCHANGE_RATES.keys()
        }

    def convert_financial_metrics(
        self,
        metrics: Dict[str, float],
        from_currency: str,
        to_currency: str
    ) -> Dict[str, float]:
        """
        Convert all financial metrics from one currency to another

        Args:
            metrics: Dictionary of financial metrics
            from_currency: Source currency
            to_currency: Target currency

        Returns:
            Converted metrics dictionary
        """
        rate = self.get_exchange_rate(from_currency, to_currency)

        converted = {}
        for key, value in metrics.items():
            if value is not None and isinstance(value, (int, float)):
                converted[key] = round(value * rate, 2)
            else:
                converted[key] = value

        return converted

    def format_amount(
        self,
        amount: float,
        currency: str,
        indian_format: bool = False
    ) -> str:
        """
        Format amount with currency symbol

        Args:
            amount: Amount to format
            currency: Currency code
            indian_format: If True and currency is INR, use Indian numbering

        Returns:
            Formatted string
        """
        symbol = self.get_currency_symbol(currency)

        if indian_format and currency.upper() == 'INR':
            return self._format_indian_number(amount, symbol)

        # Standard formatting
        if amount >= 1_000_000_000_000:  # Trillion
            return f"{symbol}{amount / 1_000_000_000_000:.2f}T"
        elif amount >= 1_000_000_000:  # Billion
            return f"{symbol}{amount / 1_000_000_000:.2f}B"
        elif amount >= 1_000_000:  # Million
            return f"{symbol}{amount / 1_000_000:.2f}M"
        elif amount >= 1_000:  # Thousand
            return f"{symbol}{amount / 1_000:.2f}K"
        else:
            return f"{symbol}{amount:,.2f}"

    def _format_indian_number(self, amount: float, symbol: str = '₹') -> str:
        """Format number in Indian numbering system (Lakhs/Crores)"""
        if amount >= 10_000_000:  # 1 Crore = 10 Million
            return f"{symbol}{amount / 10_000_000:.2f} Cr"
        elif amount >= 100_000:  # 1 Lakh = 100 Thousand
            return f"{symbol}{amount / 100_000:.2f} L"
        elif amount >= 1_000:
            return f"{symbol}{amount / 1_000:.2f} K"
        else:
            return f"{symbol}{amount:,.2f}"

    def get_historical_rates(
        self,
        from_currency: str,
        to_currency: str,
        days: int = 30
    ) -> list[Dict[str, any]]:
        """
        Get historical exchange rates

        Args:
            from_currency: Source currency
            to_currency: Target currency
            days: Number of days of historical data

        Returns:
            List of historical rates with dates
        """
        # In production, fetch from forex API
        # For now, generate sample data with small variations

        base_rate = self.get_exchange_rate(from_currency, to_currency)
        historical = []

        current_date = datetime.now()

        for i in range(days):
            date = current_date - timedelta(days=i)
            # Add small random variation
            variation = random.uniform(-0.02, 0.02)  # ±2%
            rate = base_rate * (1 + variation)

            historical.append({
                'date': date.strftime('%Y-%m-%d'),
                'rate': round(rate, 4),
                'from_currency': from_currency.upper(),
                'to_currency': to_currency.upper()
            })

        return sorted(historical, key=lambda x: x['date'], reverse=True)
