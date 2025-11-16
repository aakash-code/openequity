'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import api from '@/lib/api';

interface Portfolio {
  id: string;
  name: string;
  description: string;
  currency: string;
  strategy: string;
  tags: string[];
  is_public: boolean;
  created_at: string;
  transaction_count: number;
}

export default function PortfoliosPage() {
  const router = useRouter();
  const [portfolios, setPortfolios] = useState<Portfolio[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [creating, setCreating] = useState(false);

  // Create portfolio form state
  const [newPortfolio, setNewPortfolio] = useState({
    name: '',
    description: '',
    currency: 'USD',
    strategy: '',
    tags: [] as string[],
    is_public: false,
  });
  const [newTag, setNewTag] = useState('');

  useEffect(() => {
    fetchPortfolios();
  }, []);

  const fetchPortfolios = async () => {
    try {
      setLoading(true);
      const response = await api.getPortfolios(0, 20);
      setPortfolios(response.portfolios || []);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load portfolios');
    } finally {
      setLoading(false);
    }
  };

  const handleCreatePortfolio = async (e: React.FormEvent) => {
    e.preventDefault();
    setCreating(true);
    setError('');

    try {
      const created = await api.createPortfolio(newPortfolio);
      setShowCreateModal(false);
      setNewPortfolio({
        name: '',
        description: '',
        currency: 'USD',
        strategy: '',
        tags: [],
        is_public: false,
      });
      router.push(`/portfolios/${created.id}`);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create portfolio');
    } finally {
      setCreating(false);
    }
  };

  const addTag = () => {
    const tag = newTag.trim();
    if (tag && !newPortfolio.tags.includes(tag)) {
      setNewPortfolio({ ...newPortfolio, tags: [...newPortfolio.tags, tag] });
      setNewTag('');
    }
  };

  const removeTag = (tagToRemove: string) => {
    setNewPortfolio({
      ...newPortfolio,
      tags: newPortfolio.tags.filter((tag) => tag !== tagToRemove),
    });
  };

  const getCurrencySymbol = (currency: string) => {
    return currency === 'INR' ? '₹' : '$';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading portfolios...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">My Portfolios</h1>
            <p className="mt-2 text-gray-600">
              Manage and track your investment portfolios
            </p>
          </div>
          <button
            onClick={() => setShowCreateModal(true)}
            className="px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors font-medium"
          >
            + Create Portfolio
          </button>
        </div>

        {/* Error Message */}
        {error && !showCreateModal && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-red-800">{error}</p>
          </div>
        )}

        {/* Portfolio Grid */}
        {portfolios.length === 0 ? (
          <div className="text-center py-12">
            <svg
              className="mx-auto h-12 w-12 text-gray-400"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"
              />
            </svg>
            <h3 className="mt-2 text-sm font-medium text-gray-900">No portfolios</h3>
            <p className="mt-1 text-sm text-gray-500">
              Get started by creating your first portfolio.
            </p>
            <div className="mt-6">
              <button
                onClick={() => setShowCreateModal(true)}
                className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700"
              >
                + Create Portfolio
              </button>
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {portfolios.map((portfolio) => (
              <div
                key={portfolio.id}
                onClick={() => router.push(`/portfolios/${portfolio.id}`)}
                className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow cursor-pointer border border-gray-200"
              >
                {/* Portfolio Header */}
                <div className="flex justify-between items-start mb-4">
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-900 mb-1">
                      {portfolio.name}
                    </h3>
                    {portfolio.description && (
                      <p className="text-sm text-gray-600 line-clamp-2">
                        {portfolio.description}
                      </p>
                    )}
                  </div>
                  {portfolio.is_public && (
                    <span className="ml-2 px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded-full">
                      Public
                    </span>
                  )}
                </div>

                {/* Strategy and Currency */}
                <div className="flex items-center gap-3 mb-4 text-sm">
                  {portfolio.strategy && (
                    <span className="px-2 py-1 bg-primary-100 text-primary-700 rounded-md">
                      {portfolio.strategy}
                    </span>
                  )}
                  <span className="px-2 py-1 bg-gray-100 text-gray-700 rounded-md">
                    {portfolio.currency}
                  </span>
                </div>

                {/* Tags */}
                {portfolio.tags && portfolio.tags.length > 0 && (
                  <div className="flex flex-wrap gap-2 mb-4">
                    {portfolio.tags.slice(0, 3).map((tag, idx) => (
                      <span
                        key={idx}
                        className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-md"
                      >
                        {tag}
                      </span>
                    ))}
                    {portfolio.tags.length > 3 && (
                      <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-md">
                        +{portfolio.tags.length - 3} more
                      </span>
                    )}
                  </div>
                )}

                {/* Stats */}
                <div className="pt-4 border-t border-gray-200">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Transactions</span>
                    <span className="font-medium text-gray-900">
                      {portfolio.transaction_count}
                    </span>
                  </div>
                  <div className="flex justify-between text-sm mt-2">
                    <span className="text-gray-600">Created</span>
                    <span className="font-medium text-gray-900">
                      {new Date(portfolio.created_at).toLocaleDateString()}
                    </span>
                  </div>
                </div>

                {/* View Details */}
                <div className="mt-4 pt-4 border-t border-gray-200">
                  <button className="w-full text-center text-sm font-medium text-primary-600 hover:text-primary-700">
                    View Details →
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Create Portfolio Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              {/* Modal Header */}
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold text-gray-900">
                  Create New Portfolio
                </h2>
                <button
                  onClick={() => setShowCreateModal(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <svg
                    className="w-6 h-6"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M6 18L18 6M6 6l12 12"
                    />
                  </svg>
                </button>
              </div>

              {/* Error Message */}
              {error && (
                <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
                  <p className="text-red-800">{error}</p>
                </div>
              )}

              {/* Create Form */}
              <form onSubmit={handleCreatePortfolio}>
                {/* Portfolio Name */}
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Portfolio Name *
                  </label>
                  <input
                    type="text"
                    value={newPortfolio.name}
                    onChange={(e) =>
                      setNewPortfolio({ ...newPortfolio, name: e.target.value })
                    }
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    placeholder="e.g., Growth Portfolio, Retirement Account"
                    required
                  />
                </div>

                {/* Description */}
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Description
                  </label>
                  <textarea
                    value={newPortfolio.description}
                    onChange={(e) =>
                      setNewPortfolio({ ...newPortfolio, description: e.target.value })
                    }
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    rows={3}
                    placeholder="Optional description of your portfolio strategy and goals"
                  />
                </div>

                {/* Currency and Strategy */}
                <div className="grid grid-cols-2 gap-4 mb-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Currency
                    </label>
                    <select
                      value={newPortfolio.currency}
                      onChange={(e) =>
                        setNewPortfolio({ ...newPortfolio, currency: e.target.value })
                      }
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    >
                      <option value="USD">USD ($)</option>
                      <option value="INR">INR (₹)</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Strategy
                    </label>
                    <select
                      value={newPortfolio.strategy}
                      onChange={(e) =>
                        setNewPortfolio({ ...newPortfolio, strategy: e.target.value })
                      }
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    >
                      <option value="">Select Strategy</option>
                      <option value="Value">Value</option>
                      <option value="Growth">Growth</option>
                      <option value="Dividend">Dividend</option>
                      <option value="Index">Index</option>
                      <option value="Momentum">Momentum</option>
                      <option value="Quality">Quality</option>
                      <option value="Mixed">Mixed</option>
                    </select>
                  </div>
                </div>

                {/* Tags */}
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Tags
                  </label>
                  <div className="flex gap-2 mb-2">
                    <input
                      type="text"
                      value={newTag}
                      onChange={(e) => setNewTag(e.target.value)}
                      onKeyPress={(e) => {
                        if (e.key === 'Enter') {
                          e.preventDefault();
                          addTag();
                        }
                      }}
                      className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                      placeholder="Add a tag and press Enter"
                    />
                    <button
                      type="button"
                      onClick={addTag}
                      className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300"
                    >
                      Add
                    </button>
                  </div>
                  {newPortfolio.tags.length > 0 && (
                    <div className="flex flex-wrap gap-2">
                      {newPortfolio.tags.map((tag, idx) => (
                        <span
                          key={idx}
                          className="px-3 py-1 bg-primary-100 text-primary-700 rounded-full text-sm flex items-center gap-2"
                        >
                          {tag}
                          <button
                            type="button"
                            onClick={() => removeTag(tag)}
                            className="text-primary-600 hover:text-primary-800"
                          >
                            ×
                          </button>
                        </span>
                      ))}
                    </div>
                  )}
                </div>

                {/* Public Portfolio */}
                <div className="mb-6">
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={newPortfolio.is_public}
                      onChange={(e) =>
                        setNewPortfolio({ ...newPortfolio, is_public: e.target.checked })
                      }
                      className="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
                    />
                    <span className="ml-2 text-sm text-gray-700">
                      Make this portfolio public (others can view it)
                    </span>
                  </label>
                </div>

                {/* Actions */}
                <div className="flex justify-end gap-3">
                  <button
                    type="button"
                    onClick={() => setShowCreateModal(false)}
                    className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
                    disabled={creating}
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50"
                    disabled={creating}
                  >
                    {creating ? 'Creating...' : 'Create Portfolio'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
