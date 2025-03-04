import React from 'react';
import { Box, HStack, Text } from '@chakra-ui/react';
import { useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import { ValueDisplay } from './valueDisplay';

interface SortableValueProps {
  id: string;
  value: string;
  availableId?: string;
  type?: string;
  isFromParam?: boolean;
  paramSource?: string;
  isEditable?: boolean;
  onDelete?: () => void;
  onEdit?: () => void;
}

export const SortableValue: React.FC<SortableValueProps> = ({
  id,
  value,
  availableId,
  type = 'string',
  isFromParam = false,
  paramSource,
  isEditable = true,
  onDelete,
  onEdit,
}) => {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({
    id: availableId || id,
    data: {
      type: 'value',
      value,
      metadata: {
        type,
        isFromParam,
        paramSource,
        isEditable,
      },
    },
  });

  // For drag animation
  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.4 : 1,
    cursor: 'grab',
    userSelect: 'none' as const,
  };

  return (
    <Box
      ref={setNodeRef}
      {...attributes}
      {...listeners}
      style={style}
      borderWidth="1px"
      borderRadius="md"
      p={2}
      bg="white"
      _dark={{ bg: 'gray.700' }}
      _hover={{ boxShadow: 'sm' }}
    >
      <HStack gap={2} justify="space-between">
        <ValueDisplay
          value={value}
          type={type}
          isFromParam={isFromParam}
          paramSource={paramSource}
          isEditable={isEditable}
        />

        {/* Add edit/delete buttons if needed */}
        {(onEdit || onDelete) && (
          <HStack gap={1}>
            {onEdit && (
              <Box
                as="button"
                onClick={onEdit}
                p={1}
                borderRadius="sm"
                _hover={{ bg: 'gray.100', _dark: { bg: 'gray.600' } }}
              >
                <Text>✏️</Text>
              </Box>
            )}
            {onDelete && isEditable && (
              <Box
                as="button"
                onClick={onDelete}
                p={1}
                borderRadius="sm"
                _hover={{ bg: 'red.50', _dark: { bg: 'red.900' } }}
              >
                <Text>🗑️</Text>
              </Box>
            )}
          </HStack>
        )}
      </HStack>
    </Box>
  );
};
