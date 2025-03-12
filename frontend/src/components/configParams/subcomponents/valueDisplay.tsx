import React, { useState, useEffect } from 'react';
import { HStack, Text, Badge, Box } from '@chakra-ui/react';
import { BooleanInput } from '../inputs/BooleanInput';
import { NumberInput } from '../inputs/NumericInput';
import { StringInput } from '../inputs/StringInput';
import { Tooltip } from "@/components/ui/tooltip";
import { useNestedMapping } from '../contexts/nestedMappingContext';
import { ParameterConstraints, NestedConstraint } from '../utils/parameterUtils';

interface ValueDisplayProps {
  value: any;
  type?: string;
  isFromParam?: boolean;
  paramSource?: string;
  isEditable?: boolean;
  isEditing?: boolean;
  onFocus?: () => void;
  onBlur?: () => void;
  onValueChange?: (newValue: any) => void;
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
  // Get the context input ref and config from context
  const { inputRef: contextInputRef, config } = useNestedMapping();

  // Keep track of the internal value state while editing
  const [internalValue, setInternalValue] = useState<any>(value);

  // Use prop inputRef if provided, otherwise use the one from context
  const inputRef = propInputRef || contextInputRef;

  // Update internal value when prop value changes
  useEffect(() => {
    if (!isEditing) {
      setInternalValue(value);
    }
  }, [value, isEditing]);

  // Convert value to appropriate type
  const parseValue = (val: any, valueType: string): any => {
    if (val === null || val === undefined) return val;

    const normalizedType = valueType?.toLowerCase();

    switch (normalizedType) {
      case 'boolean':
      case 'bool':
        return typeof val === 'boolean' ? val : String(val).toLowerCase() === 'true';

      case 'number':
      case 'int':
      case 'integer':
      case 'float':
      case 'double':
        const parsed = Number(val);
        return isNaN(parsed) ? 0 : parsed;

      case 'string':
      case 'str':
      default:
        return String(val);
    }
  };

  // Handle internal value change (only update local state)
  const handleInternalChange = (_name: string, newValue: any) => {
    // Immediately propagate change rather than waiting for blur
    setInternalValue(newValue);
    if (onValueChange) {
      onValueChange(parseValue(newValue, type));
    }
  };

  // Handle blur event to commit changes for all types
  const handleBlur = () => {
    if (onValueChange && internalValue !== value) {
      onValueChange(parseValue(internalValue, type));
    }
    onBlur?.();
  };

  // Render an input field when in editing mode
  if (isEditing && isEditable) {
    // Build value constraints object to hold applicable constraints
    const valueConstraints: ParameterConstraints = {};

    // Apply constraints from the nested structure
    const nestedConstraints = config?.constraints?.value_constraints;
    if (nestedConstraints) {
      applyConstraints(nestedConstraints, valueConstraints, type);
    }

    // Create a proper config object for input components
    const inputConfig = {
      type: type?.toLowerCase(),
      constraints: valueConstraints
    };

    // Normalize the type for component selection
    const normalizedType = type?.toLowerCase();

    // Render different input types based on the data type
    switch (normalizedType) {
      case 'boolean':
      case 'bool':
        return (
          <Box width="100%">
            <BooleanInput
              name="value"
              value={internalValue}
              config={inputConfig}
              onChange={handleInternalChange}
              onBlur={handleBlur}
            />
          </Box>
        );

      case 'number':
      case 'int':
      case 'integer':
      case 'float':
      case 'double':
        // Pass the raw internalValue (not parsed) for NumberInput
        return (
          <Box width="100%">
            <NumberInput
              name="value"
              value={internalValue}
              config={inputConfig}
              onChange={handleInternalChange}
              onBlur={handleBlur}
              ref={inputRef}
            />
          </Box>
        );

      case 'string':
      case 'str':
      default:
        return (
          <Box width="100%">
            {/* Pass disableAutocomplete to force plain input */}
            <StringInput
              disableAutocomplete
              name="value"
              value={internalValue || ''}
              config={inputConfig}
              onChange={handleInternalChange}
              onBlur={handleBlur}
              ref={inputRef}
            />
          </Box>
        );
    }
  }

  // Format value display based on type
  const displayValue = () => {
    if (value === undefined || value === null) {
      return <Text color="gray.400">(empty)</Text>;
    }

    const normalizedType = type?.toLowerCase();

    switch (normalizedType) {
      case 'boolean':
      case 'bool':
        const boolValue = typeof value === 'boolean' ? value : String(value).toLowerCase() === 'true';
        return <Text fontWeight="medium">{boolValue ? 'True' : 'False'}</Text>;

      case 'number':
      case 'int':
      case 'integer':
      case 'float':
      case 'double':
        return <Text fontWeight="medium">{value}</Text>;

      case 'string':
      case 'str':
      default:
        return <Text fontWeight="medium">{String(value)}</Text>;
    }
  };

  return (
    <Tooltip content={isEditable ? "Click to edit" : "Read-only value"}>
      <HStack
        gap={2}
        onClick={isEditable && !isFromParam ? onFocus : undefined}
        width="100%"
        cursor={isEditable && !isFromParam ? "pointer" : "default"}
        _hover={isEditable && !isFromParam ? { bg: "gray.50", _dark: { bg: "gray.700" } } : {}}
        padding={1}
        borderRadius="md"
        justify="space-between"
      >
        <Box>{displayValue()}</Box>

        <HStack gap={1}>
          {/* Type Badge */}
          <Badge size="sm" colorScheme={getTypeColorScheme(type)} variant="subtle">
            {type || 'string'}
          </Badge>

          {/* Parameter Source Badge */}
          {isFromParam && (
            <Badge size="sm" colorScheme="blue" title={`From parameter: ${paramSource}`}>
              {paramSource || 'param'}
            </Badge>
          )}

          {/* Editability Badge */}
          {isEditable !== undefined && (
            <Badge
              size="sm"
              colorScheme={isEditable ? "green" : "gray"}
              variant="subtle"
            >
              {isEditable ? "editable" : "read-only"}
            </Badge>
          )}
        </HStack>
      </HStack>
    </Tooltip>
  );
};

/**
 * Get appropriate color scheme based on value type
 */
function getTypeColorScheme(type?: string): string {
  if (!type) return 'gray';

  const normalizedType = type.toLowerCase();

  switch (normalizedType) {
    case 'boolean':
    case 'bool':
      return 'purple';
    case 'number':
    case 'int':
    case 'integer':
    case 'float':
    case 'double':
      return 'orange';
    case 'string':
    case 'str':
      return 'blue';
    default:
      return 'gray';
  }
}

/**
 * Apply constraints from the nested constraint structure based on value type
 */
function applyConstraints(
  nestedConstraints: NestedConstraint | undefined,
  valueConstraints: ParameterConstraints,
  type: string
) {
  if (!nestedConstraints) return;

  // Always copy over common constraints that apply to all types
  if (nestedConstraints.array) valueConstraints.array = nestedConstraints.array;
  if (nestedConstraints.array_len !== undefined) valueConstraints.array_len = nestedConstraints.array_len;

  // Apply type-specific constraints
  switch (type?.toLowerCase()) {
    case 'number':
    case 'int':
    case 'integer':
    case 'float':
    case 'double':
      // Numeric constraints
      if (nestedConstraints.min_value !== undefined)
        valueConstraints.min_value = nestedConstraints.min_value;
      if (nestedConstraints.max_value !== undefined)
        valueConstraints.max_value = nestedConstraints.max_value;
      if (nestedConstraints.step !== undefined)
        valueConstraints.step = nestedConstraints.step;
      break;

    case 'string':
    case 'str':
      // String constraints
      if (nestedConstraints.min_len !== undefined)
        valueConstraints.min_len = nestedConstraints.min_len;
      if (nestedConstraints.max_len !== undefined)
        valueConstraints.max_len = nestedConstraints.max_len;
      if (nestedConstraints.regex !== undefined)
        valueConstraints.regex = nestedConstraints.regex;
      break;
  }
}
