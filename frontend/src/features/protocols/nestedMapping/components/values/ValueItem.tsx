import React, { useState, useRef, useEffect } from 'react';
import { HStack, IconButton } from '@chakra-ui/react';
import { LuX, LuPencil } from 'react-icons/lu';
import { ValueDisplay } from './ValueDisplay';
import { DraggableSortableItem } from '@praxis-ui';

// Export the interface so tests can use it
export interface ValueItemProps {
  id: string;
  value: string | any;
  availableId?: string;  // Optional ID for available values section
  type?: string;
  isFromParam?: boolean;
  paramSource?: string;
  isEditable?: boolean;
  isEditing?: boolean;
  dragMode?: 'sortable' | 'draggable';
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
export const ValueItem: React.FC<ValueItemProps> = ({
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

  // Handle value changes
  const handleValueChange = (newValue: any) => {
    setLocalValue(newValue);
    if (onValueChange) {
      onValueChange(newValue);
    }
  };

  // Create action buttons - Always create them but conditionally render
  const actionButtons = (
    <HStack gap={1}>
      {isEditable && !isEditing && (
        <IconButton
          aria-label="Edit value"
          size="xs"
          variant="ghost"
          onClick={(e) => {
            e.stopPropagation();
            if (onEdit) onEdit();
          }}
        >
          <LuPencil size="1em" />
        </IconButton>
      )}
      {onDelete && !isEditing && (
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
  );

  // Only show action buttons if there are buttons to show
  const showActionButtons = (isEditable || onDelete) ? actionButtons : undefined;

  return (
    <DraggableSortableItem
      id={itemId}
      itemType="value"
      metadata={{
        id,
        type,
        isFromParam,
        paramSource,
        isEditable,
        value: localValue
      }}
      isEditing={isEditing}
      isDraggable={!isEditing && isEditable}
      dragMode={dragMode}
      actionButtons={showActionButtons}
      onFocus={onFocus}
      onBlur={onBlur}
    >
      <ValueDisplay
        value={localValue}
        type={type}
        isFromParam={isFromParam}
        paramSource={paramSource}
        isEditable={isEditable && !isFromParam}
        isEditing={isEditing}
        onFocus={onFocus}
        onBlur={onBlur}
        onValueChange={handleValueChange}
        inputRef={inputRef}
      />
    </DraggableSortableItem>
  );
};