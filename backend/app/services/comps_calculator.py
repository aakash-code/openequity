"""
Comparable Company Analysis Calculator
Calculates trading multiples and statistics for peer group analysis
"""
from typing import Dict, List, Optional
import statistics
import httpx
from app.services.ratios import FinancialRatiosCalculator


class CompsCalculator:
    """
    Calculator for comparable company analysis (trading comps)
    Fetches financial data and calculates multiples for peer companies
    """

    def __init__(self):
        self.ratios_calculator = FinancialRatiosCalculator()

    async def fetch_company_metrics(self, ticker: str) -> Dict:
        """
        Fetch key metrics for a company from Yahoo Finance

        Args:
            ticker: Company ticker symbol

        Returns:
            Dictionary with company metrics and multiples
        """
        try:
            # Determine market suffix
            # For simplicity, try without suffix first (US), then .NS (NSE), then .BO (BSE)
            yahoo_ticker = ticker
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Try US ticker first
                url = f"https://query2.finance.yahoo.com/v10/finance/quoteSummary/{yahoo_ticker}"
                params = {
                    "modules": "defaultKeyStatistics,financialData,summaryDetail,price,incomeStatementHistory,balanceSheetHistory,cashflowStatementHistory"
                }

                response = await client.get(url, params=params)
                if response.status_code != 200:
                    # Try Indian markets
                    for suffix in [".NS", ".BO"]:
                        yahoo_ticker = f"{ticker}{suffix}"
                        response = await client.get(
                            f"https://query2.finance.yahoo.com/v10/finance/quoteSummary/{yahoo_ticker}",
                            params=params,
                        )
                        if response.status_code == 200:
                            break

                if response.status_code != 200:
                    return None

                data = response.json()
                result = data.get("quoteSummary", {}).get("result", [])
                if not result:
                    return None

                company_data = result[0]

                # Extract key metrics
                price_data = company_data.get("price", {})
                summary_detail = company_data.get("summaryDetail", {})
                key_stats = company_data.get("defaultKeyStatistics", {})
                financial_data = company_data.get("financialData", {})

                # Get company info
                company_name = price_data.get("shortName", ticker)
                market_cap = price_data.get("marketCap", {}).get("raw", 0)
                currency = price_data.get("currency", "USD")

                # Get price metrics
                current_price = price_data.get("regularMarketPrice", {}).get("raw", 0)

                # Get multiples
                pe_ratio = summary_detail.get("trailingPE", {}).get("raw")
                forward_pe = summary_detail.get("forwardPE", {}).get("raw")
                peg_ratio = key_stats.get("pegRatio", {}).get("raw")
                price_to_book = key_stats.get("priceToBook", {}).get("raw")
                price_to_sales = key_stats.get("priceToSalesTrailing12Months", {}).get(
                    "raw"
                )
                enterprise_value = key_stats.get("enterpriseValue", {}).get("raw", 0)
                ev_to_revenue = key_stats.get("enterpriseToRevenue", {}).get("raw")
                ev_to_ebitda = key_stats.get("enterpriseToEbitda", {}).get("raw")

                # Get profitability metrics
                profit_margins = financial_data.get("profitMargins", {}).get("raw")
                operating_margins = financial_data.get("operatingMargins", {}).get("raw")
                gross_margins = financial_data.get("grossMargins", {}).get("raw")
                roe = financial_data.get("returnOnEquity", {}).get("raw")
                roa = financial_data.get("returnOnAssets", {}).get("raw")

                # Get growth metrics
                revenue_growth = financial_data.get("revenueGrowth", {}).get("raw")
                earnings_growth = financial_data.get("earningsGrowth", {}).get("raw")

                # Get balance sheet metrics
                total_debt = financial_data.get("totalDebt", {}).get("raw", 0)
                total_cash = financial_data.get("totalCash", {}).get("raw", 0)

                # Calculate EV/EBIT (if not available)
                ebit = financial_data.get("ebit", {}).get("raw")
                ev_to_ebit = None
                if ebit and ebit != 0 and enterprise_value:
                    ev_to_ebit = enterprise_value / ebit

                return {
                    "ticker": ticker,
                    "company_name": company_name,
                    "market_cap": market_cap,
                    "enterprise_value": enterprise_value,
                    "current_price": current_price,
                    "currency": currency,
                    # Valuation multiples
                    "pe_ratio": pe_ratio,
                    "forward_pe": forward_pe,
                    "peg_ratio": peg_ratio,
                    "price_to_book": price_to_book,
                    "price_to_sales": price_to_sales,
                    "ev_to_revenue": ev_to_revenue,
                    "ev_to_ebitda": ev_to_ebitda,
                    "ev_to_ebit": ev_to_ebit,
                    # Profitability
                    "gross_margin": gross_margins * 100 if gross_margins else None,
                    "operating_margin": operating_margins * 100
                    if operating_margins
                    else None,
                    "net_margin": profit_margins * 100 if profit_margins else None,
                    "roe": roe * 100 if roe else None,
                    "roa": roa * 100 if roa else None,
                    # Growth
                    "revenue_growth": revenue_growth * 100 if revenue_growth else None,
                    "earnings_growth": earnings_growth * 100
                    if earnings_growth
                    else None,
                }

        except Exception as e:
            print(f"Error fetching metrics for {ticker}: {e}")
            return None

    async def analyze_peer_group(
        self, target_ticker: str, peer_tickers: List[str]
    ) -> Dict:
        """
        Perform comparable company analysis for a peer group

        Args:
            target_ticker: The target company ticker
            peer_tickers: List of peer company tickers

        Returns:
            Dictionary with comparable analysis results
        """
        # Fetch metrics for target and all peers
        all_tickers = [target_ticker] + peer_tickers
        company_metrics = []

        for ticker in all_tickers:
            metrics = await self.fetch_company_metrics(ticker)
            if metrics:
                company_metrics.append(metrics)

        if not company_metrics:
            return {"error": "Unable to fetch company metrics"}

        # Separate target from peers
        target_metrics = next(
            (m for m in company_metrics if m["ticker"] == target_ticker), None
        )
        peer_metrics = [m for m in company_metrics if m["ticker"] != target_ticker]

        # Calculate statistics for each multiple
        multiples_stats = self._calculate_multiples_statistics(peer_metrics)

        # Calculate implied values for target based on peer multiples
        implied_values = self._calculate_implied_values(
            target_metrics, multiples_stats
        )

        return {
            "target": target_metrics,
            "peers": peer_metrics,
            "peer_statistics": multiples_stats,
            "implied_valuations": implied_values,
        }

    def _calculate_multiples_statistics(
        self, peer_metrics: List[Dict]
    ) -> Dict[str, Dict]:
        """
        Calculate median, mean, min, max for each multiple across peers

        Args:
            peer_metrics: List of peer company metrics

        Returns:
            Dictionary with statistics for each multiple
        """
        multiples_to_analyze = [
            "pe_ratio",
            "forward_pe",
            "peg_ratio",
            "price_to_book",
            "price_to_sales",
            "ev_to_revenue",
            "ev_to_ebitda",
            "ev_to_ebit",
            "gross_margin",
            "operating_margin",
            "net_margin",
            "roe",
            "roa",
            "revenue_growth",
            "earnings_growth",
        ]

        stats = {}
        for multiple in multiples_to_analyze:
            values = [
                peer[multiple]
                for peer in peer_metrics
                if peer.get(multiple) is not None
            ]
            if values:
                stats[multiple] = {
                    "median": statistics.median(values),
                    "mean": statistics.mean(values),
                    "min": min(values),
                    "max": max(values),
                    "count": len(values),
                }
            else:
                stats[multiple] = {
                    "median": None,
                    "mean": None,
                    "min": None,
                    "max": None,
                    "count": 0,
                }

        return stats

    def _calculate_implied_values(
        self, target_metrics: Dict, peer_stats: Dict
    ) -> Dict:
        """
        Calculate implied equity values for target based on peer multiples

        Args:
            target_metrics: Target company metrics
            peer_stats: Peer statistics

        Returns:
            Dictionary with implied values
        """
        # This is simplified - in reality, you'd need more fundamental data
        # For demonstration, we'll show how multiples compare

        implied = {}

        # Calculate premium/discount for each multiple
        multiples_to_check = [
            "pe_ratio",
            "forward_pe",
            "price_to_book",
            "price_to_sales",
            "ev_to_ebitda",
        ]

        for multiple in multiples_to_check:
            target_value = target_metrics.get(multiple)
            peer_median = peer_stats.get(multiple, {}).get("median")

            if target_value and peer_median:
                premium_discount = ((target_value - peer_median) / peer_median) * 100
                implied[f"{multiple}_premium_discount"] = round(premium_discount, 2)
            else:
                implied[f"{multiple}_premium_discount"] = None

        return implied

    def calculate_company_score(self, metrics: Dict) -> float:
        """
        Calculate an overall score for a company based on various metrics
        Higher score = more attractive valuation

        Args:
            metrics: Company metrics

        Returns:
            Score from 0-100
        """
        score = 0
        factors = 0

        # Profitability scoring (higher is better)
        if metrics.get("roe"):
            roe = metrics["roe"]
            if roe > 20:
                score += 20
            elif roe > 15:
                score += 15
            elif roe > 10:
                score += 10
            factors += 1

        if metrics.get("operating_margin"):
            margin = metrics["operating_margin"]
            if margin > 20:
                score += 20
            elif margin > 15:
                score += 15
            elif margin > 10:
                score += 10
            factors += 1

        # Growth scoring (higher is better)
        if metrics.get("revenue_growth"):
            growth = metrics["revenue_growth"]
            if growth > 20:
                score += 20
            elif growth > 10:
                score += 15
            elif growth > 5:
                score += 10
            factors += 1

        # Valuation scoring (lower multiples get higher scores for value)
        if metrics.get("pe_ratio"):
            pe = metrics["pe_ratio"]
            if pe < 15:
                score += 20
            elif pe < 25:
                score += 15
            elif pe < 35:
                score += 10
            factors += 1

        # Normalize to 0-100 scale
        if factors > 0:
            return round((score / (factors * 20)) * 100, 2)
        return 0
