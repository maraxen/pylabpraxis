import React from 'react';
import { IconButton, IconButtonProps } from '@chakra-ui/react';
import { LuX, LuPencil, LuPlus, LuTrash, LuCopy, LuInfo } from 'react-icons/lu';

export type ActionType = 'edit' | 'delete' | 'add' | 'remove' | 'copy' | 'info';

interface ActionButtonProps extends Omit<IconButtonProps, 'aria-label'> {
  action: ActionType;
  label?: string;
  testId?: string;
}

/**
 * A standardized action button component with consistent iconography and styling
 */
export const ActionButton: React.FC<ActionButtonProps> = ({
  action,
  label,
  testId,
  size = "sm",
  variant = "ghost",
  ...props
}) => {
  const config = getActionConfig(action, label);

  return (
    <IconButton
      aria-label={config.ariaLabel}
      size={size}
      variant={variant}
      colorScheme={config.colorScheme}
      data-testid={testId || `action-button-${action}`}
      {...props}
    >
      <config.icon />
    </IconButton>
  );
};

// Helper function to get action-specific configuration
function getActionConfig(action: ActionType, customLabel?: string) {
  switch (action) {
    case 'edit':
      return {
        icon: LuPencil,
        ariaLabel: customLabel || 'Edit item',
        colorScheme: 'blue'
      };
    case 'delete':
      return {
        icon: LuX,
        ariaLabel: customLabel || 'Delete item',
        colorScheme: 'red'
      };
    case 'add':
      return {
        icon: LuPlus,
        ariaLabel: customLabel || 'Add item',
        colorScheme: 'green'
      };
    case 'remove':
      return {
        icon: LuTrash,
        ariaLabel: customLabel || 'Remove item',
        colorScheme: 'red'
      };
    case 'copy':
      return {
        icon: LuCopy,
        ariaLabel: customLabel || 'Copy item',
        colorScheme: 'blue'
      };
    case 'info':
      return {
        icon: LuInfo,
        ariaLabel: customLabel || 'Show information',
        colorScheme: 'gray'
      };
    default:
      return {
        icon: LuInfo,
        ariaLabel: customLabel || 'Action',
        colorScheme: 'gray'
      };
  }
}