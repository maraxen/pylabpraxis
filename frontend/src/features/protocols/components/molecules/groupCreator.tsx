import React, { useState, useEffect, useRef, useMemo, useCallback } from 'react';
import { Box, Text } from '@chakra-ui/react';
import { Button } from '@/components/ui/button'
import { LuPlus } from "react-icons/lu";
import { AutoComplete, AutoCompleteInput, AutoCompleteItem, AutoCompleteList, AutoCompleteCreatable } from "@choc-ui/chakra-autocomplete";
import { useNestedMapping } from '../contexts/nestedMappingContext';
import { StringInput } from '../../../../shared/components/ui/StringInput';
import { NumberInput } from '../../../../shared/components/ui/NumericInput';
import { createMemoComponent } from '../../utils/memoUtils';

interface GroupCreatorProps {
  value: Record<string, any>;
}

const GroupCreatorComponent: React.FC<GroupCreatorProps> = ({ value }) => {
  // Extract context values including creatable flags
  const {
    localParentOptions,
    creationMode,
    setCreationMode,
    creatableKey,
    createGroup,
    valueType,
    config
  } = useNestedMapping();

  // Debug logs should be disabled in production
  const DEBUG_ENABLED = false;

  const inputRef = useRef<HTMLInputElement>(null);
  const [newValue, setNewValue] = useState<any>('');

  // Use useMemo to calculate derived values and prevent re-renders
  const keyType = useMemo(() => {
    const constraints = config?.constraints;
    return constraints?.key_constraints?.type
      ? String(constraints.key_constraints.type).toLowerCase()
      : valueType?.toLowerCase() || 'string';
  }, [config?.constraints, valueType]);

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

  const handleSetCreationMode = useCallback((mode: string | null) => {
    console.log("Setting creation mode for group:", mode);
    setCreationMode(mode);
  }, [setCreationMode]);

  const handleCreateGroup = useCallback(() => {
    if (newValue !== '' && newValue !== undefined && newValue !== null && !value[newValue]) {
      createGroup(newValue);
      setCreationMode(null);
      setNewValue('');
    }
  }, [newValue, value, createGroup, setCreationMode]);

  const handleInputChange = useCallback((_: string, val: any) => {
    setNewValue(val);
  }, []);

  // If not in creation mode, check creatable status and show button if allowed
  if (creationMode !== 'group') {
    const canCreate = creatableKey || !!config?.constraints?.creatable;

    if (DEBUG_ENABLED) {
      console.log("GroupCreator status:", { creationMode, canCreate, creatableKey });
    }

    return (
      <Button
        onClick={() => {
          console.log("Group button clicked, setting mode to group");
          setCreationMode('group');
        }}
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
            onClick={() => handleSetCreationMode(null)}
          >
            Close
          </Button>
        </Box>
      </Box>
    );
  }

  // Check if we should use the AutoComplete component
  const shouldUseAutocomplete = keyType === 'string' && (availableOptions.length > 0 || creatableKey);

  if (shouldUseAutocomplete) {
    console.log("Using autocomplete for group creation");
    console.log("Available options:", availableOptions);
    console.log("Creatable key:", creatableKey);
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
            handleSetCreationMode(null);
          }}
        >
          <AutoCompleteInput
            placeholder="Enter group name..."
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
          onClick={() => handleSetCreationMode(null)}
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
          onChange={handleInputChange}
          onBlur={() => { }}
          ref={inputRef}
        />
      ) : (
        <StringInput
          name="newGroup"
          value={newValue}
          config={inputConfig}
          onChange={handleInputChange}
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
          onClick={() => handleSetCreationMode(null)}
        >
          Cancel
        </Button>
      </Box>
    </Box>
  );
};

// Use memoization to prevent unnecessary re-renders
export const GroupCreator = createMemoComponent(
  GroupCreatorComponent,
  'GroupCreator',
  false // Set to true for debugging re-renders
);
