// filepath: /Users/mar/MIT Dropbox/Marielle Russo/PLR_workspace/pylabpraxis/frontend/src/features/protocols/features/mappings/components/GroupItem.tsx
import React, { useState, useRef, useCallback } from 'react';
import { Box, Text, HStack, IconButton, Badge, Input } from '@chakra-ui/react';
import { droppable, DelayedField, StringInput } from "@praxis-ui";
import { LuX, LuPencil } from 'react-icons/lu';
import { DroppableGroup } from './DroppableGroup';
import { SortableValueItem } from './SortableValueItem';
import { useNestedMapping } from './contexts/nestedMappingContext';
import { useEditing } from './managers/editingManager';
import { GroupValueLimit } from '../../../../../shared/components/ui/LimitCounter';

// Types
interface ValueMetadata {
  type?: string;
  isFromParam?: boolean;
  paramSource?: string;
  isEditable?: boolean;
}

interface ValueData {
  id: string;
  value: any;
  type: string;
  isEditable: boolean;
  isFromParam?: boolean;
  paramSource?: string;
}

interface GroupData {
  id: string;
  name: string;
  values: ValueData[];
  isEditable: boolean;
}

interface GroupItemProps {
  groupId: string;
  group: GroupData;
  onDelete?: () => void;
  isHighlighted?: boolean;
}

export const GroupItem: React.FC<GroupItemProps> = ({
  groupId,
  group,
  onDelete,
  isHighlighted = false,
}) => {
  const {
    value,
    onChange,
    dragInfo,
    valueType,
    getValueMetadata,
    config
  } = useNestedMapping();

  const {
    isEditing,
    handleStartEditing,
    handleEditingChange,
    handleFinishEditing
  } = useEditing();

  // State for group name editing
  const [isEditingName, setIsEditingName] = useState(false);
  const [editedName, setEditedName] = useState(group.name);
  const nameInputRef = useRef<HTMLInputElement>(null);

  // Extract constraints from config
  const constraints = config?.constraints || {};
  const keyConstraints = constraints.key_constraints || {};
  const valueConstraints = constraints.value_constraints || {};

  // Determine group editability - simplified to use only nested constraints
  const groupExplicitlyEditable = group.isEditable === true;
  const groupExplicitlyReadOnly = group.isEditable === false;

  // Group is editable if:
  // 1. Explicitly marked as editable, OR
  // 2. Not explicitly read-only AND has editable or creatable flag in key_constraints or global constraints
  const keyEditableByConstraints =
    !!keyConstraints.editable ||
    !!constraints.editable;
  const keyCreatableByConstraints =
    !!keyConstraints.creatable ||
    !!constraints.creatable;
  const groupEditable =
    groupExplicitlyEditable ||
    (!groupExplicitlyReadOnly && (keyEditableByConstraints || keyCreatableByConstraints));

  // Group should not be deletable if it contains parameter values or is not editable
  const hasParameterValues = group.values?.some(valueData => {
    const metadata = getValueMetadata(valueData);
    return metadata.isFromParam;
  });
  const allowDelete = groupEditable && !hasParameterValues;

  // Handle starting group name edit
  const startEditingName = () => {
    if (groupEditable && !dragInfo.isDragging) {
      setIsEditingName(true);
      setEditedName(group.name);
      setTimeout(() => {
        nameInputRef.current?.focus();
        nameInputRef.current?.select();
      }, 50);
    }
  };

  // Handle saving group name edit
  const saveGroupName = () => {
    if (editedName !== group.name && editedName.trim() !== '') {
      onChange({
        ...value,
        [groupId]: {
          ...group,
          name: editedName.trim()
        }
      });
    }
    setIsEditingName(false);
  };

  // Handle cancelation of group name edit
  const cancelEditName = () => {
    setEditedName(group.name);
    setIsEditingName(false);
  };

  // Handle deleting a value from this group
  const handleDeleteValue = (valueId: string) => {
    if (!groupEditable) return;
    const updatedValues = group.values.filter(v => v.id !== valueId);
    onChange({
      ...value,
      [groupId]: {
        ...group,
        values: updatedValues
      }
    });
  };

  const values = group.values || [];

  // Refined value editability check with clearer precedence
  const isValueEditable = useCallback((valueItem: ValueData, metadata: ValueMetadata) => {
    const {
      creatableValue,
      valueType,
      config
    } = useNestedMapping();

    // 1. Parameter values are never editable
    if (metadata.isFromParam || valueItem.isFromParam) {
      return false;
    }

    // 2. Explicit flag on the value item has highest precedence
    if (valueItem.isEditable === false) {
      return false;
    }
    if (valueItem.isEditable === true) {
      return true;
    }

    // 3. If values are creatable (at any level), make them editable
    const constraints = config?.constraints || {};
    const valueConstraints = constraints.value_constraints || {};
    if (creatableValue || valueConstraints.creatable || constraints.creatable) {
      return true;
    }

    // 4. If the group is not editable, values inherit that restriction
    if (!groupEditable) {
      return false;
    }

    // 5. Get explicit editable flags from constraints
    const valueExplicitEditable = valueConstraints?.editable;
    const globalExplicitEditable = constraints?.editable;

    // If both are undefined, default to true
    // If either is explicitly false, use false
    // Otherwise use true
    if (valueExplicitEditable === false || globalExplicitEditable === false) {
      return false;
    }

    return true;
  }, [groupEditable, useNestedMapping]);

  return (
    <Box
      borderWidth={1}
      borderRadius="md"
      p={3}
      bg="white"
      _dark={{ bg: "gray.700" }}
      position="relative"
    >
      {/* Group Header with nested constraint-based metadata */}
      <HStack justify="space-between" mb={2}>
        <HStack>
          {/* Group name with inline editing */}
          {isEditingName ? (
            <DelayedField
              value={group.name}
              onBlur={(finalValue) => {
                setEditedName(finalValue);
                if (finalValue.trim() !== '' && finalValue !== group.name) {
                  onChange({
                    ...value,
                    [groupId]: {
                      ...group,
                      name: finalValue.trim()
                    }
                  });
                }
                setIsEditingName(false);
              }}
            >
              {(localValue, handleChange, handleBlur) => (
                <StringInput
                  disableAutocomplete
                  name="groupName"
                  value={localValue}
                  config={{ type: 'string' }}
                  onChange={(_, val) => handleChange(val)}
                  onBlur={handleBlur}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                      handleBlur();
                    } else if (e.key === 'Escape') {
                      setEditedName(group.name);
                      setIsEditingName(false);
                    }
                  }}
                  ref={nameInputRef}
                />
              )}
            </DelayedField>
          ) : (
            <Text
              fontWeight="medium"
              cursor={groupEditable ? "pointer" : "default"}
              onClick={startEditingName}
              _hover={groupEditable ? { textDecoration: "underline" } : {}}
            >
              {group.name}
            </Text>
          )}
          {/* Group value limit */}
          <GroupValueLimit groupId={groupId} />
          {/* Group metadata badges with simplified constraint info */}
          <Badge
            colorScheme={groupEditable ? "green" : "gray"}
            variant="outline"
            title={
              !groupEditable ? "This group cannot be modified" :
                keyConstraints.editable ? "Editable via key_constraints" :
                  constraints.editable ? "Editable via global constraints" :
                    keyConstraints.creatable ? "Creatable via key_constraints" :
                      constraints.creatable ? "Creatable via global constraints" :
                        "Editable"
            }
          >
            {groupEditable ? "editable" : "read-only"}
          </Badge>
          {/* Parameter values badge */}
          {hasParameterValues && (
            <Badge colorScheme="blue" variant="outline" title="Contains parameter values">
              parameter values
            </Badge>
          )}
        </HStack>
        <HStack>
          {/* Edit name button */}
          {groupEditable && !isEditingName && (
            <IconButton
              aria-label="Edit group name"
              size="sm"
              variant="ghost"
              onClick={startEditingName}
            ><LuPencil /></IconButton>
          )}
          {/* Delete button */}
          {allowDelete && onDelete && (
            <IconButton
              aria-label="Delete group"
              size="sm"
              variant="ghost"
              colorScheme="red"
              onClick={onDelete}
            ><LuX /></IconButton>
          )}
        </HStack>
      </HStack>
      {/* Droppable Area */}
      <DroppableGroup
        id={groupId}
        isOver={isHighlighted}
        isDragging={dragInfo.isDragging}
      >
        {values.length > 0 ? (
          <Box display="flex" flexDirection="column" gap={2}>
            {values.map((valueItem: ValueData) => {
              // Get metadata but prioritize explicit flags from the value item
              const baseMetadata = getValueMetadata(valueItem.value);
              const metadata = {
                ...baseMetadata,
                isFromParam: valueItem.isFromParam !== undefined ? valueItem.isFromParam : baseMetadata.isFromParam,
                paramSource: valueItem.paramSource || baseMetadata.paramSource,
                type: valueItem.type || baseMetadata.type || valueType
              };
              // Determine if this specific value is editable
              const valueIsEditable = isValueEditable(valueItem, metadata);
              return (
                <SortableValueItem
                  key={valueItem.id}
                  id={valueItem.id}
                  value={valueItem.value}
                  type={valueItem.type || metadata.type || valueType}
                  isFromParam={metadata.isFromParam}
                  paramSource={metadata.paramSource}
                  isEditable={valueIsEditable}
                  isEditing={isEditing(valueItem.id, groupId)}
                  onFocus={() => handleStartEditing(valueItem.id, valueItem.value, groupId)}
                  onBlur={handleFinishEditing}
                  onValueChange={handleEditingChange}
                  onDelete={valueIsEditable ? () => handleDeleteValue(valueItem.id) : undefined}
                />
              );
            })}
          </Box>
        ) : null}
      </DroppableGroup>
    </Box>
  );
};