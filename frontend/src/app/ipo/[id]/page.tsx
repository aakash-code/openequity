'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { api } from '@/lib/api';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface PageProps {
  params: { id: string };
}

export default function IPODetailPage({ params }: PageProps) {
  const router = useRouter();
  const [ipo, setIpo] = useState<any>(null);
  const [subscription, setSubscription] = useState<any>(null);
  const [gmp, setGMP] = useState<any>(null);
  const [listingGains, setListingGains] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'overview' | 'subscription' | 'financials' | 'gmp'>('overview');

  useEffect(() => {
    fetchIPODetails();
  }, [params.id]);

  const fetchIPODetails = async () => {
    setLoading(true);
    try {
      const ipoData = await api.getIPODetails(params.id);
      setIpo(ipoData);

      // Fetch subscription data if IPO is open/closed/listed
      if (['open', 'closed', 'listed'].includes(ipoData.status)) {
        try {
          const subData = await api.getIPOSubscription(params.id);
          setSubscription(subData);
        } catch (err) {
          console.log('Subscription data not available');
        }
      }

      // Fetch GMP if IPO is upcoming/open
      if (['upcoming', 'open'].includes(ipoData.status)) {
        try {
          const gmpData = await api.getIPOGreyMarketPremium(params.id);
          setGMP(gmpData);
        } catch (err) {
          console.log('GMP data not available');
        }
      }

      // Fetch listing gains if IPO is listed
      if (ipoData.status === 'listed') {
        try {
          const gainsData = await api.getIPOListingGains(params.id);
          setListingGains(gainsData);
        } catch (err) {
          console.log('Listing gains not available');
        }
      }
    } catch (error) {
      console.error('Error fetching IPO details:', error);
    } finally {
      setLoading(false);
    }
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

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin h-12 w-12 border-4 border-primary-500 rounded-full border-t-transparent"></div>
      </div>
    );
  }

  if (!ipo) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900">IPO Not Found</h2>
          <button onClick={() => router.push('/ipo')} className="mt-4 text-primary-600 hover:text-primary-700">
            Back to IPO List
          </button>
        </div>
      </div>
    );
  }

  const subscriptionData = subscription ? [
    { category: 'Retail', subscription: subscription.categories.retail.subscription_times },
    { category: 'HNI', subscription: subscription.categories.hni.subscription_times },
    { category: 'QIB', subscription: subscription.categories.qib.subscription_times }
  ] : [];

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <button onClick={() => router.push('/ipo')} className="text-sm text-primary-600 hover:text-primary-700 mb-4">
            ← Back to IPO List
          </button>
          <div className="flex justify-between items-start">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">{ipo.company_name}</h1>
              <p className="text-gray-600 mt-2">{ipo.sector} • {ipo.exchange}</p>
            </div>
            <span className={`px-4 py-2 rounded-lg text-sm font-semibold ${
              ipo.status === 'open' ? 'bg-green-100 text-green-700' :
              ipo.status === 'upcoming' ? 'bg-blue-100 text-blue-700' :
              ipo.status === 'closed' ? 'bg-yellow-100 text-yellow-700' :
              ipo.status === 'listed' ? 'bg-purple-100 text-purple-700' :
              'bg-gray-100 text-gray-700'
            }`}>
              {ipo.status.toUpperCase()}
            </span>
          </div>

          {/* Key Metrics */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
            <div className="bg-gray-50 p-4 rounded">
              <p className="text-sm text-gray-500">Issue Size</p>
              <p className="text-xl font-bold text-gray-900">{formatCurrency(ipo.issue_size)}</p>
            </div>
            <div className="bg-gray-50 p-4 rounded">
              <p className="text-sm text-gray-500">Price Range</p>
              <p className="text-xl font-bold text-gray-900">₹{ipo.price_range[0]} - ₹{ipo.price_range[1]}</p>
            </div>
            <div className="bg-gray-50 p-4 rounded">
              <p className="text-sm text-gray-500">Lot Size</p>
              <p className="text-xl font-bold text-gray-900">{ipo.lot_size} shares</p>
            </div>
            <div className="bg-gray-50 p-4 rounded">
              <p className="text-sm text-gray-500">Min Investment</p>
              <p className="text-xl font-bold text-gray-900">₹{ipo.minimum_investment?.toLocaleString('en-IN')}</p>
            </div>
          </div>
        </div>

        {/* Timeline */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Timeline</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-sm">
            <div>
              <p className="text-gray-500">Open Date</p>
              <p className="font-semibold text-gray-900">{formatDate(ipo.open_date)}</p>
            </div>
            <div>
              <p className="text-gray-500">Close Date</p>
              <p className="font-semibold text-gray-900">{formatDate(ipo.close_date)}</p>
            </div>
            <div>
              <p className="text-gray-500">Allotment</p>
              <p className="font-semibold text-gray-900">{formatDate(ipo.allotment_date)}</p>
            </div>
            <div>
              <p className="text-gray-500">Listing Date</p>
              <p className="font-semibold text-gray-900">{formatDate(ipo.listing_date)}</p>
            </div>
          </div>
        </div>

        {/* GMP Banner (if available) */}
        {gmp && (
          <div className={`rounded-lg shadow p-6 mb-6 ${
            gmp.grey_market_premium > 0 ? 'bg-green-50 border-2 border-green-200' :
            gmp.grey_market_premium < 0 ? 'bg-red-50 border-2 border-red-200' :
            'bg-gray-50 border-2 border-gray-200'
          }`}>
            <h2 className="text-xl font-bold text-gray-900 mb-4">Grey Market Premium (GMP)</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <p className="text-sm text-gray-600">GMP</p>
                <p className={`text-2xl font-bold ${
                  gmp.grey_market_premium > 0 ? 'text-green-600' :
                  gmp.grey_market_premium < 0 ? 'text-red-600' : 'text-gray-600'
                }`}>
                  ₹{gmp.grey_market_premium} ({gmp.gmp_percent > 0 ? '+' : ''}{gmp.gmp_percent.toFixed(2)}%)
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Expected Listing Price</p>
                <p className="text-2xl font-bold text-gray-900">₹{gmp.expected_listing_price.toFixed(2)}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Sentiment</p>
                <p className="text-xl font-bold text-gray-900">{gmp.sentiment}</p>
              </div>
              <div>
                <p className="text-xs text-gray-500 italic">Subject to market risk. Not guaranteed.</p>
              </div>
            </div>
          </div>
        )}

        {/* Listing Gains (if available) */}
        {listingGains && (
          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Listing Performance</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <p className="text-sm text-gray-500">Issue Price</p>
                <p className="text-xl font-bold text-gray-900">₹{listingGains.issue_price}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Listing Price</p>
                <p className="text-xl font-bold text-gray-900">₹{listingGains.listing_price}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Listing Gain</p>
                <p className={`text-xl font-bold ${
                  listingGains.listing_gain_percent >= 0 ? 'text-green-600' : 'text-red-600'
                }`}>
                  {listingGains.listing_gain_percent >= 0 ? '+' : ''}{listingGains.listing_gain_percent.toFixed(2)}%
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Current Price</p>
                <p className="text-xl font-bold text-gray-900">₹{listingGains.current_price}</p>
              </div>
            </div>
          </div>
        )}

        {/* Tabs */}
        <div className="bg-white rounded-lg shadow mb-6">
          <div className="border-b border-gray-200">
            <nav className="flex space-x-8 px-6" aria-label="Tabs">
              {[
                { id: 'overview', label: 'Overview' },
                { id: 'subscription', label: 'Subscription' },
                { id: 'financials', label: 'Financials' },
                { id: 'gmp', label: 'Grey Market' }
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

          <div className="p-6">
            {/* Overview Tab */}
            {activeTab === 'overview' && (
              <div className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <h3 className="font-semibold text-gray-900 mb-3">Company Details</h3>
                    {ipo.company_details && (
                      <div className="space-y-2 text-sm">
                        <div><span className="text-gray-600">Founded:</span> <span className="font-medium">{ipo.company_details.founded}</span></div>
                        <div><span className="text-gray-600">Headquarters:</span> <span className="font-medium">{ipo.company_details.headquarters}</span></div>
                        <div><span className="text-gray-600">Employees:</span> <span className="font-medium">{ipo.company_details.employees?.toLocaleString('en-IN')}</span></div>
                      </div>
                    )}
                  </div>

                  <div>
                    <h3 className="font-semibold text-gray-900 mb-3">Issue Details</h3>
                    <div className="space-y-2 text-sm">
                      <div><span className="text-gray-600">Issue Type:</span> <span className="font-medium">{ipo.issue_type}</span></div>
                      <div><span className="text-gray-600">Face Value:</span> <span className="font-medium">₹{ipo.face_value}</span></div>
                      <div><span className="text-gray-600">Registrar:</span> <span className="font-medium">{ipo.registrar}</span></div>
                    </div>
                  </div>
                </div>

                {ipo.objectives && (
                  <div>
                    <h3 className="font-semibold text-gray-900 mb-3">Objectives</h3>
                    <ul className="list-disc list-inside space-y-1 text-sm text-gray-700">
                      {ipo.objectives.map((obj: string, idx: number) => (
                        <li key={idx}>{obj}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {ipo.strengths && (
                  <div>
                    <h3 className="font-semibold text-gray-900 mb-3">Strengths</h3>
                    <ul className="list-disc list-inside space-y-1 text-sm text-green-700">
                      {ipo.strengths.map((str: string, idx: number) => (
                        <li key={idx}>{str}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {ipo.risks && (
                  <div>
                    <h3 className="font-semibold text-gray-900 mb-3">Risks</h3>
                    <ul className="list-disc list-inside space-y-1 text-sm text-red-700">
                      {ipo.risks.map((risk: string, idx: number) => (
                        <li key={idx}>{risk}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}

            {/* Subscription Tab */}
            {activeTab === 'subscription' && (
              <div>
                {subscription ? (
                  <div className="space-y-6">
                    <div>
                      <h3 className="font-semibold text-gray-900 mb-4">Overall Subscription</h3>
                      <p className="text-4xl font-bold text-primary-600">{subscription.overall_subscription}x</p>
                      <p className="text-sm text-gray-500 mt-1">Last updated: {new Date(subscription.last_updated).toLocaleString()}</p>
                    </div>

                    <div className="h-80">
                      <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={subscriptionData}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="category" />
                          <YAxis label={{ value: 'Times Subscribed', angle: -90, position: 'insideLeft' }} />
                          <Tooltip />
                          <Bar dataKey="subscription" fill="#3b82f6" />
                        </BarChart>
                      </ResponsiveContainer>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      {Object.entries(subscription.categories).map(([category, data]: [string, any]) => (
                        <div key={category} className="bg-gray-50 p-4 rounded">
                          <h4 className="font-semibold text-gray-900 mb-2">{category.toUpperCase()}</h4>
                          <p className="text-2xl font-bold text-primary-600">{data.subscription_times}x</p>
                          <p className="text-sm text-gray-600 mt-2">Applications: {data.applications?.toLocaleString('en-IN')}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                ) : (
                  <p className="text-gray-500 text-center py-12">Subscription data not available yet</p>
                )}
              </div>
            )}

            {/* Financials Tab */}
            {activeTab === 'financials' && (
              <div>
                {ipo.financials ? (
                  <div className="space-y-6">
                    <div>
                      <h3 className="font-semibold text-gray-900 mb-4">Revenue (₹ Cr)</h3>
                      <div className="grid grid-cols-3 gap-4">
                        <div className="bg-gray-50 p-4 rounded">
                          <p className="text-sm text-gray-600">FY 2023</p>
                          <p className="text-xl font-bold text-gray-900">{formatCurrency(ipo.financials.revenue_fy23)}</p>
                        </div>
                        <div className="bg-gray-50 p-4 rounded">
                          <p className="text-sm text-gray-600">FY 2022</p>
                          <p className="text-xl font-bold text-gray-900">{formatCurrency(ipo.financials.revenue_fy22)}</p>
                        </div>
                        <div className="bg-gray-50 p-4 rounded">
                          <p className="text-sm text-gray-600">FY 2021</p>
                          <p className="text-xl font-bold text-gray-900">{formatCurrency(ipo.financials.revenue_fy21)}</p>
                        </div>
                      </div>
                    </div>

                    <div>
                      <h3 className="font-semibold text-gray-900 mb-4">Net Profit (₹ Cr)</h3>
                      <div className="grid grid-cols-3 gap-4">
                        <div className="bg-gray-50 p-4 rounded">
                          <p className="text-sm text-gray-600">FY 2023</p>
                          <p className="text-xl font-bold text-gray-900">{formatCurrency(ipo.financials.net_profit_fy23)}</p>
                        </div>
                        <div className="bg-gray-50 p-4 rounded">
                          <p className="text-sm text-gray-600">FY 2022</p>
                          <p className="text-xl font-bold text-gray-900">{formatCurrency(ipo.financials.net_profit_fy22)}</p>
                        </div>
                        <div className="bg-gray-50 p-4 rounded">
                          <p className="text-sm text-gray-600">FY 2021</p>
                          <p className="text-xl font-bold text-gray-900">{formatCurrency(ipo.financials.net_profit_fy21)}</p>
                        </div>
                      </div>
                    </div>

                    <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                      <div className="bg-gray-50 p-4 rounded">
                        <p className="text-sm text-gray-600">EPS (FY23)</p>
                        <p className="text-xl font-bold text-gray-900">₹{ipo.financials.eps_fy23}</p>
                      </div>
                      <div className="bg-gray-50 p-4 rounded">
                        <p className="text-sm text-gray-600">ROE</p>
                        <p className="text-xl font-bold text-gray-900">{ipo.financials.roe}%</p>
                      </div>
                      <div className="bg-gray-50 p-4 rounded">
                        <p className="text-sm text-gray-600">D/E Ratio</p>
                        <p className="text-xl font-bold text-gray-900">{ipo.financials.debt_to_equity}</p>
                      </div>
                    </div>

                    {ipo.valuation && (
                      <div>
                        <h3 className="font-semibold text-gray-900 mb-4">Valuation</h3>
                        <div className="grid grid-cols-2 gap-4">
                          <div className="bg-gray-50 p-4 rounded">
                            <p className="text-sm text-gray-600">P/E Ratio (at upper price)</p>
                            <p className="text-xl font-bold text-gray-900">{ipo.valuation.pe_ratio_at_upper_price}</p>
                          </div>
                          <div className="bg-gray-50 p-4 rounded">
                            <p className="text-sm text-gray-600">Book Value</p>
                            <p className="text-xl font-bold text-gray-900">₹{ipo.valuation.book_value}</p>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                ) : (
                  <p className="text-gray-500 text-center py-12">Financial data not available</p>
                )}
              </div>
            )}

            {/* Grey Market Tab */}
            {activeTab === 'gmp' && (
              <div>
                {gmp ? (
                  <div className="space-y-6">
                    <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                      <p className="text-sm text-yellow-800">
                        <strong>Disclaimer:</strong> Grey market premium is unofficial and unregulated. It is subject to market risk and should not be considered as guaranteed listing price.
                      </p>
                    </div>

                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      <div className="bg-gray-50 p-4 rounded">
                        <p className="text-sm text-gray-600">Issue Price (Upper)</p>
                        <p className="text-xl font-bold text-gray-900">₹{gmp.issue_price}</p>
                      </div>
                      <div className="bg-gray-50 p-4 rounded">
                        <p className="text-sm text-gray-600">Grey Market Premium</p>
                        <p className={`text-xl font-bold ${
                          gmp.grey_market_premium > 0 ? 'text-green-600' :
                          gmp.grey_market_premium < 0 ? 'text-red-600' : 'text-gray-600'
                        }`}>
                          ₹{gmp.grey_market_premium}
                        </p>
                      </div>
                      <div className="bg-gray-50 p-4 rounded">
                        <p className="text-sm text-gray-600">Expected Listing</p>
                        <p className="text-xl font-bold text-gray-900">₹{gmp.expected_listing_price.toFixed(2)}</p>
                      </div>
                      <div className="bg-gray-50 p-4 rounded">
                        <p className="text-sm text-gray-600">GMP %</p>
                        <p className={`text-xl font-bold ${
                          gmp.gmp_percent > 0 ? 'text-green-600' :
                          gmp.gmp_percent < 0 ? 'text-red-600' : 'text-gray-600'
                        }`}>
                          {gmp.gmp_percent > 0 ? '+' : ''}{gmp.gmp_percent.toFixed(2)}%
                        </p>
                      </div>
                    </div>

                    <div className="bg-gray-50 p-6 rounded">
                      <h4 className="font-semibold text-gray-900 mb-2">Market Sentiment</h4>
                      <p className={`text-2xl font-bold ${
                        gmp.sentiment === 'Positive' ? 'text-green-600' :
                        gmp.sentiment === 'Negative' ? 'text-red-600' : 'text-gray-600'
                      }`}>
                        {gmp.sentiment}
                      </p>
                    </div>
                  </div>
                ) : (
                  <p className="text-gray-500 text-center py-12">Grey market data not available for this IPO</p>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
