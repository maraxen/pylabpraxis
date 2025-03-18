import React from 'react';
import { useDroppable } from '@dnd-kit/core';
import { Box } from '@chakra-ui/react';

interface DroppableAreaProps {
  children?: React.ReactNode;
  id: string;
  defaultFull: boolean;
  isOver?: boolean;
  isDragging?: boolean;
  isFull?: (id: string) => boolean;
}


export const DroppableArea: React.FC<DroppableAreaProps> = ({
  children,
  id,
  defaultFull,
  isOver,
  isDragging,
  isFull,

}) => {
  const { setNodeRef } = useDroppable({
    id,
  });

  const isFullStatus = isFull ? isFull(id) : defaultFull;

  // Determine if we can accept drops into this group
  const canReceiveDrops = !isFullStatus;

  return (
    <Box
      ref={setNodeRef}
      borderWidth={1}
      borderRadius="md"
      p={2}
      bg={isOver && canReceiveDrops ? "brand.100" : "transparent"}
      borderStyle="dashed"
      borderColor={
        isOver && canReceiveDrops
          ? "brand.500"
          : isDragging && canReceiveDrops
            ? "brand.400"
            : isFull
              ? "red.200"
              : "gray.200"
      }
      _hover={{
        borderColor: !isOver && isDragging && canReceiveDrops ? "brand.400" : undefined,
      }}
      _dark={{
        borderColor: isOver && canReceiveDrops
          ? "brand.500"
          : isDragging && canReceiveDrops
            ? "brand.400"
            : isFull
              ? "red.500"
              : "gray.600",
        _hover: {
          borderColor: !isOver && isDragging && canReceiveDrops ? "brand.400" : undefined,
        }
      }}
      minHeight="50px"
      transition="all 0.2s"
      position="relative"
      data-droppable-id={id}
      data-full={isFull}
    >
      {children}
      {/* Show a status indicator as needed */}
      {isFullStatus && (
        <Box
          position="absolute"
          top={1}
          right={1}
          px={1}
          py={0}
          fontSize="xs"
          background="red.100"
          color="red.600"
          borderRadius="sm"
          opacity={0.7}
          _dark={{
            background: "red.900",
            color: "red.300"
          }}
        >
          full
        </Box>
      )}
      {/* Empty state hint */}
      {(!children || React.Children.count(children) === 0) && (
        <Box
          color="gray.400"
          _dark={{ color: "gray.500" }}
          textAlign="center"
          fontSize="sm"
          py={4}
        >
          {isFullStatus ? "Full" : "Drop here"}
        </Box>
      )}
    </Box>
  );
};