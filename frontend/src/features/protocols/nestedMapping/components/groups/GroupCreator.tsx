import React, { useState, useEffect, useRef, useMemo, useCallback } from 'react';
import { Box, Text } from '@chakra-ui/react';
import { Button } from '@praxis-ui';
import { LuPlus } from "react-icons/lu";
import { InputRenderer } from '@/features/protocols/components/common/InputRenderer';
import { useNestedMapping } from '@/features/protocols/contexts/nestedMappingContext';

interface GroupCreatorProps {
  value: Record<string, any>;
}

const GroupCreator: React.FC<GroupCreatorProps> = ({ value }) => {
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
      array: availableOptions,
      creatable: creatableKey // This maps to our InputRenderer's understanding
    }
  }), [keyType, availableOptions, creatableKey]);

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
    if (DEBUG_ENABLED) {
      console.log("Setting creation mode for group:", mode);
    }
    setCreationMode(mode);
  }, [setCreationMode, DEBUG_ENABLED]);

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

  const handleKeyDown = useCallback((e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      if (newValue && !value[newValue]) {
        handleCreateGroup();
      }
    } else if (e.key === 'Escape') {
      handleSetCreationMode(null);
    }
  }, [newValue, value, handleCreateGroup, handleSetCreationMode]);

  // If not in creation mode, check creatable status and show button if allowed
  if (creationMode !== 'group') {
    const canCreate = creatableKey || !!config?.constraints?.creatable;
    if (DEBUG_ENABLED) {
      console.log("GroupCreator status:", { creationMode, canCreate, creatableKey });
    }
    return (
      <Button
        onClick={() => {
          if (DEBUG_ENABLED) {
            console.log("Group button clicked, setting mode to group");
          }
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

  // Use InputRenderer for all input types
  return (
    <Box width="100%" borderWidth={1} borderRadius="md" p={4} bg="white" _dark={{ bg: "gray.700" }}>
      <Text fontWeight="medium" mb={1}>
        {keyType === 'string' ? 'Select or create group' : 'Enter new group'}
      </Text>

      <InputRenderer
        name="newGroup"
        value={newValue}
        config={inputConfig}
        onChange={handleInputChange}
        onKeyDown={handleKeyDown}
        inputRef={inputRef}
      />

      <Box mt={3} display="flex" gap={2}>
        <Button
          onClick={handleCreateGroup}
          disabled={!newValue || value[newValue]}
        >
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

export default GroupCreator;