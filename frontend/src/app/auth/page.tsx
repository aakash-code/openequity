'use client';

import React, { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import AuthForm from '@/components/AuthForm';
import { useAuth } from '@/lib/auth-context';

export default function AuthPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { isAuthenticated } = useAuth();

  const [mode, setMode] = useState<'login' | 'register'>('login');

  useEffect(() => {
    // Get mode from URL params
    const urlMode = searchParams.get('mode');
    if (urlMode === 'register') {
      setMode('register');
    }
  }, [searchParams]);

  useEffect(() => {
    // Redirect to dashboard if already authenticated
    if (isAuthenticated) {
      router.push('/dashboard');
    }
  }, [isAuthenticated, router]);

  const handleSuccess = () => {
    router.push('/dashboard');
  };

  const toggleMode = () => {
    const newMode = mode === 'login' ? 'register' : 'login';
    setMode(newMode);
    router.push(`/auth${newMode === 'register' ? '?mode=register' : ''}`);
  };

  if (isAuthenticated) {
    return null; // Will redirect
  }

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">OpenEquity</h1>
          <p className="text-gray-600">Professional equity research, democratized.</p>
        </div>

        <AuthForm mode={mode} onSuccess={handleSuccess} onToggleMode={toggleMode} />

        <div className="mt-6 text-center text-sm text-gray-600">
          <p>
            By signing in, you agree to our Terms of Service and Privacy Policy.
          </p>
        </div>
      </div>
    </div>
  );
}
