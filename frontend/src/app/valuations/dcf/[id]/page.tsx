'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth-context';
import { api, DCFValuation } from '@/lib/api';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar, AreaChart, Area } from 'recharts';

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
  const [monteCarloData, setMonteCarloData] = useState<any>(null);
  const [scenarioData, setScenarioData] = useState<any>(null);
  const [runningMonteCarlo, setRunningMonteCarlo] = useState(false);
  const [runningScenario, setRunningScenario] = useState(false);

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

  const runMonteCarlo = async () => {
    if (!dcf) return;

    setRunningMonteCarlo(true);
    try {
      // Extract base revenue from projections
      const baseRevenue = dcf.projections?.revenues?.[0] || 0;

      // Calculate average revenue growth
      const avgGrowth = dcf.revenue_growth_rates.reduce((a: number, b: number) => a + b, 0) / dcf.revenue_growth_rates.length;

      const result = await api.runMonteCarloSimulation({
        base_revenue: baseRevenue,
        base_revenue_growth: avgGrowth,
        revenue_growth_volatility: 0.05, // 5% volatility
        base_ebitda_margin: dcf.ebitda_margin,
        ebitda_margin_volatility: 0.02, // 2% volatility
        projection_years: dcf.projection_years,
        base_wacc: dcf.wacc,
        wacc_volatility: 0.01, // 1% volatility
        base_terminal_growth: dcf.terminal_growth_rate || 0.025,
        terminal_growth_volatility: 0.005, // 0.5% volatility
        capex_percent: dcf.capex_pct_revenue,
        nwc_change_percent: dcf.nwc_pct_revenue,
        tax_rate: dcf.tax_rate,
        shares_outstanding: dcf.shares_outstanding,
        num_simulations: 10000,
        distribution: 'normal'
      });

      setMonteCarloData(result);
    } catch (err: any) {
      setError(err.message || 'Failed to run Monte Carlo simulation');
    } finally {
      setRunningMonteCarlo(false);
    }
  };

  const runScenarioAnalysis = async () => {
    if (!dcf) return;

    setRunningScenario(true);
    try {
      const baseRevenue = dcf.projections?.revenues?.[0] || 0;

      const result = await api.runScenarioAnalysis({
        base_revenue: baseRevenue,
        revenue_growth_rates: dcf.revenue_growth_rates,
        ebitda_margin: dcf.ebitda_margin,
        tax_rate: dcf.tax_rate,
        capex_percent: dcf.capex_pct_revenue,
        nwc_change_percent: dcf.nwc_pct_revenue,
        wacc: dcf.wacc,
        terminal_growth_rate: dcf.terminal_growth_rate || 0.025,
        shares_outstanding: dcf.shares_outstanding,
        net_debt: 0 // Assuming no net debt adjustment needed
      });

      setScenarioData(result);
    } catch (err: any) {
      setError(err.message || 'Failed to run scenario analysis');
    } finally {
      setRunningScenario(false);
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
          <div className="bg-white rounded-lg shadow-md p-6 mb-8">
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

        {/* Monte Carlo Simulation */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold text-gray-900">Monte Carlo Simulation</h2>
            <button
              onClick={runMonteCarlo}
              disabled={runningMonteCarlo}
              className="bg-primary-600 text-white px-4 py-2 rounded-md hover:bg-primary-700 disabled:bg-gray-400 transition"
            >
              {runningMonteCarlo ? 'Running...' : monteCarloData ? 'Re-run Simulation' : 'Run Simulation'}
            </button>
          </div>

          {monteCarloData ? (
            <>
              <p className="text-sm text-gray-600 mb-6">
                Probabilistic valuation based on {monteCarloData.num_simulations?.toLocaleString()} simulations
              </p>

              {/* Monte Carlo Summary Cards */}
              <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-6">
                <div className="bg-blue-50 p-4 rounded-lg">
                  <p className="text-xs text-blue-700 font-medium mb-1">Mean Value</p>
                  <p className="text-xl font-bold text-blue-900">${monteCarloData.mean?.toFixed(2)}</p>
                </div>
                <div className="bg-green-50 p-4 rounded-lg">
                  <p className="text-xs text-green-700 font-medium mb-1">Median (P50)</p>
                  <p className="text-xl font-bold text-green-900">${monteCarloData.median?.toFixed(2)}</p>
                </div>
                <div className="bg-purple-50 p-4 rounded-lg">
                  <p className="text-xs text-purple-700 font-medium mb-1">Std Deviation</p>
                  <p className="text-xl font-bold text-purple-900">${monteCarloData.std_dev?.toFixed(2)}</p>
                </div>
                <div className="bg-orange-50 p-4 rounded-lg">
                  <p className="text-xs text-orange-700 font-medium mb-1">Min Value</p>
                  <p className="text-xl font-bold text-orange-900">${monteCarloData.min?.toFixed(2)}</p>
                </div>
                <div className="bg-red-50 p-4 rounded-lg">
                  <p className="text-xs text-red-700 font-medium mb-1">Max Value</p>
                  <p className="text-xl font-bold text-red-900">${monteCarloData.max?.toFixed(2)}</p>
                </div>
              </div>

              {/* Percentile Table */}
              <div className="mb-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-3">Value Percentiles</h3>
                <div className="grid grid-cols-5 gap-4">
                  {monteCarloData.percentiles && Object.entries(monteCarloData.percentiles).map(([key, value]: [string, any]) => (
                    <div key={key} className="border border-gray-200 rounded p-3 text-center">
                      <p className="text-xs text-gray-600 mb-1">{key.toUpperCase()}</p>
                      <p className="text-lg font-semibold text-gray-900">${value?.toFixed(2)}</p>
                    </div>
                  ))}
                </div>
              </div>

              {/* Distribution Histogram */}
              {monteCarloData.distribution && monteCarloData.distribution.length > 0 && (
                <div className="mb-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-3">Valuation Distribution</h3>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart
                      data={monteCarloData.distribution.map((bin: any) => ({
                        range: `$${bin.range_start.toFixed(0)}-${bin.range_end.toFixed(0)}`,
                        frequency: bin.frequency * 100,
                        count: bin.count
                      }))}
                    >
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="range" angle={-45} textAnchor="end" height={80} tick={{ fontSize: 10 }} />
                      <YAxis label={{ value: 'Frequency (%)', angle: -90, position: 'insideLeft' }} />
                      <Tooltip formatter={(value: number, name: string) => [name === 'frequency' ? `${value.toFixed(2)}%` : value, name === 'frequency' ? 'Frequency' : 'Count']} />
                      <Bar dataKey="frequency" fill="#3b82f6" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              )}

              {/* Probability Ranges */}
              {monteCarloData.probability_ranges && (
                <div className="bg-blue-50 border-l-4 border-blue-400 p-4">
                  <h4 className="text-sm font-semibold text-blue-900 mb-2">Probability Analysis</h4>
                  <div className="grid grid-cols-3 gap-4 text-sm text-blue-800">
                    <div>
                      <span className="font-medium">Above Mean:</span> {(monteCarloData.probability_ranges.above_mean * 100).toFixed(1)}%
                    </div>
                    <div>
                      <span className="font-medium">Within ±10%:</span> {(monteCarloData.probability_ranges.within_10_percent * 100).toFixed(1)}%
                    </div>
                    <div>
                      <span className="font-medium">Within ±25%:</span> {(monteCarloData.probability_ranges.within_25_percent * 100).toFixed(1)}%
                    </div>
                  </div>
                </div>
              )}
            </>
          ) : (
            <div className="text-center py-12 bg-gray-50 rounded-lg">
              <p className="text-gray-600 mb-4">Run Monte Carlo simulation to see probabilistic valuation ranges</p>
              <p className="text-sm text-gray-500">This analysis will run 10,000 simulations with randomized assumptions</p>
            </div>
          )}
        </div>

        {/* Scenario Analysis */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold text-gray-900">Scenario Analysis</h2>
            <button
              onClick={runScenarioAnalysis}
              disabled={runningScenario}
              className="bg-primary-600 text-white px-4 py-2 rounded-md hover:bg-primary-700 disabled:bg-gray-400 transition"
            >
              {runningScenario ? 'Running...' : scenarioData ? 'Re-run Analysis' : 'Run Analysis'}
            </button>
          </div>

          {scenarioData ? (
            <>
              <p className="text-sm text-gray-600 mb-6">
                Best, base, and worst case valuation scenarios
              </p>

              {/* Scenario Summary Cards */}
              {scenarioData.summary && (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                  <div className="bg-green-50 p-6 rounded-lg border-2 border-green-200">
                    <p className="text-sm text-green-700 font-medium mb-1">Optimistic Case</p>
                    <p className="text-3xl font-bold text-green-900">${scenarioData.summary.optimistic_value?.toFixed(2)}</p>
                    <p className="text-xs text-green-600 mt-2">
                      +{scenarioData.summary.upside_potential_percent?.toFixed(1)}% vs Base
                    </p>
                  </div>
                  <div className="bg-blue-50 p-6 rounded-lg border-2 border-blue-200">
                    <p className="text-sm text-blue-700 font-medium mb-1">Base Case</p>
                    <p className="text-3xl font-bold text-blue-900">${scenarioData.summary.base_value?.toFixed(2)}</p>
                    <p className="text-xs text-blue-600 mt-2">Current model valuation</p>
                  </div>
                  <div className="bg-red-50 p-6 rounded-lg border-2 border-red-200">
                    <p className="text-sm text-red-700 font-medium mb-1">Pessimistic Case</p>
                    <p className="text-3xl font-bold text-red-900">${scenarioData.summary.pessimistic_value?.toFixed(2)}</p>
                    <p className="text-xs text-red-600 mt-2">
                      -{scenarioData.summary.downside_risk_percent?.toFixed(1)}% vs Base
                    </p>
                  </div>
                </div>
              )}

              {/* Risk-Reward Metrics */}
              {scenarioData.summary && (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                  <div className="border border-gray-200 rounded-lg p-4">
                    <p className="text-sm text-gray-600 mb-1">Value Range</p>
                    <p className="text-xl font-semibold text-gray-900">${scenarioData.summary.value_range?.toFixed(2)}</p>
                  </div>
                  <div className="border border-gray-200 rounded-lg p-4">
                    <p className="text-sm text-gray-600 mb-1">Upside Potential</p>
                    <p className="text-xl font-semibold text-green-600">+{scenarioData.summary.upside_potential_percent?.toFixed(2)}%</p>
                  </div>
                  <div className="border border-gray-200 rounded-lg p-4">
                    <p className="text-sm text-gray-600 mb-1">Downside Risk</p>
                    <p className="text-xl font-semibold text-red-600">-{scenarioData.summary.downside_risk_percent?.toFixed(2)}%</p>
                  </div>
                </div>
              )}

              {/* Scenario Comparison Chart */}
              {scenarioData.scenarios && (
                <div className="mb-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-3">Scenario Comparison</h3>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart
                      data={[
                        {
                          scenario: 'Pessimistic',
                          value: scenarioData.scenarios.pessimistic_case?.valuation?.equity_value_per_share || 0
                        },
                        {
                          scenario: 'Base',
                          value: scenarioData.scenarios.base_case?.valuation?.equity_value_per_share || 0
                        },
                        {
                          scenario: 'Optimistic',
                          value: scenarioData.scenarios.optimistic_case?.valuation?.equity_value_per_share || 0
                        }
                      ]}
                    >
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="scenario" />
                      <YAxis label={{ value: 'Value per Share ($)', angle: -90, position: 'insideLeft' }} />
                      <Tooltip formatter={(value: number) => [`$${value.toFixed(2)}`, 'Value per Share']} />
                      <Bar dataKey="value" fill="#3b82f6">
                        {[
                          <Bar key="pessimistic" fill="#ef4444" />,
                          <Bar key="base" fill="#3b82f6" />,
                          <Bar key="optimistic" fill="#10b981" />
                        ]}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              )}

              {/* Risk-Reward Interpretation */}
              {scenarioData.summary?.risk_reward_ratio !== null && (
                <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4">
                  <div className="flex">
                    <div className="flex-shrink-0">
                      <svg className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                      </svg>
                    </div>
                    <div className="ml-3">
                      <p className="text-sm text-yellow-700">
                        <strong>Risk-Reward Ratio: {scenarioData.summary.risk_reward_ratio?.toFixed(2)}x</strong>
                        {scenarioData.summary.risk_reward_ratio > 2
                          ? ' - Favorable risk-reward profile with significant upside potential relative to downside risk.'
                          : scenarioData.summary.risk_reward_ratio > 1
                          ? ' - Moderate risk-reward profile.'
                          : ' - Limited upside relative to downside risk. Consider if downside scenarios are acceptable.'}
                      </p>
                    </div>
                  </div>
                </div>
              )}
            </>
          ) : (
            <div className="text-center py-12 bg-gray-50 rounded-lg">
              <p className="text-gray-600 mb-4">Run scenario analysis to see best/base/worst case valuations</p>
              <p className="text-sm text-gray-500">This analysis will show optimistic, base, and pessimistic scenarios</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
