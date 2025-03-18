import React, { useState, useRef, useEffect, useCallback, useMemo } from 'react';
import { Box, Text } from '@chakra-ui/react';
import { Button } from '@praxis-ui';
import { InputRenderer } from '@/features/protocols/components/common/InputRenderer';
import { useNestedMapping } from '@protocols/contexts/nestedMappingContext';
import { LuPlus } from 'react-icons/lu';
import { ValueData } from '@shared/types/protocol';

interface ValueCreatorProps {
  value: ValueData[];
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

  const DEBUG_ENABLED = false;
  const inputRef = useRef<HTMLInputElement>(null);
  const [newValue, setNewValue] = useState<string | number | boolean>('');

  // Memoize the check function - properly type the values
  const isValueInAnyGroup = useCallback((opt: string): boolean => {
    if (!Array.isArray(value)) return false;

    return value.some((item: ValueData) =>
      typeof item.value === 'object' ?
        String(item.value) === opt :
        String(item.value) === opt
    );
  }, [value]);

  // Available options that aren't already in a group
  const availableOptions = useMemo(() => {
    return localChildOptions.filter(opt => !isValueInAnyGroup(String(opt)));
  }, [localChildOptions, isValueInAnyGroup]);

  // Input config for the specific input components
  const inputConfig = useMemo(() => ({
    type: valueType?.toLowerCase() || 'string',
    constraints: {
      array: availableOptions,
      creatable: !config?.constraints?.creatable // Invert to match restrictedOptions
    }
  }), [valueType, availableOptions, config?.constraints?.creatable]);

  // Focus the input when entering creation mode
  useEffect(() => {
    if (creationMode === 'value' && inputRef.current) {
      inputRef.current.focus();
    }
  }, [creationMode]);

  const handleSetCreationMode = useCallback((mode: string | null) => {
    setCreationMode(mode);
  }, [setCreationMode]);

  const handleCreateValue = useCallback(() => {
    if (newValue !== '' && newValue !== undefined && newValue !== null) {
      createValue(newValue);
      setNewValue('');
      setCreationMode(null);
    }
  }, [newValue, createValue, setCreationMode]);

  const handleInputChange = useCallback((_: string, val: any) => {
    setNewValue(val);
  }, []);

  if (creationMode !== 'value') {
    const canCreate = creatableValue || !!config?.constraints?.creatable;
    if (DEBUG_ENABLED) {
      console.log("ValueCreator status:", { creationMode, canCreate, creatableValue });
    }
    return (
      <Button
        onClick={() => {
          setCreationMode('value');
        }}
        disabled={!canCreate}
        _disabled={{ opacity: 0.5, cursor: 'not-allowed' }}
      >
        <LuPlus /> Add Value
      </Button>
    );
  }

  return (
    <Box width="100%" borderWidth={1} borderRadius="md" p={4} bg="white" _dark={{ bg: "gray.700" }}>
      <Text fontWeight="medium" mb={1}>Enter new value</Text>

      <InputRenderer
        name="newValue"
        value={newValue}
        config={inputConfig}
        onChange={handleInputChange}
        inputRef={inputRef}
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