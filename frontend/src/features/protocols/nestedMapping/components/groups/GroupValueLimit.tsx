import { useNestedMapping } from '@features/protocols/contexts/nestedMappingContext';
import React from 'react';
import { LimitCounter } from '@praxis-ui';

export const GroupValueLimit: React.FC<{ groupId: string, showAlways?: boolean }> = ({
  groupId,
  showAlways = false
}) => {
  const { value, getMaxValuesPerGroup } = useNestedMapping();

  if (!value[groupId]) return null;

  const valueCount = value[groupId].values?.length || 0;
  const maxValues = getMaxValuesPerGroup();

  return (
    <LimitCounter
      current={valueCount}
      max={maxValues}
      label="Values in Group"
      showAlways={showAlways}
    />
  );
};