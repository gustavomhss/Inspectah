/**
 * Tests for memoization utilities
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { shallowEqual, deepEqual, typedMemo, memoOnProps, memoIgnoreProps } from '../../core/performance/memo';
import type { FC } from 'react';

describe('shallowEqual', () => {
  it('should return true for same reference', () => {
    const obj = { a: 1, b: 2 };
    expect(shallowEqual(obj, obj)).toBe(true);
  });

  it('should return true for equal objects', () => {
    const obj1 = { a: 1, b: 2 };
    const obj2 = { a: 1, b: 2 };
    expect(shallowEqual(obj1, obj2)).toBe(true);
  });

  it('should return false for different values', () => {
    const obj1 = { a: 1, b: 2 };
    const obj2 = { a: 1, b: 3 };
    expect(shallowEqual(obj1, obj2)).toBe(false);
  });

  it('should return false for different keys', () => {
    const obj1 = { a: 1, b: 2 } as Record<string, number>;
    const obj2 = { a: 1, c: 2 } as Record<string, number>;
    expect(shallowEqual(obj1, obj2)).toBe(false);
  });

  it('should return false for different number of keys', () => {
    const obj1 = { a: 1, b: 2 };
    const obj2 = { a: 1 };
    expect(shallowEqual(obj1, obj2)).toBe(false);
  });

  it('should not deep compare', () => {
    const obj1 = { a: { nested: 1 } };
    const obj2 = { a: { nested: 1 } };
    expect(shallowEqual(obj1, obj2)).toBe(false); // Different references
  });
});

describe('deepEqual', () => {
  it('should return true for same reference', () => {
    const obj = { a: 1 };
    expect(deepEqual(obj, obj)).toBe(true);
  });

  it('should return true for equal primitives', () => {
    expect(deepEqual(1, 1)).toBe(true);
    expect(deepEqual('a', 'a')).toBe(true);
    expect(deepEqual(true, true)).toBe(true);
    expect(deepEqual(null, null)).toBe(true);
  });

  it('should return false for different types', () => {
    expect(deepEqual(1, '1')).toBe(false);
    expect(deepEqual(null, undefined)).toBe(false);
  });

  it('should compare nested objects', () => {
    const obj1 = { a: { b: { c: 1 } } };
    const obj2 = { a: { b: { c: 1 } } };
    expect(deepEqual(obj1, obj2)).toBe(true);
  });

  it('should compare arrays', () => {
    expect(deepEqual([1, 2, 3], [1, 2, 3])).toBe(true);
    expect(deepEqual([1, 2], [1, 2, 3])).toBe(false);
    expect(deepEqual([1, 2, 3], [1, 3, 2])).toBe(false);
  });

  it('should compare nested arrays', () => {
    const arr1 = [{ a: 1 }, { b: 2 }];
    const arr2 = [{ a: 1 }, { b: 2 }];
    expect(deepEqual(arr1, arr2)).toBe(true);
  });

  it('should return false for different nested values', () => {
    const obj1 = { a: { b: 1 } };
    const obj2 = { a: { b: 2 } };
    expect(deepEqual(obj1, obj2)).toBe(false);
  });
});

describe('typedMemo', () => {
  it('should memoize component', () => {
    const renderFn = vi.fn();

    interface TestProps {
      value: number;
    }

    const TestComponent: FC<TestProps> = ({ value }) => {
      renderFn();
      return <div>{value}</div>;
    };

    const MemoizedComponent = typedMemo(TestComponent);

    const { rerender } = render(<MemoizedComponent value={1} />);
    expect(renderFn).toHaveBeenCalledTimes(1);

    // Same props - should not re-render
    rerender(<MemoizedComponent value={1} />);
    expect(renderFn).toHaveBeenCalledTimes(1);

    // Different props - should re-render
    rerender(<MemoizedComponent value={2} />);
    expect(renderFn).toHaveBeenCalledTimes(2);
  });

  it('should preserve display name', () => {
    const TestComponent: FC = () => <div>Test</div>;
    TestComponent.displayName = 'TestComponent';

    const MemoizedComponent = typedMemo(TestComponent);

    expect(MemoizedComponent.displayName).toBe('Memo(TestComponent)');
  });

  it('should use custom comparison function', () => {
    interface TestProps {
      id: number;
      label: string;
    }

    const TestComponent: FC<TestProps> = ({ id, label }) => (
      <div data-testid="test">{`${id}-${label}`}</div>
    );

    // Only compare by id
    const MemoizedComponent = typedMemo(TestComponent, (prev, next) => prev.id === next.id);

    const { rerender } = render(<MemoizedComponent id={1} label="a" />);
    expect(screen.getByTestId('test')).toHaveTextContent('1-a');

    // Different label but same id - should not re-render
    rerender(<MemoizedComponent id={1} label="b" />);
    expect(screen.getByTestId('test')).toHaveTextContent('1-a'); // Still shows old label

    // Different id - should re-render
    rerender(<MemoizedComponent id={2} label="c" />);
    expect(screen.getByTestId('test')).toHaveTextContent('2-c');
  });
});

describe('memoOnProps', () => {
  it('should only re-render when watched props change', () => {
    const renderFn = vi.fn();

    interface TestProps {
      important: number;
      notImportant: string;
    }

    const TestComponent: FC<TestProps> = ({ important, notImportant }) => {
      renderFn();
      return <div>{`${important}-${notImportant}`}</div>;
    };

    const MemoizedComponent = memoOnProps(TestComponent, ['important']);

    const { rerender } = render(<MemoizedComponent important={1} notImportant="a" />);
    expect(renderFn).toHaveBeenCalledTimes(1);

    // Change notImportant - should not re-render
    rerender(<MemoizedComponent important={1} notImportant="b" />);
    expect(renderFn).toHaveBeenCalledTimes(1);

    // Change important - should re-render
    rerender(<MemoizedComponent important={2} notImportant="b" />);
    expect(renderFn).toHaveBeenCalledTimes(2);
  });
});

describe('memoIgnoreProps', () => {
  it('should re-render unless ignored props change', () => {
    const renderFn = vi.fn();

    interface TestProps {
      important: number;
      ignored: () => void;
    }

    const TestComponent: FC<TestProps> = ({ important }) => {
      renderFn();
      return <div>{important}</div>;
    };

    const MemoizedComponent = memoIgnoreProps(TestComponent, ['ignored']);

    const callback1 = () => {};
    const callback2 = () => {};

    const { rerender } = render(<MemoizedComponent important={1} ignored={callback1} />);
    expect(renderFn).toHaveBeenCalledTimes(1);

    // Change ignored prop - should not re-render
    rerender(<MemoizedComponent important={1} ignored={callback2} />);
    expect(renderFn).toHaveBeenCalledTimes(1);

    // Change important - should re-render
    rerender(<MemoizedComponent important={2} ignored={callback2} />);
    expect(renderFn).toHaveBeenCalledTimes(2);
  });
});
