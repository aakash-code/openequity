'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { api } from '@/lib/api';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar } from 'recharts';

export default function IndianMarketPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [marketStatus, setMarketStatus] = useState<any>(null);
  const [indices, setIndices] = useState<any[]>([]);
  const [fiiDiiData, setFiiDiiData] = useState<any[]>([]);
  const [sectors, setSectors] = useState<string[]>([]);
  const [exchangeRate, setExchangeRate] = useState<any>(null);

  // Currency converter state
  const [amount, setAmount] = useState<string>('1000');
  const [fromCurrency, setFromCurrency] = useState('USD');
  const [toCurrency, setToCurrency] = useState('INR');
  const [convertedAmount, setConvertedAmount] = useState<any>(null);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    setLoading(true);
    try {
      const [statusData, indicesData, fiiDiiRes, sectorsData, rateData] = await Promise.all([
        api.getMarketStatus(),
        api.getIndianIndices(),
        api.getFiiDiiActivity(30),
        api.getNseSectors(),
        api.getExchangeRate('USD', 'INR')
      ]);

      setMarketStatus(statusData);
      setIndices(indicesData.indices || []);
      setFiiDiiData(fiiDiiRes.data || []);
      setSectors(sectorsData.sectors || []);
      setExchangeRate(rateData);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleConvertCurrency = async () => {
    try {
      const result = await api.convertCurrency(parseFloat(amount), fromCurrency, toCurrency);
      setConvertedAmount(result);
    } catch (error) {
      console.error('Error converting currency:', error);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading Indian market data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Indian Market Dashboard</h1>
          <p className="mt-2 text-gray-600">NSE/BSE market data, indices, and institutional activity</p>
        </div>

        {/* Market Status Banner */}
        {marketStatus && (
          <div className={`mb-6 p-4 rounded-lg ${marketStatus.is_open ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'}`}>
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-lg font-semibold text-gray-900">
                  Market Status: {marketStatus.status}
                </h2>
                <p className="text-sm text-gray-600 mt-1">
                  {marketStatus.message}
                </p>
              </div>
              <div className="text-sm text-gray-600">
                <div>Market Hours: {marketStatus.market_hours.open} - {marketStatus.market_hours.close} IST</div>
                {marketStatus.next_open && (
                  <div className="mt-1">Next Open: {marketStatus.next_open}</div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Exchange Rate */}
        {exchangeRate && (
          <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold text-gray-900">USD/INR Exchange Rate</h3>
                <p className="text-2xl font-bold text-primary-600 mt-1">
                  {exchangeRate.from_symbol}1 = {exchangeRate.to_symbol}{exchangeRate.rate.toFixed(2)}
                </p>
              </div>
              <div className="text-xs text-gray-500">
                Updated: {new Date(exchangeRate.timestamp).toLocaleString()}
              </div>
            </div>
          </div>
        )}

        {/* Indian Indices */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Market Indices</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {indices.map((index) => (
              <div key={index.symbol} className="bg-white rounded-lg shadow p-6 border border-gray-200">
                <div className="flex justify-between items-start mb-2">
                  <h3 className="text-lg font-semibold text-gray-900">{index.name}</h3>
                  <span className="text-xs text-gray-500">{index.symbol}</span>
                </div>
                <p className="text-sm text-gray-600 mb-3">{index.description}</p>
                <div className="text-2xl font-bold text-gray-900">
                  {index.current_value?.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) || 'N/A'}
                </div>
                {index.change_percent !== undefined && (
                  <div className={`text-sm mt-2 ${index.change_percent >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {index.change_percent >= 0 ? '▲' : '▼'} {Math.abs(index.change_percent).toFixed(2)}%
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* FII/DII Activity Chart */}
        {fiiDiiData.length > 0 && (
          <div className="mb-8 bg-white rounded-lg shadow p-6 border border-gray-200">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              FII/DII Activity (Last 30 Days)
            </h2>
            <p className="text-sm text-gray-600 mb-4">
              Foreign and Domestic Institutional Investor net buy/sell activity
            </p>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={fiiDiiData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip formatter={(value: any) => `₹${(value / 10000000).toFixed(2)} Cr`} />
                <Legend />
                <Bar dataKey="fii_net" name="FII Net (Cr)" fill="#3b82f6" />
                <Bar dataKey="dii_net" name="DII Net (Cr)" fill="#10b981" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Currency Converter */}
          <div className="bg-white rounded-lg shadow p-6 border border-gray-200">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Currency Converter</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Amount</label>
                <input
                  type="number"
                  value={amount}
                  onChange={(e) => setAmount(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                  placeholder="Enter amount"
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">From</label>
                  <select
                    value={fromCurrency}
                    onChange={(e) => setFromCurrency(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                  >
                    <option value="USD">USD</option>
                    <option value="INR">INR</option>
                    <option value="EUR">EUR</option>
                    <option value="GBP">GBP</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">To</label>
                  <select
                    value={toCurrency}
                    onChange={(e) => setToCurrency(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                  >
                    <option value="INR">INR</option>
                    <option value="USD">USD</option>
                    <option value="EUR">EUR</option>
                    <option value="GBP">GBP</option>
                  </select>
                </div>
              </div>
              <button
                onClick={handleConvertCurrency}
                className="w-full bg-primary-600 hover:bg-primary-700 text-white px-4 py-2 rounded-md transition"
              >
                Convert
              </button>
              {convertedAmount && (
                <div className="mt-4 p-4 bg-gray-50 rounded-md border border-gray-200">
                  <div className="text-sm text-gray-600">Converted Amount:</div>
                  <div className="text-2xl font-bold text-gray-900 mt-1">
                    {convertedAmount.to_formatted_indian || convertedAmount.to_formatted}
                  </div>
                  <div className="text-xs text-gray-500 mt-2">
                    Exchange Rate: {convertedAmount.exchange_rate.toFixed(4)}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* NSE Sectors */}
          <div className="bg-white rounded-lg shadow p-6 border border-gray-200">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">NSE Sectors</h2>
            <div className="grid grid-cols-2 gap-2 max-h-96 overflow-y-auto">
              {sectors.map((sector) => (
                <div
                  key={sector}
                  className="px-3 py-2 bg-gray-50 rounded-md text-sm text-gray-700 border border-gray-200"
                >
                  {sector}
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="mt-8 bg-white rounded-lg shadow p-6 border border-gray-200">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Quick Actions</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <button
              onClick={() => router.push('/screener')}
              className="p-4 border-2 border-primary-200 rounded-lg hover:bg-primary-50 transition text-left"
            >
              <h3 className="font-semibold text-gray-900 mb-1">Stock Screener</h3>
              <p className="text-sm text-gray-600">Filter stocks by custom criteria</p>
            </button>
            <button
              onClick={() => router.push('/companies')}
              className="p-4 border-2 border-primary-200 rounded-lg hover:bg-primary-50 transition text-left"
            >
              <h3 className="font-semibold text-gray-900 mb-1">Browse Companies</h3>
              <p className="text-sm text-gray-600">Explore Indian companies</p>
            </button>
            <button
              onClick={() => router.push('/portfolios')}
              className="p-4 border-2 border-primary-200 rounded-lg hover:bg-primary-50 transition text-left"
            >
              <h3 className="font-semibold text-gray-900 mb-1">My Portfolios</h3>
              <p className="text-sm text-gray-600">Track your investments</p>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
