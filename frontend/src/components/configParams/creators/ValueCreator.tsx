import React, { useState, useEffect, useRef, useMemo } from 'react';
import { Box, Text } from '@chakra-ui/react';
import { Button } from '@/components/ui/button'
import { LuPlus } from "react-icons/lu";
import { AutoComplete, AutoCompleteInput, AutoCompleteItem, AutoCompleteList, AutoCompleteCreatable } from "@choc-ui/chakra-autocomplete";
import { useNestedMapping } from '../contexts/nestedMappingContext';
import { StringInput } from '../inputs/StringInput';
import { NumberInput } from '../inputs/NumericInput';
import { BooleanInput } from '../inputs/BooleanInput';

interface ValueCreatorProps {
  value: Record<string, any>;
}

export const ValueCreator: React.FC<ValueCreatorProps> = ({ value }) => {
  // Extract context values including creatable flags
  const {
    localChildOptions,
    creationMode,
    setCreationMode,
    creatableValue,
    createValue,
    valueType,
    config
  } = useNestedMapping();

  // Debug logs to check creatable status
  const constraints = config?.constraints;
  const isCreatable = !!constraints?.creatable || !!constraints?.creatable_value;
  console.log("ValueCreator creatable status:", {
    creatableValue,
    constraints_creatable: constraints?.creatable,
    constraints_creatable_value: constraints?.creatable_value,
    isCreatable
  });

  const inputRef = useRef<HTMLInputElement>(null);
  const [newValue, setNewValue] = useState<any>('');

  // Use useMemo for computed values to prevent unnecessary re-rendering
  const valueTypeForInput = useMemo(() =>
    valueType?.toLowerCase() || 'string',
    [valueType]);

  // Memoize the helper function
  const isValueInAnyGroup = useMemo(() => {
    return (opt: string) => {
      return Object.values(value || {}).some((groupValues: any) => {
        if (!groupValues) return false;
        const values = Array.isArray(groupValues)
          ? groupValues
          : (groupValues.values || []);
        return values?.includes(opt);
      });
    };
  }, [value]);

  // Available options that aren't already in a group
  const availableOptions = useMemo(() => {
    return localChildOptions.filter(opt => !isValueInAnyGroup(opt));
  }, [localChildOptions, isValueInAnyGroup]);

  // Input config for the specific input components
  const inputConfig = useMemo(() => ({
    type: valueTypeForInput,
    constraints: {
      array: availableOptions
    }
  }), [valueTypeForInput, availableOptions]);

  // Focus the input when entering creation mode
  useEffect(() => {
    if (creationMode === 'value') {
      setNewValue('');
      setTimeout(() => {
        inputRef.current?.focus();
      }, 100);
    }
  }, [creationMode]);

  const handleCreateValue = () => {
    if (newValue !== '' && newValue !== undefined && newValue !== null) {
      console.log("Creating value:", newValue);
      createValue(newValue);
      setCreationMode(null);
      setNewValue('');
    }
  };

  // If not in creation mode, check creatable status and show button if allowed
  if (creationMode !== 'value') {
    const canCreate = creatableValue || isCreatable;
    console.log("Can create value:", canCreate);

    return (
      <Button
        onClick={() => setCreationMode('value')}
        disabled={!canCreate}
        _disabled={{ opacity: 0.5, cursor: 'not-allowed' }}
      >
        <LuPlus /> Add Value
      </Button>
    );
  }

  // Check if we should use the AutoComplete component for string type
  const shouldUseAutocomplete = valueTypeForInput === 'string' && availableOptions.length > 0;

  // For string type with autocomplete options
  if (shouldUseAutocomplete) {
    return (
      <Box width="100%" borderWidth={1} borderRadius="md" p={4} bg="white" _dark={{ bg: "gray.700" }}>
        <Text fontWeight="medium" mb={1}>Select or create value</Text>
        <AutoComplete
          openOnFocus
          suggestWhenEmpty
          creatable={creatableValue}
          onSelectOption={(item) => {
            if (!item?.item?.value) return;
            createValue(item.item.value.trim());
            setCreationMode(null);
          }}
        >
          <AutoCompleteInput
            placeholder="Enter value name..."
            autoFocus
            ref={inputRef}
            onBlur={() => setTimeout(() => setCreationMode(null), 200)}
          />
          <AutoCompleteList>
            {availableOptions.map((opt: string) => (
              <AutoCompleteItem key={opt} value={opt}>
                {opt}
              </AutoCompleteItem>
            ))}
            {creatableValue && (
              <AutoCompleteCreatable>
                {({ value }) => `Create value "${value}"`}
              </AutoCompleteCreatable>
            )}
          </AutoCompleteList>
        </AutoComplete>
        <Button
          visual="outline"
          mt={3}
          onClick={() => setCreationMode(null)}
        >
          Cancel
        </Button>
      </Box>
    );
  }

  // For boolean type
  if (valueTypeForInput === 'boolean' || valueTypeForInput === 'bool') {
    return (
      <Box width="100%" borderWidth={1} borderRadius="md" p={4} bg="white" _dark={{ bg: "gray.700" }}>
        <Text fontWeight="medium" mb={1}>Value</Text>
        <BooleanInput
          name="newValue"
          value={newValue}
          config={inputConfig}
          onChange={(_, val) => setNewValue(val)}
          onBlur={() => { }}
        />
        <Box mt={3} display="flex" gap={2}>
          <Button onClick={handleCreateValue}>
            Create
          </Button>
          <Button
            visual="outline"
            onClick={() => setCreationMode(null)}
          >
            Cancel
          </Button>
        </Box>
      </Box>
    );
  }

  // For number type
  if (valueTypeForInput === 'number' || valueTypeForInput === 'int' ||
    valueTypeForInput === 'integer' || valueTypeForInput === 'float' ||
    valueTypeForInput === 'double') {
    return (
      <Box width="100%" borderWidth={1} borderRadius="md" p={4} bg="white" _dark={{ bg: "gray.700" }}>
        <Text fontWeight="medium" mb={1}>Enter new value</Text>
        <NumberInput
          name="newValue"
          value={newValue}
          config={inputConfig}
          onChange={(_, val) => setNewValue(val)}
          onBlur={() => { }}
          ref={inputRef}
        />
        <Box mt={3} display="flex" gap={2}>
          <Button onClick={handleCreateValue}>
            Create
          </Button>
          <Button
            visual="outline"
            onClick={() => setCreationMode(null)}
          >
            Cancel
          </Button>
        </Box>
      </Box>
    );
  }

  // Default fallback - String input without autocomplete
  return (
    <Box width="100%" borderWidth={1} borderRadius="md" p={4} bg="white" _dark={{ bg: "gray.700" }}>
      <Text fontWeight="medium" mb={1}>Enter new value</Text>
      <StringInput
        name="newValue"
        value={newValue}
        config={inputConfig}
        onChange={(_, val) => setNewValue(val)}
        onBlur={() => { }}
        ref={inputRef}
      />
      <Box mt={3} display="flex" gap={2}>
        <Button onClick={handleCreateValue}>
          Create
        </Button>
        <Button
          visual="outline"
          onClick={() => setCreationMode(null)}
        >
          Cancel
        </Button>
      </Box>
    </Box>
  );
};
