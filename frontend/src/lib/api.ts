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
}

export const api = new APIClient();
