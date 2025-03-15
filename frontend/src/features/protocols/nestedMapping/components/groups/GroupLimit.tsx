import { LimitCounter } from "@praxis-ui";
import React from 'react';
import { useNestedMapping } from '@features/protocols/contexts/nestedMappingContext';

// Component for showing group limits (total number of groups)
export const GroupLimit: React.FC<{ showAlways?: boolean }> = ({ showAlways = false }) => {
  const { value, getMaxTotalValues } = useNestedMapping();
  const groupCount = Object.keys(value).length;
  const maxGroups = getMaxTotalValues();

  return (
    <LimitCounter
      current={groupCount}
      max={maxGroups}
      label="Groups"
      showAlways={showAlways}
    />
  );
};
