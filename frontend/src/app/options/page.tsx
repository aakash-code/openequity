'use client';

import React, { useState, useEffect } from 'react';
import { api } from '@/lib/api';

export default function OptionsChainPage() {
  const [ticker, setTicker] = useState('RELIANCE');
  const [chainData, setChainData] = useState<any>(null);
  const [selectedExpiry, setSelectedExpiry] = useState('');
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<'chain' | 'futures' | 'oi'>('chain');

  useEffect(() => {
    if (ticker) {
      fetchOptionsChain();
    }
  }, [ticker, selectedExpiry]);

  const fetchOptionsChain = async () => {
    setLoading(true);
    try {
      const data = await api.getOptionsChain(ticker, selectedExpiry || undefined);
      setChainData(data);
      if (!selectedExpiry && data.available_expiries?.length > 0) {
        setSelectedExpiry(data.available_expiries[0]);
      }
    } catch (error) {
      console.error('Error fetching options chain:', error);
    } finally {
      setLoading(false);
    }
  };

  const getMoneynessBadge = (moneyness: string) => {
    const colors = {
      'ITM': 'bg-green-100 text-green-700',
      'ATM': 'bg-yellow-100 text-yellow-700',
      'OTM': 'bg-gray-100 text-gray-700'
    };
    return colors[moneyness as keyof typeof colors] || 'bg-gray-100 text-gray-700';
  };

  const formatGreek = (value: number) => {
    return value?.toFixed(4) || '0.0000';
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-[1600px] mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Options Chain</h1>
          <p className="mt-2 text-gray-600">Real-time options data with Greeks and analytics</p>
        </div>

        {/* Search and Filters */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Stock Ticker</label>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={ticker}
                  onChange={(e) => setTicker(e.target.value.toUpperCase())}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                  placeholder="Enter ticker (e.g., RELIANCE)"
                />
                <button
                  onClick={fetchOptionsChain}
                  disabled={loading}
                  className="bg-primary-600 hover:bg-primary-700 text-white px-6 py-2 rounded-md transition disabled:opacity-50"
                >
                  {loading ? 'Loading...' : 'Search'}
                </button>
              </div>
            </div>

            {chainData?.available_expiries && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Expiry Date</label>
                <select
                  value={selectedExpiry}
                  onChange={(e) => setSelectedExpiry(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                >
                  {chainData.available_expiries.map((expiry: string) => (
                    <option key={expiry} value={expiry}>{expiry}</option>
                  ))}
                </select>
              </div>
            )}

            {chainData && (
              <div className="bg-blue-50 rounded-lg p-4">
                <p className="text-sm text-gray-600">Spot Price</p>
                <p className="text-2xl font-bold text-gray-900">₹{chainData.spot_price?.toLocaleString('en-IN')}</p>
                <p className="text-xs text-gray-500 mt-1">ATM: ₹{chainData.analytics?.atm_strike}</p>
              </div>
            )}
          </div>
        </div>

        {/* Analytics Summary */}
        {chainData && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div className="bg-white rounded-lg shadow p-4">
              <p className="text-sm text-gray-600">Max Pain</p>
              <p className="text-xl font-bold text-gray-900">₹{chainData.analytics?.max_pain}</p>
              <p className="text-xs text-gray-500 mt-1">Strike with min writer loss</p>
            </div>
            <div className="bg-white rounded-lg shadow p-4">
              <p className="text-sm text-gray-600">PCR (OI)</p>
              <p className="text-xl font-bold text-gray-900">{chainData.analytics?.pcr_oi}</p>
              <p className="text-xs text-gray-500 mt-1">Put-Call Ratio</p>
            </div>
            <div className="bg-white rounded-lg shadow p-4">
              <p className="text-sm text-gray-600">Total Call OI</p>
              <p className="text-xl font-bold text-green-600">{(chainData.analytics?.total_call_oi / 1000).toFixed(1)}K</p>
            </div>
            <div className="bg-white rounded-lg shadow p-4">
              <p className="text-sm text-gray-600">Total Put OI</p>
              <p className="text-xl font-bold text-red-600">{(chainData.analytics?.total_put_oi / 1000).toFixed(1)}K</p>
            </div>
          </div>
        )}

        {/* Options Chain Table */}
        {loading ? (
          <div className="flex justify-center py-12 bg-white rounded-lg">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
          </div>
        ) : chainData ? (
          <div className="bg-white rounded-lg shadow overflow-hidden">
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    {/* Calls Headers */}
                    <th colSpan={7} className="px-6 py-3 text-center text-xs font-medium text-green-700 uppercase tracking-wider bg-green-50">
                      Calls
                    </th>
                    {/* Strike */}
                    <th className="px-4 py-3 text-center text-xs font-medium text-gray-900 uppercase tracking-wider bg-yellow-50">
                      Strike
                    </th>
                    {/* Puts Headers */}
                    <th colSpan={7} className="px-6 py-3 text-center text-xs font-medium text-red-700 uppercase tracking-wider bg-red-50">
                      Puts
                    </th>
                  </tr>
                  <tr className="bg-gray-50">
                    {/* Calls */}
                    <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">OI</th>
                    <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Vol</th>
                    <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">IV</th>
                    <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">LTP</th>
                    <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Δ</th>
                    <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Θ</th>
                    <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">γ</th>
                    {/* Strike */}
                    <th className="px-4 py-2 text-center text-xs font-medium text-gray-700 uppercase bg-yellow-50"></th>
                    {/* Puts */}
                    <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">γ</th>
                    <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Θ</th>
                    <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Δ</th>
                    <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">LTP</th>
                    <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">IV</th>
                    <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Vol</th>
                    <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">OI</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {chainData.calls?.map((call: any, idx: number) => {
                    const put = chainData.puts[idx];
                    const isATM = call.moneyness === 'ATM';

                    return (
                      <tr key={call.strike} className={`${isATM ? 'bg-yellow-50' : 'hover:bg-gray-50'}`}>
                        {/* Call Data */}
                        <td className="px-3 py-3 text-sm text-gray-900">{(call.open_interest / 1000).toFixed(1)}K</td>
                        <td className="px-3 py-3 text-sm text-gray-600">{(call.volume / 1000).toFixed(1)}K</td>
                        <td className="px-3 py-3 text-sm text-gray-600">{call.implied_volatility}%</td>
                        <td className="px-3 py-3 text-sm font-semibold text-green-600">₹{call.last_price}</td>
                        <td className="px-3 py-3 text-xs text-gray-600">{formatGreek(call.delta)}</td>
                        <td className="px-3 py-3 text-xs text-gray-600">{formatGreek(call.theta)}</td>
                        <td className="px-3 py-3 text-xs text-gray-600">{formatGreek(call.gamma)}</td>

                        {/* Strike */}
                        <td className={`px-4 py-3 text-center font-bold ${isATM ? 'bg-yellow-100' : ''}`}>
                          <div>
                            <span className="text-gray-900">{call.strike}</span>
                            {isATM && (
                              <span className="ml-2 px-2 py-1 bg-yellow-200 text-yellow-800 text-xs rounded">ATM</span>
                            )}
                          </div>
                        </td>

                        {/* Put Data */}
                        <td className="px-3 py-3 text-xs text-gray-600">{formatGreek(put.gamma)}</td>
                        <td className="px-3 py-3 text-xs text-gray-600">{formatGreek(put.theta)}</td>
                        <td className="px-3 py-3 text-xs text-gray-600">{formatGreek(put.delta)}</td>
                        <td className="px-3 py-3 text-sm font-semibold text-red-600">₹{put.last_price}</td>
                        <td className="px-3 py-3 text-sm text-gray-600">{put.implied_volatility}%</td>
                        <td className="px-3 py-3 text-sm text-gray-600">{(put.volume / 1000).toFixed(1)}K</td>
                        <td className="px-3 py-3 text-sm text-gray-900">{(put.open_interest / 1000).toFixed(1)}K</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        ) : (
          <div className="text-center py-12 bg-white rounded-lg">
            <p className="text-gray-500">Enter a ticker and click Search to view options chain</p>
          </div>
        )}

        {/* Greeks Legend */}
        {chainData && (
          <div className="mt-6 bg-white rounded-lg shadow p-6">
            <h3 className="font-semibold text-gray-900 mb-3">Greeks Guide</h3>
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4 text-sm">
              <div>
                <span className="font-semibold">Delta (Δ):</span> Price sensitivity to ₹1 move in underlying
              </div>
              <div>
                <span className="font-semibold">Gamma (γ):</span> Rate of change of Delta
              </div>
              <div>
                <span className="font-semibold">Theta (Θ):</span> Daily time decay (negative = loss per day)
              </div>
              <div>
                <span className="font-semibold">Vega (V):</span> Sensitivity to 1% change in volatility
              </div>
              <div>
                <span className="font-semibold">PCR:</span> Bullish if &gt;1.2, Bearish if &lt;0.8
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
