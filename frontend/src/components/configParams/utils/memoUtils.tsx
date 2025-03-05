import React from 'react';

/**
 * Creates a memoized version of a component that only re-renders when props change
 * and provides debug information about renders when needed.
 */
export function createMemoComponent<P extends object>(
  Component: React.ComponentType<P>,
  componentName: string,
  debug: boolean = false
): React.MemoExoticComponent<React.ComponentType<P>> {
  // Custom comparison function to check if props have changed
  const areEqual = (prevProps: P, nextProps: P): boolean => {
    if (debug) {
      // Log changes for debugging
      const allKeys = new Set([...Object.keys(prevProps), ...Object.keys(nextProps)]);
      const changedProps: string[] = [];

      allKeys.forEach(key => {
        if (prevProps[key as keyof P] !== nextProps[key as keyof P]) {
          changedProps.push(key);
        }
      });

      if (changedProps.length > 0) {
        console.log(`${componentName} re-rendering due to changes in:`, changedProps);
        return false;
      }
      return true;
    }

    // Default React shallow comparison
    return false;
  };

  return React.memo(Component, areEqual);
}
