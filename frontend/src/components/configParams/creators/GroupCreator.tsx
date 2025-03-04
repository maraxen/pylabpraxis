import React, { useState, useEffect, useRef, useMemo } from 'react';
import { Box, Text } from '@chakra-ui/react';
import { Button } from '@/components/ui/button'
import { LuPlus } from "react-icons/lu";
import { AutoComplete, AutoCompleteInput, AutoCompleteItem, AutoCompleteList, AutoCompleteCreatable } from "@choc-ui/chakra-autocomplete";
import { useNestedMapping } from '../contexts/nestedMappingContext';
import { StringInput } from '../inputs/StringInput';
import { NumberInput } from '../inputs/NumericInput';

interface GroupCreatorProps {
  value: Record<string, any>;
}

export const GroupCreator: React.FC<GroupCreatorProps> = ({ value }) => {
  // Extract context values including creatable flags
  const {
    localParentOptions,
    creationMode,
    setCreationMode,
    creatableKey,
    createGroup,
    isParentKey,
    valueType,
    config
  } = useNestedMapping();

  // Debug logs to check creatable status
  const constraints = config?.constraints;
  const isCreatable = !!constraints?.creatable || !!constraints?.creatable_key;
  console.log("GroupCreator creatable status:", {
    creatableKey,
    constraints_creatable: constraints?.creatable,
    constraints_creatable_key: constraints?.creatable_key,
    isCreatable
  });

  const inputRef = useRef<HTMLInputElement>(null);
  const [newValue, setNewValue] = useState<any>('');

  // Use useMemo to calculate derived values and prevent re-renders
  const keyType = useMemo(() => {
    const constraints = config?.constraints;
    return constraints?.key_type
      ? String(constraints.key_type).toLowerCase()
      : isParentKey
        ? 'string' // Default for keys if not specified
        : valueType?.toLowerCase() || 'string';
  }, [config?.constraints?.key_type, isParentKey, valueType]);

  const isUnsupportedType = useMemo(() => {
    return keyType === 'boolean' || keyType === 'bool';
  }, [keyType]);

  // Available options that aren't already used as group names
  const availableOptions = useMemo(() => {
    return localParentOptions.filter(opt => !value[opt]);
  }, [localParentOptions, value]);

  // Input config for the specific input components
  const inputConfig = useMemo(() => ({
    type: keyType,
    constraints: {
      array: availableOptions
    }
  }), [keyType, availableOptions]);

  // Focus the input when entering creation mode
  useEffect(() => {
    if (creationMode === 'group') {
      setNewValue('');
      setTimeout(() => {
        inputRef.current?.focus();
      }, 100);
    }
  }, [creationMode]);

  // If not in creation mode, check creatable status and show button if allowed
  if (creationMode !== 'group') {
    const canCreate = creatableKey || isCreatable;
    console.log("Can create group:", canCreate);

    return (
      <Button
        onClick={() => setCreationMode('group')}
        disabled={!canCreate || isUnsupportedType}
        _disabled={{ opacity: 0.5, cursor: 'not-allowed' }}
      >
        <LuPlus /> Add Group
      </Button>
    );
  }

  // Error message for boolean types
  if (isUnsupportedType) {
    return (
      <Box width="100%" borderWidth={1} borderRadius="md" p={4} bg="white" _dark={{ bg: "gray.700" }}>
        <Text fontWeight="bold" color="red.500" mb={2}>Unsupported Group Type</Text>
        <Text>
          Boolean values cannot be used as group identifiers. Please use strings or numbers instead.
        </Text>
        <Box mt={3} display="flex" gap={2} justifyContent="flex-end">
          <Button
            visual="outline"
            onClick={() => setCreationMode(null)}
          >
            Close
          </Button>
        </Box>
      </Box>
    );
  }

  const handleCreateGroup = () => {
    if (newValue !== '' && newValue !== undefined && newValue !== null && !value[newValue]) {
      createGroup(newValue);
      setCreationMode(null);
      setNewValue('');
    }
  };

  // Check if we should use the AutoComplete component
  const shouldUseAutocomplete = keyType === 'string' && availableOptions.length > 0;

  if (shouldUseAutocomplete) {
    return (
      <Box width="100%" borderWidth={1} borderRadius="md" p={4} bg="white" _dark={{ bg: "gray.700" }}>
        <Text fontWeight="medium" mb={1}>Select or create group</Text>
        <AutoComplete
          openOnFocus
          suggestWhenEmpty
          creatable={creatableKey}
          onSelectOption={(item) => {
            if (!item?.item?.value) return;
            const groupName = item.item.value.trim();
            if (!groupName || value[groupName]) return;
            createGroup(groupName);
            setCreationMode(null);
          }}
        >
          <AutoCompleteInput
            placeholder="Enter group name..."
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
            {creatableKey && (
              <AutoCompleteCreatable>
                {({ value }) => `Create group "${value}"`}
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

  // For numeric or other input types
  return (
    <Box width="100%" borderWidth={1} borderRadius="md" p={4} bg="white" _dark={{ bg: "gray.700" }}>
      <Text fontWeight="medium" mb={1}>Enter new group</Text>
      {keyType === 'number' || keyType === 'int' || keyType === 'integer' || keyType === 'float' || keyType === 'double' ? (
        <NumberInput
          name="newGroup"
          value={newValue}
          config={inputConfig}
          onChange={(_, val) => setNewValue(val)}
          onBlur={() => { }}
          ref={inputRef}
        />
      ) : (
        <StringInput
          name="newGroup"
          value={newValue}
          config={inputConfig}
          onChange={(_, val) => setNewValue(val)}
          onBlur={() => { }}
          ref={inputRef}
        />
      )}
      <Box mt={3} display="flex" gap={2}>
        <Button onClick={handleCreateGroup}>
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
