/**
 * S39-FE-PERF: Virtualization Utilities
 *
 * Lightweight virtualization for lists without external dependencies.
 */

import {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
  type CSSProperties,
  type FC,
  type ReactNode,
} from 'react';

/**
 * Configuration for virtualized list
 */
interface VirtualListConfig {
  itemHeight: number;
  overscan?: number;
  containerHeight?: number;
}

/**
 * Hook for virtualizing a list
 */
export function useVirtualList<T>(
  items: T[],
  config: VirtualListConfig
): {
  virtualItems: Array<{ item: T; index: number; style: CSSProperties }>;
  totalHeight: number;
  containerRef: React.RefObject<HTMLDivElement>;
  scrollToIndex: (index: number) => void;
} {
  const { itemHeight, overscan = 3 } = config;
  const containerRef = useRef<HTMLDivElement>(null);
  const [scrollTop, setScrollTop] = useState(0);
  const [containerHeight, setContainerHeight] = useState(
    config.containerHeight ?? 400
  );

  // Update container height on resize
  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const updateHeight = () => {
      setContainerHeight(container.clientHeight);
    };

    updateHeight();

    const resizeObserver = new ResizeObserver(updateHeight);
    resizeObserver.observe(container);

    return () => {
      resizeObserver.disconnect();
    };
  }, []);

  // Handle scroll
  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const handleScroll = () => {
      setScrollTop(container.scrollTop);
    };

    container.addEventListener('scroll', handleScroll, { passive: true });

    return () => {
      container.removeEventListener('scroll', handleScroll);
    };
  }, []);

  // Calculate visible range
  const { startIndex, endIndex } = useMemo(() => {
    const start = Math.max(0, Math.floor(scrollTop / itemHeight) - overscan);
    const visibleCount = Math.ceil(containerHeight / itemHeight);
    const end = Math.min(items.length - 1, start + visibleCount + overscan * 2);

    return { startIndex: start, endIndex: end };
  }, [scrollTop, itemHeight, containerHeight, items.length, overscan]);

  // Generate virtual items
  const virtualItems = useMemo(() => {
    const result: Array<{ item: T; index: number; style: CSSProperties }> = [];

    for (let i = startIndex; i <= endIndex; i++) {
      result.push({
        item: items[i],
        index: i,
        style: {
          position: 'absolute',
          top: i * itemHeight,
          left: 0,
          right: 0,
          height: itemHeight,
        },
      });
    }

    return result;
  }, [items, startIndex, endIndex, itemHeight]);

  const totalHeight = items.length * itemHeight;

  const scrollToIndex = useCallback(
    (index: number) => {
      containerRef.current?.scrollTo({
        top: index * itemHeight,
        behavior: 'smooth',
      });
    },
    [itemHeight]
  );

  return {
    virtualItems,
    totalHeight,
    containerRef,
    scrollToIndex,
  };
}

/**
 * Props for VirtualList component
 */
interface VirtualListProps<T> {
  items: T[];
  itemHeight: number;
  overscan?: number;
  className?: string;
  style?: CSSProperties;
  renderItem: (item: T, index: number) => ReactNode;
  getKey?: (item: T, index: number) => string | number;
}

/**
 * Virtualized list component
 */
export function VirtualList<T>({
  items,
  itemHeight,
  overscan,
  className = '',
  style,
  renderItem,
  getKey = (_, index) => index,
}: VirtualListProps<T>): JSX.Element {
  const { virtualItems, totalHeight, containerRef } = useVirtualList(items, {
    itemHeight,
    overscan,
  });

  return (
    <div
      ref={containerRef}
      className={`overflow-auto relative ${className}`}
      style={style}
    >
      <div style={{ height: totalHeight, position: 'relative' }}>
        {virtualItems.map(({ item, index, style: itemStyle }) => (
          <div key={getKey(item, index)} style={itemStyle}>
            {renderItem(item, index)}
          </div>
        ))}
      </div>
    </div>
  );
}

/**
 * Hook for infinite scroll
 */
interface UseInfiniteScrollOptions {
  hasMore: boolean;
  isLoading: boolean;
  onLoadMore: () => void;
  threshold?: number;
}

export function useInfiniteScroll({
  hasMore,
  isLoading,
  onLoadMore,
  threshold = 100,
}: UseInfiniteScrollOptions): React.RefObject<HTMLDivElement> {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const handleScroll = () => {
      if (isLoading || !hasMore) return;

      const { scrollTop, scrollHeight, clientHeight } = container;
      const distanceFromBottom = scrollHeight - scrollTop - clientHeight;

      if (distanceFromBottom < threshold) {
        onLoadMore();
      }
    };

    container.addEventListener('scroll', handleScroll, { passive: true });

    return () => {
      container.removeEventListener('scroll', handleScroll);
    };
  }, [hasMore, isLoading, onLoadMore, threshold]);

  return containerRef;
}

/**
 * Props for InfiniteScrollList component
 */
interface InfiniteScrollListProps<T> {
  items: T[];
  hasMore: boolean;
  isLoading: boolean;
  onLoadMore: () => void;
  className?: string;
  style?: CSSProperties;
  renderItem: (item: T, index: number) => ReactNode;
  getKey?: (item: T, index: number) => string | number;
  loadingIndicator?: ReactNode;
  emptyMessage?: ReactNode;
}

/**
 * Infinite scroll list component
 */
export function InfiniteScrollList<T>({
  items,
  hasMore,
  isLoading,
  onLoadMore,
  className = '',
  style,
  renderItem,
  getKey = (_, index) => index,
  loadingIndicator = <div className="p-4 text-center">Loading...</div>,
  emptyMessage = <div className="p-4 text-center text-gray-500">No items</div>,
}: InfiniteScrollListProps<T>): JSX.Element {
  const containerRef = useInfiniteScroll({
    hasMore,
    isLoading,
    onLoadMore,
  });

  return (
    <div ref={containerRef} className={`overflow-auto ${className}`} style={style}>
      {items.length === 0 && !isLoading ? (
        emptyMessage
      ) : (
        <>
          {items.map((item, index) => (
            <div key={getKey(item, index)}>{renderItem(item, index)}</div>
          ))}
          {isLoading && loadingIndicator}
        </>
      )}
    </div>
  );
}
