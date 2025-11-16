'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import api from '@/lib/api';

interface ScreeningResult {
  ticker: string;
  name: string;
  sector: string;
  market_cap: number;
  pe_ratio: number;
  pb_ratio: number;
  roe: number;
  revenue_growth: number;
  dividend_yield: number;
  debt_to_equity: number;
}

export default function ScreenerPage() {
  const router = useRouter();
  const [templates, setTemplates] = useState<any>(null);
  const [selectedTemplate, setSelectedTemplate] = useState('');
  const [results, setResults] = useState<ScreeningResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Custom criteria
  const [criteria, setCriteria] = useState({
    market_cap_min: '',
    market_cap_max: '',
    pe_ratio_max: '',
    pb_ratio_max: '',
    roe_min: '',
    revenue_growth_min: '',
    dividend_yield_min: '',
    debt_to_equity_max: '',
  });

  useEffect(() => {
    fetchTemplates();
  }, []);

  const fetchTemplates = async () => {
    try {
      const data = await api.getScreeningTemplates();
      setTemplates(data.templates);
    } catch (err: any) {
      console.error('Failed to load templates:', err);
    }
  };

  const handleTemplateScreen = async (templateId: string) => {
    setLoading(true);
    setError('');
    setSelectedTemplate(templateId);

    try {
      const data = await api.screenByTemplate(templateId);
      setResults(data.results || []);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to screen stocks');
    } finally {
      setLoading(false);
    }
  };

  const handleCustomScreen = async () => {
    setLoading(true);
    setError('');
    setSelectedTemplate('');

    try {
      // Convert string values to numbers, excluding empty strings
      const numericCriteria: any = {};
      Object.entries(criteria).forEach(([key, value]) => {
        if (value !== '') {
          numericCriteria[key] = parseFloat(value);
        }
      });

      const data = await api.screenStocks(numericCriteria);
      setResults(data.results || []);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to screen stocks');
    } finally {
      setLoading(false);
    }
  };

  const formatNumber = (num: number | null, decimals: number = 2) => {
    if (num === null || num === undefined) return '-';
    return num.toLocaleString('en-US', {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals,
    });
  };

  const formatMarketCap = (marketCap: number | null) => {
    if (!marketCap) return '-';
    if (marketCap >= 1e12) return `$${(marketCap / 1e12).toFixed(2)}T`;
    if (marketCap >= 1e9) return `$${(marketCap / 1e9).toFixed(2)}B`;
    if (marketCap >= 1e6) return `$${(marketCap / 1e6).toFixed(2)}M`;
    return `$${marketCap.toFixed(0)}`;
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Stock Screener</h1>
          <p className="mt-2 text-gray-600">
            Find investment opportunities using pre-built templates or custom filters
          </p>
        </div>

        {/* Template Selection */}
        {templates && (
          <div className="mb-8">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Pre-built Templates</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {Object.entries(templates).map(([id, template]: [string, any]) => (
                <button
                  key={id}
                  onClick={() => handleTemplateScreen(id)}
                  className={`p-4 rounded-lg border-2 transition-all ${
                    selectedTemplate === id
                      ? 'border-primary-600 bg-primary-50'
                      : 'border-gray-200 bg-white hover:border-primary-300'
                  }`}
                >
                  <h3 className="font-semibold text-gray-900 mb-2">{template.name}</h3>
                  <p className="text-sm text-gray-600">{template.description}</p>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Custom Filters */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Custom Filters</h2>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Min Market Cap ($M)
              </label>
              <input
                type="number"
                value={criteria.market_cap_min}
                onChange={(e) => setCriteria({ ...criteria, market_cap_min: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                placeholder="e.g., 1000"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Max Market Cap ($M)
              </label>
              <input
                type="number"
                value={criteria.market_cap_max}
                onChange={(e) => setCriteria({ ...criteria, market_cap_max: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                placeholder="e.g., 10000"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Max P/E Ratio
              </label>
              <input
                type="number"
                value={criteria.pe_ratio_max}
                onChange={(e) => setCriteria({ ...criteria, pe_ratio_max: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                placeholder="e.g., 20"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Max P/B Ratio
              </label>
              <input
                type="number"
                value={criteria.pb_ratio_max}
                onChange={(e) => setCriteria({ ...criteria, pb_ratio_max: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                placeholder="e.g., 3"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Min ROE (%)
              </label>
              <input
                type="number"
                value={criteria.roe_min}
                onChange={(e) => setCriteria({ ...criteria, roe_min: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                placeholder="e.g., 15"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Min Revenue Growth (%)
              </label>
              <input
                type="number"
                value={criteria.revenue_growth_min}
                onChange={(e) => setCriteria({ ...criteria, revenue_growth_min: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                placeholder="e.g., 10"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Min Dividend Yield (%)
              </label>
              <input
                type="number"
                value={criteria.dividend_yield_min}
                onChange={(e) => setCriteria({ ...criteria, dividend_yield_min: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                placeholder="e.g., 2"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Max Debt/Equity
              </label>
              <input
                type="number"
                value={criteria.debt_to_equity_max}
                onChange={(e) => setCriteria({ ...criteria, debt_to_equity_max: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                placeholder="e.g., 0.5"
              />
            </div>
          </div>

          <div className="mt-6 flex justify-end">
            <button
              onClick={handleCustomScreen}
              className="px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors font-medium"
            >
              Apply Filters
            </button>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-red-800">{error}</p>
          </div>
        )}

        {/* Loading State */}
        {loading && (
          <div className="flex items-center justify-center py-12">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
              <p className="mt-4 text-gray-600">Screening stocks...</p>
            </div>
          </div>
        )}

        {/* Results */}
        {!loading && results.length > 0 && (
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold text-gray-900">
                Results ({results.length} stocks)
              </h2>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-gray-200">
                    <th className="text-left py-3 px-2 text-sm font-semibold text-gray-700">Ticker</th>
                    <th className="text-left py-3 px-2 text-sm font-semibold text-gray-700">Name</th>
                    <th className="text-left py-3 px-2 text-sm font-semibold text-gray-700">Sector</th>
                    <th className="text-right py-3 px-2 text-sm font-semibold text-gray-700">Market Cap</th>
                    <th className="text-right py-3 px-2 text-sm font-semibold text-gray-700">P/E</th>
                    <th className="text-right py-3 px-2 text-sm font-semibold text-gray-700">P/B</th>
                    <th className="text-right py-3 px-2 text-sm font-semibold text-gray-700">ROE</th>
                    <th className="text-right py-3 px-2 text-sm font-semibold text-gray-700">Rev Growth</th>
                    <th className="text-right py-3 px-2 text-sm font-semibold text-gray-700">Div Yield</th>
                    <th className="text-right py-3 px-2 text-sm font-semibold text-gray-700">D/E</th>
                  </tr>
                </thead>
                <tbody>
                  {results.map((stock) => (
                    <tr
                      key={stock.ticker}
                      className="border-b border-gray-100 hover:bg-gray-50 cursor-pointer"
                      onClick={() => router.push(`/company/${stock.ticker}`)}
                    >
                      <td className="py-3 px-2 text-sm font-medium text-primary-600">
                        {stock.ticker}
                      </td>
                      <td className="py-3 px-2 text-sm text-gray-900">{stock.name}</td>
                      <td className="py-3 px-2 text-sm text-gray-600">{stock.sector || '-'}</td>
                      <td className="text-right py-3 px-2 text-sm">{formatMarketCap(stock.market_cap)}</td>
                      <td className="text-right py-3 px-2 text-sm">{formatNumber(stock.pe_ratio)}</td>
                      <td className="text-right py-3 px-2 text-sm">{formatNumber(stock.pb_ratio)}</td>
                      <td className="text-right py-3 px-2 text-sm">{formatNumber(stock.roe)}</td>
                      <td className="text-right py-3 px-2 text-sm">{formatNumber(stock.revenue_growth)}</td>
                      <td className="text-right py-3 px-2 text-sm">{formatNumber(stock.dividend_yield)}</td>
                      <td className="text-right py-3 px-2 text-sm">{formatNumber(stock.debt_to_equity)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {!loading && results.length === 0 && !error && selectedTemplate && (
          <div className="bg-white rounded-lg shadow-md p-12 text-center">
            <p className="text-gray-500">
              No stocks match the selected criteria. Try adjusting your filters.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
