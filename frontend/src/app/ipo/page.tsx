'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { api } from '@/lib/api';

export default function IPODashboard() {
  const router = useRouter();
  const [activeTab, setActiveTab] = useState<'ipos' | 'rights' | 'ofs' | 'buybacks'>('ipos');
  const [ipoStatus, setIpoStatus] = useState<string>('');
  const [ipos, setIpos] = useState<any[]>([]);
  const [rightsIssues, setRightsIssues] = useState<any[]>([]);
  const [ofsList, setOfsList] = useState<any[]>([]);
  const [buybacks, setBuybacks] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, [activeTab, ipoStatus]);

  const fetchData = async () => {
    setLoading(true);
    try {
      if (activeTab === 'ipos') {
        const data = await api.getIPOs(ipoStatus || undefined);
        setIpos(data.ipos || []);
      } else if (activeTab === 'rights') {
        const data = await api.getRightsIssues();
        setRightsIssues(data.rights_issues || []);
      } else if (activeTab === 'ofs') {
        const data = await api.getOFSList();
        setOfsList(data.ofs || []);
      } else if (activeTab === 'buybacks') {
        const data = await api.getBuybacks();
        setBuybacks(data.buybacks || []);
      }
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status: string) => {
    const statusColors: Record<string, string> = {
      upcoming: 'bg-blue-100 text-blue-700',
      open: 'bg-green-100 text-green-700',
      closed: 'bg-yellow-100 text-yellow-700',
      listed: 'bg-purple-100 text-purple-700',
      withdrawn: 'bg-red-100 text-red-700'
    };
    return statusColors[status] || 'bg-gray-100 text-gray-700';
  };

  const formatCurrency = (value: number) => {
    if (value >= 10000) {
      return `₹${(value / 10000).toFixed(2)} Cr`;
    } else if (value >= 100) {
      return `₹${(value / 100).toFixed(2)} L`;
    }
    return `₹${value.toFixed(2)}`;
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-IN', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">IPO & Primary Markets</h1>
          <p className="mt-2 text-gray-600">Track IPOs, Rights Issues, OFS, and Buybacks</p>
        </div>

        {/* Main Tabs */}
        <div className="mb-6 border-b border-gray-200">
          <nav className="flex space-x-8" aria-label="Tabs">
            {[
              { id: 'ipos', label: 'IPOs' },
              { id: 'rights', label: 'Rights Issues' },
              { id: 'ofs', label: 'OFS' },
              { id: 'buybacks', label: 'Buybacks' }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab.id
                    ? 'border-primary-600 text-primary-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </nav>
        </div>

        {/* IPO Status Filter */}
        {activeTab === 'ipos' && (
          <div className="mb-6 flex gap-2">
            {['', 'upcoming', 'open', 'closed', 'listed'].map((status) => (
              <button
                key={status}
                onClick={() => setIpoStatus(status)}
                className={`px-4 py-2 rounded-md text-sm font-medium transition ${
                  ipoStatus === status
                    ? 'bg-primary-600 text-white'
                    : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
                }`}
              >
                {status === '' ? 'All' : status.charAt(0).toUpperCase() + status.slice(1)}
              </button>
            ))}
          </div>
        )}

        {/* Content */}
        {loading ? (
          <div className="flex justify-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
          </div>
        ) : (
          <>
            {/* IPO List */}
            {activeTab === 'ipos' && (
              <div className="space-y-4">
                {ipos.length === 0 ? (
                  <div className="text-center py-12 bg-white rounded-lg">
                    <p className="text-gray-500">No IPOs found</p>
                  </div>
                ) : (
                  ipos.map((ipo) => (
                    <div
                      key={ipo.id}
                      onClick={() => router.push(`/ipo/${ipo.id}`)}
                      className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition cursor-pointer border border-gray-200"
                    >
                      <div className="flex justify-between items-start mb-4">
                        <div className="flex-1">
                          <h3 className="text-xl font-bold text-gray-900">{ipo.company_name}</h3>
                          <p className="text-sm text-gray-600 mt-1">{ipo.sector} • {ipo.exchange}</p>
                        </div>
                        <span className={`px-3 py-1 rounded-full text-xs font-semibold ${getStatusBadge(ipo.status)}`}>
                          {ipo.status.toUpperCase()}
                        </span>
                      </div>

                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                        <div>
                          <p className="text-xs text-gray-500">Issue Size</p>
                          <p className="font-semibold text-gray-900">{formatCurrency(ipo.issue_size)}</p>
                        </div>
                        <div>
                          <p className="text-xs text-gray-500">Price Range</p>
                          <p className="font-semibold text-gray-900">
                            ₹{ipo.price_range[0]} - ₹{ipo.price_range[1]}
                          </p>
                        </div>
                        <div>
                          <p className="text-xs text-gray-500">Lot Size</p>
                          <p className="font-semibold text-gray-900">{ipo.lot_size} shares</p>
                        </div>
                        <div>
                          <p className="text-xs text-gray-500">Min Investment</p>
                          <p className="font-semibold text-gray-900">₹{ipo.minimum_investment?.toLocaleString('en-IN')}</p>
                        </div>
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                        <div>
                          <span className="text-gray-600">Open:</span>{' '}
                          <span className="font-medium text-gray-900">{formatDate(ipo.open_date)}</span>
                        </div>
                        <div>
                          <span className="text-gray-600">Close:</span>{' '}
                          <span className="font-medium text-gray-900">{formatDate(ipo.close_date)}</span>
                        </div>
                        <div>
                          <span className="text-gray-600">Listing:</span>{' '}
                          <span className="font-medium text-gray-900">{formatDate(ipo.listing_date)}</span>
                        </div>
                      </div>

                      {ipo.subscription_times && (
                        <div className="mt-4 pt-4 border-t border-gray-200">
                          <div className="flex items-center gap-2">
                            <span className="text-sm text-gray-600">Subscription:</span>
                            <span className="text-sm font-bold text-primary-600">{ipo.subscription_times}x</span>
                          </div>
                        </div>
                      )}

                      {ipo.status === 'listed' && ipo.listing_gain_percent !== undefined && (
                        <div className="mt-4 pt-4 border-t border-gray-200">
                          <div className="flex items-center gap-4">
                            <div>
                              <span className="text-sm text-gray-600">Listing Gain:</span>
                              <span className={`ml-2 text-sm font-bold ${
                                ipo.listing_gain_percent >= 0 ? 'text-green-600' : 'text-red-600'
                              }`}>
                                {ipo.listing_gain_percent >= 0 ? '+' : ''}{ipo.listing_gain_percent.toFixed(2)}%
                              </span>
                            </div>
                            <div>
                              <span className="text-sm text-gray-600">Current:</span>
                              <span className="ml-2 text-sm font-medium text-gray-900">₹{ipo.current_price?.toFixed(2)}</span>
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  ))
                )}
              </div>
            )}

            {/* Rights Issues */}
            {activeTab === 'rights' && (
              <div className="space-y-4">
                {rightsIssues.length === 0 ? (
                  <div className="text-center py-12 bg-white rounded-lg">
                    <p className="text-gray-500">No rights issues found</p>
                  </div>
                ) : (
                  rightsIssues.map((issue) => (
                    <div
                      key={issue.id}
                      className="bg-white rounded-lg shadow p-6 border border-gray-200"
                    >
                      <div className="flex justify-between items-start mb-4">
                        <div>
                          <h3 className="text-xl font-bold text-gray-900">{issue.company_name}</h3>
                          <p className="text-sm text-gray-600 mt-1">{issue.ticker}</p>
                        </div>
                        <span className={`px-3 py-1 rounded-full text-xs font-semibold ${getStatusBadge(issue.status)}`}>
                          {issue.status.toUpperCase()}
                        </span>
                      </div>

                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div>
                          <p className="text-xs text-gray-500">Issue Size</p>
                          <p className="font-semibold text-gray-900">{formatCurrency(issue.issue_size)}</p>
                        </div>
                        <div>
                          <p className="text-xs text-gray-500">Issue Price</p>
                          <p className="font-semibold text-gray-900">₹{issue.issue_price}</p>
                        </div>
                        <div>
                          <p className="text-xs text-gray-500">Rights Ratio</p>
                          <p className="font-semibold text-gray-900">{issue.rights_ratio.display}</p>
                        </div>
                        <div>
                          <p className="text-xs text-gray-500">Purpose</p>
                          <p className="font-semibold text-gray-900 text-sm">{issue.purpose}</p>
                        </div>
                      </div>

                      <div className="mt-4 grid grid-cols-2 gap-4 text-sm">
                        <div>
                          <span className="text-gray-600">Open:</span>{' '}
                          <span className="font-medium text-gray-900">{formatDate(issue.open_date)}</span>
                        </div>
                        <div>
                          <span className="text-gray-600">Close:</span>{' '}
                          <span className="font-medium text-gray-900">{formatDate(issue.close_date)}</span>
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            )}

            {/* OFS */}
            {activeTab === 'ofs' && (
              <div className="space-y-4">
                {ofsList.length === 0 ? (
                  <div className="text-center py-12 bg-white rounded-lg">
                    <p className="text-gray-500">No OFS found</p>
                  </div>
                ) : (
                  ofsList.map((ofs) => (
                    <div
                      key={ofs.id}
                      className="bg-white rounded-lg shadow p-6 border border-gray-200"
                    >
                      <div className="flex justify-between items-start mb-4">
                        <div>
                          <h3 className="text-xl font-bold text-gray-900">{ofs.company_name}</h3>
                          <p className="text-sm text-gray-600 mt-1">By: {ofs.promoter}</p>
                        </div>
                        <span className={`px-3 py-1 rounded-full text-xs font-semibold ${getStatusBadge(ofs.status)}`}>
                          {ofs.status.toUpperCase()}
                        </span>
                      </div>

                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div>
                          <p className="text-xs text-gray-500">Offer Size</p>
                          <p className="font-semibold text-gray-900">{formatCurrency(ofs.offer_size)}</p>
                        </div>
                        <div>
                          <p className="text-xs text-gray-500">Floor Price</p>
                          <p className="font-semibold text-gray-900">₹{ofs.floor_price}</p>
                        </div>
                        <div>
                          <p className="text-xs text-gray-500">Shares Offered</p>
                          <p className="font-semibold text-gray-900">{(ofs.shares_offered / 10000000).toFixed(2)} Cr</p>
                        </div>
                        <div>
                          <p className="text-xs text-gray-500">Retail Discount</p>
                          <p className="font-semibold text-gray-900">{ofs.discount_retail}%</p>
                        </div>
                      </div>

                      <div className="mt-4 text-sm">
                        <span className="text-gray-600">Offer Date:</span>{' '}
                        <span className="font-medium text-gray-900">{formatDate(ofs.offer_date)}</span>
                      </div>
                    </div>
                  ))
                )}
              </div>
            )}

            {/* Buybacks */}
            {activeTab === 'buybacks' && (
              <div className="space-y-4">
                {buybacks.length === 0 ? (
                  <div className="text-center py-12 bg-white rounded-lg">
                    <p className="text-gray-500">No buybacks found</p>
                  </div>
                ) : (
                  buybacks.map((buyback) => (
                    <div
                      key={buyback.id}
                      className="bg-white rounded-lg shadow p-6 border border-gray-200"
                    >
                      <div className="flex justify-between items-start mb-4">
                        <div>
                          <h3 className="text-xl font-bold text-gray-900">{buyback.company_name}</h3>
                          <p className="text-sm text-gray-600 mt-1">{buyback.ticker}</p>
                        </div>
                        <span className={`px-3 py-1 rounded-full text-xs font-semibold ${getStatusBadge(buyback.status)}`}>
                          {buyback.status.toUpperCase()}
                        </span>
                      </div>

                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div>
                          <p className="text-xs text-gray-500">Buyback Size</p>
                          <p className="font-semibold text-gray-900">{formatCurrency(buyback.buyback_size)}</p>
                        </div>
                        <div>
                          <p className="text-xs text-gray-500">Buyback Price</p>
                          <p className="font-semibold text-gray-900">₹{buyback.buyback_price}</p>
                        </div>
                        <div>
                          <p className="text-xs text-gray-500">Method</p>
                          <p className="font-semibold text-gray-900">{buyback.method}</p>
                        </div>
                        <div>
                          <p className="text-xs text-gray-500">% of Equity</p>
                          <p className="font-semibold text-gray-900">{buyback.percent_of_equity}%</p>
                        </div>
                      </div>

                      <div className="mt-4 grid grid-cols-2 gap-4 text-sm">
                        <div>
                          <span className="text-gray-600">Open:</span>{' '}
                          <span className="font-medium text-gray-900">{formatDate(buyback.open_date)}</span>
                        </div>
                        <div>
                          <span className="text-gray-600">Close:</span>{' '}
                          <span className="font-medium text-gray-900">{formatDate(buyback.close_date)}</span>
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
