/**
 * Tests for virtualization utilities
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { renderHook, act } from '@testing-library/react';
import { useVirtualList, VirtualList, useInfiniteScroll } from '../../core/performance/virtualization';

// Mock ResizeObserver
class MockResizeObserver {
  callback: ResizeObserverCallback;

  constructor(callback: ResizeObserverCallback) {
    this.callback = callback;
  }

  observe() {
    // Simulate initial call
    this.callback([], this as unknown as ResizeObserver);
  }

  disconnect() {}
  unobserve() {}
}

beforeEach(() => {
  globalThis.ResizeObserver = MockResizeObserver as unknown as typeof ResizeObserver;
});

describe('useVirtualList', () => {
  it('should calculate virtual items for visible range', () => {
    const items = Array.from({ length: 100 }, (_, i) => ({ id: i, name: `Item ${i}` }));

    const { result } = renderHook(() =>
      useVirtualList(items, { itemHeight: 40, overscan: 2, containerHeight: 400 })
    );

    // Should have some virtual items (based on visible range + overscan)
    expect(result.current.virtualItems.length).toBeGreaterThan(0);
    expect(result.current.virtualItems.length).toBeLessThan(items.length);

    // Total height should be items * itemHeight
    expect(result.current.totalHeight).toBe(100 * 40);
  });

  it('should provide scrollToIndex function', () => {
    const items = Array.from({ length: 100 }, (_, i) => ({ id: i }));

    const { result } = renderHook(() =>
      useVirtualList(items, { itemHeight: 40 })
    );

    expect(typeof result.current.scrollToIndex).toBe('function');
  });

  it('should provide container ref', () => {
    const items = [{ id: 1 }];

    const { result } = renderHook(() =>
      useVirtualList(items, { itemHeight: 40 })
    );

    expect(result.current.containerRef).toBeDefined();
  });
});

describe('VirtualList', () => {
  it('should render visible items', () => {
    const items = Array.from({ length: 100 }, (_, i) => ({ id: i, name: `Item ${i}` }));

    render(
      <VirtualList
        items={items}
        itemHeight={40}
        style={{ height: 200 }}
        renderItem={(item) => <div data-testid={`item-${item.id}`}>{item.name}</div>}
        getKey={(item) => item.id}
      />
    );

    // Should render some items but not all
    const renderedItems = screen.queryAllByTestId(/^item-/);
    expect(renderedItems.length).toBeGreaterThan(0);
    expect(renderedItems.length).toBeLessThan(100);
  });

  it('should use custom getKey function', () => {
    const items = [
      { customId: 'a', name: 'Item A' },
      { customId: 'b', name: 'Item B' },
    ];

    const getKey = vi.fn((item: typeof items[0]) => item.customId);

    render(
      <VirtualList
        items={items}
        itemHeight={40}
        style={{ height: 200 }}
        renderItem={(item) => <div>{item.name}</div>}
        getKey={getKey}
      />
    );

    expect(getKey).toHaveBeenCalled();
  });

  it('should apply custom className', () => {
    const items = [{ id: 1 }];

    const { container } = render(
      <VirtualList
        items={items}
        itemHeight={40}
        className="custom-class"
        renderItem={(item) => <div>{item.id}</div>}
      />
    );

    expect(container.firstChild).toHaveClass('custom-class');
  });
});

describe('useInfiniteScroll', () => {
  it('should return container ref', () => {
    const onLoadMore = vi.fn();

    const { result } = renderHook(() =>
      useInfiniteScroll({
        hasMore: true,
        isLoading: false,
        onLoadMore,
      })
    );

    expect(result.current).toBeDefined();
  });

  it('should not call onLoadMore when loading', () => {
    const onLoadMore = vi.fn();

    renderHook(() =>
      useInfiniteScroll({
        hasMore: true,
        isLoading: true,
        onLoadMore,
      })
    );

    expect(onLoadMore).not.toHaveBeenCalled();
  });

  it('should not call onLoadMore when hasMore is false', () => {
    const onLoadMore = vi.fn();

    renderHook(() =>
      useInfiniteScroll({
        hasMore: false,
        isLoading: false,
        onLoadMore,
      })
    );

    expect(onLoadMore).not.toHaveBeenCalled();
  });
});

describe('InfiniteScrollList', () => {
  // Import dynamically to avoid issues
  it('should render items', async () => {
    const { InfiniteScrollList } = await import('../../core/performance/virtualization');
    const items = [{ id: 1, name: 'Item 1' }, { id: 2, name: 'Item 2' }];
    const onLoadMore = vi.fn();

    render(
      <InfiniteScrollList
        items={items}
        hasMore={true}
        isLoading={false}
        onLoadMore={onLoadMore}
        renderItem={(item) => <div data-testid={`item-${item.id}`}>{item.name}</div>}
        getKey={(item) => item.id}
      />
    );

    expect(screen.getByTestId('item-1')).toBeInTheDocument();
    expect(screen.getByTestId('item-2')).toBeInTheDocument();
  });

  it('should show empty message when no items', async () => {
    const { InfiniteScrollList } = await import('../../core/performance/virtualization');
    const onLoadMore = vi.fn();

    render(
      <InfiniteScrollList
        items={[]}
        hasMore={false}
        isLoading={false}
        onLoadMore={onLoadMore}
        renderItem={() => <div />}
        emptyMessage={<div data-testid="empty">No items found</div>}
      />
    );

    expect(screen.getByTestId('empty')).toBeInTheDocument();
  });

  it('should show loading indicator when loading', async () => {
    const { InfiniteScrollList } = await import('../../core/performance/virtualization');
    const items = [{ id: 1 }];
    const onLoadMore = vi.fn();

    render(
      <InfiniteScrollList
        items={items}
        hasMore={true}
        isLoading={true}
        onLoadMore={onLoadMore}
        renderItem={(item) => <div>{item.id}</div>}
        loadingIndicator={<div data-testid="loading">Loading...</div>}
      />
    );

    expect(screen.getByTestId('loading')).toBeInTheDocument();
  });
});
