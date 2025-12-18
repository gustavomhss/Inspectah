/**
 * S39-FE-PERF: Performance Module Exports
 */

export {
  typedMemo,
  shallowEqual,
  deepEqual,
  memoOnProps,
  memoIgnoreProps,
  staticComponent,
  ConditionalRender,
  RenderWhenVisible,
} from './memo';

export {
  lazyWithRetry,
  withSuspense,
  lazyLoad,
  preloadComponent,
  createLazyComponent,
  LazyRoute,
  lazyLoadAll,
} from './lazy';

export {
  useVirtualList,
  VirtualList,
  useInfiniteScroll,
  InfiniteScrollList,
} from './virtualization';
