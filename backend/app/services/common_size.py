"""
Common-Size Statement Calculator
Converts financial statements to common-size format for better comparison
"""
from typing import Dict, List, Any


class CommonSizeCalculator:
    """
    Calculates common-size financial statements
    - Income Statement: Each item as % of Total Revenue
    - Balance Sheet: Each item as % of Total Assets
    - Cash Flow: Each item as % of Operating Cash Flow
    """

    def calculate_common_size_income(self, income_statement: Dict[str, Any]) -> Dict[str, float]:
        """
        Calculate common-size income statement
        All items expressed as % of total revenue

        Args:
            income_statement: Raw income statement data

        Returns:
            Dictionary with common-size percentages
        """
        total_revenue = income_statement.get('total_revenue', 0) or income_statement.get('revenue', 0)

        if not total_revenue or total_revenue == 0:
            return {}

        common_size = {}

        # Revenue items
        common_size['total_revenue'] = 100.0

        # Cost and expenses
        if income_statement.get('cost_of_revenue'):
            common_size['cost_of_revenue'] = (income_statement['cost_of_revenue'] / total_revenue) * 100

        if income_statement.get('gross_profit'):
            common_size['gross_profit'] = (income_statement['gross_profit'] / total_revenue) * 100

        if income_statement.get('operating_expenses'):
            common_size['operating_expenses'] = (income_statement['operating_expenses'] / total_revenue) * 100

        if income_statement.get('research_development'):
            common_size['research_development'] = (income_statement['research_development'] / total_revenue) * 100

        if income_statement.get('selling_general_administrative'):
            common_size['selling_general_administrative'] = (income_statement['selling_general_administrative'] / total_revenue) * 100

        if income_statement.get('operating_income'):
            common_size['operating_income'] = (income_statement['operating_income'] / total_revenue) * 100

        # Other income/expenses
        if income_statement.get('interest_expense'):
            common_size['interest_expense'] = (income_statement['interest_expense'] / total_revenue) * 100

        if income_statement.get('interest_income'):
            common_size['interest_income'] = (income_statement['interest_income'] / total_revenue) * 100

        if income_statement.get('other_income_expense'):
            common_size['other_income_expense'] = (income_statement['other_income_expense'] / total_revenue) * 100

        # Pre-tax and net income
        if income_statement.get('income_before_tax'):
            common_size['income_before_tax'] = (income_statement['income_before_tax'] / total_revenue) * 100

        if income_statement.get('income_tax_expense'):
            common_size['income_tax_expense'] = (income_statement['income_tax_expense'] / total_revenue) * 100

        if income_statement.get('net_income'):
            common_size['net_income'] = (income_statement['net_income'] / total_revenue) * 100

        if income_statement.get('ebitda'):
            common_size['ebitda'] = (income_statement['ebitda'] / total_revenue) * 100

        return common_size

    def calculate_common_size_balance(self, balance_sheet: Dict[str, Any]) -> Dict[str, float]:
        """
        Calculate common-size balance sheet
        All items expressed as % of total assets

        Args:
            balance_sheet: Raw balance sheet data

        Returns:
            Dictionary with common-size percentages
        """
        total_assets = balance_sheet.get('total_assets', 0)

        if not total_assets or total_assets == 0:
            return {}

        common_size = {}

        # Assets
        common_size['total_assets'] = 100.0

        # Current assets
        if balance_sheet.get('total_current_assets'):
            common_size['total_current_assets'] = (balance_sheet['total_current_assets'] / total_assets) * 100

        if balance_sheet.get('cash'):
            common_size['cash'] = (balance_sheet['cash'] / total_assets) * 100

        if balance_sheet.get('cash_and_cash_equivalents'):
            common_size['cash_and_cash_equivalents'] = (balance_sheet['cash_and_cash_equivalents'] / total_assets) * 100

        if balance_sheet.get('short_term_investments'):
            common_size['short_term_investments'] = (balance_sheet['short_term_investments'] / total_assets) * 100

        if balance_sheet.get('accounts_receivable'):
            common_size['accounts_receivable'] = (balance_sheet['accounts_receivable'] / total_assets) * 100

        if balance_sheet.get('inventory'):
            common_size['inventory'] = (balance_sheet['inventory'] / total_assets) * 100

        # Non-current assets
        if balance_sheet.get('property_plant_equipment'):
            common_size['property_plant_equipment'] = (balance_sheet['property_plant_equipment'] / total_assets) * 100

        if balance_sheet.get('intangible_assets'):
            common_size['intangible_assets'] = (balance_sheet['intangible_assets'] / total_assets) * 100

        if balance_sheet.get('goodwill'):
            common_size['goodwill'] = (balance_sheet['goodwill'] / total_assets) * 100

        # Liabilities
        if balance_sheet.get('total_liabilities'):
            common_size['total_liabilities'] = (balance_sheet['total_liabilities'] / total_assets) * 100

        if balance_sheet.get('total_current_liabilities'):
            common_size['total_current_liabilities'] = (balance_sheet['total_current_liabilities'] / total_assets) * 100

        if balance_sheet.get('accounts_payable'):
            common_size['accounts_payable'] = (balance_sheet['accounts_payable'] / total_assets) * 100

        if balance_sheet.get('short_term_debt'):
            common_size['short_term_debt'] = (balance_sheet['short_term_debt'] / total_assets) * 100

        if balance_sheet.get('long_term_debt'):
            common_size['long_term_debt'] = (balance_sheet['long_term_debt'] / total_assets) * 100

        # Equity
        if balance_sheet.get('total_stockholder_equity'):
            common_size['total_stockholder_equity'] = (balance_sheet['total_stockholder_equity'] / total_assets) * 100

        if balance_sheet.get('retained_earnings'):
            common_size['retained_earnings'] = (balance_sheet['retained_earnings'] / total_assets) * 100

        return common_size

    def calculate_common_size_cashflow(self, cashflow_statement: Dict[str, Any]) -> Dict[str, float]:
        """
        Calculate common-size cash flow statement
        All items expressed as % of operating cash flow

        Args:
            cashflow_statement: Raw cash flow statement data

        Returns:
            Dictionary with common-size percentages
        """
        operating_cf = cashflow_statement.get('operating_cashflow', 0) or cashflow_statement.get('total_cash_from_operating_activities', 0)

        if not operating_cf or operating_cf == 0:
            return {}

        common_size = {}

        # Operating activities
        common_size['operating_cashflow'] = 100.0

        if cashflow_statement.get('depreciation'):
            common_size['depreciation'] = (cashflow_statement['depreciation'] / operating_cf) * 100

        if cashflow_statement.get('change_to_inventory'):
            common_size['change_to_inventory'] = (cashflow_statement['change_to_inventory'] / operating_cf) * 100

        if cashflow_statement.get('change_to_accounts_receivable'):
            common_size['change_to_accounts_receivable'] = (cashflow_statement['change_to_accounts_receivable'] / operating_cf) * 100

        # Investing activities
        if cashflow_statement.get('total_cashflows_from_investing_activities'):
            common_size['investing_activities'] = (cashflow_statement['total_cashflows_from_investing_activities'] / operating_cf) * 100

        if cashflow_statement.get('capital_expenditures'):
            common_size['capital_expenditures'] = (cashflow_statement['capital_expenditures'] / operating_cf) * 100

        # Financing activities
        if cashflow_statement.get('total_cash_from_financing_activities'):
            common_size['financing_activities'] = (cashflow_statement['total_cash_from_financing_activities'] / operating_cf) * 100

        if cashflow_statement.get('dividends_paid'):
            common_size['dividends_paid'] = (cashflow_statement['dividends_paid'] / operating_cf) * 100

        if cashflow_statement.get('issuance_of_stock'):
            common_size['issuance_of_stock'] = (cashflow_statement['issuance_of_stock'] / operating_cf) * 100

        if cashflow_statement.get('repurchase_of_stock'):
            common_size['repurchase_of_stock'] = (cashflow_statement['repurchase_of_stock'] / operating_cf) * 100

        # Free cash flow
        capex = cashflow_statement.get('capital_expenditures', 0) or 0
        free_cash_flow = operating_cf + capex  # capex is usually negative
        if operating_cf != 0:
            common_size['free_cash_flow'] = (free_cash_flow / operating_cf) * 100

        return common_size

    def calculate_multi_period_common_size(
        self, statements: List[Dict[str, Any]], statement_type: str
    ) -> List[Dict[str, Any]]:
        """
        Calculate common-size statements for multiple periods

        Args:
            statements: List of financial statements
            statement_type: Type of statement ('income', 'balance', 'cashflow')

        Returns:
            List of common-size statements with period information
        """
        results = []

        for statement in statements:
            if statement_type == 'income':
                common_size = self.calculate_common_size_income(statement.get('data', {}))
            elif statement_type == 'balance':
                common_size = self.calculate_common_size_balance(statement.get('data', {}))
            elif statement_type == 'cashflow':
                common_size = self.calculate_common_size_cashflow(statement.get('data', {}))
            else:
                continue

            if common_size:
                results.append({
                    'period_end': statement.get('period_end'),
                    'fiscal_year': statement.get('fiscal_year'),
                    'common_size': common_size
                })

        return results
