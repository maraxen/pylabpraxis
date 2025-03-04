import React from 'react';
import { HStack, Text, Badge, Box, Input } from '@chakra-ui/react';
import { LuInfo } from 'react-icons/lu';
import { useNestedMapping } from '../contexts/nestedMappingContext';

interface ValueDisplayProps {
  value: string;
  type?: string;
  isFromParam?: boolean;
  paramSource?: string;
  isEditable?: boolean;
  isEditing?: boolean;
  onFocus?: () => void;
  onBlur?: () => void;
  onValueChange?: (newValue: string) => void;
  inputRef?: React.RefObject<HTMLInputElement>;
}

export const ValueDisplay: React.FC<ValueDisplayProps> = ({
  value,
  type = 'string',
  isFromParam = false,
  paramSource,
  isEditable = true,
  isEditing = false,
  onFocus,
  onBlur,
  onValueChange,
  inputRef: propInputRef
}) => {
  // Get the context input ref if not provided via props
  const { inputRef: contextInputRef } = useNestedMapping();
  // Use prop inputRef if provided, otherwise use the one from context
  const inputRef = propInputRef || contextInputRef;

  // Render an input field when in editing mode
  if (isEditing && isEditable) {
    return (
      <Box width="100%">
        <Input
          ref={inputRef}
          value={value || ''}
          onChange={(e) => onValueChange?.(e.target.value)}
          onBlur={onBlur}
          size="sm"
          autoFocus
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault();
              onBlur?.();
            } else if (e.key === 'Escape') {
              e.preventDefault();
              // Call onBlur with special flag to indicate cancellation
              const customEvent = new FocusEvent('blur', { bubbles: true });
              Object.defineProperty(customEvent, 'cancelEdit', { value: true });
              inputRef?.current?.dispatchEvent(customEvent);
            }
          }}
        />
      </Box>
    );
  }

  // Format value display based on type
  const displayValue = () => {
    if (value === undefined || value === null) {
      return <Text color="gray.400">(empty)</Text>;
    }

    switch (type.toLowerCase()) {
      case 'boolean':
      case 'bool':
        return <Text>{String(value) === 'true' ? 'True' : 'False'}</Text>;

      case 'number':
      case 'int':
      case 'integer':
      case 'float':
      case 'double':
        return <Text>{value}</Text>;

      case 'string':
      default:
        return <Text>{value}</Text>;
    }
  };

  return (
    <HStack
      gap={2}
      onClick={isEditable ? onFocus : undefined}
      width="100%"
      cursor={isEditable ? "pointer" : "default"}
      _hover={isEditable ? { bg: "gray.50", _dark: { bg: "gray.700" } } : {}}
      padding={1}
      borderRadius="md"
    >
      {displayValue()}

      {isFromParam && (
        <Box>
          <Badge size="sm" colorScheme="blue" title={`From parameter: ${paramSource}`}>
            <LuInfo size="0.8em" />
          </Badge>
        </Box>
      )}

      {!isEditable && (
        <Box>
          <Badge size="sm" colorScheme="gray" title="Read-only value">
            RO
          </Badge>
        </Box>
      )}
    </HStack>
  );
};
