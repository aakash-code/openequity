"""
Financial data service for fetching company financials from multiple sources
Supports US (SEC EDGAR) and Indian (NSE/BSE) markets
"""
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import httpx
from sqlalchemy.orm import Session

from app.models.company import Company
from app.models.financial_statement import FinancialStatement, StatementType, PeriodType


class FinancialDataService:
    """Service for fetching and storing financial data from multiple sources"""

    def __init__(self, db: Session):
        self.db = db

    async def fetch_financials(
        self, ticker: str, market: str = "US"
    ) -> Dict[str, Any]:
        """
        Fetch financial data for a company

        Args:
            ticker: Company ticker symbol
            market: Market (US, NSE, BSE)

        Returns:
            Dictionary containing financial statements
        """
        if market == "US":
            return await self._fetch_us_financials(ticker)
        elif market in ["NSE", "BSE"]:
            return await self._fetch_indian_financials(ticker, market)
        else:
            raise ValueError(f"Unsupported market: {market}")

    async def _fetch_us_financials(self, ticker: str) -> Dict[str, Any]:
        """Fetch US company financials from SEC EDGAR / Yahoo Finance"""
        # For MVP, we'll use Yahoo Finance as it's more accessible
        # Production version should integrate SEC EDGAR XBRL parser
        try:
            async with httpx.AsyncClient() as client:
                # Yahoo Finance endpoint for financial data
                url = f"https://query2.finance.yahoo.com/v10/finance/quoteSummary/{ticker}"
                params = {
                    "modules": "incomeStatementHistory,balanceSheetHistory,cashflowStatementHistory"
                }

                response = await client.get(url, params=params, timeout=10.0)
                response.raise_for_status()

                data = response.json()
                return self._parse_yahoo_finance_data(ticker, data)

        except Exception as e:
            print(f"Error fetching US financials for {ticker}: {e}")
            return {}

    async def _fetch_indian_financials(
        self, ticker: str, market: str
    ) -> Dict[str, Any]:
        """Fetch Indian company financials from NSE/BSE"""
        # For MVP, we'll create sample data structure
        # Production version should integrate with NSE/BSE APIs or screener.in
        try:
            # NSE symbol format: RELIANCE.NS
            # BSE symbol format: RELIANCE.BO
            symbol_suffix = ".NS" if market == "NSE" else ".BO"
            yahoo_symbol = f"{ticker}{symbol_suffix}"

            async with httpx.AsyncClient() as client:
                url = f"https://query2.finance.yahoo.com/v10/finance/quoteSummary/{yahoo_symbol}"
                params = {
                    "modules": "incomeStatementHistory,balanceSheetHistory,cashflowStatementHistory"
                }

                response = await client.get(url, params=params, timeout=10.0)
                response.raise_for_status()

                data = response.json()
                return self._parse_yahoo_finance_data(ticker, data, market)

        except Exception as e:
            print(f"Error fetching Indian financials for {ticker}: {e}")
            return {}

    def _parse_yahoo_finance_data(
        self, ticker: str, data: Dict, market: str = "US"
    ) -> Dict[str, Any]:
        """Parse Yahoo Finance API response"""
        try:
            quote_summary = data.get("quoteSummary", {})
            result = quote_summary.get("result", [{}])[0]

            parsed_data = {
                "ticker": ticker,
                "market": market,
                "income_statements": [],
                "balance_sheets": [],
                "cashflow_statements": [],
            }

            # Parse income statements
            income_history = result.get("incomeStatementHistory", {}).get(
                "incomeStatementHistory", []
            )
            for statement in income_history:
                parsed_data["income_statements"].append(
                    self._parse_income_statement(statement)
                )

            # Parse balance sheets
            balance_history = result.get("balanceSheetHistory", {}).get(
                "balanceSheetStatements", []
            )
            for statement in balance_history:
                parsed_data["balance_sheets"].append(
                    self._parse_balance_sheet(statement)
                )

            # Parse cash flow statements
            cashflow_history = result.get("cashflowStatementHistory", {}).get(
                "cashflowStatements", []
            )
            for statement in cashflow_history:
                parsed_data["cashflow_statements"].append(
                    self._parse_cashflow_statement(statement)
                )

            return parsed_data

        except Exception as e:
            print(f"Error parsing Yahoo Finance data: {e}")
            return {}

    def _parse_income_statement(self, statement: Dict) -> Dict:
        """Parse income statement from Yahoo Finance"""
        return {
            "period_end": statement.get("endDate", {}).get("fmt", ""),
            "total_revenue": statement.get("totalRevenue", {}).get("raw", 0),
            "cost_of_revenue": statement.get("costOfRevenue", {}).get("raw", 0),
            "gross_profit": statement.get("grossProfit", {}).get("raw", 0),
            "operating_expenses": statement.get("totalOperatingExpenses", {}).get(
                "raw", 0
            ),
            "operating_income": statement.get("operatingIncome", {}).get("raw", 0),
            "ebit": statement.get("ebit", {}).get("raw", 0),
            "interest_expense": statement.get("interestExpense", {}).get("raw", 0),
            "income_before_tax": statement.get("incomeBeforeTax", {}).get("raw", 0),
            "income_tax_expense": statement.get("incomeTaxExpense", {}).get("raw", 0),
            "net_income": statement.get("netIncome", {}).get("raw", 0),
            "research_development": statement.get("researchDevelopment", {}).get(
                "raw", 0
            ),
            "selling_general_administrative": statement.get(
                "sellingGeneralAdministrative", {}
            ).get("raw", 0),
        }

    def _parse_balance_sheet(self, statement: Dict) -> Dict:
        """Parse balance sheet from Yahoo Finance"""
        return {
            "period_end": statement.get("endDate", {}).get("fmt", ""),
            "total_assets": statement.get("totalAssets", {}).get("raw", 0),
            "current_assets": statement.get("totalCurrentAssets", {}).get("raw", 0),
            "cash": statement.get("cash", {}).get("raw", 0),
            "short_term_investments": statement.get("shortTermInvestments", {}).get(
                "raw", 0
            ),
            "net_receivables": statement.get("netReceivables", {}).get("raw", 0),
            "inventory": statement.get("inventory", {}).get("raw", 0),
            "total_liabilities": statement.get("totalLiab", {}).get("raw", 0),
            "current_liabilities": statement.get("totalCurrentLiabilities", {}).get(
                "raw", 0
            ),
            "long_term_debt": statement.get("longTermDebt", {}).get("raw", 0),
            "short_term_debt": statement.get("shortLongTermDebt", {}).get("raw", 0),
            "total_stockholder_equity": statement.get("totalStockholderEquity", {}).get(
                "raw", 0
            ),
            "retained_earnings": statement.get("retainedEarnings", {}).get("raw", 0),
            "common_stock": statement.get("commonStock", {}).get("raw", 0),
        }

    def _parse_cashflow_statement(self, statement: Dict) -> Dict:
        """Parse cash flow statement from Yahoo Finance"""
        return {
            "period_end": statement.get("endDate", {}).get("fmt", ""),
            "operating_cashflow": statement.get("totalCashFromOperatingActivities", {}).get(
                "raw", 0
            ),
            "investing_cashflow": statement.get("totalCashflowsFromInvestingActivities", {}).get(
                "raw", 0
            ),
            "financing_cashflow": statement.get("totalCashFromFinancingActivities", {}).get(
                "raw", 0
            ),
            "capital_expenditures": statement.get("capitalExpenditures", {}).get(
                "raw", 0
            ),
            "free_cash_flow": statement.get("freeCashFlow", {}).get("raw", 0),
            "dividends_paid": statement.get("dividendsPaid", {}).get("raw", 0),
            "change_in_cash": statement.get("changeInCash", {}).get("raw", 0),
        }

    async def store_financials(
        self, ticker: str, financial_data: Dict[str, Any]
    ) -> bool:
        """Store financial data in database"""
        try:
            company = self.db.query(Company).filter(Company.ticker == ticker).first()
            if not company:
                return False

            # Store income statements
            for statement in financial_data.get("income_statements", []):
                self._store_statement(
                    ticker, StatementType.INCOME, statement, PeriodType.ANNUAL
                )

            # Store balance sheets
            for statement in financial_data.get("balance_sheets", []):
                self._store_statement(
                    ticker, StatementType.BALANCE, statement, PeriodType.ANNUAL
                )

            # Store cash flow statements
            for statement in financial_data.get("cashflow_statements", []):
                self._store_statement(
                    ticker, StatementType.CASHFLOW, statement, PeriodType.ANNUAL
                )

            self.db.commit()
            return True

        except Exception as e:
            print(f"Error storing financials: {e}")
            self.db.rollback()
            return False

    def _store_statement(
        self,
        ticker: str,
        statement_type: StatementType,
        data: Dict,
        period_type: PeriodType,
    ):
        """Store individual financial statement"""
        period_end = data.get("period_end", "")
        if not period_end:
            return

        # Convert period_end to date
        try:
            period_date = datetime.strptime(period_end, "%Y-%m-%d").date()
        except:
            return

        # Check if statement already exists
        existing = (
            self.db.query(FinancialStatement)
            .filter(
                FinancialStatement.ticker == ticker,
                FinancialStatement.statement_type == statement_type,
                FinancialStatement.period_end == period_date,
            )
            .first()
        )

        if existing:
            # Update existing statement
            existing.data = data
        else:
            # Create new statement
            statement = FinancialStatement(
                ticker=ticker,
                statement_type=statement_type,
                period_type=period_type,
                period_end=period_date,
                fiscal_year=period_date.year,
                data=data,
                source="Yahoo Finance",
            )
            self.db.add(statement)
