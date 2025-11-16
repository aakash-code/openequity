'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useParams } from 'next/navigation';
import api from '@/lib/api';
import {
  PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip,
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
  LineChart, Line, AreaChart, Area
} from 'recharts';

// [Previous interfaces remain the same - Position, Transaction, Portfolio]
interface Position {
  ticker: string;
  quantity: number;
  avg_cost: number;
  total_cost: number;
  current_price: number;
  current_value: number;
  unrealized_gain: number;
  unrealized_gain_percent: number;
  weight: number;
}

interface Transaction {
  id: string;
  ticker: string;
  transaction_type: string;
  transaction_date: string;
  quantity: number;
  price: number;
  commission: number;
  total_amount: number;
  notes: string;
  created_at: string;
}

interface Portfolio {
  id: string;
  name: string;
  description: string;
  currency: string;
  strategy: string;
  tags: string[];
  is_public: boolean;
  created_at: string;
  updated_at: string;
  total_value: number;
  total_cost: number;
  total_gain: number;
  total_return_percent: number;
  position_count: number;
  positions: Position[];
  concentration: {
    top_position_weight: number;
    top_3_weight: number;
    top_5_weight: number;
    herfindahl_index: number;
  };
  transaction_count: number;
}

export default function PortfolioDetailPage() {
  const router = useRouter();
  const params = useParams();
  const portfolioId = params.id as string;

  // Tab state
  const [activeTab, setActiveTab] = useState('overview');

  // Existing states
  const [portfolio, setPortfolio] = useState<Portfolio | null>(null);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showAddTransaction, setShowAddTransaction] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [deletingPortfolio, setDeletingPortfolio] = useState(false);

  // Analytics states
  const [performance, setPerformance] = useState<any>(null);
  const [riskMetrics, setRiskMetrics] = useState<any>(null);
  const [benchmarkComparison, setBenchmarkComparison] = useState<any>(null);
  const [loadingAnalytics, setLoadingAnalytics] = useState(false);
  const [selectedBenchmark, setSelectedBenchmark] = useState('SPY');

  // Add transaction form state
  const [newTransaction, setNewTransaction] = useState({
    ticker: '',
    transaction_type: 'buy',
    transaction_date: new Date().toISOString().split('T')[0],
    quantity: '',
    price: '',
    commission: '0',
    notes: '',
  });
  const [addingTransaction, setAddingTransaction] = useState(false);

  useEffect(() => {
    fetchPortfolioData();
    fetchTransactions();
  }, [portfolioId]);

  useEffect(() => {
    if (activeTab === 'performance' && !performance) {
      fetchPerformanceData();
    } else if (activeTab === 'risk' && !riskMetrics) {
      fetchRiskData();
    }
  }, [activeTab]);

  const fetchPortfolioData = async () => {
    try {
      setLoading(true);
      const data = await api.getPortfolio(portfolioId);
      setPortfolio(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load portfolio');
    } finally {
      setLoading(false);
    }
  };

  const fetchTransactions = async () => {
    try {
      const response = await api.getTransactions(portfolioId, 0, 100);
      setTransactions(response.transactions || []);
    } catch (err: any) {
      console.error('Failed to load transactions:', err);
    }
  };

  const fetchPerformanceData = async () => {
    setLoadingAnalytics(true);
    try {
      const [perfData, benchData] = await Promise.all([
        api.getPortfolioPerformance(portfolioId),
        api.getPortfolioBenchmarkComparison(portfolioId, selectedBenchmark)
      ]);
      setPerformance(perfData.performance);
      setBenchmarkComparison(benchData.comparison);
    } catch (err: any) {
      console.error('Failed to load performance data:', err);
    } finally {
      setLoadingAnalytics(false);
    }
  };

  const fetchRiskData = async () => {
    setLoadingAnalytics(true);
    try {
      const riskData = await api.getPortfolioRiskMetrics(portfolioId, selectedBenchmark);
      setRiskMetrics(riskData.risk_metrics);
    } catch (err: any) {
      console.error('Failed to load risk data:', err);
    } finally {
      setLoadingAnalytics(false);
    }
  };

  const handleAddTransaction = async (e: React.FormEvent) => {
    e.preventDefault();
    setAddingTransaction(true);
    setError('');

    try {
      await api.addTransaction(portfolioId, {
        ticker: newTransaction.ticker.toUpperCase(),
        transaction_type: newTransaction.transaction_type,
        transaction_date: new Date(newTransaction.transaction_date).toISOString(),
        quantity: parseFloat(newTransaction.quantity),
        price: parseFloat(newTransaction.price),
        commission: parseFloat(newTransaction.commission),
        notes: newTransaction.notes,
      });

      setShowAddTransaction(false);
      setNewTransaction({
        ticker: '',
        transaction_type: 'buy',
        transaction_date: new Date().toISOString().split('T')[0],
        quantity: '',
        price: '',
        commission: '0',
        notes: '',
      });

      // Refresh data
      await fetchPortfolioData();
      await fetchTransactions();
      // Clear analytics so they reload
      setPerformance(null);
      setRiskMetrics(null);
      setBenchmarkComparison(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to add transaction');
    } finally {
      setAddingTransaction(false);
    }
  };

  const handleDeleteTransaction = async (transactionId: string) => {
    if (!confirm('Are you sure you want to delete this transaction?')) return;

    try {
      await api.deleteTransaction(portfolioId, transactionId);
      await fetchPortfolioData();
      await fetchTransactions();
      // Clear analytics so they reload
      setPerformance(null);
      setRiskMetrics(null);
      setBenchmarkComparison(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to delete transaction');
    }
  };

  const handleDeletePortfolio = async () => {
    setDeletingPortfolio(true);
    try {
      await api.deletePortfolio(portfolioId);
      router.push('/portfolios');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to delete portfolio');
      setDeletingPortfolio(false);
    }
  };

  const getCurrencySymbol = (currency: string) => {
    return currency === 'INR' ? '₹' : '$';
  };

  const formatNumber = (num: number, decimals: number = 2) => {
    return num.toLocaleString('en-US', {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals,
    });
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading portfolio...</p>
        </div>
      </div>
    );
  }

  if (error && !portfolio) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600 mb-4">{error}</p>
          <button
            onClick={() => router.push('/portfolios')}
            className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
          >
            Back to Portfolios
          </button>
        </div>
      </div>
    );
  }

  if (!portfolio) return null;

  const currencySymbol = getCurrencySymbol(portfolio.currency);

  // Prepare chart data
  const allocationData = portfolio.positions.map((pos) => ({
    name: pos.ticker,
    value: pos.current_value,
    weight: pos.weight,
  }));

  const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899', '#14B8A6', '#F97316'];

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={() => router.push('/portfolios')}
            className="text-primary-600 hover:text-primary-700 mb-4 flex items-center gap-2"
          >
            ← Back to Portfolios
          </button>

          <div className="flex justify-between items-start mb-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">{portfolio.name}</h1>
              {portfolio.description && (
                <p className="mt-2 text-gray-600">{portfolio.description}</p>
              )}
              <div className="flex items-center gap-3 mt-3">
                {portfolio.strategy && (
                  <span className="px-3 py-1 bg-primary-100 text-primary-700 rounded-md text-sm">
                    {portfolio.strategy}
                  </span>
                )}
                <span className="px-3 py-1 bg-gray-100 text-gray-700 rounded-md text-sm">
                  {portfolio.currency}
                </span>
                {portfolio.tags.map((tag, idx) => (
                  <span key={idx} className="px-3 py-1 bg-gray-100 text-gray-600 rounded-md text-sm">
                    {tag}
                  </span>
                ))}
              </div>
            </div>
            <div className="flex gap-3">
              <button
                onClick={() => setShowAddTransaction(true)}
                className="px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors font-medium"
              >
                + Add Transaction
              </button>
              <button
                onClick={() => setShowDeleteConfirm(true)}
                className="px-6 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors font-medium"
              >
                Delete
              </button>
            </div>
          </div>

          {/* Tab Navigation */}
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8">
              <button
                onClick={() => setActiveTab('overview')}
                className={`${
                  activeTab === 'overview'
                    ? 'border-primary-600 text-primary-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm transition`}
              >
                Overview
              </button>
              <button
                onClick={() => setActiveTab('performance')}
                className={`${
                  activeTab === 'performance'
                    ? 'border-primary-600 text-primary-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm transition`}
              >
                Performance
              </button>
              <button
                onClick={() => setActiveTab('risk')}
                className={`${
                  activeTab === 'risk'
                    ? 'border-primary-600 text-primary-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm transition`}
              >
                Risk Analysis
              </button>
            </nav>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-red-800">{error}</p>
          </div>
        )}

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow-md p-6">
            <p className="text-sm text-gray-600 mb-1">Total Value</p>
            <p className="text-2xl font-bold text-gray-900">
              {currencySymbol}{formatNumber(portfolio.total_value)}
            </p>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <p className="text-sm text-gray-600 mb-1">Total Cost</p>
            <p className="text-2xl font-bold text-gray-900">
              {currencySymbol}{formatNumber(portfolio.total_cost)}
            </p>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <p className="text-sm text-gray-600 mb-1">Total Gain/Loss</p>
            <p className={`text-2xl font-bold ${portfolio.total_gain >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {portfolio.total_gain >= 0 ? '+' : ''}{currencySymbol}{formatNumber(portfolio.total_gain)}
            </p>
            <p className={`text-sm mt-1 ${portfolio.total_return_percent >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {portfolio.total_return_percent >= 0 ? '+' : ''}{formatNumber(portfolio.total_return_percent)}%
            </p>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <p className="text-sm text-gray-600 mb-1">Positions</p>
            <p className="text-2xl font-bold text-gray-900">{portfolio.position_count}</p>
            <p className="text-sm text-gray-500 mt-1">{portfolio.transaction_count} transactions</p>
          </div>
        </div>

        {/* Tab Content */}
        {activeTab === 'overview' && (
          <OverviewTab
            portfolio={portfolio}
            transactions={transactions}
            currencySymbol={currencySymbol}
            formatNumber={formatNumber}
            allocationData={allocationData}
            COLORS={COLORS}
            router={router}
            handleDeleteTransaction={handleDeleteTransaction}
          />
        )}

        {activeTab === 'performance' && (
          <PerformanceTab
            performance={performance}
            benchmarkComparison={benchmarkComparison}
            loading={loadingAnalytics}
            currencySymbol={currencySymbol}
            formatNumber={formatNumber}
            selectedBenchmark={selectedBenchmark}
            setSelectedBenchmark={setSelectedBenchmark}
            onBenchmarkChange={fetchPerformanceData}
          />
        )}

        {activeTab === 'risk' && (
          <RiskAnalysisTab
            riskMetrics={riskMetrics}
            loading={loadingAnalytics}
            formatNumber={formatNumber}
            selectedBenchmark={selectedBenchmark}
            setSelectedBenchmark={setSelectedBenchmark}
            onBenchmarkChange={fetchRiskData}
          />
        )}
      </div>

      {/* Modals - Add Transaction and Delete Portfolio */}
      {/* [Modals remain the same as original] */}
      {showAddTransaction && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold text-gray-900">Add Transaction</h2>
                <button
                  onClick={() => setShowAddTransaction(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              {error && (
                <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
                  <p className="text-red-800">{error}</p>
                </div>
              )}

              <form onSubmit={handleAddTransaction}>
                <div className="grid grid-cols-2 gap-4 mb-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Ticker *</label>
                    <input
                      type="text"
                      value={newTransaction.ticker}
                      onChange={(e) => setNewTransaction({ ...newTransaction, ticker: e.target.value })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent uppercase"
                      placeholder="AAPL"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Type *</label>
                    <select
                      value={newTransaction.transaction_type}
                      onChange={(e) => setNewTransaction({ ...newTransaction, transaction_type: e.target.value })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    >
                      <option value="buy">Buy</option>
                      <option value="sell">Sell</option>
                      <option value="dividend">Dividend</option>
                      <option value="split">Split</option>
                    </select>
                  </div>
                </div>

                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">Date *</label>
                  <input
                    type="date"
                    value={newTransaction.transaction_date}
                    onChange={(e) => setNewTransaction({ ...newTransaction, transaction_date: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    required
                  />
                </div>

                <div className="grid grid-cols-3 gap-4 mb-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Quantity *</label>
                    <input
                      type="number"
                      step="0.01"
                      value={newTransaction.quantity}
                      onChange={(e) => setNewTransaction({ ...newTransaction, quantity: e.target.value })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                      placeholder="10"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Price *</label>
                    <input
                      type="number"
                      step="0.01"
                      value={newTransaction.price}
                      onChange={(e) => setNewTransaction({ ...newTransaction, price: e.target.value })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                      placeholder="150.00"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Commission</label>
                    <input
                      type="number"
                      step="0.01"
                      value={newTransaction.commission}
                      onChange={(e) => setNewTransaction({ ...newTransaction, commission: e.target.value })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                      placeholder="0.00"
                    />
                  </div>
                </div>

                <div className="mb-6">
                  <label className="block text-sm font-medium text-gray-700 mb-2">Notes</label>
                  <textarea
                    value={newTransaction.notes}
                    onChange={(e) => setNewTransaction({ ...newTransaction, notes: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    rows={3}
                    placeholder="Optional notes about this transaction"
                  />
                </div>

                <div className="flex justify-end gap-3">
                  <button
                    type="button"
                    onClick={() => setShowAddTransaction(false)}
                    className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
                    disabled={addingTransaction}
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50"
                    disabled={addingTransaction}
                  >
                    {addingTransaction ? 'Adding...' : 'Add Transaction'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}

      {showDeleteConfirm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-md w-full p-6">
            <h3 className="text-xl font-bold text-gray-900 mb-4">Delete Portfolio?</h3>
            <p className="text-gray-600 mb-6">
              Are you sure you want to delete "{portfolio.name}"? This will permanently delete all transactions and data. This action cannot be undone.
            </p>
            <div className="flex justify-end gap-3">
              <button
                onClick={() => setShowDeleteConfirm(false)}
                className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
                disabled={deletingPortfolio}
              >
                Cancel
              </button>
              <button
                onClick={handleDeletePortfolio}
                className="px-6 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50"
                disabled={deletingPortfolio}
              >
                {deletingPortfolio ? 'Deleting...' : 'Delete Portfolio'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// Overview Tab Component
function OverviewTab({ portfolio, transactions, currencySymbol, formatNumber, allocationData, COLORS, router, handleDeleteTransaction }: any) {
  return (
    <div>
      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
        {/* Positions List */}
        <div className="lg:col-span-2">
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Current Positions</h2>

            {portfolio.positions.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <p>No positions yet. Add your first transaction to get started.</p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-gray-200">
                      <th className="text-left py-3 px-2 text-sm font-semibold text-gray-700">Ticker</th>
                      <th className="text-right py-3 px-2 text-sm font-semibold text-gray-700">Quantity</th>
                      <th className="text-right py-3 px-2 text-sm font-semibold text-gray-700">Avg Cost</th>
                      <th className="text-right py-3 px-2 text-sm font-semibold text-gray-700">Current Price</th>
                      <th className="text-right py-3 px-2 text-sm font-semibold text-gray-700">Value</th>
                      <th className="text-right py-3 px-2 text-sm font-semibold text-gray-700">Gain/Loss</th>
                      <th className="text-right py-3 px-2 text-sm font-semibold text-gray-700">Weight</th>
                    </tr>
                  </thead>
                  <tbody>
                    {portfolio.positions.map((position: any) => (
                      <tr key={position.ticker} className="border-b border-gray-100 hover:bg-gray-50">
                        <td className="py-3 px-2">
                          <button
                            onClick={() => router.push(`/company/${position.ticker}`)}
                            className="text-primary-600 hover:text-primary-700 font-medium"
                          >
                            {position.ticker}
                          </button>
                        </td>
                        <td className="text-right py-3 px-2 text-sm">{formatNumber(position.quantity, 2)}</td>
                        <td className="text-right py-3 px-2 text-sm">{currencySymbol}{formatNumber(position.avg_cost)}</td>
                        <td className="text-right py-3 px-2 text-sm">{currencySymbol}{formatNumber(position.current_price)}</td>
                        <td className="text-right py-3 px-2 text-sm font-medium">{currencySymbol}{formatNumber(position.current_value)}</td>
                        <td className={`text-right py-3 px-2 text-sm font-medium ${position.unrealized_gain >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                          {position.unrealized_gain >= 0 ? '+' : ''}{currencySymbol}{formatNumber(position.unrealized_gain)}
                          <div className="text-xs">
                            ({position.unrealized_gain_percent >= 0 ? '+' : ''}{formatNumber(position.unrealized_gain_percent)}%)
                          </div>
                        </td>
                        <td className="text-right py-3 px-2 text-sm">{formatNumber(position.weight)}%</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>

        {/* Allocation Chart and Concentration */}
        <div className="space-y-6">
          {/* Allocation Pie Chart */}
          {portfolio.positions.length > 0 && (
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-bold text-gray-900 mb-4">Asset Allocation</h3>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={allocationData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={(entry) => `${entry.name} (${entry.weight.toFixed(1)}%)`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {allocationData.map((entry: any, index: number) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip
                    formatter={(value: number) => `${currencySymbol}${formatNumber(value)}`}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
          )}

          {/* Concentration Metrics */}
          {portfolio.positions.length > 0 && (
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-bold text-gray-900 mb-4">Concentration</h3>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Top Position</span>
                  <span className="text-sm font-medium">{formatNumber(portfolio.concentration.top_position_weight)}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Top 3 Positions</span>
                  <span className="text-sm font-medium">{formatNumber(portfolio.concentration.top_3_weight)}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Top 5 Positions</span>
                  <span className="text-sm font-medium">{formatNumber(portfolio.concentration.top_5_weight)}%</span>
                </div>
                <div className="flex justify-between border-t pt-3">
                  <span className="text-sm text-gray-600">HHI (Diversification)</span>
                  <span className="text-sm font-medium">{formatNumber(portfolio.concentration.herfindahl_index, 4)}</span>
                </div>
                <p className="text-xs text-gray-500 mt-2">
                  Lower HHI indicates better diversification. HHI &lt; 0.15 is diversified, &gt; 0.25 is concentrated.
                </p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Transaction History */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Transaction History</h2>

        {transactions.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <p>No transactions yet.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-3 px-2 text-sm font-semibold text-gray-700">Date</th>
                  <th className="text-left py-3 px-2 text-sm font-semibold text-gray-700">Ticker</th>
                  <th className="text-left py-3 px-2 text-sm font-semibold text-gray-700">Type</th>
                  <th className="text-right py-3 px-2 text-sm font-semibold text-gray-700">Quantity</th>
                  <th className="text-right py-3 px-2 text-sm font-semibold text-gray-700">Price</th>
                  <th className="text-right py-3 px-2 text-sm font-semibold text-gray-700">Commission</th>
                  <th className="text-right py-3 px-2 text-sm font-semibold text-gray-700">Total</th>
                  <th className="text-left py-3 px-2 text-sm font-semibold text-gray-700">Notes</th>
                  <th className="text-center py-3 px-2 text-sm font-semibold text-gray-700">Actions</th>
                </tr>
              </thead>
              <tbody>
                {transactions.map((txn: any) => (
                  <tr key={txn.id} className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="py-3 px-2 text-sm">
                      {new Date(txn.transaction_date).toLocaleDateString()}
                    </td>
                    <td className="py-3 px-2 text-sm font-medium">{txn.ticker}</td>
                    <td className="py-3 px-2 text-sm">
                      <span className={`px-2 py-1 rounded-md text-xs ${
                        txn.transaction_type === 'buy' ? 'bg-green-100 text-green-700' :
                        txn.transaction_type === 'sell' ? 'bg-red-100 text-red-700' :
                        'bg-blue-100 text-blue-700'
                      }`}>
                        {txn.transaction_type.toUpperCase()}
                      </span>
                    </td>
                    <td className="text-right py-3 px-2 text-sm">{formatNumber(txn.quantity, 2)}</td>
                    <td className="text-right py-3 px-2 text-sm">{currencySymbol}{formatNumber(txn.price)}</td>
                    <td className="text-right py-3 px-2 text-sm">{currencySymbol}{formatNumber(txn.commission)}</td>
                    <td className="text-right py-3 px-2 text-sm font-medium">{currencySymbol}{formatNumber(txn.total_amount)}</td>
                    <td className="py-3 px-2 text-sm text-gray-600">{txn.notes || '-'}</td>
                    <td className="text-center py-3 px-2">
                      <button
                        onClick={() => handleDeleteTransaction(txn.id)}
                        className="text-red-600 hover:text-red-700 text-sm"
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

// Performance Tab Component
function PerformanceTab({ performance, benchmarkComparison, loading, currencySymbol, formatNumber, selectedBenchmark, setSelectedBenchmark, onBenchmarkChange }: any) {
  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading performance data...</p>
        </div>
      </div>
    );
  }

  if (!performance) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6 text-center text-gray-500">
        <p>No performance data available. Add transactions to see performance metrics.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Benchmark Selector */}
      <div className="bg-white rounded-lg shadow-md p-4 flex items-center justify-between">
        <span className="text-sm font-medium text-gray-700">Compare to Benchmark:</span>
        <select
          value={selectedBenchmark}
          onChange={(e) => {
            setSelectedBenchmark(e.target.value);
            onBenchmarkChange();
          }}
          className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
        >
          <option value="SPY">S&P 500 (SPY)</option>
          <option value="QQQ">NASDAQ-100 (QQQ)</option>
          <option value="IWM">Russell 2000 (IWM)</option>
          <option value="NIFTY50">NIFTY 50</option>
          <option value="SENSEX">BSE SENSEX</option>
        </select>
      </div>

      {/* Performance Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow-md p-6">
          <p className="text-sm text-gray-600 mb-1">Annualized Return</p>
          <p className="text-2xl font-bold text-gray-900">{formatNumber(performance.annualized_return)}%</p>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <p className="text-sm text-gray-600 mb-1">Total Return</p>
          <p className={`text-2xl font-bold ${performance.total_return >= 0 ? 'text-green-600' : 'text-red-600'}`}>
            {performance.total_return >= 0 ? '+' : ''}{formatNumber(performance.total_return)}%
          </p>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <p className="text-sm text-gray-600 mb-1">1 Year Return</p>
          <p className="text-2xl font-bold text-gray-900">
            {formatNumber(performance.period_returns?.['1_year'] || 0)}%
          </p>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <p className="text-sm text-gray-600 mb-1">YTD Return</p>
          <p className="text-2xl font-bold text-gray-900">
            {formatNumber(performance.period_returns?.['ytd'] || 0)}%
          </p>
        </div>
      </div>

      {/* Cumulative Returns Chart */}
      {performance.cumulative_returns && performance.cumulative_returns.length > 0 && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-bold text-gray-900 mb-4">Cumulative Returns</h3>
          <ResponsiveContainer width="100%" height={400}>
            <AreaChart data={performance.cumulative_returns}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                dataKey="date"
                tickFormatter={(date) => new Date(date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
              />
              <YAxis tickFormatter={(value) => `${value}%`} />
              <Tooltip
                formatter={(value: number) => [`${formatNumber(value)}%`, 'Return']}
                labelFormatter={(date) => new Date(date).toLocaleDateString()}
              />
              <Area
                type="monotone"
                dataKey="cumulative_return"
                stroke="#3B82F6"
                fill="#3B82F6"
                fillOpacity={0.3}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Benchmark Comparison */}
      {benchmarkComparison && benchmarkComparison.portfolio_cumulative && benchmarkComparison.benchmark_cumulative && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-bold text-gray-900 mb-4">
            Portfolio vs {benchmarkComparison.benchmark_name}
          </h3>
          <ResponsiveContainer width="100%" height={400}>
            <LineChart>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                dataKey="date"
                data={benchmarkComparison.portfolio_cumulative}
                tickFormatter={(date) => new Date(date).toLocaleDateString('en-US', { month: 'short' })}
              />
              <YAxis tickFormatter={(value) => `${value}%`} />
              <Tooltip
                formatter={(value: number) => `${formatNumber(value)}%`}
                labelFormatter={(date) => new Date(date).toLocaleDateString()}
              />
              <Legend />
              <Line
                data={benchmarkComparison.portfolio_cumulative}
                type="monotone"
                dataKey="cumulative_return"
                stroke="#3B82F6"
                name="Portfolio"
                dot={false}
              />
              <Line
                data={benchmarkComparison.benchmark_cumulative}
                type="monotone"
                dataKey="cumulative_return"
                stroke="#10B981"
                name={benchmarkComparison.benchmark_name}
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>

          {/* Comparison Metrics */}
          <div className="grid grid-cols-3 gap-6 mt-6">
            <div className="text-center">
              <p className="text-sm text-gray-600 mb-1">Portfolio Return</p>
              <p className="text-lg font-bold text-gray-900">
                {formatNumber(benchmarkComparison.portfolio_cumulative_return)}%
              </p>
            </div>
            <div className="text-center">
              <p className="text-sm text-gray-600 mb-1">Benchmark Return</p>
              <p className="text-lg font-bold text-gray-900">
                {formatNumber(benchmarkComparison.benchmark_cumulative_return)}%
              </p>
            </div>
            <div className="text-center">
              <p className="text-sm text-gray-600 mb-1">Excess Return</p>
              <p className={`text-lg font-bold ${benchmarkComparison.excess_return >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {benchmarkComparison.excess_return >= 0 ? '+' : ''}{formatNumber(benchmarkComparison.excess_return)}%
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Period Returns Table */}
      {performance.period_returns && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-bold text-gray-900 mb-4">Period Returns</h3>
          <div className="grid grid-cols-3 md:grid-cols-7 gap-4">
            <div className="text-center">
              <p className="text-sm text-gray-600 mb-1">1 Day</p>
              <p className="font-bold text-gray-900">{formatNumber(performance.period_returns['1_day'])}%</p>
            </div>
            <div className="text-center">
              <p className="text-sm text-gray-600 mb-1">1 Week</p>
              <p className="font-bold text-gray-900">{formatNumber(performance.period_returns['1_week'])}%</p>
            </div>
            <div className="text-center">
              <p className="text-sm text-gray-600 mb-1">1 Month</p>
              <p className="font-bold text-gray-900">{formatNumber(performance.period_returns['1_month'])}%</p>
            </div>
            <div className="text-center">
              <p className="text-sm text-gray-600 mb-1">3 Months</p>
              <p className="font-bold text-gray-900">{formatNumber(performance.period_returns['3_months'])}%</p>
            </div>
            <div className="text-center">
              <p className="text-sm text-gray-600 mb-1">6 Months</p>
              <p className="font-bold text-gray-900">{formatNumber(performance.period_returns['6_months'])}%</p>
            </div>
            <div className="text-center">
              <p className="text-sm text-gray-600 mb-1">1 Year</p>
              <p className="font-bold text-gray-900">{formatNumber(performance.period_returns['1_year'])}%</p>
            </div>
            <div className="text-center">
              <p className="text-sm text-gray-600 mb-1">YTD</p>
              <p className="font-bold text-gray-900">{formatNumber(performance.period_returns['ytd'])}%</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// Risk Analysis Tab Component
function RiskAnalysisTab({ riskMetrics, loading, formatNumber, selectedBenchmark, setSelectedBenchmark, onBenchmarkChange }: any) {
  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading risk metrics...</p>
        </div>
      </div>
    );
  }

  if (!riskMetrics) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6 text-center text-gray-500">
        <p>No risk data available. Add transactions to see risk metrics.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Benchmark Selector */}
      <div className="bg-white rounded-lg shadow-md p-4 flex items-center justify-between">
        <span className="text-sm font-medium text-gray-700">Benchmark for Beta/Alpha:</span>
        <select
          value={selectedBenchmark}
          onChange={(e) => {
            setSelectedBenchmark(e.target.value);
            onBenchmarkChange();
          }}
          className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
        >
          <option value="SPY">S&P 500 (SPY)</option>
          <option value="QQQ">NASDAQ-100 (QQQ)</option>
          <option value="IWM">Russell 2000 (IWM)</option>
          <option value="NIFTY50">NIFTY 50</option>
          <option value="SENSEX">BSE SENSEX</option>
        </select>
      </div>

      {/* Risk-Adjusted Returns */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-bold text-gray-900 mb-4">Risk-Adjusted Returns</h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="text-center">
            <p className="text-sm text-gray-600 mb-1">Sharpe Ratio</p>
            <p className="text-2xl font-bold text-gray-900">{formatNumber(riskMetrics.sharpe_ratio)}</p>
            <p className="text-xs text-gray-500 mt-1">&gt; 1.0 is good</p>
          </div>
          <div className="text-center">
            <p className="text-sm text-gray-600 mb-1">Sortino Ratio</p>
            <p className="text-2xl font-bold text-gray-900">{formatNumber(riskMetrics.sortino_ratio)}</p>
            <p className="text-xs text-gray-500 mt-1">&gt; 1.5 is good</p>
          </div>
          <div className="text-center">
            <p className="text-sm text-gray-600 mb-1">Calmar Ratio</p>
            <p className="text-2xl font-bold text-gray-900">{formatNumber(riskMetrics.calmar_ratio)}</p>
            <p className="text-xs text-gray-500 mt-1">&gt; 0.5 is good</p>
          </div>
          <div className="text-center">
            <p className="text-sm text-gray-600 mb-1">Win Rate</p>
            <p className="text-2xl font-bold text-gray-900">{formatNumber(riskMetrics.win_rate)}%</p>
            <p className="text-xs text-gray-500 mt-1">% positive days</p>
          </div>
        </div>
      </div>

      {/* Volatility & Drawdown */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-bold text-gray-900 mb-4">Volatility</h3>
          <div className="space-y-4">
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Annualized Return</span>
              <span className="font-bold text-gray-900">{formatNumber(riskMetrics.annualized_return)}%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Annualized Volatility</span>
              <span className="font-bold text-gray-900">{formatNumber(riskMetrics.annualized_volatility)}%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Daily Volatility</span>
              <span className="font-bold text-gray-900">{formatNumber(riskMetrics.daily_volatility, 4)}%</span>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-bold text-gray-900 mb-4">Maximum Drawdown</h3>
          <div className="space-y-4">
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Max Drawdown</span>
              <span className="font-bold text-red-600">{formatNumber(riskMetrics.max_drawdown?.max_drawdown_percent)}%</span>
            </div>
            {riskMetrics.max_drawdown?.peak_date && (
              <>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Peak Date</span>
                  <span className="font-bold text-gray-900">
                    {new Date(riskMetrics.max_drawdown.peak_date).toLocaleDateString()}
                  </span>
                </div>
                {riskMetrics.max_drawdown.trough_date && (
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Trough Date</span>
                    <span className="font-bold text-gray-900">
                      {new Date(riskMetrics.max_drawdown.trough_date).toLocaleDateString()}
                    </span>
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      </div>

      {/* Drawdown Chart */}
      {riskMetrics.max_drawdown?.drawdown_series && riskMetrics.max_drawdown.drawdown_series.length > 0 && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-bold text-gray-900 mb-4">Drawdown Over Time</h3>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={riskMetrics.max_drawdown.drawdown_series}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                dataKey="date"
                tickFormatter={(date) => new Date(date).toLocaleDateString('en-US', { month: 'short' })}
              />
              <YAxis tickFormatter={(value) => `${value}%`} />
              <Tooltip
                formatter={(value: number) => [`${formatNumber(value)}%`, 'Drawdown']}
                labelFormatter={(date) => new Date(date).toLocaleDateString()}
              />
              <Area
                type="monotone"
                dataKey="drawdown_percent"
                stroke="#EF4444"
                fill="#EF4444"
                fillOpacity={0.3}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Value at Risk */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-bold text-gray-900 mb-4">Value at Risk (VaR)</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
          <div className="text-center">
            <p className="text-sm text-gray-600 mb-1">VaR 95%</p>
            <p className="text-xl font-bold text-gray-900">{formatNumber(riskMetrics.var_95)}%</p>
            <p className="text-xs text-gray-500 mt-1">1-day, 95% confidence</p>
          </div>
          <div className="text-center">
            <p className="text-sm text-gray-600 mb-1">VaR 99%</p>
            <p className="text-xl font-bold text-gray-900">{formatNumber(riskMetrics.var_99)}%</p>
            <p className="text-xs text-gray-500 mt-1">1-day, 99% confidence</p>
          </div>
          <div className="text-center">
            <p className="text-sm text-gray-600 mb-1">CVaR 95%</p>
            <p className="text-xl font-bold text-gray-900">{formatNumber(riskMetrics.cvar_95)}%</p>
            <p className="text-xs text-gray-500 mt-1">Expected shortfall</p>
          </div>
          <div className="text-center">
            <p className="text-sm text-gray-600 mb-1">CVaR 99%</p>
            <p className="text-xl font-bold text-gray-900">{formatNumber(riskMetrics.cvar_99)}%</p>
            <p className="text-xs text-gray-500 mt-1">Expected shortfall</p>
          </div>
        </div>
      </div>

      {/* Market Sensitivity */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-bold text-gray-900 mb-4">Market Sensitivity (vs {selectedBenchmark})</h3>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-6">
          <div className="text-center">
            <p className="text-sm text-gray-600 mb-1">Beta</p>
            <p className="text-2xl font-bold text-gray-900">{formatNumber(riskMetrics.beta)}</p>
            <p className="text-xs text-gray-500 mt-1">Market sensitivity</p>
          </div>
          <div className="text-center">
            <p className="text-sm text-gray-600 mb-1">Alpha</p>
            <p className={`text-2xl font-bold ${riskMetrics.alpha >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {riskMetrics.alpha >= 0 ? '+' : ''}{formatNumber(riskMetrics.alpha)}%
            </p>
            <p className="text-xs text-gray-500 mt-1">Excess return</p>
          </div>
          <div className="text-center">
            <p className="text-sm text-gray-600 mb-1">Correlation</p>
            <p className="text-2xl font-bold text-gray-900">{formatNumber(riskMetrics.correlation)}</p>
            <p className="text-xs text-gray-500 mt-1">-1 to 1</p>
          </div>
          <div className="text-center">
            <p className="text-sm text-gray-600 mb-1">Up Capture</p>
            <p className="text-2xl font-bold text-gray-900">{formatNumber(riskMetrics.up_capture)}%</p>
            <p className="text-xs text-gray-500 mt-1">&gt; 100% is good</p>
          </div>
          <div className="text-center">
            <p className="text-sm text-gray-600 mb-1">Down Capture</p>
            <p className="text-2xl font-bold text-gray-900">{formatNumber(riskMetrics.down_capture)}%</p>
            <p className="text-xs text-gray-500 mt-1">&lt; 100% is good</p>
          </div>
        </div>
      </div>
    </div>
  );
}
