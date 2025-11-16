'use client';

import React from 'react';

interface WebSocketStatusProps {
  isConnected: boolean;
  showLabel?: boolean;
  size?: 'sm' | 'md' | 'lg';
}

export default function WebSocketStatus({
  isConnected,
  showLabel = true,
  size = 'sm'
}: WebSocketStatusProps) {
  const sizeClasses = {
    sm: 'w-2 h-2',
    md: 'w-3 h-3',
    lg: 'w-4 h-4'
  };

  const textSizeClasses = {
    sm: 'text-xs',
    md: 'text-sm',
    lg: 'text-base'
  };

  return (
    <div className="flex items-center gap-2">
      <div className="relative">
        <div
          className={`${sizeClasses[size]} rounded-full ${
            isConnected ? 'bg-green-500' : 'bg-red-500'
          }`}
        />
        {isConnected && (
          <div
            className={`absolute inset-0 ${sizeClasses[size]} rounded-full bg-green-500 animate-ping opacity-75`}
          />
        )}
      </div>
      {showLabel && (
        <span className={`${textSizeClasses[size]} font-medium ${isConnected ? 'text-green-700' : 'text-red-700'}`}>
          {isConnected ? 'Live' : 'Disconnected'}
        </span>
      )}
    </div>
  );
}
