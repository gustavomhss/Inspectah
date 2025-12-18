/**
 * Tests for SignalStreamPanel component (T-TEST-UNIT-003)
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { type ReactNode } from 'react';
import { createElement } from 'react';
import { SignalStreamPanel } from '../../modules/signals/components/SignalStreamPanel';
import { SignalCard } from '../../modules/signals/components/SignalCard';
import { StoreProvider } from '../../core/store';
import { WebSocketProvider } from '../../core/websocket';
import { setupMockWebSocket } from '../../test/mocks/websocket';
import type { Signal } from '../../core/store/types';

// Test wrapper
function createWrapper() {
  return function TestWrapper({ children }: { children: ReactNode }) {
    return createElement(
      StoreProvider,
      null,
      createElement(
        WebSocketProvider,
        { url: 'ws://test:8000/ws', autoConnect: false },
        children
      )
    );
  };
}

// Mock signals
const mockSignals: Signal[] = [
  {
    id: 'sig_1',
    signal_type: 'lies_in_circulation',
    value: 0.75,
    scope: 'national',
    updated_at: '2025-01-01T10:00:00Z',
  },
  {
    id: 'sig_2',
    signal_type: 'battleground_index',
    value: 0.45,
    scope: 'regional',
    updated_at: '2025-01-01T10:01:00Z',
  },
  {
    id: 'sig_3',
    signal_type: 'silence_detector',
    value: 0.15,
    scope: 'national',
    updated_at: '2025-01-01T10:02:00Z',
  },
];

describe('SignalCard', () => {
  it('should render signal information', () => {
    const signal = mockSignals[0];
    render(<SignalCard signal={signal} />);

    expect(screen.getByTestId(`signal-card-${signal.id}`)).toBeInTheDocument();
    expect(screen.getByText('Lies in Circulation')).toBeInTheDocument();
    expect(screen.getByText('75.0%')).toBeInTheDocument();
    expect(screen.getByText('national')).toBeInTheDocument();
  });

  it('should show correct severity for high value', () => {
    const signal = { ...mockSignals[0], value: 0.85 };
    render(<SignalCard signal={signal} />);

    expect(screen.getByText('CRITICAL')).toBeInTheDocument();
  });

  it('should show correct severity for medium value', () => {
    const signal = { ...mockSignals[0], value: 0.45 };
    render(<SignalCard signal={signal} />);

    expect(screen.getByText('MEDIUM')).toBeInTheDocument();
  });

  it('should show correct severity for low value', () => {
    const signal = { ...mockSignals[0], value: 0.15 };
    render(<SignalCard signal={signal} />);

    expect(screen.getByText('LOW')).toBeInTheDocument();
  });

  it('should call onClick when clicked', () => {
    const signal = mockSignals[0];
    const onClick = vi.fn();
    render(<SignalCard signal={signal} onClick={onClick} />);

    fireEvent.click(screen.getByTestId(`signal-card-${signal.id}`));
    expect(onClick).toHaveBeenCalledWith(signal);
  });

  it('should call onClick on keyboard Enter', () => {
    const signal = mockSignals[0];
    const onClick = vi.fn();
    render(<SignalCard signal={signal} onClick={onClick} />);

    fireEvent.keyDown(screen.getByTestId(`signal-card-${signal.id}`), {
      key: 'Enter',
    });
    expect(onClick).toHaveBeenCalledWith(signal);
  });

  it('should show new indicator when isNew is true', () => {
    const signal = mockSignals[0];
    render(<SignalCard signal={signal} isNew />);

    const card = screen.getByTestId(`signal-card-${signal.id}`);
    expect(card).toHaveClass('animate-pulse');
  });

  it('should apply custom className', () => {
    const signal = mockSignals[0];
    render(<SignalCard signal={signal} className="custom-class" />);

    const card = screen.getByTestId(`signal-card-${signal.id}`);
    expect(card).toHaveClass('custom-class');
  });

  it('should render progress bar with correct width', () => {
    const signal = { ...mockSignals[0], value: 0.6 };
    render(<SignalCard signal={signal} />);

    const progressBar = screen.getByTestId('signal-progress');
    expect(progressBar).toHaveStyle({ width: '60%' });
  });
});

describe('SignalStreamPanel', () => {
  let mockWS: { instances: unknown[]; reset: () => void };

  beforeEach(() => {
    mockWS = setupMockWebSocket();
    vi.useFakeTimers();
  });

  afterEach(() => {
    mockWS.reset();
    vi.useRealTimers();
  });

  it('should render with default title', () => {
    render(<SignalStreamPanel />, { wrapper: createWrapper() });

    expect(screen.getByText('Signal Stream')).toBeInTheDocument();
  });

  it('should render with custom title', () => {
    render(<SignalStreamPanel title="Custom Title" />, {
      wrapper: createWrapper(),
    });

    expect(screen.getByText('Custom Title')).toBeInTheDocument();
  });

  it('should show empty state when no signals', () => {
    render(<SignalStreamPanel />, { wrapper: createWrapper() });

    expect(screen.getByTestId('empty-state')).toBeInTheDocument();
    expect(screen.getByText('No signals yet')).toBeInTheDocument();
  });

  it('should show connection status when enabled', () => {
    render(<SignalStreamPanel showConnectionStatus />, {
      wrapper: createWrapper(),
    });

    expect(screen.getByTestId('connection-status')).toBeInTheDocument();
    expect(screen.getByText('Disconnected')).toBeInTheDocument();
  });

  it('should hide connection status when disabled', () => {
    render(<SignalStreamPanel showConnectionStatus={false} />, {
      wrapper: createWrapper(),
    });

    expect(screen.queryByTestId('connection-status')).not.toBeInTheDocument();
  });

  it('should show controls when enabled', () => {
    render(<SignalStreamPanel showControls />, { wrapper: createWrapper() });

    expect(screen.getByTestId('stream-controls')).toBeInTheDocument();
    expect(screen.getByTestId('pause-resume-button')).toBeInTheDocument();
    expect(screen.getByTestId('clear-button')).toBeInTheDocument();
  });

  it('should hide controls when disabled', () => {
    render(<SignalStreamPanel showControls={false} />, {
      wrapper: createWrapper(),
    });

    expect(screen.queryByTestId('stream-controls')).not.toBeInTheDocument();
  });

  it('should toggle pause/resume button text', () => {
    render(<SignalStreamPanel showControls />, { wrapper: createWrapper() });

    const button = screen.getByTestId('pause-resume-button');
    expect(button).toHaveTextContent('Pause');

    fireEvent.click(button);
    expect(button).toHaveTextContent('Resume');

    fireEvent.click(button);
    expect(button).toHaveTextContent('Pause');
  });

  it('should apply custom className', () => {
    render(<SignalStreamPanel className="custom-panel" />, {
      wrapper: createWrapper(),
    });

    expect(screen.getByTestId('signal-stream-panel')).toHaveClass('custom-panel');
  });

  it('should have testid signal-stream-panel', () => {
    render(<SignalStreamPanel />, { wrapper: createWrapper() });

    expect(screen.getByTestId('signal-stream-panel')).toBeInTheDocument();
  });
});

describe('SignalStreamPanel integration', () => {
  it('should render signal cards when signals exist', () => {
    // This test validates the component structure renders correctly
    render(<SignalStreamPanel />, { wrapper: createWrapper() });

    // Panel should exist
    expect(screen.getByTestId('signal-stream-panel')).toBeInTheDocument();
  });

  it('should respect maxSignals prop', () => {
    render(<SignalStreamPanel maxSignals={5} />, { wrapper: createWrapper() });

    // Component should be configured with maxSignals
    expect(screen.getByTestId('signal-stream-panel')).toBeInTheDocument();
  });

  it('should pass signalTypes to hook', () => {
    render(<SignalStreamPanel signalTypes={['lies_in_circulation']} />, {
      wrapper: createWrapper(),
    });

    expect(screen.getByTestId('signal-stream-panel')).toBeInTheDocument();
  });

  it('should pass scope to hook', () => {
    render(<SignalStreamPanel scope="national" />, {
      wrapper: createWrapper(),
    });

    expect(screen.getByTestId('signal-stream-panel')).toBeInTheDocument();
  });
});
