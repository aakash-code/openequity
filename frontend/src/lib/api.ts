/**
 * API client for OpenEquity backend
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export class APIError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'APIError';
  }
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
  full_name?: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface User {
  id: string;
  email: string;
  full_name?: string;
  role: string;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
}

export interface Company {
  ticker: string;
  name: string;
  sector?: string;
  industry?: string;
  market_cap?: number;
  exchange?: string;
  description?: string;
}

export interface FinancialStatement {
  id: string;
  ticker: string;
  statement_type: 'income' | 'balance' | 'cashflow';
  period_type: 'annual' | 'quarterly';
  period_end: string;
  fiscal_year: number;
  data: Record<string, any>;
  source?: string;
}

export interface FinancialRatios {
  ticker: string;
  period_end: string;
  ratios: {
    profitability: Record<string, number>;
    liquidity: Record<string, number>;
    leverage: Record<string, number>;
    efficiency: Record<string, number>;
    valuation?: Record<string, number>;
    cashflow: Record<string, number>;
    dupont?: Record<string, number>;
  };
}

export interface DCFAssumptions {
  risk_free_rate: number;
  equity_risk_premium: number;
  beta: number;
  cost_of_debt: number;
  tax_rate: number;
  debt_weight: number;
  equity_weight: number;
  projection_years: number;
  revenue_growth_rates: number[];
  ebitda_margin: number;
  depreciation_pct_revenue: number;
  capex_pct_revenue: number;
  nwc_pct_revenue: number;
  terminal_growth_rate?: number;
  terminal_ebitda_multiple?: number;
}

export interface CreateDCFRequest {
  ticker: string;
  name: string;
  description?: string;
  is_public?: boolean;
  base_revenue: number;
  net_debt: number;
  shares_outstanding: number;
  current_price?: number;
  assumptions: DCFAssumptions;
}

export interface DCFValuation {
  id: string;
  ticker: string;
  user_id: string;
  name: string;
  description?: string;
  is_public: boolean;
  risk_free_rate: number;
  equity_risk_premium: number;
  beta: number;
  cost_of_debt: number;
  tax_rate: number;
  debt_weight: number;
  equity_weight: number;
  wacc: number;
  projection_years: number;
  revenue_growth_rates: number[];
  ebitda_margin: number;
  depreciation_pct_revenue: number;
  capex_pct_revenue: number;
  nwc_pct_revenue: number;
  terminal_growth_rate?: number;
  terminal_ebitda_multiple?: number;
  enterprise_value: number;
  equity_value: number;
  shares_outstanding: number;
  value_per_share: number;
  current_price?: number;
  upside_downside?: number;
  projections: any;
  fcf_projections: number[];
  terminal_value: number;
  pv_terminal_value: number;
  pv_fcf: number;
  sensitivity_analysis?: any;
  created_at: string;
  updated_at?: string;
}

export interface PeerGroup {
  id: string;
  ticker: string;
  user_id: string;
  name: string;
  description?: string;
  peer_tickers: string[];
  is_public: boolean;
  analysis_results?: any;
  last_analyzed?: string;
  created_at: string;
  updated_at?: string;
}

export interface CreatePeerGroupRequest {
  ticker: string;
  name: string;
  description?: string;
  peer_tickers: string[];
  is_public?: boolean;
}

export interface CompanyMetrics {
  ticker: string;
  company_name: string;
  market_cap: number;
  enterprise_value: number;
  current_price: number;
  currency: string;
  pe_ratio?: number;
  forward_pe?: number;
  peg_ratio?: number;
  price_to_book?: number;
  price_to_sales?: number;
  ev_to_revenue?: number;
  ev_to_ebitda?: number;
  ev_to_ebit?: number;
  gross_margin?: number;
  operating_margin?: number;
  net_margin?: number;
  roe?: number;
  roa?: number;
  revenue_growth?: number;
  earnings_growth?: number;
}

export interface ComparableAnalysis {
  target: CompanyMetrics;
  peers: CompanyMetrics[];
  peer_statistics: Record<string, any>;
  implied_valuations: Record<string, any>;
}

class APIClient {
  private baseURL: string;

  constructor(baseURL: string = API_BASE_URL) {
    this.baseURL = baseURL;
  }

  private getAuthHeader(): Record<string, string> {
    const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
    return token ? { Authorization: `Bearer ${token}` } : {};
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;

    const headers = {
      'Content-Type': 'application/json',
      ...this.getAuthHeader(),
      ...options.headers,
    };

    const response = await fetch(url, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'An error occurred' }));
      throw new APIError(response.status, errorData.detail || response.statusText);
    }

    // Handle 204 No Content
    if (response.status === 204) {
      return {} as T;
    }

    return response.json();
  }

  // Authentication endpoints
  async register(data: RegisterData): Promise<User> {
    return this.request<User>('/api/v1/auth/register', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async login(credentials: LoginCredentials): Promise<TokenResponse> {
    return this.request<TokenResponse>('/api/v1/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials),
    });
  }

  async getCurrentUser(): Promise<User> {
    return this.request<User>('/api/v1/auth/me');
  }

  async logout(): Promise<void> {
    await this.request<void>('/api/v1/auth/logout', {
      method: 'POST',
    });
  }

  // Company endpoints
  async searchCompanies(query: string, limit: number = 10): Promise<Company[]> {
    const params = new URLSearchParams({
      q: query,
      limit: limit.toString(),
    });
    return this.request<Company[]>(`/api/v1/companies/search?${params}`);
  }

  async getCompanies(options?: {
    skip?: number;
    limit?: number;
    sector?: string;
    exchange?: string;
  }): Promise<Company[]> {
    const params = new URLSearchParams();
    if (options?.skip) params.append('skip', options.skip.toString());
    if (options?.limit) params.append('limit', options.limit.toString());
    if (options?.sector) params.append('sector', options.sector);
    if (options?.exchange) params.append('exchange', options.exchange);

    return this.request<Company[]>(`/api/v1/companies?${params}`);
  }

  async getCompany(ticker: string): Promise<Company> {
    return this.request<Company>(`/api/v1/companies/${ticker}`);
  }

  // Financial data endpoints
  async getFinancialStatements(
    ticker: string,
    statementType?: 'income' | 'balance' | 'cashflow',
    limit: number = 5
  ): Promise<FinancialStatement[]> {
    const params = new URLSearchParams({ limit: limit.toString() });
    if (statementType) params.append('statement_type', statementType);

    return this.request<FinancialStatement[]>(
      `/api/v1/financials/${ticker}/statements?${params}`
    );
  }

  async getFinancialRatios(ticker: string): Promise<FinancialRatios> {
    return this.request<FinancialRatios>(`/api/v1/financials/${ticker}/ratios`);
  }

  async refreshFinancialData(ticker: string): Promise<{ message: string; status: string }> {
    return this.request<{ message: string; status: string }>(
      `/api/v1/financials/${ticker}/refresh`,
      { method: 'POST' }
    );
  }

  // DCF Valuation endpoints
  async createDCFValuation(data: CreateDCFRequest): Promise<DCFValuation> {
    return this.request<DCFValuation>('/api/v1/valuations/dcf', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getDCFValuations(ticker?: string, skip: number = 0, limit: number = 20): Promise<{ valuations: DCFValuation[]; total: number }> {
    const params = new URLSearchParams({ skip: skip.toString(), limit: limit.toString() });
    if (ticker) params.append('ticker', ticker);
    return this.request<{ valuations: DCFValuation[]; total: number }>(`/api/v1/valuations/dcf?${params}`);
  }

  async getDCFValuation(valuationId: string): Promise<DCFValuation> {
    return this.request<DCFValuation>(`/api/v1/valuations/dcf/${valuationId}`);
  }

  async updateDCFValuation(valuationId: string, data: Partial<CreateDCFRequest>): Promise<DCFValuation> {
    return this.request<DCFValuation>(`/api/v1/valuations/dcf/${valuationId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteDCFValuation(valuationId: string): Promise<void> {
    return this.request<void>(`/api/v1/valuations/dcf/${valuationId}`, {
      method: 'DELETE',
    });
  }

  // Peer Group / Comps endpoints
  async createPeerGroup(data: CreatePeerGroupRequest): Promise<PeerGroup> {
    return this.request<PeerGroup>('/api/v1/valuations/comps/peer-groups', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getPeerGroups(ticker?: string, skip: number = 0, limit: number = 20): Promise<{ peer_groups: PeerGroup[]; total: number }> {
    const params = new URLSearchParams({ skip: skip.toString(), limit: limit.toString() });
    if (ticker) params.append('ticker', ticker);
    return this.request<{ peer_groups: PeerGroup[]; total: number }>(`/api/v1/valuations/comps/peer-groups?${params}`);
  }

  async getPeerGroup(groupId: string): Promise<PeerGroup> {
    return this.request<PeerGroup>(`/api/v1/valuations/comps/peer-groups/${groupId}`);
  }

  async updatePeerGroup(groupId: string, data: Partial<CreatePeerGroupRequest>): Promise<PeerGroup> {
    return this.request<PeerGroup>(`/api/v1/valuations/comps/peer-groups/${groupId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deletePeerGroup(groupId: string): Promise<void> {
    return this.request<void>(`/api/v1/valuations/comps/peer-groups/${groupId}`, {
      method: 'DELETE',
    });
  }

  async analyzePeerGroup(groupId: string): Promise<ComparableAnalysis> {
    return this.request<ComparableAnalysis>(`/api/v1/valuations/comps/analyze/${groupId}`, {
      method: 'POST',
    });
  }

  async quickCompsAnalysis(ticker: string, peerTickers: string[]): Promise<ComparableAnalysis> {
    const params = new URLSearchParams({
      peer_tickers: peerTickers.join(','),
    });
    return this.request<ComparableAnalysis>(`/api/v1/valuations/comps/analyze/ticker/${ticker}?${params}`);
  }

  // WACC Calculator
  async calculateWACC(data: {
    risk_free_rate: number;
    beta: number;
    equity_risk_premium: number;
    cost_of_debt: number;
    tax_rate: number;
    equity_weight: number;
    debt_weight: number;
  }): Promise<{ cost_of_equity: number; wacc: number }> {
    return this.request<{ cost_of_equity: number; wacc: number }>('/api/v1/valuations/wacc/calculate', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // Enhanced Analysis endpoints
  async getCommonSizeStatements(
    ticker: string,
    statementType: 'income' | 'balance' | 'cashflow',
    limit: number = 5
  ): Promise<any> {
    const params = new URLSearchParams({ limit: limit.toString() });
    return this.request<any>(`/api/v1/analysis/${ticker}/common-size/${statementType}?${params}`);
  }

  async getTrendAnalysis(ticker: string, limit: number = 10): Promise<any> {
    const params = new URLSearchParams({ limit: limit.toString() });
    return this.request<any>(`/api/v1/analysis/${ticker}/trends?${params}`);
  }

  async getRevenueTrend(ticker: string, limit: number = 10): Promise<any> {
    const params = new URLSearchParams({ limit: limit.toString() });
    return this.request<any>(`/api/v1/analysis/${ticker}/revenue-trend?${params}`);
  }

  async getProfitabilityTrend(ticker: string, limit: number = 10): Promise<any> {
    const params = new URLSearchParams({ limit: limit.toString() });
    return this.request<any>(`/api/v1/analysis/${ticker}/profitability-trend?${params}`);
  }

  async getBalanceSheetTrend(ticker: string, limit: number = 10): Promise<any> {
    const params = new URLSearchParams({ limit: limit.toString() });
    return this.request<any>(`/api/v1/analysis/${ticker}/balance-sheet-trend?${params}`);
  }

  async getCashflowTrend(ticker: string, limit: number = 10): Promise<any> {
    const params = new URLSearchParams({ limit: limit.toString() });
    return this.request<any>(`/api/v1/analysis/${ticker}/cashflow-trend?${params}`);
  }

  // Advanced Valuation endpoints
  async runMonteCarloSimulation(data: {
    base_revenue: number;
    base_revenue_growth: number;
    revenue_growth_volatility?: number;
    base_ebitda_margin: number;
    ebitda_margin_volatility?: number;
    projection_years?: number;
    base_wacc: number;
    wacc_volatility?: number;
    base_terminal_growth: number;
    terminal_growth_volatility?: number;
    capex_percent?: number;
    nwc_change_percent?: number;
    tax_rate?: number;
    shares_outstanding: number;
    num_simulations?: number;
    distribution?: string;
  }): Promise<any> {
    return this.request<any>('/api/v1/advanced-valuations/monte-carlo', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async calculateGordonGrowth(data: {
    current_dividend: number;
    growth_rate: number;
    required_return: number;
  }): Promise<any> {
    return this.request<any>('/api/v1/advanced-valuations/ddm/gordon-growth', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async calculateTwoStageDDM(data: {
    current_dividend: number;
    high_growth_rate: number;
    high_growth_years: number;
    stable_growth_rate: number;
    required_return: number;
  }): Promise<any> {
    return this.request<any>('/api/v1/advanced-valuations/ddm/two-stage', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async calculateThreeStageDDM(data: {
    current_dividend: number;
    high_growth_rate: number;
    high_growth_years: number;
    transition_growth_rate: number;
    transition_years: number;
    stable_growth_rate: number;
    required_return: number;
  }): Promise<any> {
    return this.request<any>('/api/v1/advanced-valuations/ddm/three-stage', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getEVAAnalysis(ticker: string, wacc: number, limit: number = 10): Promise<any> {
    const params = new URLSearchParams({
      wacc: wacc.toString(),
      limit: limit.toString()
    });
    return this.request<any>(`/api/v1/advanced-valuations/${ticker}/eva?${params}`);
  }

  async runScenarioAnalysis(data: {
    base_revenue: number;
    revenue_growth_rates: number[];
    ebitda_margin: number;
    tax_rate: number;
    capex_percent: number;
    nwc_change_percent: number;
    wacc: number;
    terminal_growth_rate: number;
    shares_outstanding: number;
    net_debt?: number;
  }): Promise<any> {
    return this.request<any>('/api/v1/advanced-valuations/scenario-analysis', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // Earnings Quality endpoints
  async getBeneishMScore(ticker: string): Promise<any> {
    return this.request<any>(`/api/v1/earnings-quality/${ticker}/beneish-mscore`);
  }

  async getAltmanZScore(
    ticker: string,
    marketCap?: number,
    companyType: string = 'public_manufacturing',
    limit: number = 5
  ): Promise<any> {
    const params = new URLSearchParams({
      company_type: companyType,
      limit: limit.toString()
    });
    if (marketCap) params.append('market_cap', marketCap.toString());
    return this.request<any>(`/api/v1/earnings-quality/${ticker}/altman-zscore?${params}`);
  }

  async getEarningsQuality(ticker: string, limit: number = 5): Promise<any> {
    const params = new URLSearchParams({ limit: limit.toString() });
    return this.request<any>(`/api/v1/earnings-quality/${ticker}/earnings-quality?${params}`);
  }

  async getQualityDashboard(
    ticker: string,
    marketCap?: number,
    companyType: string = 'public_manufacturing'
  ): Promise<any> {
    const params = new URLSearchParams({ company_type: companyType });
    if (marketCap) params.append('market_cap', marketCap.toString());
    return this.request<any>(`/api/v1/earnings-quality/${ticker}/quality-dashboard?${params}`);
  }

  // Portfolio endpoints
  async createPortfolio(data: {
    name: string;
    description?: string;
    currency?: string;
    strategy?: string;
    tags?: string[];
    is_public?: boolean;
  }): Promise<any> {
    return this.request<any>('/api/v1/portfolios/portfolios', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getPortfolios(skip: number = 0, limit: number = 20): Promise<any> {
    const params = new URLSearchParams({ skip: skip.toString(), limit: limit.toString() });
    return this.request<any>(`/api/v1/portfolios/portfolios?${params}`);
  }

  async getPortfolio(portfolioId: string): Promise<any> {
    return this.request<any>(`/api/v1/portfolios/portfolios/${portfolioId}`);
  }

  async updatePortfolio(portfolioId: string, data: {
    name?: string;
    description?: string;
    strategy?: string;
    tags?: string[];
    is_public?: boolean;
  }): Promise<any> {
    return this.request<any>(`/api/v1/portfolios/portfolios/${portfolioId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deletePortfolio(portfolioId: string): Promise<void> {
    return this.request<void>(`/api/v1/portfolios/portfolios/${portfolioId}`, {
      method: 'DELETE',
    });
  }

  async addTransaction(portfolioId: string, data: {
    ticker: string;
    transaction_type: 'buy' | 'sell' | 'dividend' | 'split';
    transaction_date: string;
    quantity: number;
    price: number;
    commission?: number;
    notes?: string;
  }): Promise<any> {
    return this.request<any>(`/api/v1/portfolios/portfolios/${portfolioId}/transactions`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getTransactions(portfolioId: string, skip: number = 0, limit: number = 100): Promise<any> {
    const params = new URLSearchParams({ skip: skip.toString(), limit: limit.toString() });
    return this.request<any>(`/api/v1/portfolios/portfolios/${portfolioId}/transactions?${params}`);
  }

  async deleteTransaction(portfolioId: string, transactionId: string): Promise<void> {
    return this.request<void>(`/api/v1/portfolios/portfolios/${portfolioId}/transactions/${transactionId}`, {
      method: 'DELETE',
    });
  }

  async getPortfolioAnalytics(portfolioId: string): Promise<any> {
    return this.request<any>(`/api/v1/portfolios/portfolios/${portfolioId}/analytics`);
  }

  async getPortfolioPerformance(portfolioId: string): Promise<any> {
    return this.request<any>(`/api/v1/portfolios/portfolios/${portfolioId}/performance`);
  }

  async getPortfolioRiskMetrics(portfolioId: string, benchmarkSymbol: string = 'SPY'): Promise<any> {
    return this.request<any>(`/api/v1/portfolios/portfolios/${portfolioId}/risk-metrics?benchmark_symbol=${benchmarkSymbol}`);
  }

  async getPortfolioBenchmarkComparison(portfolioId: string, benchmarkSymbol: string = 'SPY'): Promise<any> {
    return this.request<any>(`/api/v1/portfolios/portfolios/${portfolioId}/benchmark-comparison?benchmark_symbol=${benchmarkSymbol}`);
  }

  // Watchlist methods
  async createWatchlist(data: { name: string; description?: string; is_public?: boolean; tags?: string[] }): Promise<any> {
    return this.request<any>('/api/v1/watchlists/watchlists', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getWatchlists(skip: number = 0, limit: number = 20): Promise<any> {
    return this.request<any>(`/api/v1/watchlists/watchlists?skip=${skip}&limit=${limit}`);
  }

  async getWatchlist(watchlistId: string): Promise<any> {
    return this.request<any>(`/api/v1/watchlists/watchlists/${watchlistId}`);
  }

  async updateWatchlist(watchlistId: string, data: { name?: string; description?: string; tags?: string[]; is_public?: boolean }): Promise<any> {
    return this.request<any>(`/api/v1/watchlists/watchlists/${watchlistId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteWatchlist(watchlistId: string): Promise<void> {
    return this.request<void>(`/api/v1/watchlists/watchlists/${watchlistId}`, {
      method: 'DELETE',
    });
  }

  async addWatchlistItem(watchlistId: string, data: { ticker: string; notes?: string; target_price?: number }): Promise<any> {
    return this.request<any>(`/api/v1/watchlists/watchlists/${watchlistId}/items`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async removeWatchlistItem(watchlistId: string, itemId: string): Promise<void> {
    return this.request<void>(`/api/v1/watchlists/watchlists/${watchlistId}/items/${itemId}`, {
      method: 'DELETE',
    });
  }

  // Stock screening methods
  async getScreeningTemplates(): Promise<any> {
    return this.request<any>('/api/v1/screening/screening/templates');
  }

  async getScreeningTemplate(templateId: string): Promise<any> {
    return this.request<any>(`/api/v1/screening/screening/templates/${templateId}`);
  }

  async screenStocks(criteria: any): Promise<any> {
    return this.request<any>('/api/v1/screening/screening/screen', {
      method: 'POST',
      body: JSON.stringify(criteria),
    });
  }

  async screenByTemplate(templateId: string, additionalCriteria?: any): Promise<any> {
    return this.request<any>(`/api/v1/screening/screening/screen-by-template/${templateId}`, {
      method: 'POST',
      body: additionalCriteria ? JSON.stringify(additionalCriteria) : undefined,
    });
  }

  // Indian Market endpoints
  async getIndianIndices(): Promise<any> {
    return this.request<any>('/api/v1/indian-market/indices');
  }

  async getMarketStatus(): Promise<any> {
    return this.request<any>('/api/v1/indian-market/market-status');
  }

  async getCorporateActions(ticker: string, actionType?: string, days: number = 90): Promise<any> {
    const params = new URLSearchParams({ days: days.toString() });
    if (actionType) params.append('action_type', actionType);
    return this.request<any>(`/api/v1/indian-market/corporate-actions/${ticker}?${params}`);
  }

  async getPriceBands(ticker: string, currentPrice: number): Promise<any> {
    const params = new URLSearchParams({ current_price: currentPrice.toString() });
    return this.request<any>(`/api/v1/indian-market/price-bands/${ticker}?${params}`);
  }

  async getDeliveryPercentage(ticker: string, days: number = 30): Promise<any> {
    const params = new URLSearchParams({ days: days.toString() });
    return this.request<any>(`/api/v1/indian-market/delivery/${ticker}?${params}`);
  }

  async getFiiDiiActivity(days: number = 30): Promise<any> {
    const params = new URLSearchParams({ days: days.toString() });
    return this.request<any>(`/api/v1/indian-market/fii-dii?${params}`);
  }

  async getNseSectors(): Promise<any> {
    return this.request<any>('/api/v1/indian-market/sectors');
  }

  // SEBI Filings endpoints
  async getSebiFilingTypes(): Promise<any> {
    return this.request<any>('/api/v1/sebi/filing-types');
  }

  async getSebiFilings(ticker: string, filingType?: string, days: number = 90, limit: number = 50): Promise<any> {
    const params = new URLSearchParams({
      days: days.toString(),
      limit: limit.toString()
    });
    if (filingType) params.append('filing_type', filingType);
    return this.request<any>(`/api/v1/sebi/filings/${ticker}?${params}`);
  }

  async getShareholdingPattern(ticker: string, quarter?: string): Promise<any> {
    const params = quarter ? new URLSearchParams({ quarter }) : new URLSearchParams();
    return this.request<any>(`/api/v1/sebi/shareholding/${ticker}?${params}`);
  }

  async getBoardMeetings(ticker: string, daysAhead: number = 30, daysBack: number = 90): Promise<any> {
    const params = new URLSearchParams({
      days_ahead: daysAhead.toString(),
      days_back: daysBack.toString()
    });
    return this.request<any>(`/api/v1/sebi/board-meetings/${ticker}?${params}`);
  }

  async getInsiderTrading(ticker: string, days: number = 180, limit: number = 50): Promise<any> {
    const params = new URLSearchParams({
      days: days.toString(),
      limit: limit.toString()
    });
    return this.request<any>(`/api/v1/sebi/insider-trading/${ticker}?${params}`);
  }

  async getComplianceStatus(ticker: string): Promise<any> {
    return this.request<any>(`/api/v1/sebi/compliance/${ticker}`);
  }

  // Currency Conversion endpoints
  async getSupportedCurrencies(): Promise<any> {
    return this.request<any>('/api/v1/currency/supported');
  }

  async getExchangeRate(fromCurrency: string, toCurrency: string): Promise<any> {
    const params = new URLSearchParams({
      from_currency: fromCurrency,
      to_currency: toCurrency
    });
    return this.request<any>(`/api/v1/currency/rate?${params}`);
  }

  async convertCurrency(amount: number, fromCurrency: string, toCurrency: string): Promise<any> {
    return this.request<any>('/api/v1/currency/convert', {
      method: 'POST',
      body: JSON.stringify({
        amount,
        from_currency: fromCurrency,
        to_currency: toCurrency
      }),
    });
  }

  async convertMetrics(metrics: Record<string, number>, fromCurrency: string, toCurrency: string): Promise<any> {
    return this.request<any>('/api/v1/currency/convert-metrics', {
      method: 'POST',
      body: JSON.stringify({
        metrics,
        from_currency: fromCurrency,
        to_currency: toCurrency
      }),
    });
  }

  async getHistoricalRates(fromCurrency: string, toCurrency: string, days: number = 30): Promise<any> {
    const params = new URLSearchParams({
      from_currency: fromCurrency,
      to_currency: toCurrency,
      days: days.toString()
    });
    return this.request<any>(`/api/v1/currency/historical?${params}`);
  }
}

export const api = new APIClient();
