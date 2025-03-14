import React, { useState, useRef, useEffect } from 'react';
import { Box, HStack, IconButton } from '@chakra-ui/react';
import { useSortable } from '@dnd-kit/sortable';
import { useDraggable } from '@dnd-kit/core';
import { CSS } from '@dnd-kit/utilities';
import { LuX, LuPencil } from 'react-icons/lu';
import { ValueDisplay } from '../../../../components/configParams/subcomponents/valueDisplay';
import { VStack, Text } from '@chakra-ui/react'

// Export the interface so tests can use it
export interface SortableValueItemProps {
  id: string;
  value: string | any;
  availableId?: string;  // Optional ID for available values section
  type?: string;
  isFromParam?: boolean;
  paramSource?: string;
  isEditable?: boolean;
  isEditing?: boolean;

  // Drag mode - 'sortable' uses useSortable, 'draggable' uses useDraggable
  dragMode?: 'sortable' | 'draggable';

  // Callbacks
  onDelete?: () => void;
  onEdit?: () => void;
  onFocus?: () => void;
  onBlur?: () => void;
  onValueChange?: (newValue: any) => void;
}

/**
 * A versatile draggable/sortable value component that can be used throughout the app.
 * Supports both useSortable and useDraggable modes from dnd-kit.
 */
export const SortableValueItem: React.FC<SortableValueItemProps> = ({
  id,
  value,
  availableId,
  type = 'string',
  isFromParam = false,
  paramSource,
  isEditable = true,
  isEditing = false,
  dragMode = 'sortable',
  onDelete,
  onEdit,
  onFocus,
  onBlur,
  onValueChange
}) => {
  const [isHovering, setIsHovering] = useState(false);
  const [localValue, setLocalValue] = useState<any>(value);
  const inputRef = useRef<HTMLInputElement>(null);

  // Use the provided ID or fallback to the value's ID
  const itemId = availableId || id;

  // Sync localValue with parent value when not editing
  useEffect(() => {
    if (!isEditing) {
      setLocalValue(value);
    }
  }, [value, isEditing]);

  // Focus the input when editing starts
  useEffect(() => {
    if (isEditing && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isEditing]);

  // Common data object for both drag modes
  const dragData = {
    type: 'value',
    value,
    metadata: {
      id,
      type,
      isFromParam,
      paramSource,
      isEditable,
    },
  };

  // Choose between sortable and draggable based on dragMode
  let attributes: any = {};
  let listeners: any = {};
  let setNodeRef: any = () => { };
  let transform: any = null;
  let transition: any = '';
  let isDragging = false;

  if (dragMode === 'sortable') {
    const sortable = useSortable({
      id: itemId,
      disabled: isEditing,
      data: dragData,
    });

    attributes = sortable.attributes;
    listeners = sortable.listeners;
    setNodeRef = sortable.setNodeRef;
    transform = sortable.transform;
    transition = sortable.transition;
    isDragging = sortable.isDragging;
  } else {
    const draggable = useDraggable({
      id: itemId,
      data: dragData,
      disabled: isEditing,
    });

    attributes = draggable.attributes;
    listeners = draggable.listeners;
    setNodeRef = draggable.setNodeRef;
    transform = draggable.transform;
    isDragging = draggable.isDragging;
    // No transition from useDraggable, so use a default
    transition = 'transform 250ms ease';
  }

  // For drag animation
  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.4 : 1,
    cursor: isEditing ? 'text' : 'grab',
    userSelect: 'none' as const,
    zIndex: isDragging ? 1000 : undefined,
  };

  // Handle value changes with type conversion
  const handleValueChange = (newValue: any) => {
    // Properly convert value based on type
    let typedValue = newValue;
    console.log("Handling value change:", newValue, type);

    // Only do conversion if we have a definitive type
    switch (type?.toLowerCase()) {
      case 'number':
      case 'int':
      case 'integer':
      case 'float':
      case 'double':
        typedValue = Number(newValue);
        // Check for NaN and reset to 0 if necessary
        if (isNaN(typedValue)) typedValue = 0;
        break;
      case 'boolean':
      case 'bool':
        // Convert to actual boolean
        typedValue = typeof newValue === 'boolean' ? newValue : String(newValue).toLowerCase() === 'true';
        break;
      case 'string':
      case 'str':
      default:
        typedValue = String(newValue);
        break;
    }

    setLocalValue(typedValue);
    onValueChange?.(typedValue);
  };

  const handleFocus = () => {
    if (isEditable && !isFromParam) {
      onFocus?.();
    }
  };

  // Only show delete button if the value is editable and not from a parameter
  const canDelete = isEditable && !isFromParam && onDelete;

  // Only show edit button if the value is editable
  const canEdit = isEditable && onEdit;

  return (
    <Box
      ref={setNodeRef}
      {...attributes}
      {...(isEditing ? {} : listeners)}
      style={style}
      borderWidth="1px"
      borderRadius="md"
      p={2}
      bg={isEditing ? "blue.50" : "white"}
      _dark={{ bg: isEditing ? "blue.900" : "gray.700" }}
      _hover={{ boxShadow: 'sm' }}
      position="relative"
      onMouseEnter={() => setIsHovering(true)}
      onMouseLeave={() => setIsHovering(false)}
      width="100%"
      minHeight="42px"
    >
      <HStack gap={2} justify="space-between">
        <HStack gap={2}>
          {/* Drag handle */}
          <Box
            cursor={isEditing ? "default" : "grab"}
            opacity={isEditing ? 0.5 : 1}
          >
            ☰
          </Box>

          {/* Value display with special handling for dict/object types */}
          {type?.toLowerCase() === 'dict' && typeof value === 'object' && value !== null && !isEditing ? (
            <Box width="100%">
              <Text fontWeight="medium" mb={1}>
                {value.name || 'Nested Object'}
              </Text>
              <VStack align="start" gap={1} pl={2}>
                {Array.isArray(value.values) && value.values.map((subValue: any, index: number) => (
                  <Text key={index} fontSize="sm">
                    • {typeof subValue === 'object' && subValue !== null ?
                      (subValue.value !== undefined ? String(subValue.value) : JSON.stringify(subValue))
                      : String(subValue)}
                  </Text>
                ))}
              </VStack>
            </Box>
          ) : (
            <ValueDisplay
              value={localValue}
              type={type}
              isFromParam={isFromParam}
              paramSource={paramSource}
              isEditable={isEditable && !isFromParam}
              isEditing={isEditing}
              onFocus={handleFocus}
              onBlur={onBlur}
              onValueChange={handleValueChange}
              inputRef={inputRef}
            />
          )}
        </HStack>

        {/* Action buttons */}
        {(canEdit || canDelete) && isHovering && !isDragging && (
          <HStack gap={1}>
            {canEdit && !isEditing && (
              <IconButton
                aria-label="Edit value"
                size="xs"
                variant="ghost"
                onClick={(e) => {
                  e.stopPropagation();
                  onEdit();
                }}
              >
                <LuPencil size="1em" />
              </IconButton>
            )}
            {canDelete && !isEditing && (
              <IconButton
                aria-label="Delete value"
                size="xs"
                variant="ghost"
                colorScheme="red"
                onClick={(e) => {
                  e.stopPropagation();
                  onDelete();
                }}
              >
                <LuX size="1em" />
              </IconButton>
            )}
          </HStack>
        )}
      </HStack>
    </Box>
  );
};
