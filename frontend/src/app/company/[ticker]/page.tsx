'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth-context';
import { api, Company, FinancialStatement, FinancialRatios } from '@/lib/api';

interface PageProps {
  params: { ticker: string };
}

export default function CompanyDetailPage({ params }: PageProps) {
  const router = useRouter();
  const { isAuthenticated, loading: authLoading } = useAuth();
  const [company, setCompany] = useState<Company | null>(null);
  const [statements, setStatements] = useState<FinancialStatement[]>([]);
  const [ratios, setRatios] = useState<FinancialRatios | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'overview' | 'financials' | 'ratios'>('overview');
  const [statementType, setStatementType] = useState<'income' | 'balance' | 'cashflow'>('income');
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/auth');
    }
  }, [isAuthenticated, authLoading, router]);

  useEffect(() => {
    const fetchData = async () => {
      if (!isAuthenticated) return;

      try {
        setLoading(true);
        const [companyData, statementsData] = await Promise.all([
          api.getCompany(params.ticker),
          api.getFinancialStatements(params.ticker, statementType, 3),
        ]);

        setCompany(companyData);
        setStatements(statementsData);

        // Try to fetch ratios (may fail if no data)
        try {
          const ratiosData = await api.getFinancialRatios(params.ticker);
          setRatios(ratiosData);
        } catch (err) {
          console.log('Ratios not available yet');
        }
      } catch (error: any) {
        console.error('Error fetching company data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [params.ticker, statementType, isAuthenticated]);

  const handleRefreshData = async () => {
    try {
      setRefreshing(true);
      await api.refreshFinancialData(params.ticker);
      // Wait a bit for data to be fetched
      setTimeout(async () => {
        const [statementsData, ratiosData] = await Promise.all([
          api.getFinancialStatements(params.ticker, statementType, 3),
          api.getFinancialRatios(params.ticker).catch(() => null),
        ]);
        setStatements(statementsData);
        setRatios(ratiosData);
        setRefreshing(false);
      }, 3000);
    } catch (error) {
      console.error('Error refreshing data:', error);
      setRefreshing(false);
    }
  };

  const formatCurrency = (value: number, currency: string = 'USD') => {
    if (!value) return 'N/A';
    const locale = currency === 'INR' ? 'en-IN' : 'en-US';
    const symbol = currency === 'INR' ? '₹' : '$';

    if (Math.abs(value) >= 1e9) {
      return `${symbol}${(value / 1e9).toFixed(2)}B`;
    } else if (Math.abs(value) >= 1e6) {
      return `${symbol}${(value / 1e6).toFixed(2)}M`;
    } else if (Math.abs(value) >= 1e3) {
      return `${symbol}${(value / 1e3).toFixed(2)}K`;
    }
    return `${symbol}${value.toLocaleString(locale)}`;
  };

  const getCurrency = (exchange?: string) => {
    return exchange === 'NSE' || exchange === 'BSE' ? 'INR' : 'USD';
  };

  if (authLoading || loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin h-12 w-12 border-4 border-primary-500 rounded-full border-t-transparent"></div>
      </div>
    );
  }

  if (!company) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900">Company Not Found</h2>
          <button onClick={() => router.push('/dashboard')} className="mt-4 text-primary-600 hover:text-primary-700">
            Back to Dashboard
          </button>
        </div>
      </div>
    );
  }

  const currency = getCurrency(company.exchange);

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <div className="flex justify-between items-start">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">{company.name}</h1>
              <div className="flex items-center gap-4 mt-2">
                <span className="text-2xl font-semibold text-primary-600">{company.ticker}</span>
                <span className="px-3 py-1 bg-gray-100 rounded text-sm">{company.exchange}</span>
                {company.sector && (
                  <span className="text-gray-600">{company.sector}</span>
                )}
              </div>
              {company.market_cap && (
                <p className="text-lg text-gray-700 mt-2">
                  Market Cap: {formatCurrency(company.market_cap, currency)}
                </p>
              )}
            </div>
            <button
              onClick={handleRefreshData}
              disabled={refreshing}
              className="bg-primary-600 text-white px-4 py-2 rounded-md hover:bg-primary-700 transition disabled:opacity-50"
            >
              {refreshing ? 'Refreshing...' : 'Refresh Data'}
            </button>
          </div>
        </div>

        {/* Tabs */}
        <div className="bg-white rounded-lg shadow-md mb-6">
          <div className="border-b border-gray-200">
            <nav className="flex space-x-8 px-6" aria-label="Tabs">
              {(['overview', 'financials', 'ratios'] as const).map((tab) => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={`py-4 px-1 border-b-2 font-medium text-sm ${
                    activeTab === tab
                      ? 'border-primary-600 text-primary-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  {tab.charAt(0).toUpperCase() + tab.slice(1)}
                </button>
              ))}
            </nav>
          </div>

          <div className="p-6">
            {/* Overview Tab */}
            {activeTab === 'overview' && (
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">Company Overview</h3>
                  <p className="text-gray-700">{company.description || 'No description available.'}</p>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  <div className="bg-gray-50 p-4 rounded">
                    <p className="text-sm text-gray-500">Industry</p>
                    <p className="font-semibold text-gray-900">{company.industry || 'N/A'}</p>
                  </div>
                  <div className="bg-gray-50 p-4 rounded">
                    <p className="text-sm text-gray-500">Headquarters</p>
                    <p className="font-semibold text-gray-900">{company.headquarters || 'N/A'}</p>
                  </div>
                  <div className="bg-gray-50 p-4 rounded">
                    <p className="text-sm text-gray-500">Website</p>
                    {company.website ? (
                      <a href={company.website} target="_blank" rel="noopener noreferrer" className="text-primary-600 hover:text-primary-700">
                        Visit Website
                      </a>
                    ) : (
                      <p className="font-semibold text-gray-900">N/A</p>
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* Financials Tab */}
            {activeTab === 'financials' && (
              <div>
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-lg font-semibold text-gray-900">Financial Statements</h3>
                  <div className="flex gap-2">
                    {(['income', 'balance', 'cashflow'] as const).map((type) => (
                      <button
                        key={type}
                        onClick={() => setStatementType(type)}
                        className={`px-4 py-2 rounded ${
                          statementType === type
                            ? 'bg-primary-600 text-white'
                            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                        }`}
                      >
                        {type === 'income' ? 'Income' : type === 'balance' ? 'Balance Sheet' : 'Cash Flow'}
                      </button>
                    ))}
                  </div>
                </div>

                {statements.length > 0 ? (
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Period
                          </th>
                          {statements.map((stmt) => (
                            <th key={stmt.id} className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                              {new Date(stmt.period_end).getFullYear()}
                            </th>
                          ))}
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {statementType === 'income' && (
                          <>
                            <tr>
                              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">Revenue</td>
                              {statements.map((stmt) => (
                                <td key={stmt.id} className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-900">
                                  {formatCurrency(stmt.data.total_revenue, currency)}
                                </td>
                              ))}
                            </tr>
                            <tr>
                              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">Gross Profit</td>
                              {statements.map((stmt) => (
                                <td key={stmt.id} className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-900">
                                  {formatCurrency(stmt.data.gross_profit, currency)}
                                </td>
                              ))}
                            </tr>
                            <tr>
                              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">Operating Income</td>
                              {statements.map((stmt) => (
                                <td key={stmt.id} className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-900">
                                  {formatCurrency(stmt.data.operating_income, currency)}
                                </td>
                              ))}
                            </tr>
                            <tr className="bg-gray-50">
                              <td className="px-6 py-4 whitespace-nowrap text-sm font-semibold text-gray-900">Net Income</td>
                              {statements.map((stmt) => (
                                <td key={stmt.id} className="px-6 py-4 whitespace-nowrap text-sm text-right font-semibold text-gray-900">
                                  {formatCurrency(stmt.data.net_income, currency)}
                                </td>
                              ))}
                            </tr>
                          </>
                        )}
                        {statementType === 'balance' && (
                          <>
                            <tr>
                              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">Total Assets</td>
                              {statements.map((stmt) => (
                                <td key={stmt.id} className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-900">
                                  {formatCurrency(stmt.data.total_assets, currency)}
                                </td>
                              ))}
                            </tr>
                            <tr>
                              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">Current Assets</td>
                              {statements.map((stmt) => (
                                <td key={stmt.id} className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-900">
                                  {formatCurrency(stmt.data.current_assets, currency)}
                                </td>
                              ))}
                            </tr>
                            <tr>
                              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">Total Liabilities</td>
                              {statements.map((stmt) => (
                                <td key={stmt.id} className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-900">
                                  {formatCurrency(stmt.data.total_liabilities, currency)}
                                </td>
                              ))}
                            </tr>
                            <tr className="bg-gray-50">
                              <td className="px-6 py-4 whitespace-nowrap text-sm font-semibold text-gray-900">Total Equity</td>
                              {statements.map((stmt) => (
                                <td key={stmt.id} className="px-6 py-4 whitespace-nowrap text-sm text-right font-semibold text-gray-900">
                                  {formatCurrency(stmt.data.total_stockholder_equity, currency)}
                                </td>
                              ))}
                            </tr>
                          </>
                        )}
                        {statementType === 'cashflow' && (
                          <>
                            <tr>
                              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">Operating Cash Flow</td>
                              {statements.map((stmt) => (
                                <td key={stmt.id} className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-900">
                                  {formatCurrency(stmt.data.operating_cashflow, currency)}
                                </td>
                              ))}
                            </tr>
                            <tr>
                              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">Investing Cash Flow</td>
                              {statements.map((stmt) => (
                                <td key={stmt.id} className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-900">
                                  {formatCurrency(stmt.data.investing_cashflow, currency)}
                                </td>
                              ))}
                            </tr>
                            <tr>
                              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">Financing Cash Flow</td>
                              {statements.map((stmt) => (
                                <td key={stmt.id} className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-900">
                                  {formatCurrency(stmt.data.financing_cashflow, currency)}
                                </td>
                              ))}
                            </tr>
                            <tr className="bg-gray-50">
                              <td className="px-6 py-4 whitespace-nowrap text-sm font-semibold text-gray-900">Free Cash Flow</td>
                              {statements.map((stmt) => (
                                <td key={stmt.id} className="px-6 py-4 whitespace-nowrap text-sm text-right font-semibold text-gray-900">
                                  {formatCurrency(stmt.data.free_cash_flow, currency)}
                                </td>
                              ))}
                            </tr>
                          </>
                        )}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <div className="text-center py-12">
                    <p className="text-gray-600 mb-4">No financial data available yet.</p>
                    <button
                      onClick={handleRefreshData}
                      className="bg-primary-600 text-white px-6 py-2 rounded-md hover:bg-primary-700"
                    >
                      Fetch Financial Data
                    </button>
                  </div>
                )}
              </div>
            )}

            {/* Ratios Tab */}
            {activeTab === 'ratios' && (
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Financial Ratios</h3>
                {ratios ? (
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {/* Profitability */}
                    <div className="bg-gray-50 p-4 rounded-lg">
                      <h4 className="font-semibold text-gray-900 mb-3">Profitability</h4>
                      <div className="space-y-2">
                        {Object.entries(ratios.ratios.profitability).map(([key, value]) => (
                          <div key={key} className="flex justify-between">
                            <span className="text-sm text-gray-600">{key.replace(/_/g, ' ').toUpperCase()}</span>
                            <span className="text-sm font-medium">{typeof value === 'number' ? value.toFixed(2) + '%' : value}</span>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Liquidity */}
                    <div className="bg-gray-50 p-4 rounded-lg">
                      <h4 className="font-semibold text-gray-900 mb-3">Liquidity</h4>
                      <div className="space-y-2">
                        {Object.entries(ratios.ratios.liquidity).map(([key, value]) => (
                          <div key={key} className="flex justify-between">
                            <span className="text-sm text-gray-600">{key.replace(/_/g, ' ').toUpperCase()}</span>
                            <span className="text-sm font-medium">{typeof value === 'number' ? value.toFixed(2) : formatCurrency(value as number, currency)}</span>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Leverage */}
                    <div className="bg-gray-50 p-4 rounded-lg">
                      <h4 className="font-semibold text-gray-900 mb-3">Leverage</h4>
                      <div className="space-y-2">
                        {Object.entries(ratios.ratios.leverage).map(([key, value]) => (
                          <div key={key} className="flex justify-between">
                            <span className="text-sm text-gray-600">{key.replace(/_/g, ' ').toUpperCase()}</span>
                            <span className="text-sm font-medium">{typeof value === 'number' ? value.toFixed(2) : value}</span>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Efficiency */}
                    <div className="bg-gray-50 p-4 rounded-lg">
                      <h4 className="font-semibold text-gray-900 mb-3">Efficiency</h4>
                      <div className="space-y-2">
                        {Object.entries(ratios.ratios.efficiency).map(([key, value]) => (
                          <div key={key} className="flex justify-between">
                            <span className="text-sm text-gray-600">{key.replace(/_/g, ' ').toUpperCase()}</span>
                            <span className="text-sm font-medium">{typeof value === 'number' ? value.toFixed(2) : value}</span>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Cash Flow */}
                    <div className="bg-gray-50 p-4 rounded-lg">
                      <h4 className="font-semibold text-gray-900 mb-3">Cash Flow</h4>
                      <div className="space-y-2">
                        {Object.entries(ratios.ratios.cashflow).map(([key, value]) => (
                          <div key={key} className="flex justify-between">
                            <span className="text-sm text-gray-600">{key.replace(/_/g, ' ').toUpperCase()}</span>
                            <span className="text-sm font-medium">{typeof value === 'number' ? value.toFixed(2) : formatCurrency(value as number, currency)}</span>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* DuPont Analysis */}
                    {ratios.ratios.dupont && (
                      <div className="bg-primary-50 p-4 rounded-lg">
                        <h4 className="font-semibold text-gray-900 mb-3">DuPont Analysis</h4>
                        <div className="space-y-2">
                          {Object.entries(ratios.ratios.dupont).map(([key, value]) => (
                            <div key={key} className="flex justify-between">
                              <span className="text-sm text-gray-600">{key.replace(/_/g, ' ').toUpperCase()}</span>
                              <span className="text-sm font-medium">{typeof value === 'number' ? value.toFixed(2) : value}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="text-center py-12">
                    <p className="text-gray-600 mb-4">No ratio data available yet.</p>
                    <button
                      onClick={handleRefreshData}
                      className="bg-primary-600 text-white px-6 py-2 rounded-md hover:bg-primary-700"
                    >
                      Fetch Financial Data
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
