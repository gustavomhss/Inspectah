/**
 * S39-FE-PERF: Memoization Utilities
 *
 * Higher-order components and utilities for performance optimization.
 */

import {
  memo,
  useEffect,
  useRef,
  useState,
  type FC,
  type ReactNode,
} from 'react';

/**
 * Type-safe memo wrapper with display name preservation
 */
export function typedMemo<P extends object>(
  Component: FC<P>,
  propsAreEqual?: (prevProps: Readonly<P>, nextProps: Readonly<P>) => boolean
): FC<P> {
  const MemoizedComponent = memo(Component, propsAreEqual) as FC<P>;
  MemoizedComponent.displayName = `Memo(${Component.displayName || Component.name || 'Component'})`;
  return MemoizedComponent;
}

/**
 * Shallow comparison for simple objects
 */
export function shallowEqual<T extends Record<string, unknown>>(
  objA: T,
  objB: T
): boolean {
  if (objA === objB) return true;

  const keysA = Object.keys(objA);
  const keysB = Object.keys(objB);

  if (keysA.length !== keysB.length) return false;

  for (const key of keysA) {
    if (objA[key] !== objB[key]) return false;
  }

  return true;
}

/**
 * Deep comparison for nested objects (use sparingly)
 */
export function deepEqual(a: unknown, b: unknown): boolean {
  if (a === b) return true;

  if (typeof a !== typeof b) return false;

  if (a === null || b === null) return a === b;

  if (Array.isArray(a) && Array.isArray(b)) {
    if (a.length !== b.length) return false;
    return a.every((item, index) => deepEqual(item, b[index]));
  }

  if (typeof a === 'object' && typeof b === 'object') {
    const keysA = Object.keys(a as object);
    const keysB = Object.keys(b as object);

    if (keysA.length !== keysB.length) return false;

    return keysA.every((key) =>
      deepEqual(
        (a as Record<string, unknown>)[key],
        (b as Record<string, unknown>)[key]
      )
    );
  }

  return false;
}

/**
 * Create a memoized component that only re-renders when specific props change
 */
export function memoOnProps<P extends object, K extends keyof P>(
  Component: FC<P>,
  watchedKeys: K[]
): FC<P> {
  return typedMemo(Component, (prevProps, nextProps) => {
    return watchedKeys.every((key) => prevProps[key] === nextProps[key]);
  });
}

/**
 * Create a memoized component that ignores specific props for comparison
 */
export function memoIgnoreProps<P extends object, K extends keyof P>(
  Component: FC<P>,
  ignoredKeys: K[]
): FC<P> {
  return typedMemo(Component, (prevProps, nextProps) => {
    const keysToCompare = Object.keys(prevProps).filter(
      (key) => !ignoredKeys.includes(key as K)
    ) as Array<keyof P>;

    return keysToCompare.every((key) => prevProps[key] === nextProps[key]);
  });
}

/**
 * Wrapper for components that should never re-render
 */
export function staticComponent<P extends object>(Component: FC<P>): FC<P> {
  return typedMemo(Component, () => true);
}

/**
 * Props for conditional rendering wrapper
 */
interface ConditionalRenderProps {
  when: boolean;
  children: ReactNode;
  fallback?: ReactNode;
}

/**
 * Memoized conditional render component
 */
export const ConditionalRender: FC<ConditionalRenderProps> = typedMemo(
  ({ when, children, fallback = null }) => {
    return <>{when ? children : fallback}</>;
  }
);

/**
 * Props for render-when-visible wrapper
 */
interface RenderWhenVisibleProps {
  children: ReactNode;
  placeholder?: ReactNode;
  rootMargin?: string;
}

/**
 * Component that renders children only when visible in viewport
 */
export const RenderWhenVisible: FC<RenderWhenVisibleProps> = ({
  children,
  placeholder = null,
  rootMargin = '50px',
}) => {
  const [isVisible, setIsVisible] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const element = ref.current;
    if (!element) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
          observer.disconnect();
        }
      },
      { rootMargin }
    );

    observer.observe(element);

    return () => {
      observer.disconnect();
    };
  }, [rootMargin]);

  return <div ref={ref}>{isVisible ? children : placeholder}</div>;
};

