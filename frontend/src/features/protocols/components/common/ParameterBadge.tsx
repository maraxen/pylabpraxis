import React from 'react';
import { Badge } from '@chakra-ui/react';

interface ParameterBadgeProps {
  variant: 'editable' | 'readonly' | 'parameter';
  tooltip?: string;
}

export const ParameterBadge: React.FC<ParameterBadgeProps> = ({ variant, tooltip }) => {
  let colorScheme;
  let label;

  switch (variant) {
    case 'editable':
      colorScheme = "green";
      label = "editable";
      break;
    case 'readonly':
      colorScheme = "gray";
      label = "read-only";
      break;
    case 'parameter':
      colorScheme = "blue";
      label = "parameter values";
      break;
  }

  return (
    <Badge
      colorScheme={colorScheme}
      variant="outline"
      title={tooltip}
    >
      {label}
    </Badge>
  );
};