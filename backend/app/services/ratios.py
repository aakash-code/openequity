"""
Financial ratios calculator for comprehensive equity analysis
Supports both US GAAP and Indian Accounting Standards
"""
from typing import Dict, Optional, List
from decimal import Decimal


class FinancialRatiosCalculator:
    """Calculate 30+ key financial ratios for equity research"""

    def calculate_all_ratios(
        self,
        income_statement: Dict,
        balance_sheet: Dict,
        cashflow_statement: Dict,
        market_data: Optional[Dict] = None,
    ) -> Dict[str, any]:
        """
        Calculate all financial ratios

        Args:
            income_statement: Income statement data
            balance_sheet: Balance sheet data
            cashflow_statement: Cash flow statement data
            market_data: Optional market data (price, shares outstanding)

        Returns:
            Dictionary of calculated ratios by category
        """
        ratios = {
            "profitability": self.calculate_profitability_ratios(
                income_statement, balance_sheet
            ),
            "liquidity": self.calculate_liquidity_ratios(balance_sheet),
            "leverage": self.calculate_leverage_ratios(income_statement, balance_sheet),
            "efficiency": self.calculate_efficiency_ratios(
                income_statement, balance_sheet
            ),
            "valuation": self.calculate_valuation_ratios(
                income_statement, balance_sheet, market_data
            ) if market_data else {},
            "cashflow": self.calculate_cashflow_ratios(
                income_statement, balance_sheet, cashflow_statement
            ),
        }

        return ratios

    # ========== PROFITABILITY RATIOS ==========

    def calculate_profitability_ratios(
        self, income: Dict, balance: Dict
    ) -> Dict[str, float]:
        """Calculate profitability ratios"""
        ratios = {}

        revenue = income.get("total_revenue", 0) or 0
        gross_profit = income.get("gross_profit", 0) or 0
        operating_income = income.get("operating_income", 0) or 0
        net_income = income.get("net_income", 0) or 0
        total_assets = balance.get("total_assets", 0) or 0
        total_equity = balance.get("total_stockholder_equity", 0) or 0

        # Gross Profit Margin
        if revenue:
            ratios["gross_profit_margin"] = round((gross_profit / revenue) * 100, 2)

        # Operating Profit Margin
        if revenue:
            ratios["operating_profit_margin"] = round(
                (operating_income / revenue) * 100, 2
            )

        # Net Profit Margin
        if revenue:
            ratios["net_profit_margin"] = round((net_income / revenue) * 100, 2)

        # Return on Assets (ROA)
        if total_assets:
            ratios["roa"] = round((net_income / total_assets) * 100, 2)

        # Return on Equity (ROE)
        if total_equity:
            ratios["roe"] = round((net_income / total_equity) * 100, 2)

        # EBIT Margin
        ebit = income.get("ebit", 0) or operating_income
        if revenue and ebit:
            ratios["ebit_margin"] = round((ebit / revenue) * 100, 2)

        return ratios

    # ========== LIQUIDITY RATIOS ==========

    def calculate_liquidity_ratios(self, balance: Dict) -> Dict[str, float]:
        """Calculate liquidity ratios"""
        ratios = {}

        current_assets = balance.get("current_assets", 0) or 0
        current_liabilities = balance.get("current_liabilities", 0) or 0
        cash = balance.get("cash", 0) or 0
        inventory = balance.get("inventory", 0) or 0
        receivables = balance.get("net_receivables", 0) or 0

        # Current Ratio
        if current_liabilities:
            ratios["current_ratio"] = round(current_assets / current_liabilities, 2)

        # Quick Ratio (Acid Test)
        if current_liabilities:
            quick_assets = current_assets - inventory
            ratios["quick_ratio"] = round(quick_assets / current_liabilities, 2)

        # Cash Ratio
        if current_liabilities:
            ratios["cash_ratio"] = round(cash / current_liabilities, 2)

        # Working Capital
        ratios["working_capital"] = current_assets - current_liabilities

        return ratios

    # ========== LEVERAGE RATIOS ==========

    def calculate_leverage_ratios(
        self, income: Dict, balance: Dict
    ) -> Dict[str, float]:
        """Calculate leverage/solvency ratios"""
        ratios = {}

        total_assets = balance.get("total_assets", 0) or 0
        total_liabilities = balance.get("total_liabilities", 0) or 0
        total_equity = balance.get("total_stockholder_equity", 0) or 0
        long_term_debt = balance.get("long_term_debt", 0) or 0
        short_term_debt = balance.get("short_term_debt", 0) or 0
        total_debt = long_term_debt + short_term_debt
        ebit = income.get("ebit", 0) or income.get("operating_income", 0) or 0
        interest_expense = abs(income.get("interest_expense", 0) or 0)

        # Debt-to-Equity Ratio
        if total_equity:
            ratios["debt_to_equity"] = round(total_debt / total_equity, 2)

        # Debt-to-Assets Ratio
        if total_assets:
            ratios["debt_to_assets"] = round(total_debt / total_assets, 2)

        # Equity Ratio
        if total_assets:
            ratios["equity_ratio"] = round((total_equity / total_assets) * 100, 2)

        # Interest Coverage Ratio
        if interest_expense:
            ratios["interest_coverage"] = round(ebit / interest_expense, 2)

        # Debt Service Coverage Ratio
        operating_income = income.get("operating_income", 0) or 0
        if interest_expense:
            ratios["debt_service_coverage"] = round(
                operating_income / interest_expense, 2
            )

        return ratios

    # ========== EFFICIENCY RATIOS ==========

    def calculate_efficiency_ratios(
        self, income: Dict, balance: Dict
    ) -> Dict[str, float]:
        """Calculate efficiency/activity ratios"""
        ratios = {}

        revenue = income.get("total_revenue", 0) or 0
        cogs = income.get("cost_of_revenue", 0) or 0
        total_assets = balance.get("total_assets", 0) or 0
        inventory = balance.get("inventory", 0) or 0
        receivables = balance.get("net_receivables", 0) or 0

        # Asset Turnover
        if total_assets:
            ratios["asset_turnover"] = round(revenue / total_assets, 2)

        # Inventory Turnover
        if inventory:
            ratios["inventory_turnover"] = round(cogs / inventory, 2)
            # Days Inventory Outstanding
            ratios["days_inventory_outstanding"] = round(365 / ratios["inventory_turnover"], 0)

        # Receivables Turnover
        if receivables:
            ratios["receivables_turnover"] = round(revenue / receivables, 2)
            # Days Sales Outstanding
            ratios["days_sales_outstanding"] = round(
                365 / ratios["receivables_turnover"], 0
            )

        return ratios

    # ========== VALUATION RATIOS ==========

    def calculate_valuation_ratios(
        self, income: Dict, balance: Dict, market: Optional[Dict]
    ) -> Dict[str, float]:
        """Calculate valuation ratios (requires market data)"""
        ratios = {}

        if not market:
            return ratios

        market_cap = market.get("market_cap", 0) or 0
        shares_outstanding = market.get("shares_outstanding", 0) or 0
        stock_price = market.get("stock_price", 0) or 0

        net_income = income.get("net_income", 0) or 0
        revenue = income.get("total_revenue", 0) or 0
        total_equity = balance.get("total_stockholder_equity", 0) or 0
        total_assets = balance.get("total_assets", 0) or 0
        total_liabilities = balance.get("total_liabilities", 0) or 0

        # Earnings Per Share (EPS)
        if shares_outstanding:
            eps = net_income / shares_outstanding
            ratios["eps"] = round(eps, 2)

            # Price-to-Earnings (P/E) Ratio
            if eps and stock_price:
                ratios["pe_ratio"] = round(stock_price / eps, 2)

        # Price-to-Book (P/B) Ratio
        if shares_outstanding and total_equity:
            book_value_per_share = total_equity / shares_outstanding
            if book_value_per_share and stock_price:
                ratios["pb_ratio"] = round(stock_price / book_value_per_share, 2)

        # Price-to-Sales (P/S) Ratio
        if market_cap and revenue:
            ratios["ps_ratio"] = round(market_cap / revenue, 2)

        # Enterprise Value (EV)
        long_term_debt = balance.get("long_term_debt", 0) or 0
        short_term_debt = balance.get("short_term_debt", 0) or 0
        cash = balance.get("cash", 0) or 0
        total_debt = long_term_debt + short_term_debt

        ev = market_cap + total_debt - cash
        ratios["enterprise_value"] = ev

        # EV/EBITDA
        ebit = income.get("ebit", 0) or income.get("operating_income", 0) or 0
        if ebit and ev:
            # Assuming EBITDA ≈ EBIT for simplification (need D&A from cash flow)
            ratios["ev_ebitda"] = round(ev / ebit, 2)

        return ratios

    # ========== CASH FLOW RATIOS ==========

    def calculate_cashflow_ratios(
        self, income: Dict, balance: Dict, cashflow: Dict
    ) -> Dict[str, float]:
        """Calculate cash flow ratios"""
        ratios = {}

        operating_cf = cashflow.get("operating_cashflow", 0) or 0
        free_cf = cashflow.get("free_cash_flow", 0) or 0
        capex = abs(cashflow.get("capital_expenditures", 0) or 0)
        net_income = income.get("net_income", 0) or 0
        total_debt = (balance.get("long_term_debt", 0) or 0) + (
            balance.get("short_term_debt", 0) or 0
        )

        # Operating Cash Flow Ratio
        current_liabilities = balance.get("current_liabilities", 0) or 0
        if current_liabilities:
            ratios["operating_cf_ratio"] = round(
                operating_cf / current_liabilities, 2
            )

        # Free Cash Flow to Equity
        ratios["free_cash_flow"] = free_cf

        # Cash Flow Margin
        revenue = income.get("total_revenue", 0) or 0
        if revenue:
            ratios["cf_margin"] = round((operating_cf / revenue) * 100, 2)

        # Operating Cash Flow to Net Income
        if net_income:
            ratios["cf_to_ni_ratio"] = round(operating_cf / net_income, 2)

        return ratios

    # ========== DUPONT ANALYSIS ==========

    def calculate_dupont_analysis(
        self, income: Dict, balance: Dict
    ) -> Dict[str, float]:
        """
        DuPont Analysis: ROE = Net Margin × Asset Turnover × Equity Multiplier
        """
        revenue = income.get("total_revenue", 0) or 0
        net_income = income.get("net_income", 0) or 0
        total_assets = balance.get("total_assets", 0) or 0
        total_equity = balance.get("total_stockholder_equity", 0) or 0

        dupont = {}

        # Net Profit Margin
        if revenue:
            dupont["net_margin"] = round((net_income / revenue) * 100, 2)

        # Asset Turnover
        if total_assets:
            dupont["asset_turnover"] = round(revenue / total_assets, 2)

        # Equity Multiplier
        if total_equity:
            dupont["equity_multiplier"] = round(total_assets / total_equity, 2)

        # ROE (DuPont)
        if revenue and total_assets and total_equity:
            roe_dupont = (net_income / revenue) * (revenue / total_assets) * (
                total_assets / total_equity
            )
            dupont["roe_dupont"] = round(roe_dupont * 100, 2)

        return dupont
