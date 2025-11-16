'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth-context';
import { api, Company, FinancialStatement, FinancialRatios } from '@/lib/api';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Area, AreaChart } from 'recharts';

interface PageProps {
  params: { ticker: string };
}

export default function CompanyDetailPage({ params }: PageProps) {
  const router = useRouter();
  const { isAuthenticated, loading: authLoading } = useAuth();
  const [company, setCompany] = useState<Company | null>(null);
  const [statements, setStatements] = useState<FinancialStatement[]>([]);
  const [ratios, setRatios] = useState<FinancialRatios | null>(null);
  const [trendData, setTrendData] = useState<any>(null);
  const [evaData, setEvaData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'overview' | 'financials' | 'ratios' | 'trends' | 'eva'>('overview');
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

        // Fetch trend data
        try {
          const trendsData = await api.getTrendAnalysis(params.ticker, 10);
          setTrendData(trendsData.analysis);
        } catch (err) {
          console.log('Trends not available yet');
        }

        // Fetch EVA data (assume 10% WACC as default)
        try {
          const evaAnalysis = await api.getEVAAnalysis(params.ticker, 0.10, 10);
          setEvaData(evaAnalysis.eva_analysis);
        } catch (err) {
          console.log('EVA analysis not available yet');
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
              {(['overview', 'financials', 'ratios', 'trends', 'eva'] as const).map((tab) => (
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

            {/* Trends Tab */}
            {activeTab === 'trends' && (
              <div className="space-y-8">
                <h3 className="text-xl font-semibold text-gray-900">Historical Trends & Analysis</h3>

                {trendData ? (
                  <>
                    {/* Growth Metrics Summary Cards */}
                    {trendData.revenue_analysis && (
                      <div>
                        <h4 className="text-lg font-semibold text-gray-900 mb-4">Growth Metrics</h4>
                        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                          <div className="bg-gradient-to-br from-blue-50 to-blue-100 p-4 rounded-lg">
                            <p className="text-sm text-blue-700 font-medium mb-1">Current Revenue</p>
                            <p className="text-2xl font-bold text-blue-900">
                              {formatCurrency(trendData.revenue_analysis.current_revenue, currency)}
                            </p>
                          </div>
                          {trendData.revenue_analysis.latest_growth !== null && (
                            <div className="bg-gradient-to-br from-green-50 to-green-100 p-4 rounded-lg">
                              <p className="text-sm text-green-700 font-medium mb-1">Latest YoY Growth</p>
                              <p className={`text-2xl font-bold ${trendData.revenue_analysis.latest_growth >= 0 ? 'text-green-900' : 'text-red-900'}`}>
                                {trendData.revenue_analysis.latest_growth >= 0 ? '+' : ''}{trendData.revenue_analysis.latest_growth.toFixed(2)}%
                              </p>
                            </div>
                          )}
                          {trendData.revenue_analysis.cagr !== null && (
                            <div className="bg-gradient-to-br from-purple-50 to-purple-100 p-4 rounded-lg">
                              <p className="text-sm text-purple-700 font-medium mb-1">CAGR</p>
                              <p className="text-2xl font-bold text-purple-900">
                                {trendData.revenue_analysis.cagr.toFixed(2)}%
                              </p>
                            </div>
                          )}
                          {trendData.revenue_analysis.average_growth !== null && (
                            <div className="bg-gradient-to-br from-orange-50 to-orange-100 p-4 rounded-lg">
                              <p className="text-sm text-orange-700 font-medium mb-1">Avg Growth</p>
                              <p className="text-2xl font-bold text-orange-900">
                                {trendData.revenue_analysis.average_growth.toFixed(2)}%
                              </p>
                            </div>
                          )}
                        </div>
                      </div>
                    )}

                    {/* Revenue Trend Chart */}
                    {trendData.revenue_analysis && trendData.revenue_analysis.revenues && (
                      <div className="bg-white border border-gray-200 rounded-lg p-6">
                        <h4 className="text-lg font-semibold text-gray-900 mb-4">Revenue Trend</h4>
                        <ResponsiveContainer width="100%" height={300}>
                          <AreaChart
                            data={trendData.revenue_analysis.periods.map((period: string, index: number) => ({
                              period: new Date(period).getFullYear(),
                              revenue: trendData.revenue_analysis.revenues[index] / 1e9,
                            }))}
                          >
                            <defs>
                              <linearGradient id="colorRevenue" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.8}/>
                                <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.1}/>
                              </linearGradient>
                            </defs>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="period" />
                            <YAxis label={{ value: 'Billions', angle: -90, position: 'insideLeft' }} />
                            <Tooltip formatter={(value: number) => [`${currency === 'INR' ? '₹' : '$'}${value.toFixed(2)}B`, 'Revenue']} />
                            <Area type="monotone" dataKey="revenue" stroke="#3b82f6" strokeWidth={2} fillOpacity={1} fill="url(#colorRevenue)" />
                          </AreaChart>
                        </ResponsiveContainer>
                      </div>
                    )}

                    {/* Profitability Margins Trend */}
                    {trendData.profitability_analysis && trendData.profitability_analysis.margins && (
                      <div className="bg-white border border-gray-200 rounded-lg p-6">
                        <h4 className="text-lg font-semibold text-gray-900 mb-4">Profitability Margins</h4>
                        <ResponsiveContainer width="100%" height={300}>
                          <LineChart
                            data={trendData.profitability_analysis.periods.map((period: string, index: number) => {
                              const data: any = { period: new Date(period).getFullYear() };
                              Object.entries(trendData.profitability_analysis.margins).forEach(([key, margin]: [string, any]) => {
                                if (margin.historical && margin.historical[index] !== null) {
                                  data[key] = margin.historical[index];
                                }
                              });
                              return data;
                            })}
                          >
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="period" />
                            <YAxis label={{ value: 'Margin (%)', angle: -90, position: 'insideLeft' }} />
                            <Tooltip formatter={(value: number) => [`${value.toFixed(2)}%`]} />
                            <Legend />
                            <Line type="monotone" dataKey="gross_margin" stroke="#10b981" name="Gross Margin" strokeWidth={2} />
                            <Line type="monotone" dataKey="operating_margin" stroke="#3b82f6" name="Operating Margin" strokeWidth={2} />
                            <Line type="monotone" dataKey="net_margin" stroke="#8b5cf6" name="Net Margin" strokeWidth={2} />
                          </LineChart>
                        </ResponsiveContainer>

                        {/* Margin Trends Summary */}
                        <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-4">
                          {Object.entries(trendData.profitability_analysis.margins).map(([key, margin]: [string, any]) => (
                            <div key={key} className="bg-gray-50 p-3 rounded">
                              <p className="text-xs text-gray-500 mb-1">{key.replace(/_/g, ' ').toUpperCase()}</p>
                              <div className="flex justify-between items-center">
                                <p className="text-lg font-semibold">{margin.current.toFixed(2)}%</p>
                                <span className={`text-sm px-2 py-1 rounded ${
                                  margin.trend === 'improving' ? 'bg-green-100 text-green-700' :
                                  margin.trend === 'declining' ? 'bg-red-100 text-red-700' :
                                  'bg-gray-100 text-gray-700'
                                }`}>
                                  {margin.change >= 0 ? '+' : ''}{margin.change.toFixed(2)}%
                                </span>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Balance Sheet Trend */}
                    {trendData.balance_sheet_analysis && trendData.balance_sheet_analysis.total_assets && (
                      <div className="bg-white border border-gray-200 rounded-lg p-6">
                        <h4 className="text-lg font-semibold text-gray-900 mb-4">Balance Sheet Evolution</h4>
                        <ResponsiveContainer width="100%" height={300}>
                          <BarChart
                            data={trendData.balance_sheet_analysis.periods.map((period: string, index: number) => ({
                              period: new Date(period).getFullYear(),
                              assets: trendData.balance_sheet_analysis.total_assets[index] / 1e9,
                              liabilities: trendData.balance_sheet_analysis.total_liabilities[index] / 1e9,
                              equity: trendData.balance_sheet_analysis.total_equity[index] / 1e9,
                            }))}
                          >
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="period" />
                            <YAxis label={{ value: 'Billions', angle: -90, position: 'insideLeft' }} />
                            <Tooltip formatter={(value: number) => [`${currency === 'INR' ? '₹' : '$'}${value.toFixed(2)}B`]} />
                            <Legend />
                            <Bar dataKey="assets" fill="#3b82f6" name="Total Assets" />
                            <Bar dataKey="liabilities" fill="#ef4444" name="Total Liabilities" />
                            <Bar dataKey="equity" fill="#10b981" name="Total Equity" />
                          </BarChart>
                        </ResponsiveContainer>
                      </div>
                    )}

                    {/* Cash Flow Trend */}
                    {trendData.cashflow_analysis && trendData.cashflow_analysis.operating_cashflow && (
                      <div className="bg-white border border-gray-200 rounded-lg p-6">
                        <h4 className="text-lg font-semibold text-gray-900 mb-4">Cash Flow Trends</h4>
                        <ResponsiveContainer width="100%" height={300}>
                          <BarChart
                            data={trendData.cashflow_analysis.periods.map((period: string, index: number) => ({
                              period: new Date(period).getFullYear(),
                              operating: trendData.cashflow_analysis.operating_cashflow[index] / 1e9,
                              investing: trendData.cashflow_analysis.investing_cashflow[index] / 1e9,
                              financing: trendData.cashflow_analysis.financing_cashflow[index] / 1e9,
                              free: trendData.cashflow_analysis.free_cashflow[index] / 1e9,
                            }))}
                          >
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="period" />
                            <YAxis label={{ value: 'Billions', angle: -90, position: 'insideLeft' }} />
                            <Tooltip formatter={(value: number) => [`${currency === 'INR' ? '₹' : '$'}${value.toFixed(2)}B`]} />
                            <Legend />
                            <Bar dataKey="operating" fill="#10b981" name="Operating CF" />
                            <Bar dataKey="investing" fill="#f59e0b" name="Investing CF" />
                            <Bar dataKey="financing" fill="#ef4444" name="Financing CF" />
                            <Bar dataKey="free" fill="#8b5cf6" name="Free CF" />
                          </BarChart>
                        </ResponsiveContainer>
                      </div>
                    )}
                  </>
                ) : (
                  <div className="text-center py-12">
                    <p className="text-gray-600 mb-4">No trend data available yet.</p>
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

            {/* EVA Tab */}
            {activeTab === 'eva' && (
              <div className="space-y-8">
                <h3 className="text-xl font-semibold text-gray-900">Economic Value Added (EVA) Analysis</h3>

                {evaData && evaData.periods ? (
                  <>
                    {/* EVA Summary Cards */}
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                      <div className="bg-gradient-to-br from-blue-50 to-blue-100 p-4 rounded-lg">
                        <p className="text-sm text-blue-700 font-medium mb-1">Latest EVA</p>
                        <p className={`text-2xl font-bold ${evaData.latest_eva >= 0 ? 'text-blue-900' : 'text-red-900'}`}>
                          {formatCurrency(evaData.latest_eva, currency)}
                        </p>
                        <p className="text-xs text-blue-600 mt-1">
                          {evaData.eva_trend === 'improving' ? '↑ Improving' : '↓ Declining'}
                        </p>
                      </div>

                      {evaData.average_eva !== null && (
                        <div className="bg-gradient-to-br from-purple-50 to-purple-100 p-4 rounded-lg">
                          <p className="text-sm text-purple-700 font-medium mb-1">Average EVA</p>
                          <p className={`text-2xl font-bold ${evaData.average_eva >= 0 ? 'text-purple-900' : 'text-red-900'}`}>
                            {formatCurrency(evaData.average_eva, currency)}
                          </p>
                        </div>
                      )}

                      {evaData.average_roic !== null && (
                        <div className="bg-gradient-to-br from-green-50 to-green-100 p-4 rounded-lg">
                          <p className="text-sm text-green-700 font-medium mb-1">Avg ROIC</p>
                          <p className="text-2xl font-bold text-green-900">
                            {evaData.average_roic.toFixed(2)}%
                          </p>
                        </div>
                      )}

                      {evaData.cumulative_eva !== null && (
                        <div className="bg-gradient-to-br from-orange-50 to-orange-100 p-4 rounded-lg">
                          <p className="text-sm text-orange-700 font-medium mb-1">Cumulative EVA</p>
                          <p className={`text-2xl font-bold ${evaData.cumulative_eva >= 0 ? 'text-orange-900' : 'text-red-900'}`}>
                            {formatCurrency(evaData.cumulative_eva, currency)}
                          </p>
                        </div>
                      )}
                    </div>

                    {/* EVA Trend Chart */}
                    <div className="bg-white border border-gray-200 rounded-lg p-6">
                      <h4 className="text-lg font-semibold text-gray-900 mb-4">EVA Trend</h4>
                      <ResponsiveContainer width="100%" height={300}>
                        <BarChart
                          data={evaData.periods.map((period: any) => ({
                            year: period.fiscal_year || new Date(period.period).getFullYear(),
                            eva: period.eva / 1e9,
                          }))}
                        >
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="year" />
                          <YAxis label={{ value: 'Billions', angle: -90, position: 'insideLeft' }} />
                          <Tooltip
                            formatter={(value: number) => [
                              `${currency === 'INR' ? '₹' : '$'}${value.toFixed(2)}B`,
                              'EVA'
                            ]}
                          />
                          <Bar dataKey="eva" fill="#3b82f6" name="Economic Value Added">
                            {evaData.periods.map((period: any, index: number) => (
                              <Bar key={index} fill={period.eva >= 0 ? '#10b981' : '#ef4444'} />
                            ))}
                          </Bar>
                        </BarChart>
                      </ResponsiveContainer>
                    </div>

                    {/* ROIC vs WACC */}
                    <div className="bg-white border border-gray-200 rounded-lg p-6">
                      <h4 className="text-lg font-semibold text-gray-900 mb-4">ROIC vs WACC (EVA Spread)</h4>
                      <ResponsiveContainer width="100%" height={300}>
                        <LineChart
                          data={evaData.periods.map((period: any) => ({
                            year: period.fiscal_year || new Date(period.period).getFullYear(),
                            roic: period.roic,
                            wacc: period.wacc,
                            spread: period.eva_spread,
                          }))}
                        >
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="year" />
                          <YAxis label={{ value: 'Percent (%)', angle: -90, position: 'insideLeft' }} />
                          <Tooltip formatter={(value: number) => [`${value.toFixed(2)}%`]} />
                          <Legend />
                          <Line type="monotone" dataKey="roic" stroke="#10b981" name="ROIC" strokeWidth={2} />
                          <Line type="monotone" dataKey="wacc" stroke="#ef4444" name="WACC" strokeWidth={2} />
                          <Line type="monotone" dataKey="spread" stroke="#8b5cf6" name="EVA Spread" strokeWidth={2} />
                        </LineChart>
                      </ResponsiveContainer>
                    </div>

                    {/* EVA Metrics Table */}
                    <div className="bg-white border border-gray-200 rounded-lg p-6">
                      <h4 className="text-lg font-semibold text-gray-900 mb-4">Period-by-Period EVA Metrics</h4>
                      <div className="overflow-x-auto">
                        <table className="min-w-full divide-y divide-gray-200">
                          <thead className="bg-gray-50">
                            <tr>
                              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Year</th>
                              <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">NOPAT</th>
                              <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Invested Capital</th>
                              <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Capital Charge</th>
                              <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">EVA</th>
                              <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">ROIC</th>
                              <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">EVA Spread</th>
                            </tr>
                          </thead>
                          <tbody className="bg-white divide-y divide-gray-200">
                            {evaData.periods.map((period: any, index: number) => (
                              <tr key={index} className={index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                                <td className="px-4 py-3 whitespace-nowrap text-sm font-medium text-gray-900">
                                  {period.fiscal_year || new Date(period.period).getFullYear()}
                                </td>
                                <td className="px-4 py-3 whitespace-nowrap text-sm text-right text-gray-900">
                                  {formatCurrency(period.nopat, currency)}
                                </td>
                                <td className="px-4 py-3 whitespace-nowrap text-sm text-right text-gray-900">
                                  {formatCurrency(period.invested_capital, currency)}
                                </td>
                                <td className="px-4 py-3 whitespace-nowrap text-sm text-right text-gray-900">
                                  {formatCurrency(period.capital_charge, currency)}
                                </td>
                                <td className={`px-4 py-3 whitespace-nowrap text-sm text-right font-semibold ${period.eva >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                  {formatCurrency(period.eva, currency)}
                                </td>
                                <td className="px-4 py-3 whitespace-nowrap text-sm text-right text-gray-900">
                                  {period.roic.toFixed(2)}%
                                </td>
                                <td className={`px-4 py-3 whitespace-nowrap text-sm text-right font-semibold ${period.eva_spread >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                  {period.eva_spread >= 0 ? '+' : ''}{period.eva_spread.toFixed(2)}%
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>

                    {/* EVA Interpretation */}
                    <div className="bg-blue-50 border-l-4 border-blue-400 p-4">
                      <div className="flex">
                        <div className="flex-shrink-0">
                          <svg className="h-5 w-5 text-blue-400" viewBox="0 0 20 20" fill="currentColor">
                            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                          </svg>
                        </div>
                        <div className="ml-3">
                          <p className="text-sm text-blue-700">
                            <strong>EVA Interpretation:</strong> EVA measures true economic profit by subtracting the cost of capital from operating profit.
                            {evaData.latest_eva >= 0
                              ? ' Positive EVA indicates the company is creating value for shareholders.'
                              : ' Negative EVA suggests the company is destroying shareholder value.'}
                            {evaData.periods.filter((p: any) => p.value_creation).length > 0 &&
                              ` The company has created value in ${evaData.periods.filter((p: any) => p.value_creation).length} of the last ${evaData.periods.length} years.`}
                          </p>
                        </div>
                      </div>
                    </div>
                  </>
                ) : (
                  <div className="text-center py-12">
                    <p className="text-gray-600 mb-4">No EVA analysis available yet.</p>
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
