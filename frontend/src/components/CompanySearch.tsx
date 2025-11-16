'use client';

import React, { useState, useEffect } from 'react';
import { api, Company } from '@/lib/api';
import { useAuth } from '@/lib/auth-context';

interface CompanySearchProps {
  onSelectCompany?: (company: Company) => void;
}

export default function CompanySearch({ onSelectCompany }: CompanySearchProps) {
  const { isAuthenticated } = useAuth();
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<Company[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showResults, setShowResults] = useState(false);

  // Debounced search
  useEffect(() => {
    if (!query || query.length < 2 || !isAuthenticated) {
      setResults([]);
      setShowResults(false);
      return;
    }

    const timeoutId = setTimeout(async () => {
      try {
        setLoading(true);
        setError(null);
        const companies = await api.searchCompanies(query, 10);
        setResults(companies);
        setShowResults(true);
      } catch (err: any) {
        setError(err.message || 'Search failed');
        setResults([]);
      } finally {
        setLoading(false);
      }
    }, 300);

    return () => clearTimeout(timeoutId);
  }, [query, isAuthenticated]);

  const handleSelectCompany = (company: Company) => {
    setQuery(company.ticker);
    setShowResults(false);
    onSelectCompany?.(company);
  };

  const formatMarketCap = (marketCap?: number) => {
    if (!marketCap) return 'N/A';
    if (marketCap >= 1e12) return `$${(marketCap / 1e12).toFixed(2)}T`;
    if (marketCap >= 1e9) return `$${(marketCap / 1e9).toFixed(2)}B`;
    if (marketCap >= 1e6) return `$${(marketCap / 1e6).toFixed(2)}M`;
    return `$${marketCap.toLocaleString()}`;
  };

  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="relative w-full max-w-2xl">
      <div className="relative">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onFocus={() => results.length > 0 && setShowResults(true)}
          placeholder="Search companies by ticker, name, or sector..."
          className="w-full px-4 py-3 pr-10 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
        />
        {loading && (
          <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
            <div className="animate-spin h-5 w-5 border-2 border-primary-500 rounded-full border-t-transparent"></div>
          </div>
        )}
      </div>

      {error && (
        <div className="mt-2 p-2 bg-red-50 border border-red-200 rounded-md">
          <p className="text-sm text-red-600">{error}</p>
        </div>
      )}

      {showResults && results.length > 0 && (
        <div className="absolute z-10 w-full mt-2 bg-white border border-gray-200 rounded-lg shadow-lg max-h-96 overflow-y-auto">
          {results.map((company) => (
            <button
              key={company.ticker}
              onClick={() => handleSelectCompany(company)}
              className="w-full px-4 py-3 hover:bg-gray-50 border-b border-gray-100 last:border-b-0 text-left transition"
            >
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <span className="font-semibold text-gray-900">{company.ticker}</span>
                    <span className="text-xs text-gray-500">{company.exchange}</span>
                  </div>
                  <p className="text-sm text-gray-700 mt-1">{company.name}</p>
                  {company.sector && (
                    <p className="text-xs text-gray-500 mt-1">{company.sector}</p>
                  )}
                </div>
                <div className="text-right ml-4">
                  <p className="text-sm font-medium text-gray-900">
                    {formatMarketCap(company.market_cap)}
                  </p>
                  <p className="text-xs text-gray-500">Market Cap</p>
                </div>
              </div>
            </button>
          ))}
        </div>
      )}

      {showResults && results.length === 0 && query.length >= 2 && !loading && (
        <div className="absolute z-10 w-full mt-2 bg-white border border-gray-200 rounded-lg shadow-lg p-4">
          <p className="text-sm text-gray-600">No companies found matching "{query}"</p>
        </div>
      )}
    </div>
  );
}
