'use client';

import React from 'react';
import Link from 'next/link';
import { useAuth } from '@/lib/auth-context';

export default function Navbar() {
  const { user, logout, isAuthenticated } = useAuth();

  return (
    <nav className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <Link href="/" className="flex items-center">
              <span className="text-2xl font-bold text-primary-600">OpenEquity</span>
            </Link>

            {isAuthenticated && (
              <div className="hidden md:ml-10 md:flex md:space-x-8">
                <Link
                  href="/dashboard"
                  className="text-gray-700 hover:text-primary-600 px-3 py-2 text-sm font-medium transition"
                >
                  Dashboard
                </Link>
                <Link
                  href="/companies"
                  className="text-gray-700 hover:text-primary-600 px-3 py-2 text-sm font-medium transition"
                >
                  Companies
                </Link>
                <Link
                  href="/valuations"
                  className="text-gray-700 hover:text-primary-600 px-3 py-2 text-sm font-medium transition"
                >
                  Valuations
                </Link>
                <Link
                  href="/models"
                  className="text-gray-700 hover:text-primary-600 px-3 py-2 text-sm font-medium transition"
                >
                  Models
                </Link>
                <Link
                  href="/portfolios"
                  className="text-gray-700 hover:text-primary-600 px-3 py-2 text-sm font-medium transition"
                >
                  Portfolios
                </Link>
                <Link
                  href="/screener"
                  className="text-gray-700 hover:text-primary-600 px-3 py-2 text-sm font-medium transition"
                >
                  Screener
                </Link>
                <Link
                  href="/indian-market"
                  className="text-gray-700 hover:text-primary-600 px-3 py-2 text-sm font-medium transition"
                >
                  Indian Market
                </Link>
                <Link
                  href="/ipo"
                  className="text-gray-700 hover:text-primary-600 px-3 py-2 text-sm font-medium transition"
                >
                  IPO
                </Link>
                <Link
                  href="/options"
                  className="text-gray-700 hover:text-primary-600 px-3 py-2 text-sm font-medium transition"
                >
                  Options
                </Link>
                <Link
                  href="/technical-analysis"
                  className="text-gray-700 hover:text-primary-600 px-3 py-2 text-sm font-medium transition"
                >
                  Charts
                </Link>
              </div>
            )}
          </div>

          <div className="flex items-center">
            {isAuthenticated ? (
              <div className="flex items-center gap-4">
                <span className="text-sm text-gray-700">
                  {user?.full_name || user?.email}
                </span>
                <button
                  onClick={logout}
                  className="bg-gray-100 hover:bg-gray-200 text-gray-700 px-4 py-2 rounded-md text-sm font-medium transition"
                >
                  Logout
                </button>
              </div>
            ) : (
              <div className="flex items-center gap-4">
                <Link
                  href="/auth"
                  className="text-gray-700 hover:text-primary-600 px-3 py-2 text-sm font-medium transition"
                >
                  Sign In
                </Link>
                <Link
                  href="/auth?mode=register"
                  className="bg-primary-600 hover:bg-primary-700 text-white px-4 py-2 rounded-md text-sm font-medium transition"
                >
                  Get Started
                </Link>
              </div>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}
