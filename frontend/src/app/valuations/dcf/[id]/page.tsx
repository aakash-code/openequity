'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth-context';
import { api, DCFValuation } from '@/lib/api';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar } from 'recharts';

interface PageProps {
  params: {
    id: string;
  };
}

export default function DCFDetailPage({ params }: PageProps) {
  const router = useRouter();
  const { isAuthenticated, loading: authLoading } = useAuth();
  const [dcf, setDcf] = useState<DCFValuation | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/auth');
    }
  }, [isAuthenticated, authLoading, router]);

  useEffect(() => {
    if (isAuthenticated) {
      fetchDCF();
    }
  }, [params.id, isAuthenticated]);

  const fetchDCF = async () => {
    setLoading(true);
    try {
      const data = await api.getDCFValuation(params.id);
      setDcf(data);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch DCF model');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!confirm('Are you sure you want to delete this DCF model?')) return;

    try {
      await api.deleteDCFValuation(params.id);
      router.push('/valuations');
    } catch (err: any) {
      setError(err.message || 'Failed to delete DCF model');
    }
  };

  const formatCurrency = (value: number) => {
    if (value >= 1e12) return `$${(value / 1e12).toFixed(2)}T`;
    if (value >= 1e9) return `$${(value / 1e9).toFixed(2)}B`;
    if (value >= 1e6) return `$${(value / 1e6).toFixed(2)}M`;
    return `$${value.toLocaleString()}`;
  };

  const formatPercent = (value: number) => {
    return `${(value * 100).toFixed(2)}%`;
  };

  if (authLoading || loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin h-12 w-12 border-4 border-primary-500 rounded-full border-t-transparent"></div>
      </div>
    );
  }

  if (error || !dcf) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Error</h2>
          <p className="text-gray-600 mb-4">{error || 'DCF model not found'}</p>
          <button
            onClick={() => router.push('/valuations')}
            className="bg-primary-600 text-white px-4 py-2 rounded-md hover:bg-primary-700"
          >
            Back to Valuations
          </button>
        </div>
      </div>
    );
  }

  // Prepare chart data
  const projectionsData = dcf.projections?.revenues?.map((revenue: number, index: number) => ({
    year: `Year ${index + 1}`,
    revenue: revenue / 1e9,
    ebitda: dcf.projections.ebitda[index] / 1e9,
    fcf: dcf.projections.fcf[index] / 1e9,
  })) || [];

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8 flex justify-between items-start">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <h1 className="text-3xl font-bold text-gray-900">{dcf.name}</h1>
              <span className="bg-primary-100 text-primary-700 px-3 py-1 rounded-md text-sm font-medium">
                {dcf.ticker}
              </span>
              {dcf.is_public && (
                <span className="bg-green-100 text-green-700 px-3 py-1 rounded-md text-sm">
                  Public
                </span>
              )}
            </div>
            {dcf.description && (
              <p className="text-gray-600">{dcf.description}</p>
            )}
            <p className="text-sm text-gray-500 mt-2">
              Created {new Date(dcf.created_at).toLocaleDateString()}
            </p>
          </div>
          <div className="flex gap-2">
            <button
              onClick={handleDelete}
              className="px-4 py-2 text-red-600 border border-red-300 rounded-md hover:bg-red-50 transition"
            >
              Delete
            </button>
            <button
              onClick={() => router.push('/valuations')}
              className="px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition"
            >
              Back to List
            </button>
          </div>
        </div>

        {/* Valuation Summary */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-white rounded-lg shadow-md p-6">
            <p className="text-sm text-gray-500 mb-1">Enterprise Value</p>
            <p className="text-2xl font-bold text-gray-900">{formatCurrency(dcf.enterprise_value)}</p>
          </div>
          <div className="bg-white rounded-lg shadow-md p-6">
            <p className="text-sm text-gray-500 mb-1">Equity Value</p>
            <p className="text-2xl font-bold text-gray-900">{formatCurrency(dcf.equity_value)}</p>
          </div>
          <div className="bg-white rounded-lg shadow-md p-6">
            <p className="text-sm text-gray-500 mb-1">Value per Share</p>
            <p className="text-2xl font-bold text-gray-900">${dcf.value_per_share.toFixed(2)}</p>
            {dcf.current_price && (
              <p className="text-xs text-gray-500 mt-1">Current: ${dcf.current_price.toFixed(2)}</p>
            )}
          </div>
          <div className="bg-white rounded-lg shadow-md p-6">
            <p className="text-sm text-gray-500 mb-1">Upside/Downside</p>
            {dcf.upside_downside !== null && dcf.upside_downside !== undefined ? (
              <p className={`text-2xl font-bold ${dcf.upside_downside >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {dcf.upside_downside >= 0 ? '+' : ''}{dcf.upside_downside.toFixed(2)}%
              </p>
            ) : (
              <p className="text-sm text-gray-400">N/A</p>
            )}
          </div>
        </div>

        {/* Projections Chart */}
        {projectionsData.length > 0 && (
          <div className="bg-white rounded-lg shadow-md p-6 mb-8">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Financial Projections</h2>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={projectionsData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="year" />
                <YAxis label={{ value: 'Billions ($)', angle: -90, position: 'insideLeft' }} />
                <Tooltip formatter={(value: number) => `$${value.toFixed(2)}B`} />
                <Legend />
                <Line type="monotone" dataKey="revenue" stroke="#3b82f6" name="Revenue" strokeWidth={2} />
                <Line type="monotone" dataKey="ebitda" stroke="#10b981" name="EBITDA" strokeWidth={2} />
                <Line type="monotone" dataKey="fcf" stroke="#8b5cf6" name="FCF" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* WACC Details */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">WACC Calculation</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            <div>
              <p className="text-sm text-gray-500">WACC</p>
              <p className="text-lg font-semibold text-primary-600">{formatPercent(dcf.wacc)}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Risk-Free Rate</p>
              <p className="text-lg font-semibold text-gray-900">{formatPercent(dcf.risk_free_rate)}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Equity Risk Premium</p>
              <p className="text-lg font-semibold text-gray-900">{formatPercent(dcf.equity_risk_premium)}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Beta</p>
              <p className="text-lg font-semibold text-gray-900">{dcf.beta.toFixed(2)}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Cost of Debt</p>
              <p className="text-lg font-semibold text-gray-900">{formatPercent(dcf.cost_of_debt)}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Tax Rate</p>
              <p className="text-lg font-semibold text-gray-900">{formatPercent(dcf.tax_rate)}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Debt Weight</p>
              <p className="text-lg font-semibold text-gray-900">{formatPercent(dcf.debt_weight)}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Equity Weight</p>
              <p className="text-lg font-semibold text-gray-900">{formatPercent(dcf.equity_weight)}</p>
            </div>
          </div>
        </div>

        {/* Projection Assumptions */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Projection Assumptions</h2>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-6">
            <div>
              <p className="text-sm text-gray-500">EBITDA Margin</p>
              <p className="text-lg font-semibold text-gray-900">{formatPercent(dcf.ebitda_margin)}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">D&A % Revenue</p>
              <p className="text-lg font-semibold text-gray-900">{formatPercent(dcf.depreciation_pct_revenue)}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">CapEx % Revenue</p>
              <p className="text-lg font-semibold text-gray-900">{formatPercent(dcf.capex_pct_revenue)}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">NWC % Revenue</p>
              <p className="text-lg font-semibold text-gray-900">{formatPercent(dcf.nwc_pct_revenue)}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Terminal Growth Rate</p>
              <p className="text-lg font-semibold text-gray-900">
                {dcf.terminal_growth_rate ? formatPercent(dcf.terminal_growth_rate) : 'N/A'}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Terminal EBITDA Multiple</p>
              <p className="text-lg font-semibold text-gray-900">
                {dcf.terminal_ebitda_multiple ? `${dcf.terminal_ebitda_multiple.toFixed(1)}x` : 'N/A'}
              </p>
            </div>
          </div>
          <div className="mt-6">
            <p className="text-sm text-gray-500 mb-2">Revenue Growth Rates by Year</p>
            <div className="flex gap-2 flex-wrap">
              {dcf.revenue_growth_rates.map((rate: number, index: number) => (
                <span key={index} className="bg-gray-100 px-3 py-1 rounded text-sm">
                  Year {index + 1}: {formatPercent(rate)}
                </span>
              ))}
            </div>
          </div>
        </div>

        {/* Valuation Bridge */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Valuation Bridge</h2>
          <div className="space-y-3">
            <div className="flex justify-between items-center border-b border-gray-200 pb-2">
              <span className="text-gray-700">PV of Projected FCFs</span>
              <span className="font-semibold">{formatCurrency(dcf.pv_fcf)}</span>
            </div>
            <div className="flex justify-between items-center border-b border-gray-200 pb-2">
              <span className="text-gray-700">PV of Terminal Value</span>
              <span className="font-semibold">{formatCurrency(dcf.pv_terminal_value)}</span>
            </div>
            <div className="flex justify-between items-center border-b-2 border-gray-300 pb-2 font-semibold">
              <span className="text-gray-900">Enterprise Value</span>
              <span className="text-primary-600">{formatCurrency(dcf.enterprise_value)}</span>
            </div>
            <div className="flex justify-between items-center border-b-2 border-gray-300 pb-2 font-semibold">
              <span className="text-gray-900">Equity Value</span>
              <span className="text-primary-600">{formatCurrency(dcf.equity_value)}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-700">Shares Outstanding</span>
              <span className="font-semibold">{dcf.shares_outstanding.toLocaleString()}</span>
            </div>
            <div className="flex justify-between items-center pt-2 border-t-2 border-primary-500">
              <span className="text-lg font-bold text-gray-900">Value per Share</span>
              <span className="text-2xl font-bold text-primary-600">${dcf.value_per_share.toFixed(2)}</span>
            </div>
          </div>
        </div>

        {/* Sensitivity Analysis */}
        {dcf.sensitivity_analysis && (
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Sensitivity Analysis</h2>
            <p className="text-sm text-gray-600 mb-4">
              Value per Share sensitivity to WACC and Terminal Growth Rate
            </p>
            <div className="overflow-x-auto">
              <table className="min-w-full border-collapse">
                <thead>
                  <tr>
                    <th className="border border-gray-300 bg-gray-100 px-4 py-2 text-sm font-semibold text-gray-700">
                      Terminal Growth →<br />WACC ↓
                    </th>
                    {dcf.sensitivity_analysis.terminal_growth_range.map((tg: number) => (
                      <th key={tg} className="border border-gray-300 bg-gray-100 px-4 py-2 text-sm font-semibold text-gray-700">
                        {formatPercent(tg)}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {dcf.sensitivity_analysis.wacc_range.map((wacc: number, rowIndex: number) => (
                    <tr key={wacc}>
                      <td className="border border-gray-300 bg-gray-50 px-4 py-2 text-sm font-semibold text-gray-700">
                        {formatPercent(wacc)}
                      </td>
                      {dcf.sensitivity_analysis.grid[rowIndex].map((value: number | null, colIndex: number) => {
                        const isBaseCase =
                          wacc === dcf.wacc &&
                          dcf.sensitivity_analysis.terminal_growth_range[colIndex] === dcf.terminal_growth_rate;
                        return (
                          <td
                            key={colIndex}
                            className={`border border-gray-300 px-4 py-2 text-sm text-center ${
                              isBaseCase ? 'bg-primary-100 font-bold' : 'bg-white'
                            }`}
                          >
                            {value !== null ? `$${value.toFixed(2)}` : '-'}
                          </td>
                        );
                      })}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <p className="text-xs text-gray-500 mt-2">
              Highlighted cell represents the base case valuation
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
