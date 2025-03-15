import React, { useState, useEffect } from 'react';
import { HStack, Text, Badge, Box } from '@chakra-ui/react';
import { Tooltip } from "@praxis-ui";
import { useNestedMapping } from '@protocols/contexts/nestedMappingContext';
import { InputRenderer } from '@/features/protocols/components/common/InputRenderer';
import { ParameterConstraints, NestedConstraint } from '@protocols/types/protocol';

// Export the interface so tests can use it
export interface ValueDisplayProps {
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
  const { inputRef: contextInputRef, config } = useNestedMapping();
  const [internalValue, setInternalValue] = useState<any>(value);
  const inputRef = propInputRef || contextInputRef;

  useEffect(() => {
    if (!isEditing) {
      setInternalValue(value);
    }
  }, [value, isEditing]);


  if (isEditing && isEditable) {
    // Prepare value constraints
    const valueConstraints = {};
    const nestedConstraints = config?.constraints?.value_constraints;
    if (nestedConstraints) {
      applyConstraints(nestedConstraints, valueConstraints, type);
    }

    // Create input config
    const inputConfig = {
      type: type?.toLowerCase(),
      constraints: valueConstraints
    };

    const handleInternalChange = (_name: string, newValue: any) => {
      setInternalValue(newValue);
    };

    const handleBlur = () => {
      if (onValueChange && internalValue !== value) {
        onValueChange(internalValue);
      }
      onBlur?.();
    };

    const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
      if (e.key === 'Enter') {
        handleBlur();
      } else if (e.key === 'Escape') {
        setInternalValue(value);
        onBlur?.();
      }
    };

    return (
      <InputRenderer
        name="value"
        value={internalValue}
        config={inputConfig}
        onChange={handleInternalChange}
        onBlur={handleBlur}
        onFocus={onFocus}
        onKeyDown={handleKeyDown}
        inputRef={inputRef}
      />
    );
  }

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
      case 'dict':
      case 'object':
        // Format dictionary preview with first few keys
        return formatDictPreview(value);
      case 'array':
        // Format array preview
        return formatArrayPreview(value);
      case 'string':
      case 'str':
      default:
        // Handle case where value is actually an object but type says string
        if (typeof value === 'object' && value !== null) {
          return formatObjectPreview(value);
        }
        return <Text fontWeight="medium">{String(value)}</Text>;
    }
  };

  // Helper function to format dictionary preview
  function formatDictPreview(dict: Record<string, any>) {
    if (!dict || typeof dict !== 'object') {
      return <Text fontWeight="medium">{String(dict)}</Text>;
    }

    const keys = Object.keys(dict);
    if (keys.length === 0) {
      return <Text fontWeight="medium">{'{}'}</Text>;
    }

    // Show first few keys
    const previewKeys = keys.slice(0, 2);
    const hasMore = keys.length > 2;

    return (
      <Text fontWeight="medium" truncate>
        {'{'}
        {previewKeys.map(key => `${key}: ${formatPreviewValue(dict[key])}`).join(', ')}
        {hasMore ? ', ...' : ''}
        {'}'}
      </Text>
    );
  }

  // Helper function to format array preview
  function formatArrayPreview(arr: any[]) {
    if (!Array.isArray(arr)) {
      return <Text fontWeight="medium">{String(arr)}</Text>;
    }

    if (arr.length === 0) {
      return <Text fontWeight="medium">[]</Text>;
    }

    // Show first few items
    const previewItems = arr.slice(0, 3);
    const hasMore = arr.length > 3;

    return (
      <Text fontWeight="medium" truncate>
        {'['}
        {previewItems.map(item => formatPreviewValue(item)).join(', ')}
        {hasMore ? ', ...' : ''}
        {']'}
      </Text>
    );
  }

  // Generic object preview - fallback
  function formatObjectPreview(obj: any) {
    if (!obj || typeof obj !== 'object') {
      return <Text fontWeight="medium">{String(obj)}</Text>;
    }

    // Special case for value objects
    if (obj.id && obj.value !== undefined) {
      return <Text fontWeight="medium">{String(obj.value)}</Text>;
    }

    return <Text fontWeight="medium">{'{...}'}</Text>;
  }

  // Format value for preview display
  function formatPreviewValue(val: any): string {
    if (val === null || val === undefined) {
      return 'null';
    }

    if (typeof val === 'object') {
      if (Array.isArray(val)) {
        return '[...]';
      }
      return '{...}';
    }

    if (typeof val === 'string') {
      return val.length > 10 ? `"${val.substring(0, 10)}..."` : `"${val}"`;
    }

    return String(val);
  }

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
          <Badge size="sm" colorScheme={getTypeColorScheme(type)} variant="subtle">
            {type || "string"}
          </Badge>
          {isFromParam && (
            <Badge size="sm" colorScheme="blue" variant="subtle" title={`From parameter: ${paramSource}`}>
              {paramSource || "param"}
            </Badge>
          )}
          <Badge size="sm" colorScheme={isEditable ? "green" : "gray"} variant="subtle">
            {isEditable ? "editable" : "read-only"}
          </Badge>
        </HStack>
      </HStack>
    </Tooltip>
  );
};

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

function applyConstraints(
  nestedConstraints: NestedConstraint | undefined,
  valueConstraints: ParameterConstraints,
  type: string
) {
  if (!nestedConstraints) return;

  if (nestedConstraints.array) valueConstraints.array = nestedConstraints.array;
  if (nestedConstraints.array_len !== undefined) valueConstraints.array_len = nestedConstraints.array_len;

  switch (type?.toLowerCase()) {
    case 'number':
    case 'int':
    case 'integer':
    case 'float':
    case 'double':
      if (nestedConstraints.min_value !== undefined)
        valueConstraints.min_value = nestedConstraints.min_value;
      if (nestedConstraints.max_value !== undefined)
        valueConstraints.max_value = nestedConstraints.max_value;
      if (nestedConstraints.step !== undefined)
        valueConstraints.step = nestedConstraints.step;
      break;
    case 'string':
    case 'str':
      if (nestedConstraints.min_len !== undefined)
        valueConstraints.min_len = nestedConstraints.min_len;
      if (nestedConstraints.max_len !== undefined)
        valueConstraints.max_len = nestedConstraints.max_len;
      if (nestedConstraints.regex !== undefined)
        valueConstraints.regex = nestedConstraints.regex;
      break;
  }
}