// Core types for OpenEquity Platform

export interface Company {
  ticker: string;
  name: string;
  sector?: string;
  industry?: string;
  marketCap?: number;
  employees?: number;
  foundedYear?: number;
  headquarters?: string;
  website?: string;
  description?: string;
  sicCode?: string;
  cik?: string;
  exchange?: string;
}

export interface FinancialStatement {
  id: string;
  ticker: string;
  statementType: 'income' | 'balance' | 'cashflow';
  periodType: 'annual' | 'quarterly';
  periodEnd: string;
  data: Record<string, any>;
  source?: string;
  createdAt: string;
}

export interface Price {
  ticker: string;
  price: number;
  change: number;
  changePercent: number;
  volume: number;
  timestamp: string;
}

export interface User {
  id: string;
  email: string;
  name: string;
  role: 'user' | 'admin';
  createdAt: string;
}

export interface Model {
  id: string;
  name: string;
  description?: string;
  ticker?: string;
  type: 'dcf' | 'comp' | 'precedent' | 'ddm' | 'custom';
  data: Record<string, any>;
  createdBy: string;
  updatedAt: string;
  isPublic: boolean;
}
