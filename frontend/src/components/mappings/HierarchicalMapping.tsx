import { DndContext } from '@dnd-kit/core';

export const HierarchicalMapping = ({ name, parent, value, constraints, onChange }) => {
  const isParentKey = parent === 'key';
  const parentOptions = isParentKey ? constraints.key_enum : constraints.value_enum;
  const childOptions = isParentKey ? constraints.value_enum : constraints.key_enum;

  // ... implementation with hierarchical AutoComplete components
};
