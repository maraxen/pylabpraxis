import React from 'react';
import { HStack, Text, Badge, Box } from '@chakra-ui/react';
import { BooleanInput } from '../inputs/BooleanInput';
import { NumberInput } from '../inputs/NumericInput';
import { StringInput } from '../inputs/StringInput';
import { Tooltip } from "@/components/ui/tooltip";
import { useNestedMapping } from '../contexts/nestedMappingContext';
import { ParameterConstraints, NestedConstraint } from '../utils/parameterUtils';

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
  // Get the context input ref and config from context
  const { inputRef: contextInputRef, config } = useNestedMapping();

  // Use prop inputRef if provided, otherwise use the one from context
  const inputRef = propInputRef || contextInputRef;

  // Render an input field when in editing mode
  if (isEditing && isEditable) {
    // Get parent constraints
    const parentConstraints = config?.constraints || {};

    // Build value constraints object to hold applicable constraints
    const valueConstraints: ParameterConstraints = {};

    // Determine which nested constraints to use based on parent context
    const isParentKey = parentConstraints?.parent === 'key';
    const nestedConstraints = isParentKey
      ? parentConstraints.key_constraints
      : parentConstraints.value_constraints;

    // Apply constraints from the nested structure
    if (nestedConstraints) {
      applyConstraints(nestedConstraints, valueConstraints, type);
    }

    // Create a proper config object for input components
    const inputConfig = {
      type: type?.toLowerCase(),
      constraints: valueConstraints
    };

    // Handle input change consistently
    const handleChange = (_name: string, newValue: any) => {
      onValueChange?.(String(newValue));
    };

    // Render different input types based on the data type
    switch (type?.toLowerCase()) {
      case 'boolean':
      case 'bool':
        return (
          <Box width="100%">
            <BooleanInput
              name="value"
              value={value}
              config={inputConfig}
              onChange={handleChange}
              onBlur={onBlur}
            />
          </Box>
        );

      case 'number':
      case 'int':
      case 'integer':
      case 'float':
      case 'double':
        return (
          <Box width="100%">
            <NumberInput
              name="value"
              value={Number(value) || 0}
              config={inputConfig}
              onChange={handleChange}
              onBlur={onBlur}
              ref={inputRef}
            />
          </Box>
        );

      case 'string':
      case 'str':
      default:
        return (
          <Box width="100%">
            <StringInput
              name="value"
              value={value || ''}
              config={inputConfig}
              onChange={handleChange}
              onBlur={onBlur}
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

    switch (type?.toLowerCase()) {
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
    <Tooltip content={isEditable ? "Click to edit" : "Read-only value"}>
      <HStack
        gap={2}
        onClick={isEditable ? onFocus : undefined}
        width="100%"
        cursor={isEditable ? "pointer" : "default"}
        _hover={isEditable ? { bg: "gray.50", _dark: { bg: "gray.700" } } : {}}
        padding={1}
        borderRadius="md"
        justify="space-between"
      >
        <Box>{displayValue()}</Box>

        <HStack gap={1}>
          {/* Type Badge */}
          <Badge size="sm" colorScheme="gray" variant="subtle">
            {type || 'string'}
          </Badge>

          {/* Parameter Source Badge */}
          {isFromParam && (
            <Badge size="sm" colorScheme="blue" title={`From parameter: ${paramSource}`}>
              {paramSource || 'param'}
            </Badge>
          )}

          {/* Editability Badge */}
          <Badge
            size="sm"
            colorScheme={isEditable ? "green" : "gray"}
            variant="subtle"
          >
            {isEditable ? "editable" : "read-only"}
          </Badge>
        </HStack>
      </HStack>
    </Tooltip>
  );
};

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
