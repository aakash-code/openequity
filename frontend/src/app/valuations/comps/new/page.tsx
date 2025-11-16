'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth-context';
import { api, CreatePeerGroupRequest } from '@/lib/api';
import CompanySearch from '@/components/CompanySearch';

export default function NewPeerGroupPage() {
  const router = useRouter();
  const { isAuthenticated, loading: authLoading } = useAuth();
  const [selectedTicker, setSelectedTicker] = useState('');
  const [groupName, setGroupName] = useState('');
  const [description, setDescription] = useState('');
  const [isPublic, setIsPublic] = useState(false);
  const [peerTickers, setPeerTickers] = useState<string[]>([]);
  const [newPeerTicker, setNewPeerTicker] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  React.useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/auth');
    }
  }, [isAuthenticated, authLoading, router]);

  const addPeerTicker = () => {
    const ticker = newPeerTicker.trim().toUpperCase();
    if (!ticker) return;

    if (peerTickers.includes(ticker)) {
      setError('This ticker is already in the peer group');
      return;
    }

    if (ticker === selectedTicker) {
      setError('Cannot add the target company as a peer');
      return;
    }

    setPeerTickers([...peerTickers, ticker]);
    setNewPeerTicker('');
    setError('');
  };

  const removePeerTicker = (ticker: string) => {
    setPeerTickers(peerTickers.filter((t) => t !== ticker));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!selectedTicker) {
      setError('Please select a target company');
      return;
    }

    if (!groupName.trim()) {
      setError('Please enter a group name');
      return;
    }

    if (peerTickers.length === 0) {
      setError('Please add at least one peer company');
      return;
    }

    setLoading(true);

    try {
      const data: CreatePeerGroupRequest = {
        ticker: selectedTicker,
        name: groupName,
        description: description || undefined,
        peer_tickers: peerTickers,
        is_public: isPublic,
      };

      const result = await api.createPeerGroup(data);
      router.push(`/valuations/comps/${result.id}`);
    } catch (err: any) {
      setError(err.message || 'Failed to create peer group');
      setLoading(false);
    }
  };

  if (authLoading || !isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin h-12 w-12 border-4 border-primary-500 rounded-full border-t-transparent"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Create Peer Group</h1>
          <p className="text-gray-600 mt-2">
            Select a target company and build a peer group for comparable company analysis
          </p>
        </div>

        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
            <p className="text-red-800 text-sm">{error}</p>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-8">
          {/* Group Details */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Group Details</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Target Company *
                </label>
                <CompanySearch
                  onSelectCompany={(company) => {
                    setSelectedTicker(company.ticker);
                    if (!groupName) {
                      setGroupName(`${company.ticker} Peer Group`);
                    }
                  }}
                />
                {selectedTicker && (
                  <p className="text-sm text-green-600 mt-2">Selected: {selectedTicker}</p>
                )}
                <p className="text-xs text-gray-500 mt-1">
                  The company you want to value using comparable analysis
                </p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Group Name *
                </label>
                <input
                  type="text"
                  value={groupName}
                  onChange={(e) => setGroupName(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  placeholder="e.g., AAPL Tech Peers"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Description
                </label>
                <textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  rows={3}
                  placeholder="Optional description of this peer group..."
                />
              </div>
              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="isPublic"
                  checked={isPublic}
                  onChange={(e) => setIsPublic(e.target.checked)}
                  className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                />
                <label htmlFor="isPublic" className="ml-2 block text-sm text-gray-700">
                  Make this peer group public (visible to other users)
                </label>
              </div>
            </div>
          </div>

          {/* Peer Companies */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Peer Companies</h2>
            <p className="text-sm text-gray-600 mb-4">
              Add companies that are comparable to your target (same industry, similar size, business model)
            </p>

            <div className="flex gap-2 mb-4">
              <input
                type="text"
                value={newPeerTicker}
                onChange={(e) => setNewPeerTicker(e.target.value.toUpperCase())}
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault();
                    addPeerTicker();
                  }
                }}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                placeholder="Enter ticker symbol (e.g., MSFT)"
              />
              <button
                type="button"
                onClick={addPeerTicker}
                className="px-6 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 transition"
              >
                Add Peer
              </button>
            </div>

            {peerTickers.length > 0 ? (
              <div>
                <p className="text-sm font-medium text-gray-700 mb-2">
                  Peer Companies ({peerTickers.length})
                </p>
                <div className="flex flex-wrap gap-2">
                  {peerTickers.map((ticker) => (
                    <div
                      key={ticker}
                      className="flex items-center gap-2 bg-primary-50 border border-primary-200 px-3 py-2 rounded-md"
                    >
                      <span className="text-sm font-medium text-primary-900">{ticker}</span>
                      <button
                        type="button"
                        onClick={() => removePeerTicker(ticker)}
                        className="text-primary-600 hover:text-primary-800 font-bold text-lg leading-none"
                      >
                        ×
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div className="bg-gray-50 border border-gray-200 rounded-lg p-8 text-center">
                <p className="text-gray-500">No peer companies added yet</p>
                <p className="text-xs text-gray-400 mt-1">
                  Add ticker symbols above to build your peer group
                </p>
              </div>
            )}

            <div className="mt-4 bg-blue-50 border border-blue-200 rounded-lg p-4">
              <h4 className="text-sm font-semibold text-blue-900 mb-2">💡 Tips for Selecting Peers</h4>
              <ul className="text-xs text-blue-700 space-y-1 list-disc list-inside">
                <li>Choose companies in the same industry or sector</li>
                <li>Look for similar business models and revenue streams</li>
                <li>Consider companies with comparable market capitalizations</li>
                <li>Include 5-10 peers for a robust analysis</li>
                <li>Avoid companies with significantly different growth profiles</li>
              </ul>
            </div>
          </div>

          {/* Suggested Peers (optional enhancement) */}
          {selectedTicker && (
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Suggested Peer Groups</h3>
              <p className="text-sm text-gray-600 mb-4">
                Common peer groups for {selectedTicker} (click to add):
              </p>
              <div className="space-y-2">
                {selectedTicker === 'AAPL' && (
                  <div className="flex flex-wrap gap-2">
                    <span className="text-xs text-gray-500">Tech Giants:</span>
                    {['MSFT', 'GOOGL', 'META', 'AMZN'].map((ticker) => (
                      <button
                        key={ticker}
                        type="button"
                        onClick={() => {
                          if (!peerTickers.includes(ticker)) {
                            setPeerTickers([...peerTickers, ticker]);
                          }
                        }}
                        className="text-xs bg-gray-100 hover:bg-primary-100 px-2 py-1 rounded transition"
                        disabled={peerTickers.includes(ticker)}
                      >
                        {ticker}
                      </button>
                    ))}
                  </div>
                )}
                {selectedTicker === 'TCS' && (
                  <div className="flex flex-wrap gap-2">
                    <span className="text-xs text-gray-500">Indian IT:</span>
                    {['INFY', 'WIPRO', 'HCLTECH'].map((ticker) => (
                      <button
                        key={ticker}
                        type="button"
                        onClick={() => {
                          if (!peerTickers.includes(ticker)) {
                            setPeerTickers([...peerTickers, ticker]);
                          }
                        }}
                        className="text-xs bg-gray-100 hover:bg-primary-100 px-2 py-1 rounded transition"
                        disabled={peerTickers.includes(ticker)}
                      >
                        {ticker}
                      </button>
                    ))}
                  </div>
                )}
                {!['AAPL', 'TCS'].includes(selectedTicker) && (
                  <p className="text-sm text-gray-500 italic">
                    No suggestions available for this company
                  </p>
                )}
              </div>
            </div>
          )}

          {/* Actions */}
          <div className="flex justify-end gap-4">
            <button
              type="button"
              onClick={() => router.back()}
              className="px-6 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 transition"
              disabled={loading}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-6 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 transition disabled:opacity-50"
              disabled={loading}
            >
              {loading ? 'Creating...' : 'Create Peer Group'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
