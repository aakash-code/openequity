'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth-context';
import { api, CreateDCFRequest } from '@/lib/api';
import CompanySearch from '@/components/CompanySearch';

export default function NewDCFPage() {
  const router = useRouter();
  const { isAuthenticated, loading: authLoading } = useAuth();
  const [selectedTicker, setSelectedTicker] = useState('');
  const [modelName, setModelName] = useState('');
  const [description, setDescription] = useState('');
  const [isPublic, setIsPublic] = useState(false);

  // Base data
  const [baseRevenue, setBaseRevenue] = useState('');
  const [netDebt, setNetDebt] = useState('');
  const [sharesOutstanding, setSharesOutstanding] = useState('');
  const [currentPrice, setCurrentPrice] = useState('');

  // WACC assumptions
  const [riskFreeRate, setRiskFreeRate] = useState('4.5');
  const [equityRiskPremium, setEquityRiskPremium] = useState('6.0');
  const [beta, setBeta] = useState('1.0');
  const [costOfDebt, setCostOfDebt] = useState('5.0');
  const [taxRate, setTaxRate] = useState('21.0');
  const [debtWeight, setDebtWeight] = useState('20.0');
  const [equityWeight, setEquityWeight] = useState('80.0');

  // Projection assumptions
  const [projectionYears, setProjectionYears] = useState(5);
  const [revenueGrowthRates, setRevenueGrowthRates] = useState(['10', '9', '8', '7', '6']);
  const [ebitdaMargin, setEbitdaMargin] = useState('25.0');
  const [depreciationPct, setDepreciationPct] = useState('3.0');
  const [capexPct, setCapexPct] = useState('4.0');
  const [nwcPct, setNwcPct] = useState('2.0');

  // Terminal value
  const [terminalMethod, setTerminalMethod] = useState<'growth' | 'multiple'>('growth');
  const [terminalGrowthRate, setTerminalGrowthRate] = useState('2.5');
  const [terminalEbitdaMultiple, setTerminalEbitdaMultiple] = useState('10.0');

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  React.useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/auth');
    }
  }, [isAuthenticated, authLoading, router]);

  React.useEffect(() => {
    // Adjust growth rates array when projection years change
    const currentLength = revenueGrowthRates.length;
    if (projectionYears > currentLength) {
      const lastRate = revenueGrowthRates[currentLength - 1] || '5';
      const newRates = [...revenueGrowthRates];
      for (let i = currentLength; i < projectionYears; i++) {
        newRates.push(lastRate);
      }
      setRevenueGrowthRates(newRates);
    } else if (projectionYears < currentLength) {
      setRevenueGrowthRates(revenueGrowthRates.slice(0, projectionYears));
    }
  }, [projectionYears]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!selectedTicker) {
      setError('Please select a company');
      return;
    }

    if (!modelName.trim()) {
      setError('Please enter a model name');
      return;
    }

    // Validate numeric inputs
    if (!baseRevenue || parseFloat(baseRevenue) <= 0) {
      setError('Please enter a valid base revenue');
      return;
    }

    setLoading(true);

    try {
      const data: CreateDCFRequest = {
        ticker: selectedTicker,
        name: modelName,
        description: description || undefined,
        is_public: isPublic,
        base_revenue: parseFloat(baseRevenue),
        net_debt: parseFloat(netDebt) || 0,
        shares_outstanding: parseFloat(sharesOutstanding),
        current_price: currentPrice ? parseFloat(currentPrice) : undefined,
        assumptions: {
          risk_free_rate: parseFloat(riskFreeRate) / 100,
          equity_risk_premium: parseFloat(equityRiskPremium) / 100,
          beta: parseFloat(beta),
          cost_of_debt: parseFloat(costOfDebt) / 100,
          tax_rate: parseFloat(taxRate) / 100,
          debt_weight: parseFloat(debtWeight) / 100,
          equity_weight: parseFloat(equityWeight) / 100,
          projection_years: projectionYears,
          revenue_growth_rates: revenueGrowthRates.map((r) => parseFloat(r) / 100),
          ebitda_margin: parseFloat(ebitdaMargin) / 100,
          depreciation_pct_revenue: parseFloat(depreciationPct) / 100,
          capex_pct_revenue: parseFloat(capexPct) / 100,
          nwc_pct_revenue: parseFloat(nwcPct) / 100,
          terminal_growth_rate:
            terminalMethod === 'growth' ? parseFloat(terminalGrowthRate) / 100 : undefined,
          terminal_ebitda_multiple:
            terminalMethod === 'multiple' ? parseFloat(terminalEbitdaMultiple) : undefined,
        },
      };

      const result = await api.createDCFValuation(data);
      router.push(`/valuations/dcf/${result.id}`);
    } catch (err: any) {
      setError(err.message || 'Failed to create DCF model');
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
          <h1 className="text-3xl font-bold text-gray-900">Create DCF Valuation Model</h1>
          <p className="text-gray-600 mt-2">
            Build a discounted cash flow model to estimate intrinsic equity value
          </p>
        </div>

        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
            <p className="text-red-800 text-sm">{error}</p>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-8">
          {/* Model Details */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Model Details</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Company
                </label>
                <CompanySearch
                  onSelectCompany={(company) => setSelectedTicker(company.ticker)}
                />
                {selectedTicker && (
                  <p className="text-sm text-green-600 mt-2">Selected: {selectedTicker}</p>
                )}
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Model Name *
                </label>
                <input
                  type="text"
                  value={modelName}
                  onChange={(e) => setModelName(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  placeholder="e.g., AAPL Base Case Q4 2024"
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
                  placeholder="Optional description of your assumptions..."
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
                  Make this model public (visible to other users)
                </label>
              </div>
            </div>
          </div>

          {/* Base Data */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Base Financial Data</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Base Revenue (Most Recent Year) *
                </label>
                <input
                  type="number"
                  step="0.01"
                  value={baseRevenue}
                  onChange={(e) => setBaseRevenue(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  placeholder="e.g., 394328000000"
                  required
                />
                <p className="text-xs text-gray-500 mt-1">In currency units (not millions)</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Net Debt (Total Debt - Cash)
                </label>
                <input
                  type="number"
                  step="0.01"
                  value={netDebt}
                  onChange={(e) => setNetDebt(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  placeholder="e.g., 75000000000"
                />
                <p className="text-xs text-gray-500 mt-1">Can be negative if net cash</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Shares Outstanding *
                </label>
                <input
                  type="number"
                  step="0.01"
                  value={sharesOutstanding}
                  onChange={(e) => setSharesOutstanding(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  placeholder="e.g., 15550000000"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Current Stock Price (Optional)
                </label>
                <input
                  type="number"
                  step="0.01"
                  value={currentPrice}
                  onChange={(e) => setCurrentPrice(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  placeholder="e.g., 175.50"
                />
                <p className="text-xs text-gray-500 mt-1">For upside/downside calculation</p>
              </div>
            </div>
          </div>

          {/* WACC Assumptions */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">WACC Assumptions</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Risk-Free Rate (%)
                </label>
                <input
                  type="number"
                  step="0.01"
                  value={riskFreeRate}
                  onChange={(e) => setRiskFreeRate(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
                <p className="text-xs text-gray-500 mt-1">Typically 10-year Treasury yield</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Equity Risk Premium (%)
                </label>
                <input
                  type="number"
                  step="0.01"
                  value={equityRiskPremium}
                  onChange={(e) => setEquityRiskPremium(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
                <p className="text-xs text-gray-500 mt-1">Market return - risk-free rate</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Beta</label>
                <input
                  type="number"
                  step="0.01"
                  value={beta}
                  onChange={(e) => setBeta(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
                <p className="text-xs text-gray-500 mt-1">Stock volatility vs market</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Cost of Debt (%)
                </label>
                <input
                  type="number"
                  step="0.01"
                  value={costOfDebt}
                  onChange={(e) => setCostOfDebt(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
                <p className="text-xs text-gray-500 mt-1">Pre-tax cost of debt</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Tax Rate (%)
                </label>
                <input
                  type="number"
                  step="0.01"
                  value={taxRate}
                  onChange={(e) => setTaxRate(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
                <p className="text-xs text-gray-500 mt-1">Corporate tax rate</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Debt Weight (%)
                </label>
                <input
                  type="number"
                  step="0.01"
                  value={debtWeight}
                  onChange={(e) => {
                    const debt = parseFloat(e.target.value);
                    setDebtWeight(e.target.value);
                    setEquityWeight((100 - debt).toFixed(1));
                  }}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Equity Weight (%)
                </label>
                <input
                  type="number"
                  step="0.01"
                  value={equityWeight}
                  onChange={(e) => {
                    const equity = parseFloat(e.target.value);
                    setEquityWeight(e.target.value);
                    setDebtWeight((100 - equity).toFixed(1));
                  }}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
              </div>
            </div>
          </div>

          {/* Projection Assumptions */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Projection Assumptions</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Projection Years
                </label>
                <select
                  value={projectionYears}
                  onChange={(e) => setProjectionYears(parseInt(e.target.value))}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                >
                  {[3, 4, 5, 6, 7, 8, 9, 10].map((years) => (
                    <option key={years} value={years}>
                      {years} years
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Revenue Growth Rates by Year (%)
                </label>
                <div className="grid grid-cols-2 md:grid-cols-5 gap-2">
                  {revenueGrowthRates.map((rate, index) => (
                    <div key={index}>
                      <label className="text-xs text-gray-500">Year {index + 1}</label>
                      <input
                        type="number"
                        step="0.1"
                        value={rate}
                        onChange={(e) => {
                          const newRates = [...revenueGrowthRates];
                          newRates[index] = e.target.value;
                          setRevenueGrowthRates(newRates);
                        }}
                        className="w-full px-2 py-1 text-sm border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                      />
                    </div>
                  ))}
                </div>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    EBITDA Margin (%)
                  </label>
                  <input
                    type="number"
                    step="0.1"
                    value={ebitdaMargin}
                    onChange={(e) => setEbitdaMargin(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    D&A (% of Revenue)
                  </label>
                  <input
                    type="number"
                    step="0.1"
                    value={depreciationPct}
                    onChange={(e) => setDepreciationPct(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    CapEx (% of Revenue)
                  </label>
                  <input
                    type="number"
                    step="0.1"
                    value={capexPct}
                    onChange={(e) => setCapexPct(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Change in NWC (% of Revenue)
                  </label>
                  <input
                    type="number"
                    step="0.1"
                    value={nwcPct}
                    onChange={(e) => setNwcPct(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Terminal Value */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Terminal Value</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Method</label>
                <div className="flex gap-4">
                  <label className="flex items-center">
                    <input
                      type="radio"
                      value="growth"
                      checked={terminalMethod === 'growth'}
                      onChange={() => setTerminalMethod('growth')}
                      className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300"
                    />
                    <span className="ml-2 text-sm text-gray-700">Perpetual Growth Rate</span>
                  </label>
                  <label className="flex items-center">
                    <input
                      type="radio"
                      value="multiple"
                      checked={terminalMethod === 'multiple'}
                      onChange={() => setTerminalMethod('multiple')}
                      className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300"
                    />
                    <span className="ml-2 text-sm text-gray-700">Exit Multiple</span>
                  </label>
                </div>
              </div>
              {terminalMethod === 'growth' ? (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Terminal Growth Rate (%)
                  </label>
                  <input
                    type="number"
                    step="0.1"
                    value={terminalGrowthRate}
                    onChange={(e) => setTerminalGrowthRate(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    Typically GDP growth rate (2-3%)
                  </p>
                </div>
              ) : (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Terminal EBITDA Multiple
                  </label>
                  <input
                    type="number"
                    step="0.1"
                    value={terminalEbitdaMultiple}
                    onChange={(e) => setTerminalEbitdaMultiple(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                  <p className="text-xs text-gray-500 mt-1">EV/EBITDA exit multiple</p>
                </div>
              )}
            </div>
          </div>

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
              {loading ? 'Creating...' : 'Create DCF Model'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
