import React from 'react';
import { useDroppable } from '@dnd-kit/core';
import { Box } from '@chakra-ui/react';
import { useNestedMapping } from '../contexts/nestedMappingContext';

interface DroppableGroupProps {
  children?: React.ReactNode;
  id: string;
  isOver?: boolean;
  isDragging?: boolean;
}

export const DroppableGroup: React.FC<DroppableGroupProps> = ({
  children,
  id,
  isOver,
  isDragging
}) => {
  const { setNodeRef } = useDroppable({
    id,
  });

  // Use isGroupEditable to check if the group is read-only
  const { isGroupEditable } = useNestedMapping();
  const editable = isGroupEditable(id);

  // Always allow dropping into a group, even if it's read-only
  // This is because we want to allow moving values between groups, including read-only ones
  // We just don't want to allow deleting groups or removing values back to available values

  return (
    <Box
      ref={setNodeRef}
      borderWidth={1}
      borderRadius="md"
      p={2}
      bg={isOver ? "brand.100" : "transparent"}
      borderStyle="dashed"
      borderColor={isOver ? "brand.500" : isDragging ? "brand.400" : "gray.200"}
      _hover={{
        borderColor: !isOver && isDragging ? "brand.400" : undefined,
      }}
      _dark={{
        borderColor: isOver ? "brand.500" : isDragging ? "brand.400" : "gray.600",
        _hover: {
          borderColor: !isOver && isDragging ? "brand.400" : undefined,
        }
      }}
      minHeight="50px"
      transition="all 0.2s"
      position="relative"
      data-droppable-id={id}
    >
      {children}

      {/* Show a "read-only" badge in a subtle way */}
      {!editable && (
        <Box
          position="absolute"
          top={1}
          right={1}
          px={1}
          py={0}
          fontSize="xs"
          background="gray.100"
          color="gray.500"
          borderRadius="sm"
          opacity={0.7}
          _dark={{
            background: "gray.700",
            color: "gray.400"
          }}
        >
          read-only
        </Box>
      )}

      {/* Empty state hint */}
      {!children || React.Children.count(children) === 0 ? (
        <Box
          color="gray.400"
          _dark={{ color: "gray.500" }}
          textAlign="center"
          fontSize="sm"
          py={4}
        >
          Drop values here
        </Box>
      ) : null}
    </Box>
  );
};
