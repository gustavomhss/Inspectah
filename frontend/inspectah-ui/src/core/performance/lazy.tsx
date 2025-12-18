/**
 * S39-FE-PERF: Lazy Loading Utilities
 *
 * Utilities for code splitting and lazy loading components.
 */

import {
  lazy,
  Suspense,
  type ComponentType,
  type FC,
  type ReactNode,
} from 'react';

/**
 * Default loading component
 */
const DefaultLoader: FC = () => (
  <div className="flex items-center justify-center p-8">
    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
  </div>
);

/**
 * Error fallback component
 */
interface ErrorFallbackProps {
  error: Error;
  resetError: () => void;
}

const DefaultErrorFallback: FC<ErrorFallbackProps> = ({ error, resetError }) => (
  <div className="flex flex-col items-center justify-center p-8 text-center">
    <p className="text-red-600 mb-4">Failed to load component</p>
    <p className="text-gray-500 text-sm mb-4">{error.message}</p>
    <button
      onClick={resetError}
      className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
    >
      Retry
    </button>
  </div>
);

/**
 * Options for lazy loading
 */
interface LazyOptions {
  fallback?: ReactNode;
  errorFallback?: FC<ErrorFallbackProps>;
  retries?: number;
  retryDelay?: number;
}

/**
 * Create a lazy-loaded component with retry logic
 */
export function lazyWithRetry<P extends object>(
  importFn: () => Promise<{ default: ComponentType<P> }>,
  options: LazyOptions = {}
): React.LazyExoticComponent<ComponentType<P>> {
  const { retries = 3, retryDelay = 1000 } = options;

  return lazy(async () => {
    let lastError: Error | null = null;

    for (let attempt = 0; attempt < retries; attempt++) {
      try {
        return await importFn();
      } catch (error) {
        lastError = error as Error;
        if (attempt < retries - 1) {
          await new Promise((resolve) => setTimeout(resolve, retryDelay));
        }
      }
    }

    throw lastError;
  });
}

/**
 * Wrap a lazy component with Suspense boundary
 */
export function withSuspense<P extends object>(
  LazyComponent: ComponentType<P>,
  options: LazyOptions = {}
): FC<P> {
  const { fallback = <DefaultLoader /> } = options;

  const WrappedComponent: FC<P> = (props) => (
    <Suspense fallback={fallback}>
      <LazyComponent {...props} />
    </Suspense>
  );

  WrappedComponent.displayName = `Suspense(${(LazyComponent as FC).displayName || 'Component'})`;

  return WrappedComponent;
}

/**
 * Create a lazy-loaded component with Suspense wrapper
 */
export function lazyLoad<P extends object>(
  importFn: () => Promise<{ default: ComponentType<P> }>,
  options: LazyOptions = {}
): ComponentType<P> {
  const LazyComponent = lazyWithRetry(importFn, options);
  return withSuspense(LazyComponent, options);
}

/**
 * Preload a lazy component (useful for hover preloading)
 */
export function preloadComponent(
  importFn: () => Promise<{ default: ComponentType<unknown> }>
): void {
  importFn().catch(() => {
    // Silent fail - component will be loaded on demand
  });
}

/**
 * Create a component factory with preloading support
 */
export function createLazyComponent<P extends object>(
  importFn: () => Promise<{ default: ComponentType<P> }>,
  options: LazyOptions = {}
): {
  Component: FC<P>;
  preload: () => void;
} {
  const Component = lazyLoad<P>(importFn, options);
  const preload = () => preloadComponent(importFn as () => Promise<{ default: ComponentType<unknown> }>);

  return { Component, preload };
}

/**
 * Route-level lazy loading with loading state
 */
interface LazyRouteProps {
  component: FC;
  fallback?: ReactNode;
}

export const LazyRoute: FC<LazyRouteProps> = ({
  component: Component,
  fallback = <DefaultLoader />,
}) => (
  <Suspense fallback={fallback}>
    <Component />
  </Suspense>
);

/**
 * Lazy load multiple components in parallel
 */
export function lazyLoadAll<T extends Record<string, object>>(
  imports: { [K in keyof T]: () => Promise<{ default: ComponentType<T[K]> }> },
  options: LazyOptions = {}
): { [K in keyof T]: FC<T[K]> } {
  const result = {} as { [K in keyof T]: FC<T[K]> };

  for (const key of Object.keys(imports) as Array<keyof T>) {
    result[key] = lazyLoad<T[K]>(imports[key], options);
  }

  return result;
}
