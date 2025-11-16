'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth-context';
import { api, PeerGroup, ComparableAnalysis, CompanyMetrics } from '@/lib/api';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface PageProps {
  params: {
    id: string;
  };
}

export default function CompsAnalysisPage({ params }: PageProps) {
  const router = useRouter();
  const { isAuthenticated, loading: authLoading } = useAuth();
  const [peerGroup, setPeerGroup] = useState<PeerGroup | null>(null);
  const [analysis, setAnalysis] = useState<ComparableAnalysis | null>(null);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/auth');
    }
  }, [isAuthenticated, authLoading, router]);

  useEffect(() => {
    if (isAuthenticated) {
      fetchPeerGroup();
    }
  }, [params.id, isAuthenticated]);

  const fetchPeerGroup = async () => {
    setLoading(true);
    try {
      const data = await api.getPeerGroup(params.id);
      setPeerGroup(data);
      if (data.analysis_results) {
        setAnalysis(data.analysis_results);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to fetch peer group');
    } finally {
      setLoading(false);
    }
  };

  const runAnalysis = async () => {
    setAnalyzing(true);
    setError('');
    try {
      const result = await api.analyzePeerGroup(params.id);
      setAnalysis(result);
    } catch (err: any) {
      setError(err.message || 'Failed to run analysis');
    } finally {
      setAnalyzing(false);
    }
  };

  const handleDelete = async () => {
    if (!confirm('Are you sure you want to delete this peer group?')) return;

    try {
      await api.deletePeerGroup(params.id);
      router.push('/valuations');
    } catch (err: any) {
      setError(err.message || 'Failed to delete peer group');
    }
  };

  const formatCurrency = (value: number, currency: string = 'USD') => {
    if (value >= 1e12) return `${value >= 0 ? '' : '-'}${Math.abs(value / 1e12).toFixed(2)}T`;
    if (value >= 1e9) return `${value >= 0 ? '' : '-'}${Math.abs(value / 1e9).toFixed(2)}B`;
    if (value >= 1e6) return `${value >= 0 ? '' : '-'}${Math.abs(value / 1e6).toFixed(2)}M`;
    return value.toFixed(2);
  };

  const formatPercent = (value: number | null | undefined) => {
    if (value === null || value === undefined) return 'N/A';
    return `${value.toFixed(2)}%`;
  };

  const formatMultiple = (value: number | null | undefined) => {
    if (value === null || value === undefined) return 'N/A';
    return `${value.toFixed(2)}x`;
  };

  if (authLoading || loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin h-12 w-12 border-4 border-primary-500 rounded-full border-t-transparent"></div>
      </div>
    );
  }

  if (error && !peerGroup) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Error</h2>
          <p className="text-gray-600 mb-4">{error}</p>
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

  if (!peerGroup) {
    return null;
  }

  // Prepare chart data
  const multip lesChartData = analysis?.peers?.map((peer: CompanyMetrics) => ({
    name: peer.ticker,
    'P/E': peer.pe_ratio || 0,
    'P/B': peer.price_to_book || 0,
    'EV/EBITDA': peer.ev_to_ebitda || 0,
  })) || [];

  const profitabilityChartData = analysis?.peers?.map((peer: CompanyMetrics) => ({
    name: peer.ticker,
    'Gross Margin': peer.gross_margin || 0,
    'Operating Margin': peer.operating_margin || 0,
    'Net Margin': peer.net_margin || 0,
  })) || [];

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8 flex justify-between items-start">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <h1 className="text-3xl font-bold text-gray-900">{peerGroup.name}</h1>
              <span className="bg-primary-100 text-primary-700 px-3 py-1 rounded-md text-sm font-medium">
                {peerGroup.ticker}
              </span>
              {peerGroup.is_public && (
                <span className="bg-green-100 text-green-700 px-3 py-1 rounded-md text-sm">
                  Public
                </span>
              )}
            </div>
            {peerGroup.description && (
              <p className="text-gray-600">{peerGroup.description}</p>
            )}
            <p className="text-sm text-gray-500 mt-2">
              Created {new Date(peerGroup.created_at).toLocaleDateString()}
              {peerGroup.last_analyzed && (
                <> • Last analyzed {new Date(peerGroup.last_analyzed).toLocaleDateString()}</>
              )}
            </p>
          </div>
          <div className="flex gap-2">
            <button
              onClick={runAnalysis}
              disabled={analyzing}
              className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 transition disabled:opacity-50"
            >
              {analyzing ? 'Analyzing...' : analysis ? 'Refresh Analysis' : 'Run Analysis'}
            </button>
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

        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
            <p className="text-red-800 text-sm">{error}</p>
          </div>
        )}

        {/* Peer Companies List */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Peer Companies ({peerGroup.peer_tickers.length})
          </h2>
          <div className="flex flex-wrap gap-2">
            {peerGroup.peer_tickers.map((ticker) => (
              <span
                key={ticker}
                className="bg-primary-50 border border-primary-200 px-3 py-1 rounded-md text-sm font-medium text-primary-900"
              >
                {ticker}
              </span>
            ))}
          </div>
        </div>

        {!analysis ? (
          <div className="bg-white rounded-lg shadow-md p-12 text-center">
            <div className="text-gray-400 text-5xl mb-4">📊</div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              No Analysis Yet
            </h3>
            <p className="text-gray-600 mb-6">
              Run the comparable company analysis to see multiples and statistics
            </p>
            <button
              onClick={runAnalysis}
              disabled={analyzing}
              className="bg-primary-600 text-white px-6 py-3 rounded-md hover:bg-primary-700 transition disabled:opacity-50"
            >
              {analyzing ? 'Analyzing...' : 'Run Analysis Now'}
            </button>
          </div>
        ) : (
          <>
            {/* Target Company Summary */}
            {analysis.target && (
              <div className="bg-white rounded-lg shadow-md p-6 mb-8">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">
                  Target Company: {analysis.target.company_name}
                </h2>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div>
                    <p className="text-sm text-gray-500">Market Cap</p>
                    <p className="text-lg font-semibold text-gray-900">
                      {formatCurrency(analysis.target.market_cap)} {analysis.target.currency}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Current Price</p>
                    <p className="text-lg font-semibold text-gray-900">
                      {analysis.target.current_price.toFixed(2)} {analysis.target.currency}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">P/E Ratio</p>
                    <p className="text-lg font-semibold text-gray-900">
                      {formatMultiple(analysis.target.pe_ratio)}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">EV/EBITDA</p>
                    <p className="text-lg font-semibold text-gray-900">
                      {formatMultiple(analysis.target.ev_to_ebitda)}
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* Premium/Discount Analysis */}
            {analysis.implied_valuations && (
              <div className="bg-white rounded-lg shadow-md p-6 mb-8">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">
                  Valuation vs Peer Group
                </h2>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                  {Object.entries(analysis.implied_valuations).map(([key, value]) => {
                    if (value === null) return null;
                    const multipleName = key.replace('_premium_discount', '').toUpperCase();
                    const numValue = value as number;
                    const isPremium = numValue > 0;
                    return (
                      <div key={key} className="border border-gray-200 rounded-lg p-4">
                        <p className="text-xs text-gray-500 mb-1">{multipleName}</p>
                        <p className={`text-2xl font-bold ${isPremium ? 'text-red-600' : 'text-green-600'}`}>
                          {isPremium ? '+' : ''}{numValue.toFixed(2)}%
                        </p>
                        <p className="text-xs text-gray-500 mt-1">
                          {isPremium ? 'Premium' : 'Discount'} to peers
                        </p>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* Valuation Multiples Chart */}
            {multiplesChartData.length > 0 && (
              <div className="bg-white rounded-lg shadow-md p-6 mb-8">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">Valuation Multiples Comparison</h2>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={multiplesChartData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis label={{ value: 'Multiple', angle: -90, position: 'insideLeft' }} />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="P/E" fill="#3b82f6" />
                    <Bar dataKey="P/B" fill="#10b981" />
                    <Bar dataKey="EV/EBITDA" fill="#8b5cf6" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )}

            {/* Profitability Margins Chart */}
            {profitabilityChartData.length > 0 && (
              <div className="bg-white rounded-lg shadow-md p-6 mb-8">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">Profitability Margins (%)</h2>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={profitabilityChartData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis label={{ value: 'Margin (%)', angle: -90, position: 'insideLeft' }} />
                    <Tooltip formatter={(value: number) => `${value.toFixed(2)}%`} />
                    <Legend />
                    <Bar dataKey="Gross Margin" fill="#3b82f6" />
                    <Bar dataKey="Operating Margin" fill="#10b981" />
                    <Bar dataKey="Net Margin" fill="#f59e0b" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )}

            {/* Peer Statistics Table */}
            {analysis.peer_statistics && (
              <div className="bg-white rounded-lg shadow-md p-6 mb-8">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">Peer Group Statistics</h2>
                <div className="overflow-x-auto">
                  <table className="min-w-full">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Metric</th>
                        <th className="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase">Median</th>
                        <th className="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase">Mean</th>
                        <th className="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase">Min</th>
                        <th className="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase">Max</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200">
                      {Object.entries(analysis.peer_statistics).map(([key, stats]: [string, any]) => {
                        if (stats.count === 0) return null;
                        const isPercent = key.includes('margin') || key.includes('growth') || key.includes('roe') || key.includes('roa');
                        const isMultiple = key.includes('ratio') || key.includes('_to_');
                        const formatter = isPercent ? formatPercent : isMultiple ? formatMultiple : (v: number) => v.toFixed(2);
                        return (
                          <tr key={key}>
                            <td className="px-4 py-2 text-sm text-gray-900">{key.replace(/_/g, ' ').toUpperCase()}</td>
                            <td className="px-4 py-2 text-sm text-gray-700 text-right font-medium">{formatter(stats.median)}</td>
                            <td className="px-4 py-2 text-sm text-gray-700 text-right">{formatter(stats.mean)}</td>
                            <td className="px-4 py-2 text-sm text-gray-500 text-right">{formatter(stats.min)}</td>
                            <td className="px-4 py-2 text-sm text-gray-500 text-right">{formatter(stats.max)}</td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* Individual Peer Companies */}
            {analysis.peers && analysis.peers.length > 0 && (
              <div className="bg-white rounded-lg shadow-md p-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">Peer Company Details</h2>
                <div className="space-y-6">
                  {analysis.peers.map((peer: CompanyMetrics) => (
                    <div key={peer.ticker} className="border border-gray-200 rounded-lg p-4">
                      <h3 className="text-lg font-semibold text-gray-900 mb-3">
                        {peer.ticker} - {peer.company_name}
                      </h3>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div>
                          <p className="text-xs text-gray-500">Market Cap</p>
                          <p className="text-sm font-semibold">{formatCurrency(peer.market_cap)} {peer.currency}</p>
                        </div>
                        <div>
                          <p className="text-xs text-gray-500">P/E Ratio</p>
                          <p className="text-sm font-semibold">{formatMultiple(peer.pe_ratio)}</p>
                        </div>
                        <div>
                          <p className="text-xs text-gray-500">P/B Ratio</p>
                          <p className="text-sm font-semibold">{formatMultiple(peer.price_to_book)}</p>
                        </div>
                        <div>
                          <p className="text-xs text-gray-500">EV/EBITDA</p>
                          <p className="text-sm font-semibold">{formatMultiple(peer.ev_to_ebitda)}</p>
                        </div>
                        <div>
                          <p className="text-xs text-gray-500">Operating Margin</p>
                          <p className="text-sm font-semibold">{formatPercent(peer.operating_margin)}</p>
                        </div>
                        <div>
                          <p className="text-xs text-gray-500">ROE</p>
                          <p className="text-sm font-semibold">{formatPercent(peer.roe)}</p>
                        </div>
                        <div>
                          <p className="text-xs text-gray-500">Revenue Growth</p>
                          <p className="text-sm font-semibold">{formatPercent(peer.revenue_growth)}</p>
                        </div>
                        <div>
                          <p className="text-xs text-gray-500">Current Price</p>
                          <p className="text-sm font-semibold">{peer.current_price.toFixed(2)} {peer.currency}</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
