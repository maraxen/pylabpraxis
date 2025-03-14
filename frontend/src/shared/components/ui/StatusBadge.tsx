import React from 'react';
import { Badge, BadgeProps } from '@chakra-ui/react';

type StatusType = 'editable' | 'readonly' | 'parameter' | 'required' | 'optional' | 'type';

interface StatusBadgeProps extends Omit<BadgeProps, 'colorScheme'> {
  status: StatusType;
  label?: string;
  tooltip?: string;
  colorScheme?: string;
}

/**
 * A consistent badge component for various statuses used throughout the application
 */
export const StatusBadge: React.FC<StatusBadgeProps> = ({
  status,
  label,
  tooltip,
  variant = "outline",
  ...props
}) => {
  // Default configuration based on status type
  const config = getStatusConfig(status, label);
  
  return (
    <Badge
      colorScheme={config.colorScheme}
      title={tooltip || config.tooltip}
      variant={variant}
      data-testid={`status-badge-${status}`}
      {...props}
    >
      {config.label}
    </Badge>
  );
};

// Helper function to get status-specific configuration
function getStatusConfig(status: StatusType, customLabel?: string) {
  switch (status) {
    case 'editable':
      return {
        colorScheme: 'green',
        label: customLabel || 'editable',
        tooltip: 'This item can be modified'
      };
    case 'readonly':
      return {
        colorScheme: 'gray',
        label: customLabel || 'read-only',
        tooltip: 'This item cannot be modified'
      };
    case 'parameter':
      return {
        colorScheme: 'blue',
        label: customLabel || 'parameter',
        tooltip: 'Controlled by a parameter value'
      };
    case 'required':
      return {
        colorScheme: 'red',
        label: customLabel || 'required',
        tooltip: 'This field is required'
      };
    case 'optional':
      return {
        colorScheme: 'gray',
        label: customLabel || 'optional',
        tooltip: 'This field is optional'
      };
    case 'type':
      return {
        colorScheme: 'purple',
        label: customLabel || 'type',
        tooltip: 'Data type indicator'
      };
    default:
      return {
        colorScheme: 'gray',
        label: customLabel || status,
        tooltip: ''
      };
  }
}