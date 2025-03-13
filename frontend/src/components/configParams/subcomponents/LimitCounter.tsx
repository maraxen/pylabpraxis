import React from 'react';
import { Badge } from '@chakra-ui/react';
import { Tooltip } from "@/components/ui/tooltip";
import { useNestedMapping } from '../contexts/nestedMappingContext';

// Export the interface so tests can use it
export interface BaseLimitCounterProps {
  current: number;
  max: number | typeof Infinity;
  label?: string;
  showAlways?: boolean;
}

// Base component for limit counters
export const LimitCounter: React.FC<BaseLimitCounterProps> = ({
  current,
  max,
  label = '',
  showAlways = false
}) => {
  // Only show if there's a limit (not Infinity) or showAlways is true
  if (max === Infinity && !showAlways) {
    return null;
  }

  // Determine color based on usage
  const usage = max === Infinity ? 0 : current / max;
  let colorScheme = "blue";

  if (usage >= 1) {
    colorScheme = "red"; // Full
  } else if (usage >= 0.8) {
    colorScheme = "orange"; // Nearly full
  } else if (usage >= 0.5) {
    colorScheme = "yellow"; // Getting full
  }

  const displayMax = max === Infinity ? "∞" : max;
  const tooltipLabel = label ?
    `${label}: ${current} used out of ${displayMax} maximum` :
    `${current} used out of ${displayMax} maximum`;

  return (
    <Tooltip content={tooltipLabel}>
      <Badge colorScheme={colorScheme} variant="subtle" fontSize="xs" ml={1}>
        {current}/{displayMax === "∞" ? "∞" : displayMax}
      </Badge>
    </Tooltip>
  );
};

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

// Component for showing per-group value limits
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
