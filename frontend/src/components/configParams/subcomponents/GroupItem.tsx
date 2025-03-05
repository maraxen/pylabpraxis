import React, { useState, useRef, useCallback } from 'react';
import { Box, Text, HStack, IconButton, Badge, Input } from '@chakra-ui/react';
import { LuX, LuPencil } from 'react-icons/lu';
import { DroppableGroup } from './droppableGroup';
import { SortableValueItem } from './SortableValueItem';
import { useNestedMapping } from '../contexts/nestedMappingContext';
import { useEditing } from '../managers/editingManager';
import { GroupData, ValueData, ValueMetadata } from '../utils/parameterUtils';
import { GroupValueLimit } from './LimitCounter';

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

  // Extract constraints - both root level and nested
  const constraints = config?.constraints || {};
  const keyConstraints = constraints.key_constraints || {};
  const valueConstraints = constraints.value_constraints || {};

  // Determine if this group's name/structure is editable using the nested constraint structure
  // Check editability in order of precedence:
  // 1. Group's own isEditable property (if explicitly set)
  // 2. Nested key_constraints.editable
  // 3. Common editable flag
  // 4. Legacy editable_key flag
  const groupExplicitlyEditable = group.isEditable === true;
  const groupExplicitlyReadOnly = group.isEditable === false;

  // Calculate editability based on constraints
  const keyEditableByConstraints =
    !!keyConstraints.editable ||
    !!constraints.editable ||
    !!constraints.editable_key;

  // Calculate creatability based on constraints
  const keyCreatableByConstraints =
    !!keyConstraints.creatable ||
    !!constraints.creatable ||
    !!constraints.creatable_key;

  // A group is editable if:
  // 1. It's explicitly marked as editable, OR
  // 2. It's NOT explicitly marked as read-only AND either editability or creatability flags are enabled
  const groupEditable =
    groupExplicitlyEditable ||
    (!groupExplicitlyReadOnly && (keyEditableByConstraints || keyCreatableByConstraints));

  // Check if group contains parameter-derived values (these groups shouldn't be deletable)
  const hasParameterValues = group.values?.some(valueData => {
    const metadata = getValueMetadata(valueData);
    return metadata.isFromParam;
  });

  // Group should not be deletable if it contains parameter values or is not editable
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

  // Enhanced value editability check with improved constraint handling
  const isValueEditable = useCallback((valueItem: ValueData, metadata: ValueMetadata) => {
    // First check if value is from a parameter - these are never editable
    if (metadata.isFromParam) return false;

    // Then check if the value itself has an explicit editability flag
    if (valueItem.isEditable === false) return false;
    if (valueItem.isEditable === true) return true;

    // Determine value editability from constraints in order of precedence:
    // 1. Nested value_constraints.editable
    // 2. Common editable flag
    // 3. Legacy editable_value flag
    const valueEditableByConstraints =
      !!valueConstraints.editable ||
      !!constraints.editable ||
      !!constraints.editable_value;

    // Determine value creatability from constraints in order of precedence:
    // 1. Nested value_constraints.creatable
    // 2. Common creatable flag
    // 3. Legacy creatable_value flag
    const valueCreatableByConstraints =
      !!valueConstraints.creatable ||
      !!constraints.creatable ||
      !!constraints.creatable_value;

    // Value is editable if any editability or creatability flag is enabled
    return valueEditableByConstraints || valueCreatableByConstraints;
  }, [constraints, valueConstraints]);

  return (
    <Box
      borderWidth={1}
      borderRadius="md"
      p={3}
      bg="white"
      _dark={{ bg: "gray.700" }}
      position="relative"
    >
      {/* Group Header with enhanced constraint-based display */}
      <HStack justify="space-between" mb={2}>
        <HStack>
          {/* Group name with inline editing */}
          {isEditingName ? (
            <Input
              ref={nameInputRef}
              size="sm"
              value={editedName}
              onChange={(e) => setEditedName(e.target.value)}
              onBlur={saveGroupName}
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  saveGroupName();
                } else if (e.key === 'Escape') {
                  cancelEditName();
                }
              }}
              autoFocus
              maxWidth="200px"
            />
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

          {/* Group metadata badges with constraint-aware display */}
          <Badge
            colorScheme={groupEditable ? "green" : "gray"}
            variant="outline"
            title={
              !groupEditable ? "This group cannot be modified" :
                keyConstraints.editable ? "Editable via key_constraints" :
                  constraints.editable ? "Editable via global constraints" :
                    constraints.editable_key ? "Editable via legacy constraints" :
                      keyConstraints.creatable ? "Creatable via key_constraints" :
                        constraints.creatable ? "Creatable via global constraints" :
                          constraints.creatable_key ? "Creatable via legacy constraints" :
                            "Editable"
            }
          >
            {groupEditable ? "editable" : "read-only"}
          </Badge>

          {/* Show parameter badge if group has parameter values */}
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
              const metadata = getValueMetadata(valueItem);

              return (
                <SortableValueItem
                  key={valueItem.id}
                  id={valueItem.id}
                  value={valueItem.value}
                  type={valueItem.type || metadata.type || valueType}
                  isFromParam={metadata.isFromParam}
                  paramSource={metadata.paramSource}
                  isEditable={isValueEditable(valueItem, metadata)}
                  isEditing={isEditing(valueItem.id, groupId)}
                  onFocus={() => handleStartEditing(valueItem.id, valueItem.value, groupId)}
                  onBlur={handleFinishEditing}
                  onValueChange={handleEditingChange}
                  onDelete={() => handleDeleteValue(valueItem.id)}
                />
              );
            })}
          </Box>
        ) : null}
      </DroppableGroup>
    </Box>
  );
};
