import React from 'react';
import { Box, Text } from '@chakra-ui/react';
import { DroppableArea } from '@praxis-ui';
import { useNestedMapping } from '@features/protocols/contexts/nestedMappingContext';

interface GroupDroppableAreaProps {
  groupId: string;
  children: React.ReactNode;
}

export const GroupDroppableArea: React.FC<GroupDroppableAreaProps> = ({
  groupId,
  children,
}) => {
  const {
    value,
    getMaxValuesPerGroup,
    dragInfo: { isDragging, overDroppableId }
  } = useNestedMapping();

  // Calculate if the group is at its limit
  const maxValuesPerGroup = getMaxValuesPerGroup();
  const groupValues = value[groupId]?.values || [];
  const isFull = maxValuesPerGroup !== Infinity && groupValues.length >= maxValuesPerGroup;

  // Check if this group is the current drop target
  const isOver = overDroppableId === groupId;

  return (
    <DroppableArea
      id={groupId}
      defaultFull={false}
      isOver={isOver}
      isDragging={isDragging}
      isFull={() => isFull}
    >
      {children}

      {/* Empty state hint */}
      {(!children || React.Children.count(children) === 0) && !isFull && (
        <Box
          color="gray.400"
          _dark={{ color: "gray.500" }}
          textAlign="center"
          fontSize="sm"
          py={4}
        >
          <Text>Drag values here or add a new value</Text>
        </Box>
      )}
    </DroppableArea>
  );
};