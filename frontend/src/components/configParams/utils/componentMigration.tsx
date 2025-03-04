import React from 'react';
import { SortableValueItem } from '../subcomponents/SortableValueItem';

/**
 * Migration utility functions and components to help transition
 * from deprecated components to the standardized SortableValueItem.
 */

/**
 * @deprecated Use SortableValueItem directly instead.
 * This is a wrapper component for backward compatibility.
 */
export const SortableValue = (props: any) => {
  console.warn('SortableValue is deprecated. Please use SortableValueItem instead.');

  return (
    <SortableValueItem
      {...props}
      dragMode="sortable"
    />
  );
};

/**
 * @deprecated Use SortableValueItem directly instead.
 * This is a wrapper component for backward compatibility.
 */
export const SortableItem = (props: any) => {
  console.warn('SortableItem is deprecated. Please use SortableValueItem instead.');

  return (
    <SortableValueItem
      {...props}
      dragMode="sortable"
    />
  );
};

/**
 * @deprecated Use SortableValueItem with dragMode="draggable" instead.
 * This is a wrapper component for backward compatibility.
 */
export const DraggableValue = (props: any) => {
  console.warn('DraggableValue is deprecated. Please use SortableValueItem with dragMode="draggable" instead.');

  return (
    <SortableValueItem
      {...props}
      dragMode="draggable"
    />
  );
};

/**
 * Helper function to migrate component usage in code
 */
export const migrateDndComponents = () => {
  console.info(`
Component Migration Guide:

1. Replace:
   import { SortableValue } from '../subcomponents/SortableValue';
   With:
   import { SortableValueItem } from '../subcomponents/SortableValueItem';

2. Replace:
   import { SortableItem } from '../subcomponents/SortableItem';
   With:
   import { SortableValueItem } from '../subcomponents/SortableValueItem';

3. Replace:
   import { draggableValue } from '../subcomponents/draggableValue';
   With:
   import { SortableValueItem } from '../subcomponents/SortableValueItem';

4. Update component usage:
   <DraggableValue ... />
   With:
   <SortableValueItem dragMode="draggable" ... />
  `);
};
