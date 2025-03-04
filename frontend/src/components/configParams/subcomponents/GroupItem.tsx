import React from 'react';
import { Box, HStack, Text, IconButton, VStack } from '@chakra-ui/react';
import { useDroppable } from '@dnd-kit/core';
import { LuX } from 'react-icons/lu';
import { GroupData, ValueData } from '../utils/parameterUtils';
import { SortableValueItem } from './SortableValueItem';
import { useNestedMapping } from '../contexts/nestedMappingContext';
import { useEditing } from '../managers/editingManager';

interface GroupItemProps {
  groupId: string;
  group: GroupData;
  onDelete: () => void;
  isHighlighted?: boolean;
}

export const GroupItem: React.FC<GroupItemProps> = ({
  groupId,
  group,
  onDelete,
  isHighlighted = false,
}) => {
  const { setNodeRef } = useDroppable({
    id: groupId,
  });

  const { value, onChange } = useNestedMapping();
  const {
    isEditing,
    handleStartEditing,
    handleEditingChange,
    handleFinishEditing
  } = useEditing();

  // Handle value deletion
  const handleDeleteValue = (valueId: string) => {
    if (!group || !group.values) return;

    const updatedValues = group.values.filter(item => item.id !== valueId);

    const updatedGroup = {
      ...group,
      values: updatedValues
    };

    onChange({
      ...value,
      [groupId]: updatedGroup
    });
  };

  // Handle edit mode for values
  const handleEditValue = (id: string, currentValue: string) => {
    handleStartEditing(id, currentValue, groupId);
  };

  return (
    <Box
      ref={setNodeRef}
      borderWidth={1}
      borderRadius="md"
      p={3}
      bg={isHighlighted ? 'blue.50' : 'gray.50'}
      _dark={{
        bg: isHighlighted ? 'blue.900' : 'gray.800'
      }}
      borderColor={isHighlighted ? 'blue.400' : 'gray.200'}
      transition="all 0.2s"
    >
      <HStack justifyContent="space-between" mb={2}>
        <Text fontWeight="medium">{group.name}</Text>
        <IconButton
          aria-label="Delete group"
          size="sm"
          variant="ghost"
          colorScheme="red"
          onClick={onDelete}
          disabled={!group.isEditable}
        ><LuX /></IconButton>
      </HStack>

      <VStack gap={2} align="stretch">
        {group.values && Array.isArray(group.values) && group.values.map((valueData: ValueData) => (
          <SortableValueItem
            key={valueData.id}
            id={valueData.id}
            value={String(valueData.value)}
            type={valueData.type}
            isFromParam={valueData.isFromParam}
            paramSource={valueData.paramSource}
            isEditable={valueData.isEditable}
            isEditing={isEditing(valueData.id, groupId)}
            onDelete={() => handleDeleteValue(valueData.id)}
            onEdit={() => handleEditValue(valueData.id, String(valueData.value))}
            onFocus={() => handleEditValue(valueData.id, String(valueData.value))}
            onBlur={handleFinishEditing}
            onValueChange={handleEditingChange}
          />
        ))}

        {(!group.values || group.values.length === 0) && (
          <Text color="gray.500" fontSize="sm" textAlign="center" py={2}>
            Drop values here
          </Text>
        )}
      </VStack>
    </Box>
  );
};
