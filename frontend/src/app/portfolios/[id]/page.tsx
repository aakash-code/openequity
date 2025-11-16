'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useParams } from 'next/navigation';
import api from '@/lib/api';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip, BarChart, Bar, XAxis, YAxis, CartesianGrid } from 'recharts';

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

  const [portfolio, setPortfolio] = useState<Portfolio | null>(null);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showAddTransaction, setShowAddTransaction] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [deletingPortfolio, setDeletingPortfolio] = useState(false);

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

          <div className="flex justify-between items-start">
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
                Delete Portfolio
              </button>
            </div>
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
                      {portfolio.positions.map((position) => (
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
                      {allocationData.map((entry, index) => (
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
                  {transactions.map((txn) => (
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

      {/* Add Transaction Modal */}
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

      {/* Delete Portfolio Confirmation */}
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
