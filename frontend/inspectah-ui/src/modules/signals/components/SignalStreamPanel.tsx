/**
 * S39-W4: SignalStreamPanel Component (T-TEST-UNIT-003)
 *
 * Real-time signal streaming display panel.
 */

import { type FC, memo, useState, useCallback, useMemo } from 'react';
import { useSignalStream } from '../hooks/useSignalStream';
import { SignalCard } from './SignalCard';
import type { Signal } from '../../../core/store/types';

export interface SignalStreamPanelProps {
  /** Signal types to display */
  signalTypes?: string[];
  /** Scope filter */
  scope?: string;
  /** Maximum signals to show */
  maxSignals?: number;
  /** Panel title */
  title?: string;
  /** Callback when signal is clicked */
  onSignalClick?: (signal: Signal) => void;
  /** Additional CSS classes */
  className?: string;
  /** Show connection status */
  showConnectionStatus?: boolean;
  /** Show controls (pause/resume) */
  showControls?: boolean;
}

/**
 * Connection status indicator
 */
const ConnectionStatus: FC<{ isConnected: boolean }> = memo(function ConnectionStatus({
  isConnected,
}) {
  return (
    <div className="flex items-center gap-2" data-testid="connection-status">
      <span
        className={`h-2 w-2 rounded-full ${
          isConnected ? 'bg-green-500' : 'bg-red-500'
        }`}
      />
      <span className="text-xs text-gray-500">
        {isConnected ? 'Connected' : 'Disconnected'}
      </span>
    </div>
  );
});

/**
 * Stream controls
 */
const StreamControls: FC<{
  isPaused: boolean;
  onPause: () => void;
  onResume: () => void;
  onClear: () => void;
}> = memo(function StreamControls({ isPaused, onPause, onResume, onClear }) {
  return (
    <div className="flex items-center gap-2" data-testid="stream-controls">
      <button
        onClick={isPaused ? onResume : onPause}
        className={`px-3 py-1 text-xs rounded ${
          isPaused
            ? 'bg-green-100 text-green-700 hover:bg-green-200'
            : 'bg-yellow-100 text-yellow-700 hover:bg-yellow-200'
        }`}
        data-testid="pause-resume-button"
      >
        {isPaused ? 'Resume' : 'Pause'}
      </button>
      <button
        onClick={onClear}
        className="px-3 py-1 text-xs rounded bg-gray-100 text-gray-700 hover:bg-gray-200"
        data-testid="clear-button"
      >
        Clear
      </button>
    </div>
  );
});

/**
 * Empty state
 */
const EmptyState: FC = memo(function EmptyState() {
  return (
    <div
      className="flex flex-col items-center justify-center py-12 text-gray-500"
      data-testid="empty-state"
    >
      <svg
        className="w-12 h-12 mb-4 text-gray-300"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={1.5}
          d="M13 10V3L4 14h7v7l9-11h-7z"
        />
      </svg>
      <p className="text-sm">No signals yet</p>
      <p className="text-xs text-gray-400">Waiting for real-time updates...</p>
    </div>
  );
});

/**
 * Signal Stream Panel
 */
export const SignalStreamPanel: FC<SignalStreamPanelProps> = memo(
  function SignalStreamPanel({
    signalTypes = [],
    scope,
    maxSignals = 20,
    title = 'Signal Stream',
    onSignalClick,
    className = '',
    showConnectionStatus = true,
    showControls = true,
  }) {
    const {
      signals,
      isConnected,
      isPaused,
      lastUpdate,
      pause,
      resume,
      clear,
    } = useSignalStream({
      signalTypes,
      scope,
      maxHistory: maxSignals,
    });

    // Track recently updated signals for animation
    const [recentIds, setRecentIds] = useState<Set<string>>(new Set());

    // Handle new signals with animation
    const handleNewSignals = useCallback((newSignals: Signal[]) => {
      const ids = new Set(newSignals.slice(0, 3).map((s) => s.id));
      setRecentIds(ids);

      // Clear animation after delay
      setTimeout(() => {
        setRecentIds(new Set());
      }, 2000);
    }, []);

    // Sort signals by update time
    const sortedSignals = useMemo(() => {
      return [...signals]
        .sort((a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime())
        .slice(0, maxSignals);
    }, [signals, maxSignals]);

    // Format last update time
    const lastUpdateFormatted = useMemo(() => {
      if (!lastUpdate) return null;
      return new Date(lastUpdate).toLocaleTimeString('pt-BR', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
      });
    }, [lastUpdate]);

    return (
      <div
        className={`bg-white rounded-lg border border-gray-200 ${className}`}
        data-testid="signal-stream-panel"
      >
        {/* Header */}
        <div className="px-4 py-3 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-lg font-semibold text-gray-900">{title}</h2>
              {lastUpdateFormatted && (
                <p className="text-xs text-gray-500">
                  Last update: {lastUpdateFormatted}
                </p>
              )}
            </div>
            <div className="flex items-center gap-4">
              {showConnectionStatus && <ConnectionStatus isConnected={isConnected} />}
              {showControls && (
                <StreamControls
                  isPaused={isPaused}
                  onPause={pause}
                  onResume={resume}
                  onClear={clear}
                />
              )}
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="p-4">
          {sortedSignals.length === 0 ? (
            <EmptyState />
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {sortedSignals.map((signal) => (
                <SignalCard
                  key={signal.id}
                  signal={signal}
                  onClick={onSignalClick}
                  isNew={recentIds.has(signal.id)}
                />
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        {sortedSignals.length > 0 && (
          <div className="px-4 py-2 border-t border-gray-200 bg-gray-50 rounded-b-lg">
            <div className="flex items-center justify-between text-xs text-gray-500">
              <span>
                Showing {sortedSignals.length} of {signals.length} signals
              </span>
              {isPaused && (
                <span className="text-yellow-600 font-medium">Stream paused</span>
              )}
            </div>
          </div>
        )}
      </div>
    );
  }
);

export default SignalStreamPanel;
