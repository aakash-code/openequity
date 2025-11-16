'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth-context';
import CompanySearch from '@/components/CompanySearch';
import { api, Company } from '@/lib/api';

export default function DashboardPage() {
  const router = useRouter();
  const { user, isAuthenticated, loading } = useAuth();
  const [recentCompanies, setRecentCompanies] = useState<Company[]>([]);
  const [selectedCompany, setSelectedCompany] = useState<Company | null>(null);

  useEffect(() => {
    if (!loading && !isAuthenticated) {
      router.push('/auth');
    }
  }, [isAuthenticated, loading, router]);

  useEffect(() => {
    const fetchRecentCompanies = async () => {
      if (isAuthenticated) {
        try {
          const companies = await api.getCompanies({ limit: 10 });
          setRecentCompanies(companies);
        } catch (error) {
          console.error('Failed to fetch companies:', error);
        }
      }
    };

    fetchRecentCompanies();
  }, [isAuthenticated]);

  const formatMarketCap = (marketCap?: number) => {
    if (!marketCap) return 'N/A';
    if (marketCap >= 1e12) return `$${(marketCap / 1e12).toFixed(2)}T`;
    if (marketCap >= 1e9) return `$${(marketCap / 1e9).toFixed(2)}B`;
    if (marketCap >= 1e6) return `$${(marketCap / 1e6).toFixed(2)}M`;
    return `$${marketCap.toLocaleString()}`;
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
          <h1 className="text-3xl font-bold text-gray-900">
            Welcome back, {user?.full_name || user?.email?.split('@')[0]}!
          </h1>
          <p className="text-gray-600 mt-2">
            Start your equity research with professional-grade tools
          </p>
        </div>

        {/* Company Search */}
        <div className="mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Search Companies</h2>
          <CompanySearch
            onSelectCompany={(company) => {
              setSelectedCompany(company);
            }}
          />
        </div>

        {/* Selected Company Details */}
        {selectedCompany && (
          <div className="mb-8 bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Company Details</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h3 className="text-lg font-bold text-gray-900 mb-2">
                  {selectedCompany.ticker} - {selectedCompany.name}
                </h3>
                {selectedCompany.description && (
                  <p className="text-gray-700 text-sm">{selectedCompany.description}</p>
                )}
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-gray-500">Sector</p>
                  <p className="font-medium text-gray-900">{selectedCompany.sector || 'N/A'}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Industry</p>
                  <p className="font-medium text-gray-900">{selectedCompany.industry || 'N/A'}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Market Cap</p>
                  <p className="font-medium text-gray-900">
                    {formatMarketCap(selectedCompany.market_cap)}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Exchange</p>
                  <p className="font-medium text-gray-900">{selectedCompany.exchange || 'N/A'}</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Recent Companies */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Available Companies</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {recentCompanies.map((company) => (
              <button
                key={company.ticker}
                onClick={() => setSelectedCompany(company)}
                className="p-4 border border-gray-200 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition text-left"
              >
                <div className="flex justify-between items-start mb-2">
                  <div>
                    <h3 className="font-bold text-gray-900">{company.ticker}</h3>
                    <p className="text-sm text-gray-600 truncate">{company.name}</p>
                  </div>
                  <span className="text-xs bg-gray-100 px-2 py-1 rounded">{company.exchange}</span>
                </div>
                <div className="flex justify-between items-end">
                  <span className="text-xs text-gray-500">{company.sector}</span>
                  <span className="text-sm font-medium text-primary-600">
                    {formatMarketCap(company.market_cap)}
                  </span>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Quick Actions */}
        <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Financial Models</h3>
            <p className="text-sm text-gray-600 mb-4">
              Create DCF, comparable company, and other valuation models
            </p>
            <button className="w-full bg-primary-600 text-white py-2 px-4 rounded-md hover:bg-primary-700 transition">
              Create Model
            </button>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Watchlists</h3>
            <p className="text-sm text-gray-600 mb-4">
              Track your favorite companies and monitor their performance
            </p>
            <button className="w-full bg-primary-600 text-white py-2 px-4 rounded-md hover:bg-primary-700 transition">
              View Watchlists
            </button>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">CFA Study Tools</h3>
            <p className="text-sm text-gray-600 mb-4">
              Practice problems and mock exams aligned with CFA curriculum
            </p>
            <button className="w-full bg-primary-600 text-white py-2 px-4 rounded-md hover:bg-primary-700 transition">
              Start Learning
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
