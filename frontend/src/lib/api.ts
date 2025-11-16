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
}

export const api = new APIClient();
