'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth-context';
import { api, DCFValuation, PeerGroup } from '@/lib/api';
import Link from 'next/link';

export default function ValuationsPage() {
  const router = useRouter();
  const { isAuthenticated, loading } = useAuth();
  const [activeTab, setActiveTab] = useState<'dcf' | 'comps'>('dcf');
  const [dcfValuations, setDcfValuations] = useState<DCFValuation[]>([]);
  const [peerGroups, setPeerGroups] = useState<PeerGroup[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (!loading && !isAuthenticated) {
      router.push('/auth');
    }
  }, [isAuthenticated, loading, router]);

  useEffect(() => {
    if (isAuthenticated) {
      fetchData();
    }
  }, [isAuthenticated, activeTab]);

  const fetchData = async () => {
    setIsLoading(true);
    try {
      if (activeTab === 'dcf') {
        const result = await api.getDCFValuations();
        setDcfValuations(result.valuations);
      } else {
        const result = await api.getPeerGroups();
        setPeerGroups(result.peer_groups);
      }
    } catch (error) {
      console.error('Failed to fetch data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const formatCurrency = (value: number) => {
    if (value >= 1e12) return `$${(value / 1e12).toFixed(2)}T`;
    if (value >= 1e9) return `$${(value / 1e9).toFixed(2)}B`;
    if (value >= 1e6) return `$${(value / 1e6).toFixed(2)}M`;
    return `$${value.toLocaleString()}`;
  };

  const formatPercentage = (value: number) => {
    return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`;
  };

  if (loading || !isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin h-12 w-12 border-4 border-primary-500 rounded-full border-t-transparent"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Valuation Tools</h1>
          <p className="text-gray-600 mt-2">
            Create DCF models and perform comparable company analysis
          </p>
        </div>

        {/* Tabs */}
        <div className="border-b border-gray-200 mb-6">
          <nav className="-mb-px flex space-x-8">
            <button
              onClick={() => setActiveTab('dcf')}
              className={`${
                activeTab === 'dcf'
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm transition`}
            >
              DCF Valuation
            </button>
            <button
              onClick={() => setActiveTab('comps')}
              className={`${
                activeTab === 'comps'
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm transition`}
            >
              Comparable Companies
            </button>
          </nav>
        </div>

        {/* DCF Tab Content */}
        {activeTab === 'dcf' && (
          <div>
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-semibold text-gray-900">My DCF Models</h2>
              <Link
                href="/valuations/dcf/new"
                className="bg-primary-600 text-white px-4 py-2 rounded-md hover:bg-primary-700 transition"
              >
                Create DCF Model
              </Link>
            </div>

            {isLoading ? (
              <div className="flex justify-center py-12">
                <div className="animate-spin h-8 w-8 border-4 border-primary-500 rounded-full border-t-transparent"></div>
              </div>
            ) : dcfValuations.length === 0 ? (
              <div className="bg-white rounded-lg shadow-md p-12 text-center">
                <div className="text-gray-400 text-5xl mb-4">📊</div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  No DCF Models Yet
                </h3>
                <p className="text-gray-600 mb-6">
                  Create your first DCF valuation model to get started
                </p>
                <Link
                  href="/valuations/dcf/new"
                  className="inline-block bg-primary-600 text-white px-6 py-3 rounded-md hover:bg-primary-700 transition"
                >
                  Create Your First DCF Model
                </Link>
              </div>
            ) : (
              <div className="grid grid-cols-1 gap-4">
                {dcfValuations.map((dcf) => (
                  <div
                    key={dcf.id}
                    className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition"
                  >
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <h3 className="text-lg font-bold text-gray-900">{dcf.name}</h3>
                          <span className="text-sm bg-primary-100 text-primary-700 px-2 py-1 rounded">
                            {dcf.ticker}
                          </span>
                          {dcf.is_public && (
                            <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded">
                              Public
                            </span>
                          )}
                        </div>
                        {dcf.description && (
                          <p className="text-sm text-gray-600 mb-4">{dcf.description}</p>
                        )}
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                          <div>
                            <p className="text-xs text-gray-500">Equity Value</p>
                            <p className="text-lg font-semibold text-gray-900">
                              {formatCurrency(dcf.equity_value)}
                            </p>
                          </div>
                          <div>
                            <p className="text-xs text-gray-500">Value per Share</p>
                            <p className="text-lg font-semibold text-gray-900">
                              ${dcf.value_per_share.toFixed(2)}
                            </p>
                          </div>
                          <div>
                            <p className="text-xs text-gray-500">WACC</p>
                            <p className="text-lg font-semibold text-gray-900">
                              {(dcf.wacc * 100).toFixed(2)}%
                            </p>
                          </div>
                          {dcf.upside_downside !== null && dcf.upside_downside !== undefined && (
                            <div>
                              <p className="text-xs text-gray-500">Upside/Downside</p>
                              <p
                                className={`text-lg font-semibold ${
                                  dcf.upside_downside >= 0 ? 'text-green-600' : 'text-red-600'
                                }`}
                              >
                                {formatPercentage(dcf.upside_downside)}
                              </p>
                            </div>
                          )}
                        </div>
                      </div>
                      <Link
                        href={`/valuations/dcf/${dcf.id}`}
                        className="ml-4 text-primary-600 hover:text-primary-700 font-medium text-sm"
                      >
                        View Details →
                      </Link>
                    </div>
                    <div className="mt-4 pt-4 border-t border-gray-200 text-xs text-gray-500">
                      Created {new Date(dcf.created_at).toLocaleDateString()}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Comps Tab Content */}
        {activeTab === 'comps' && (
          <div>
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-semibold text-gray-900">Peer Groups</h2>
              <Link
                href="/valuations/comps/new"
                className="bg-primary-600 text-white px-4 py-2 rounded-md hover:bg-primary-700 transition"
              >
                Create Peer Group
              </Link>
            </div>

            {isLoading ? (
              <div className="flex justify-center py-12">
                <div className="animate-spin h-8 w-8 border-4 border-primary-500 rounded-full border-t-transparent"></div>
              </div>
            ) : peerGroups.length === 0 ? (
              <div className="bg-white rounded-lg shadow-md p-12 text-center">
                <div className="text-gray-400 text-5xl mb-4">📈</div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  No Peer Groups Yet
                </h3>
                <p className="text-gray-600 mb-6">
                  Create a peer group to perform comparable company analysis
                </p>
                <Link
                  href="/valuations/comps/new"
                  className="inline-block bg-primary-600 text-white px-6 py-3 rounded-md hover:bg-primary-700 transition"
                >
                  Create Your First Peer Group
                </Link>
              </div>
            ) : (
              <div className="grid grid-cols-1 gap-4">
                {peerGroups.map((group) => (
                  <div
                    key={group.id}
                    className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition"
                  >
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <h3 className="text-lg font-bold text-gray-900">{group.name}</h3>
                          <span className="text-sm bg-primary-100 text-primary-700 px-2 py-1 rounded">
                            {group.ticker}
                          </span>
                          {group.is_public && (
                            <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded">
                              Public
                            </span>
                          )}
                        </div>
                        {group.description && (
                          <p className="text-sm text-gray-600 mb-4">{group.description}</p>
                        )}
                        <div className="mb-2">
                          <p className="text-xs text-gray-500 mb-1">Peer Companies ({group.peer_tickers.length})</p>
                          <div className="flex flex-wrap gap-2">
                            {group.peer_tickers.map((ticker) => (
                              <span
                                key={ticker}
                                className="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded"
                              >
                                {ticker}
                              </span>
                            ))}
                          </div>
                        </div>
                        {group.last_analyzed && (
                          <p className="text-xs text-gray-500 mt-2">
                            Last analyzed: {new Date(group.last_analyzed).toLocaleDateString()}
                          </p>
                        )}
                      </div>
                      <Link
                        href={`/valuations/comps/${group.id}`}
                        className="ml-4 text-primary-600 hover:text-primary-700 font-medium text-sm"
                      >
                        Analyze →
                      </Link>
                    </div>
                    <div className="mt-4 pt-4 border-t border-gray-200 text-xs text-gray-500">
                      Created {new Date(group.created_at).toLocaleDateString()}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Quick Start Guide */}
        <div className="mt-12 bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-blue-900 mb-3">💡 Quick Start Guide</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-medium text-blue-800 mb-2">DCF Valuation</h4>
              <ol className="text-sm text-blue-700 space-y-1 list-decimal list-inside">
                <li>Select a company ticker</li>
                <li>Enter WACC assumptions (risk-free rate, beta, etc.)</li>
                <li>Set projection assumptions (revenue growth, margins)</li>
                <li>Choose terminal value method</li>
                <li>Review valuation and sensitivity analysis</li>
              </ol>
            </div>
            <div>
              <h4 className="font-medium text-blue-800 mb-2">Comparable Companies</h4>
              <ol className="text-sm text-blue-700 space-y-1 list-decimal list-inside">
                <li>Select a target company</li>
                <li>Choose peer companies in the same industry</li>
                <li>Run analysis to see trading multiples</li>
                <li>Compare valuation metrics</li>
                <li>Identify premium/discount to peers</li>
              </ol>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
