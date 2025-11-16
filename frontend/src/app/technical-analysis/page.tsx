'use client';

import React, { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import { Line, Bar, ComposedChart, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ReferenceLine } from 'recharts';
import { useTickerStream } from '@/hooks/useMarketData';
import WebSocketStatus from '@/components/WebSocketStatus';

export default function TechnicalAnalysisPage() {
  const [ticker, setTicker] = useState('RELIANCE');
  const [exchange, setExchange] = useState('NSE');
  const [interval, setInterval] = useState('1d');
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<'overview' | 'indicators' | 'patterns' | 'levels'>('overview');
  const [enableLiveData, setEnableLiveData] = useState(true);

  const [analysisData, setAnalysisData] = useState<any>(null);
  const [selectedIndicators, setSelectedIndicators] = useState({
    sma_20: true,
    ema_12: false,
    bb: true,
    rsi: true,
    macd: true
  });

  // WebSocket for live ticker data
  const { ticker: liveTickerData, priceHistory, isConnected } = useTickerStream(ticker, exchange, enableLiveData);

  useEffect(() => {
    if (ticker) {
      fetchAnalysis();
    }
  }, [ticker, exchange, interval]);

  const fetchAnalysis = async () => {
    setLoading(true);
    try {
      const data = await api.getComprehensiveTechnicalAnalysis(ticker, exchange, interval);
      setAnalysisData(data);
    } catch (error) {
      console.error('Error fetching technical analysis:', error);
    } finally {
      setLoading(false);
    }
  };

  const prepareChartData = () => {
    if (!analysisData?.ohlcv_data || !analysisData?.indicators) return [];

    const ohlcv = analysisData.ohlcv_data;
    const indicators = analysisData.indicators.indicators;

    return ohlcv.map((bar: any, idx: number) => ({
      timestamp: bar.timestamp || bar.date || `Bar ${idx}`,
      close: bar.close,
      high: bar.high,
      low: bar.low,
      open: bar.open,
      volume: bar.volume,
      sma_20: indicators.sma_20?.[idx],
      sma_50: indicators.sma_50?.[idx],
      ema_12: indicators.ema_12?.[idx],
      ema_26: indicators.ema_26?.[idx],
      bb_upper: indicators.bb_upper?.[idx],
      bb_middle: indicators.bb_middle?.[idx],
      bb_lower: indicators.bb_lower?.[idx],
      rsi: indicators.rsi?.[idx],
      macd_line: indicators.macd_line?.[idx],
      macd_signal: indicators.macd_signal?.[idx],
      macd_histogram: indicators.macd_histogram?.[idx]
    }));
  };

  const chartData = prepareChartData();

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-[1800px] mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Technical Analysis</h1>
              <p className="mt-2 text-gray-600">Advanced charting with 20+ indicators and pattern recognition</p>
            </div>
            <WebSocketStatus isConnected={isConnected} size="md" />
          </div>
        </div>

        {/* Live Ticker Banner */}
        {liveTickerData && enableLiveData && (
          <div className="bg-gradient-to-r from-blue-500 to-blue-600 rounded-lg shadow-lg p-6 mb-6 text-white">
            <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
              <div className="md:col-span-2">
                <div className="flex items-center gap-2">
                  <h2 className="text-2xl font-bold">{ticker}</h2>
                  <span className="text-sm opacity-80">{exchange}</span>
                  <div className="flex items-center gap-1 ml-2">
                    <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
                    <span className="text-xs">LIVE</span>
                  </div>
                </div>
                <p className="text-3xl font-bold mt-2">₹{liveTickerData.ltp.toLocaleString('en-IN', {minimumFractionDigits: 2})}</p>
              </div>
              <div>
                <p className="text-sm opacity-80">Change</p>
                <p className={`text-xl font-semibold ${liveTickerData.change >= 0 ? 'text-green-300' : 'text-red-300'}`}>
                  {liveTickerData.change >= 0 ? '+' : ''}{liveTickerData.change.toFixed(2)}
                </p>
              </div>
              <div>
                <p className="text-sm opacity-80">Change %</p>
                <p className={`text-xl font-semibold ${liveTickerData.change_percent >= 0 ? 'text-green-300' : 'text-red-300'}`}>
                  {liveTickerData.change_percent >= 0 ? '+' : ''}{liveTickerData.change_percent.toFixed(2)}%
                </p>
              </div>
              <div>
                <p className="text-sm opacity-80">Last Update</p>
                <p className="text-sm font-medium">{new Date(liveTickerData.timestamp).toLocaleTimeString()}</p>
                <button
                  onClick={() => setEnableLiveData(!enableLiveData)}
                  className="mt-2 text-xs bg-white/20 hover:bg-white/30 px-3 py-1 rounded transition"
                >
                  {enableLiveData ? 'Pause Live' : 'Resume Live'}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Controls */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Stock Ticker</label>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={ticker}
                  onChange={(e) => setTicker(e.target.value.toUpperCase())}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                  placeholder="e.g., RELIANCE"
                />
                <button
                  onClick={fetchAnalysis}
                  disabled={loading}
                  className="bg-primary-600 hover:bg-primary-700 text-white px-6 py-2 rounded-md transition disabled:opacity-50"
                >
                  {loading ? 'Loading...' : 'Analyze'}
                </button>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Exchange</label>
              <select
                value={exchange}
                onChange={(e) => setExchange(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option value="NSE">NSE</option>
                <option value="BSE">BSE</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Timeframe</label>
              <select
                value={interval}
                onChange={(e) => setInterval(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option value="1m">1 Minute</option>
                <option value="5m">5 Minutes</option>
                <option value="15m">15 Minutes</option>
                <option value="1h">1 Hour</option>
                <option value="1d">1 Day</option>
                <option value="1w">1 Week</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Indicators</label>
              <div className="flex flex-wrap gap-2">
                <button
                  onClick={() => setSelectedIndicators({...selectedIndicators, sma_20: !selectedIndicators.sma_20})}
                  className={`px-3 py-1 rounded text-xs ${selectedIndicators.sma_20 ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-700'}`}
                >
                  SMA 20
                </button>
                <button
                  onClick={() => setSelectedIndicators({...selectedIndicators, bb: !selectedIndicators.bb})}
                  className={`px-3 py-1 rounded text-xs ${selectedIndicators.bb ? 'bg-purple-500 text-white' : 'bg-gray-200 text-gray-700'}`}
                >
                  BB
                </button>
                <button
                  onClick={() => setSelectedIndicators({...selectedIndicators, rsi: !selectedIndicators.rsi})}
                  className={`px-3 py-1 rounded text-xs ${selectedIndicators.rsi ? 'bg-green-500 text-white' : 'bg-gray-200 text-gray-700'}`}
                >
                  RSI
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="bg-white rounded-lg shadow mb-6">
          <div className="border-b border-gray-200">
            <div className="flex">
              <button
                onClick={() => setActiveTab('overview')}
                className={`px-6 py-3 font-medium ${activeTab === 'overview' ? 'border-b-2 border-primary-600 text-primary-600' : 'text-gray-500 hover:text-gray-700'}`}
              >
                Overview
              </button>
              <button
                onClick={() => setActiveTab('indicators')}
                className={`px-6 py-3 font-medium ${activeTab === 'indicators' ? 'border-b-2 border-primary-600 text-primary-600' : 'text-gray-500 hover:text-gray-700'}`}
              >
                Indicators
              </button>
              <button
                onClick={() => setActiveTab('patterns')}
                className={`px-6 py-3 font-medium ${activeTab === 'patterns' ? 'border-b-2 border-primary-600 text-primary-600' : 'text-gray-500 hover:text-gray-700'}`}
              >
                Patterns
              </button>
              <button
                onClick={() => setActiveTab('levels')}
                className={`px-6 py-3 font-medium ${activeTab === 'levels' ? 'border-b-2 border-primary-600 text-primary-600' : 'text-gray-500 hover:text-gray-700'}`}
              >
                Support/Resistance
              </button>
            </div>
          </div>
        </div>

        {/* Content */}
        {loading ? (
          <div className="flex justify-center py-12 bg-white rounded-lg">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
          </div>
        ) : analysisData ? (
          <>
            {activeTab === 'overview' && (
              <div className="space-y-6">
                {/* Summary Cards */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <div className="bg-white rounded-lg shadow p-4">
                    <p className="text-sm text-gray-600">Trend</p>
                    <p className="text-2xl font-bold text-gray-900 capitalize">{analysisData.chart_patterns?.trend?.trend || 'N/A'}</p>
                    <p className="text-xs text-gray-500 mt-1">Strength: {(analysisData.chart_patterns?.trend?.strength * 100).toFixed(1)}%</p>
                  </div>
                  <div className="bg-white rounded-lg shadow p-4">
                    <p className="text-sm text-gray-600">Chart Patterns</p>
                    <p className="text-2xl font-bold text-gray-900">{analysisData.chart_patterns?.summary?.total || 0}</p>
                    <p className="text-xs text-green-600">Bullish: {analysisData.chart_patterns?.summary?.bullish || 0}</p>
                    <p className="text-xs text-red-600">Bearish: {analysisData.chart_patterns?.summary?.bearish || 0}</p>
                  </div>
                  <div className="bg-white rounded-lg shadow p-4">
                    <p className="text-sm text-gray-600">Candlestick Patterns</p>
                    <p className="text-2xl font-bold text-gray-900">{analysisData.candlestick_patterns?.summary?.total || 0}</p>
                    <p className="text-xs text-green-600">Bullish: {analysisData.candlestick_patterns?.summary?.bullish || 0}</p>
                    <p className="text-xs text-red-600">Bearish: {analysisData.candlestick_patterns?.summary?.bearish || 0}</p>
                  </div>
                  <div className="bg-white rounded-lg shadow p-4">
                    <p className="text-sm text-gray-600">Current Price</p>
                    <p className="text-2xl font-bold text-gray-900">₹{analysisData.support_resistance?.current_price?.toLocaleString('en-IN')}</p>
                  </div>
                </div>

                {/* Price Chart */}
                <div className="bg-white rounded-lg shadow p-6">
                  <h2 className="text-lg font-semibold mb-4">Price Chart</h2>
                  <ResponsiveContainer width="100%" height={400}>
                    <ComposedChart data={chartData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="timestamp" tick={{fontSize: 12}} />
                      <YAxis yAxisId="left" domain={['auto', 'auto']} />
                      <Tooltip />
                      <Legend />

                      <Line yAxisId="left" type="monotone" dataKey="close" stroke="#3B82F6" strokeWidth={2} dot={false} name="Close" />

                      {selectedIndicators.sma_20 && (
                        <Line yAxisId="left" type="monotone" dataKey="sma_20" stroke="#10B981" strokeWidth={1.5} dot={false} name="SMA 20" />
                      )}

                      {selectedIndicators.bb && (
                        <>
                          <Line yAxisId="left" type="monotone" dataKey="bb_upper" stroke="#9333EA" strokeWidth={1} dot={false} name="BB Upper" strokeDasharray="3 3" />
                          <Line yAxisId="left" type="monotone" dataKey="bb_middle" stroke="#9333EA" strokeWidth={1} dot={false} name="BB Middle" />
                          <Line yAxisId="left" type="monotone" dataKey="bb_lower" stroke="#9333EA" strokeWidth={1} dot={false} name="BB Lower" strokeDasharray="3 3" />
                        </>
                      )}
                    </ComposedChart>
                  </ResponsiveContainer>
                </div>

                {/* RSI */}
                {selectedIndicators.rsi && (
                  <div className="bg-white rounded-lg shadow p-6">
                    <h2 className="text-lg font-semibold mb-4">RSI (Relative Strength Index)</h2>
                    <ResponsiveContainer width="100%" height={200}>
                      <ComposedChart data={chartData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="timestamp" tick={{fontSize: 12}} />
                        <YAxis domain={[0, 100]} />
                        <Tooltip />
                        <Legend />

                        <ReferenceLine y={70} stroke="#EF4444" strokeDasharray="3 3" label="Overbought" />
                        <ReferenceLine y={30} stroke="#10B981" strokeDasharray="3 3" label="Oversold" />
                        <ReferenceLine y={50} stroke="#6B7280" strokeDasharray="2 2" />

                        <Line type="monotone" dataKey="rsi" stroke="#F59E0B" strokeWidth={2} dot={false} name="RSI" />
                      </ComposedChart>
                    </ResponsiveContainer>
                  </div>
                )}

                {/* MACD */}
                {selectedIndicators.macd && (
                  <div className="bg-white rounded-lg shadow p-6">
                    <h2 className="text-lg font-semibold mb-4">MACD</h2>
                    <ResponsiveContainer width="100%" height={200}>
                      <ComposedChart data={chartData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="timestamp" tick={{fontSize: 12}} />
                        <YAxis />
                        <Tooltip />
                        <Legend />

                        <Bar dataKey="macd_histogram" fill="#94A3B8" name="Histogram" />
                        <Line type="monotone" dataKey="macd_line" stroke="#3B82F6" strokeWidth={2} dot={false} name="MACD" />
                        <Line type="monotone" dataKey="macd_signal" stroke="#EF4444" strokeWidth={2} dot={false} name="Signal" />
                        <ReferenceLine y={0} stroke="#6B7280" />
                      </ComposedChart>
                    </ResponsiveContainer>
                  </div>
                )}
              </div>
            )}

            {activeTab === 'indicators' && (
              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-lg font-semibold mb-4">Technical Indicators Summary</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {analysisData.indicators?.indicators && Object.entries(analysisData.indicators.indicators).map(([key, values]: [string, any]) => {
                    const latestValue = values[values.length - 1];
                    if (latestValue === null || latestValue === undefined) return null;

                    return (
                      <div key={key} className="border rounded-lg p-4">
                        <p className="text-sm text-gray-600 uppercase">{key.replace(/_/g, ' ')}</p>
                        <p className="text-xl font-bold text-gray-900">{typeof latestValue === 'number' ? latestValue.toFixed(2) : latestValue}</p>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {activeTab === 'patterns' && (
              <div className="space-y-6">
                {/* Chart Patterns */}
                <div className="bg-white rounded-lg shadow p-6">
                  <h2 className="text-lg font-semibold mb-4">Chart Patterns</h2>
                  {analysisData.chart_patterns?.patterns?.length > 0 ? (
                    <div className="space-y-3">
                      {analysisData.chart_patterns.patterns.map((pattern: any, idx: number) => (
                        <div key={idx} className="border-l-4 border-primary-500 bg-primary-50 p-4 rounded">
                          <div className="flex items-start justify-between">
                            <div>
                              <p className="font-semibold capitalize">{pattern.pattern.replace(/_/g, ' ')}</p>
                              <p className={`text-sm ${pattern.type === 'bullish' ? 'text-green-600' : pattern.type === 'bearish' ? 'text-red-600' : 'text-gray-600'}`}>
                                {pattern.type.toUpperCase()}
                              </p>
                            </div>
                            {pattern.confidence && (
                              <span className="px-3 py-1 bg-white rounded-full text-xs font-medium">
                                Confidence: {(pattern.confidence * 100).toFixed(0)}%
                              </span>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-gray-500">No chart patterns detected</p>
                  )}
                </div>

                {/* Candlestick Patterns */}
                <div className="bg-white rounded-lg shadow p-6">
                  <h2 className="text-lg font-semibold mb-4">Candlestick Patterns (Recent 20 Bars)</h2>
                  {analysisData.candlestick_patterns?.patterns?.length > 0 ? (
                    <div className="space-y-3">
                      {analysisData.candlestick_patterns.patterns.map((pattern: any, idx: number) => (
                        <div key={idx} className="border-l-4 border-primary-500 bg-gray-50 p-4 rounded">
                          <div className="flex items-start justify-between">
                            <div>
                              <p className="font-semibold capitalize">{pattern.pattern.replace(/_/g, ' ')}</p>
                              <p className={`text-sm ${pattern.type === 'bullish' ? 'text-green-600' : pattern.type === 'bearish' ? 'text-red-600' : 'text-gray-600'}`}>
                                {pattern.type.toUpperCase()} - {pattern.description}
                              </p>
                              <p className="text-xs text-gray-500 mt-1">{pattern.timestamp}</p>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-gray-500">No candlestick patterns detected</p>
                  )}
                </div>
              </div>
            )}

            {activeTab === 'levels' && (
              <div className="space-y-6">
                {/* Current Position */}
                <div className="bg-white rounded-lg shadow p-6">
                  <h2 className="text-lg font-semibold mb-4">Current Price Position</h2>
                  <div className="text-center">
                    <p className="text-4xl font-bold text-gray-900">₹{analysisData.support_resistance?.current_price?.toLocaleString('en-IN')}</p>
                    <p className="text-gray-600 mt-2">{ticker} • {exchange}</p>
                  </div>
                </div>

                {/* Support Levels */}
                <div className="bg-white rounded-lg shadow p-6">
                  <h2 className="text-lg font-semibold mb-4">Support Levels</h2>
                  <div className="space-y-3">
                    {analysisData.support_resistance?.nearest_support?.map((level: any, idx: number) => (
                      <div key={idx} className="flex items-center justify-between p-3 bg-green-50 border border-green-200 rounded">
                        <div>
                          <p className="font-semibold text-green-900">₹{level.price.toLocaleString('en-IN', {minimumFractionDigits: 2})}</p>
                          <p className="text-xs text-green-700 capitalize">{level.type.replace(/_/g, ' ')}</p>
                        </div>
                        <div className="text-right">
                          <p className="text-sm text-green-700">Strength: {level.strength}</p>
                          <p className="text-xs text-green-600">{((analysisData.support_resistance.current_price - level.price) / analysisData.support_resistance.current_price * 100).toFixed(2)}% below</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Resistance Levels */}
                <div className="bg-white rounded-lg shadow p-6">
                  <h2 className="text-lg font-semibold mb-4">Resistance Levels</h2>
                  <div className="space-y-3">
                    {analysisData.support_resistance?.nearest_resistance?.map((level: any, idx: number) => (
                      <div key={idx} className="flex items-center justify-between p-3 bg-red-50 border border-red-200 rounded">
                        <div>
                          <p className="font-semibold text-red-900">₹{level.price.toLocaleString('en-IN', {minimumFractionDigits: 2})}</p>
                          <p className="text-xs text-red-700 capitalize">{level.type.replace(/_/g, ' ')}</p>
                        </div>
                        <div className="text-right">
                          <p className="text-sm text-red-700">Strength: {level.strength}</p>
                          <p className="text-xs text-red-600">{((level.price - analysisData.support_resistance.current_price) / analysisData.support_resistance.current_price * 100).toFixed(2)}% above</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Pivot Points */}
                {analysisData.support_resistance?.pivot_points && (
                  <div className="bg-white rounded-lg shadow p-6">
                    <h2 className="text-lg font-semibold mb-4">Pivot Points (Standard)</h2>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      {Object.entries(analysisData.support_resistance.pivot_points.standard).map(([key, value]: [string, any]) => (
                        <div key={key} className="border rounded p-3 text-center">
                          <p className="text-xs text-gray-600 uppercase">{key}</p>
                          <p className="text-lg font-semibold">₹{value.toFixed(2)}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Fibonacci Levels */}
                {analysisData.support_resistance?.fibonacci_levels && (
                  <div className="bg-white rounded-lg shadow p-6">
                    <h2 className="text-lg font-semibold mb-4">Fibonacci Retracement</h2>
                    <div className="space-y-2">
                      {Object.entries(analysisData.support_resistance.fibonacci_levels)
                        .filter(([key]) => key.includes('%'))
                        .map(([key, value]: [string, any]) => (
                          <div key={key} className="flex justify-between items-center p-2 border-b">
                            <span className="font-medium">{key}</span>
                            <span className="text-gray-900">₹{typeof value === 'number' ? value.toFixed(2) : value}</span>
                          </div>
                        ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </>
        ) : (
          <div className="text-center py-12 bg-white rounded-lg">
            <p className="text-gray-500">Enter a ticker and click Analyze to view technical analysis</p>
          </div>
        )}
      </div>
    </div>
  );
}
