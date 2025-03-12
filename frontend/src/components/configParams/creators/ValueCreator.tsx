import React, { useState, useEffect, useRef, useMemo, useCallback } from 'react';
import { Box, Text } from '@chakra-ui/react';
import { Button } from '@/components/ui/button'
import { LuPlus } from "react-icons/lu";
import { AutoComplete, AutoCompleteInput, AutoCompleteItem, AutoCompleteList, AutoCompleteCreatable } from "@choc-ui/chakra-autocomplete";
import { useNestedMapping } from '../contexts/nestedMappingContext';
import { StringInput } from '../inputs/StringInput';
import { NumberInput } from '../inputs/NumericInput';
import { BooleanInput } from '../inputs/BooleanInput';
import { createMemoComponent } from '../utils/memoUtils';
import { clearExcessStorage } from '../utils/storageUtils';

interface ValueCreatorProps {
  value: Record<string, any>;
}

const ValueCreatorComponent: React.FC<ValueCreatorProps> = ({ value }) => {
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

  // Debug logs should be disabled in production
  const DEBUG_ENABLED = false;

  const inputRef = useRef<HTMLInputElement>(null);
  const [newValue, setNewValue] = useState<any>('');

  // Use useMemo for computed values to prevent unnecessary re-rendering
  const valueTypeForInput = useMemo(() =>
    valueType?.toLowerCase() || 'string',
    [valueType]);

  // Memoize the helper function to check if a value is in any group
  const isValueInAnyGroup = useCallback((opt: string) => {
    return Object.values(value || {}).some((groupValues: any) => {
      if (!groupValues) return false;
      const values = Array.isArray(groupValues)
        ? groupValues
        : (groupValues.values || []);
      return values?.some((v: any) =>
        typeof v === 'object' && v !== null ? String(v.value) === opt : String(v) === opt
      );
    });
  }, [value]);

  // Available options that aren't already in a group
  const availableOptions = useMemo(() => {
    return localChildOptions.filter(opt => !isValueInAnyGroup(String(opt)));
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

  const handleSetCreationMode = useCallback((mode: string | null) => {
    console.log("Setting creation mode for value:", mode);
    setCreationMode(mode);
  }, [setCreationMode]);

  const handleCreateValue = useCallback(() => {
    if (newValue !== '' && newValue !== undefined && newValue !== null) {
      try {
        if (DEBUG_ENABLED) {
          console.log("Creating value:", newValue);
        }
        // Clear excessive storage as before
        clearExcessStorage();

        // Force the created value to be treated as a string
        const typedValue = String(newValue);

        const id = createValue(typedValue);
        if (id) {
          setCreationMode(null);
          setNewValue('');
        } else {
          console.error("Failed to create value - empty ID returned");
          alert("Unable to create value. Storage quota may be exceeded.");
        }
      } catch (error) {
        console.error("Error in value creation:", error);
        alert("An error occurred while creating the value. Please try again.");
      }
    }
  }, [newValue, createValue, setCreationMode, DEBUG_ENABLED]);

  const handleInputChange = useCallback((_: string, val: any) => {
    setNewValue(val);
  }, []);

  // If not in creation mode, check creatable status and show button if allowed
  if (creationMode !== 'value') {
    const canCreate = creatableValue || !!config?.constraints?.creatable;

    if (DEBUG_ENABLED) {
      console.log("ValueCreator status:", { creationMode, canCreate, creatableValue });
    }

    return (
      <Button
        onClick={() => {
          console.log("Value button clicked, setting mode to value");
          setCreationMode('value');
        }}
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
            handleSetCreationMode(null);
          }}
        >
          <AutoCompleteInput
            placeholder="Enter value name..."
            autoFocus
            ref={inputRef}
            onBlur={() => setTimeout(() => handleSetCreationMode(null), 200)}
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
          onClick={() => handleSetCreationMode(null)}
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
          onChange={handleInputChange}
          onBlur={() => { }}
        />
        <Box mt={3} display="flex" gap={2}>
          <Button onClick={handleCreateValue}>
            Create
          </Button>
          <Button
            visual="outline"
            onClick={() => handleSetCreationMode(null)}
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
          onChange={handleInputChange}
          onBlur={() => { }}
          ref={inputRef}
        />
        <Box mt={3} display="flex" gap={2}>
          <Button onClick={handleCreateValue}>
            Create
          </Button>
          <Button
            visual="outline"
            onClick={() => handleSetCreationMode(null)}
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
        onChange={handleInputChange}
        onBlur={() => { }}
        ref={inputRef}
      />
      <Box mt={3} display="flex" gap={2}>
        <Button onClick={handleCreateValue}>
          Create
        </Button>
        <Button
          visual="outline"
          onClick={() => handleSetCreationMode(null)}
        >
          Cancel
        </Button>
      </Box>
    </Box>
  );
};

// Use memoization to prevent unnecessary re-renders
export const ValueCreator = createMemoComponent(
  ValueCreatorComponent,
  'ValueCreator',
  false // Set to true for debugging re-renders
);
