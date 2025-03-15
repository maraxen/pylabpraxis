import { useNestedMapping } from '@features/protocols/contexts/nestedMappingContext';
import React from 'react';
import { LimitCounter } from '@praxis-ui';

// Component for showing total values mapped (not in available values)
export const ValueLimit: React.FC<{ showAlways?: boolean }> = ({ showAlways = false }) => {
  const { value, getMaxTotalValues } = useNestedMapping();

  // Count total values across all groups
  let totalValues = 0;
  Object.values(value).forEach(group => {
    totalValues += group.values?.length || 0;
  });

  const maxValues = getMaxTotalValues();

  return (
    <LimitCounter
      current={totalValues}
      max={maxValues}
      label="Total Values"
      showAlways={showAlways}
    />
  );
};