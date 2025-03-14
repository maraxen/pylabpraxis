import React from 'react';
import { Badge } from '@chakra-ui/react';
import { Tooltip } from "./tooltip";

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

