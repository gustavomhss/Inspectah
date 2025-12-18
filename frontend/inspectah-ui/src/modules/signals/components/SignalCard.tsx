/**
 * S39-W4: SignalCard Component
 *
 * Individual signal display card with real-time updates.
 */

import { type FC, memo, useMemo } from 'react';
import type { Signal } from '../../../core/store/types';

export interface SignalCardProps {
  signal: Signal;
  onClick?: (signal: Signal) => void;
  isNew?: boolean;
  className?: string;
}

/**
 * Format signal value as percentage
 */
function formatValue(value: number): string {
  return `${(value * 100).toFixed(1)}%`;
}

/**
 * Get signal severity based on value
 */
function getSeverity(value: number): 'low' | 'medium' | 'high' | 'critical' {
  if (value < 0.25) return 'low';
  if (value < 0.5) return 'medium';
  if (value < 0.75) return 'high';
  return 'critical';
}

/**
 * Get color classes based on severity
 */
function getSeverityColors(severity: ReturnType<typeof getSeverity>): {
  bg: string;
  text: string;
  border: string;
} {
  switch (severity) {
    case 'low':
      return {
        bg: 'bg-green-50',
        text: 'text-green-700',
        border: 'border-green-200',
      };
    case 'medium':
      return {
        bg: 'bg-yellow-50',
        text: 'text-yellow-700',
        border: 'border-yellow-200',
      };
    case 'high':
      return {
        bg: 'bg-orange-50',
        text: 'text-orange-700',
        border: 'border-orange-200',
      };
    case 'critical':
      return {
        bg: 'bg-red-50',
        text: 'text-red-700',
        border: 'border-red-200',
      };
  }
}

/**
 * Get human-readable signal type name
 */
function getSignalTypeName(type: string): string {
  const names: Record<string, string> = {
    lies_in_circulation: 'Lies in Circulation',
    battleground_index: 'Battleground Index',
    silence_detector: 'Silence Detector',
    fragility_score: 'Fragility Score',
    velocity: 'Spread Velocity',
    impact: 'Impact Score',
  };
  return names[type] ?? type.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
}

/**
 * Format timestamp
 */
function formatTime(timestamp: string): string {
  const date = new Date(timestamp);
  return date.toLocaleTimeString('pt-BR', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  });
}

/**
 * Signal Card Component
 */
export const SignalCard: FC<SignalCardProps> = memo(function SignalCard({
  signal,
  onClick,
  isNew = false,
  className = '',
}) {
  const severity = useMemo(() => getSeverity(signal.value), [signal.value]);
  const colors = useMemo(() => getSeverityColors(severity), [severity]);

  return (
    <div
      data-testid={`signal-card-${signal.id}`}
      className={`
        relative rounded-lg border p-4 cursor-pointer
        transition-all duration-200
        hover:shadow-md
        ${colors.bg} ${colors.border}
        ${isNew ? 'animate-pulse ring-2 ring-blue-400' : ''}
        ${className}
      `}
      onClick={() => onClick?.(signal)}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          onClick?.(signal);
        }
      }}
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-2">
        <h3 className="font-medium text-gray-900 text-sm">
          {getSignalTypeName(signal.signal_type)}
        </h3>
        <span
          className={`px-2 py-0.5 rounded text-xs font-medium ${colors.text} ${colors.bg}`}
        >
          {severity.toUpperCase()}
        </span>
      </div>

      {/* Value */}
      <div className="mb-2">
        <span className={`text-2xl font-bold ${colors.text}`}>
          {formatValue(signal.value)}
        </span>
      </div>

      {/* Progress bar */}
      <div className="w-full bg-gray-200 rounded-full h-2 mb-2">
        <div
          className={`h-2 rounded-full transition-all duration-300 ${
            severity === 'low'
              ? 'bg-green-500'
              : severity === 'medium'
                ? 'bg-yellow-500'
                : severity === 'high'
                  ? 'bg-orange-500'
                  : 'bg-red-500'
          }`}
          style={{ width: `${signal.value * 100}%` }}
          data-testid="signal-progress"
        />
      </div>

      {/* Footer */}
      <div className="flex items-center justify-between text-xs text-gray-500">
        <span className="capitalize">{signal.scope}</span>
        <span>{formatTime(signal.updated_at)}</span>
      </div>

      {/* New indicator */}
      {isNew && (
        <div className="absolute -top-1 -right-1">
          <span className="flex h-3 w-3">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75" />
            <span className="relative inline-flex rounded-full h-3 w-3 bg-blue-500" />
          </span>
        </div>
      )}
    </div>
  );
});

export default SignalCard;
