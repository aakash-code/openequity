'use client';

import React, { useState, useEffect } from 'react';
import { api } from '@/lib/api';

interface SebiFilingsDisplayProps {
  ticker: string;
}

export default function SebiFilingsDisplay({ ticker }: SebiFilingsDisplayProps) {
  const [activeSection, setActiveSection] = useState<'filings' | 'shareholding' | 'insider' | 'compliance'>('filings');
  const [filings, setFilings] = useState<any[]>([]);
  const [shareholding, setShareholding] = useState<any>(null);
  const [insiderTrades, setInsiderTrades] = useState<any[]>([]);
  const [compliance, setCompliance] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [filingTypes, setFilingTypes] = useState<Record<string, string>>({});
  const [selectedFilingType, setSelectedFilingType] = useState<string>('');

  useEffect(() => {
    fetchData();
  }, [ticker, selectedFilingType]);

  const fetchData = async () => {
    setLoading(true);
    try {
      if (activeSection === 'filings') {
        const [typesData, filingsData] = await Promise.all([
          api.getSebiFilingTypes(),
          api.getSebiFilings(ticker, selectedFilingType || undefined, 90, 50)
        ]);
        setFilingTypes(typesData.filing_types || {});
        setFilings(filingsData.filings || []);
      } else if (activeSection === 'shareholding') {
        const data = await api.getShareholdingPattern(ticker);
        setShareholding(data);
      } else if (activeSection === 'insider') {
        const data = await api.getInsiderTrading(ticker, 180, 50);
        setInsiderTrades(data.trades || []);
      } else if (activeSection === 'compliance') {
        const data = await api.getComplianceStatus(ticker);
        setCompliance(data);
      }
    } catch (error) {
      console.error('Error fetching SEBI data:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [activeSection]);

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-IN', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  return (
    <div className="space-y-6">
      {/* Section Tabs */}
      <div className="border-b border-gray-200">
        <nav className="flex space-x-8" aria-label="Tabs">
          {[
            { id: 'filings', label: 'Recent Filings' },
            { id: 'shareholding', label: 'Shareholding Pattern' },
            { id: 'insider', label: 'Insider Trading' },
            { id: 'compliance', label: 'Compliance Status' }
          ].map((section) => (
            <button
              key={section.id}
              onClick={() => setActiveSection(section.id as any)}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeSection === section.id
                  ? 'border-primary-600 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              {section.label}
            </button>
          ))}
        </nav>
      </div>

      {loading ? (
        <div className="flex justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
        </div>
      ) : (
        <>
          {/* Recent Filings */}
          {activeSection === 'filings' && (
            <div>
              <div className="mb-4 flex items-center gap-4">
                <label className="text-sm font-medium text-gray-700">Filter by Type:</label>
                <select
                  value={selectedFilingType}
                  onChange={(e) => setSelectedFilingType(e.target.value)}
                  className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                >
                  <option value="">All Types</option>
                  {Object.entries(filingTypes).map(([key, value]) => (
                    <option key={key} value={key}>{value}</option>
                  ))}
                </select>
              </div>

              <div className="space-y-3">
                {filings.length === 0 ? (
                  <p className="text-gray-500 text-center py-8">No filings found</p>
                ) : (
                  filings.map((filing, index) => (
                    <div key={index} className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50">
                      <div className="flex justify-between items-start mb-2">
                        <h4 className="font-semibold text-gray-900">{filing.title}</h4>
                        <span className="text-xs text-gray-500">{formatDate(filing.filing_date)}</span>
                      </div>
                      <div className="flex items-center gap-4 text-sm">
                        <span className="px-2 py-1 bg-primary-100 text-primary-700 rounded text-xs">
                          {filing.filing_type}
                        </span>
                        <span className="text-gray-600">{filing.category}</span>
                      </div>
                      {filing.description && (
                        <p className="mt-2 text-sm text-gray-600">{filing.description}</p>
                      )}
                    </div>
                  ))
                )}
              </div>
            </div>
          )}

          {/* Shareholding Pattern */}
          {activeSection === 'shareholding' && shareholding && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {/* Promoter Holding */}
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <h4 className="font-semibold text-gray-900 mb-2">Promoter Holding</h4>
                  <p className="text-3xl font-bold text-blue-600">{shareholding.promoter_holding?.percentage?.toFixed(2)}%</p>
                  {shareholding.changes?.promoter_change !== undefined && (
                    <p className={`text-sm mt-2 ${shareholding.changes.promoter_change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {shareholding.changes.promoter_change >= 0 ? '▲' : '▼'} {Math.abs(shareholding.changes.promoter_change).toFixed(2)}% QoQ
                    </p>
                  )}
                </div>

                {/* FII Holding */}
                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <h4 className="font-semibold text-gray-900 mb-2">FII Holding</h4>
                  <p className="text-3xl font-bold text-green-600">{shareholding.institutional_holding?.fii?.percentage?.toFixed(2)}%</p>
                  {shareholding.changes?.fii_change !== undefined && (
                    <p className={`text-sm mt-2 ${shareholding.changes.fii_change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {shareholding.changes.fii_change >= 0 ? '▲' : '▼'} {Math.abs(shareholding.changes.fii_change).toFixed(2)}% QoQ
                    </p>
                  )}
                </div>

                {/* DII Holding */}
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                  <h4 className="font-semibold text-gray-900 mb-2">DII Holding</h4>
                  <p className="text-3xl font-bold text-yellow-600">{shareholding.institutional_holding?.dii?.percentage?.toFixed(2)}%</p>
                  {shareholding.changes?.dii_change !== undefined && (
                    <p className={`text-sm mt-2 ${shareholding.changes.dii_change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {shareholding.changes.dii_change >= 0 ? '▲' : '▼'} {Math.abs(shareholding.changes.dii_change).toFixed(2)}% QoQ
                    </p>
                  )}
                </div>
              </div>

              <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                <h4 className="font-semibold text-gray-900 mb-3">Retail & Others</h4>
                <p className="text-2xl font-bold text-gray-700">{shareholding.retail_holding?.percentage?.toFixed(2)}%</p>
              </div>
            </div>
          )}

          {/* Insider Trading */}
          {activeSection === 'insider' && (
            <div>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Person</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Action</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Quantity</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Value</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {insiderTrades.length === 0 ? (
                      <tr>
                        <td colSpan={6} className="px-4 py-8 text-center text-gray-500">
                          No insider trading activity found
                        </td>
                      </tr>
                    ) : (
                      insiderTrades.map((trade, index) => (
                        <tr key={index} className="hover:bg-gray-50">
                          <td className="px-4 py-3 text-sm text-gray-900">{formatDate(trade.trade_date)}</td>
                          <td className="px-4 py-3 text-sm text-gray-900">{trade.person_name}</td>
                          <td className="px-4 py-3 text-sm text-gray-600">{trade.person_category}</td>
                          <td className="px-4 py-3 text-sm">
                            <span className={`px-2 py-1 rounded text-xs ${
                              trade.transaction_type === 'Buy' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
                            }`}>
                              {trade.transaction_type}
                            </span>
                          </td>
                          <td className="px-4 py-3 text-sm text-gray-900">{trade.quantity?.toLocaleString('en-IN')}</td>
                          <td className="px-4 py-3 text-sm text-gray-900">
                            {trade.value ? `₹${(trade.value / 100000).toFixed(2)}L` : 'N/A'}
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Compliance Status */}
          {activeSection === 'compliance' && compliance && (
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {compliance.compliances?.map((item: any, index: number) => (
                  <div key={index} className={`border rounded-lg p-4 ${
                    item.status === 'Compliant' ? 'bg-green-50 border-green-200' : 'bg-yellow-50 border-yellow-200'
                  }`}>
                    <div className="flex justify-between items-start">
                      <h4 className="font-semibold text-gray-900">{item.requirement}</h4>
                      <span className={`px-2 py-1 rounded text-xs font-medium ${
                        item.status === 'Compliant' ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'
                      }`}>
                        {item.status}
                      </span>
                    </div>
                    {item.last_update && (
                      <p className="text-xs text-gray-600 mt-2">Last updated: {formatDate(item.last_update)}</p>
                    )}
                    {item.remarks && (
                      <p className="text-sm text-gray-700 mt-2">{item.remarks}</p>
                    )}
                  </div>
                ))}
              </div>

              {compliance.overall_status && (
                <div className={`p-4 rounded-lg ${
                  compliance.overall_status === 'Good Standing' ? 'bg-green-100 border-2 border-green-300' : 'bg-yellow-100 border-2 border-yellow-300'
                }`}>
                  <h3 className="font-bold text-gray-900 text-lg">
                    Overall Status: {compliance.overall_status}
                  </h3>
                </div>
              )}
            </div>
          )}
        </>
      )}
    </div>
  );
}
