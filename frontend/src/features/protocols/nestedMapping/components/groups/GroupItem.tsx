import React, { useState } from 'react';
import { Box } from '@chakra-ui/react';
import { GroupHeader } from './GroupHeader';
import { GroupDroppableArea } from './GroupDroppableArea';
import { ValueItem } from '../values/ValueItem';
import { useNestedMapping } from '../../../contexts/nestedMappingContext';
import { GroupData } from '@shared/types/protocol';

interface GroupItemProps {
  groupId: string;
  group: GroupData;
  onDelete: () => void;
  isHighlighted?: boolean;
  editingValueId: string | null;
  setEditingValueId: React.Dispatch<React.SetStateAction<string | null>>;
}

export const GroupItem: React.FC<GroupItemProps> = ({
  groupId,
  group,
  onDelete,
  isHighlighted = false
}) => {
  const [isEditingName, setIsEditingName] = useState(false);
  const [editingValueId, setEditingValueId] = useState<string | null>(null);

  const {
    onChange,
    value,
    config,
    isEditable
  } = useNestedMapping();

  // Get constraints from config
  const keyConstraints = config?.constraints?.key_constraints || {};
  const valueConstraints = config?.constraints?.value_constraints || {};

  // Check if group is editable
  const groupEditable = isEditable(groupId);

  // Check if group contains parameter values
  const groupHasParameterValues = group.values?.some(v => v.isFromParam) || false;

  // Start editing the group name
  const startEditingName = () => {
    if (groupEditable) {
      setIsEditingName(true);
    }
  };

  // Save the group name
  const saveGroupName = (newName: string) => {
    const trimmedName = newName.trim();

    // Check for duplicate group name (excluding current group)
    const duplicate = Object.entries(value).some(
      ([id, g]) => id !== groupId && g.name === trimmedName
    );

    if (duplicate) {
      alert(`Group name "${trimmedName}" already exists. Please choose a unique name.`);
      return;
    }

    // Update the group with the new name
    const updatedValue = {
      ...value,
      [groupId]: {
        ...group,
        name: trimmedName // Update the name property, not the object key
      }
    };

    onChange(updatedValue);
    setIsEditingName(false);
  };

  // Cancel editing the group name
  const cancelEditName = () => {
    setIsEditingName(false);
  };

  // Sort values if they exist
  const sortedValues = group.values ? [...group.values].sort((a, b) => {
    return a.id.localeCompare(b.id);
  }) : [];

  // Make sure we always have a name to display
  const displayName = group.name || groupId;

  return (
    <Box
      borderWidth={1}
      borderRadius="md"
      borderColor={isHighlighted ? "brand.500" : "gray.200"}
      _dark={{ borderColor: isHighlighted ? "brand.500" : "gray.600" }}
      transition="border-color 0.2s"
      bg="white"
      overflow="hidden"
    >
      <Box px={4} py={2}>
        <GroupHeader
          groupId={groupId}
          groupName={displayName} // Always use the name from group.name with fallback
          isEditingName={isEditingName}
          startEditingName={startEditingName}
          saveGroupName={saveGroupName}
          cancelEditName={cancelEditName}
          groupEditable={groupEditable}
          hasParameterValues={groupHasParameterValues}
          allowDelete={sortedValues.length === 0}
          onDelete={onDelete}
          keyConstraints={keyConstraints}
          constraints={valueConstraints}
        />
      </Box>

      <Box p={4}>
        <GroupDroppableArea groupId={groupId}>
          {sortedValues.map((item) => (
            <ValueItem
              key={item.id}
              id={item.id}
              value={item.value}
              type={item.type}
              isFromParam={item.isFromParam}
              paramSource={item.paramSource}
              isEditable={item.isEditable}
              isEditing={editingValueId === item.id}
              onEdit={() => setEditingValueId(item.id)}
              onBlur={() => setEditingValueId(null)}
              onValueChange={(newVal) => {
                // Update the value in the group
                const updatedGroup = {
                  ...group,
                  values: group.values.map((v) =>
                    v.id === item.id ? { ...v, value: newVal } : v
                  ),
                };
                onChange({
                  ...value,
                  [groupId]: updatedGroup,
                });
              }}
            />
          ))}
        </GroupDroppableArea>
      </Box>
    </Box>
  );
};