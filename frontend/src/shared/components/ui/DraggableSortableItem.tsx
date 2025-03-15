import React, { useRef, useState } from 'react';
import { Box, HStack } from '@chakra-ui/react';
import { useSortable } from '@dnd-kit/sortable';
import { useDraggable } from '@dnd-kit/core';
import { CSS } from '@dnd-kit/utilities';
import type { SyntheticListenerMap } from '@dnd-kit/core/dist/hooks/utilities';

export type DragMode = 'sortable' | 'draggable';

export interface DraggableItemMetadata {
  id: string;
  type?: string;
  [key: string]: any; // Allow for additional custom metadata
}

export interface DraggableSortableItemProps {
  /**
   * Unique identifier for the draggable item
   */
  id: string;

  /**
   * Optional local identifier for indexing within containers
   */
  localIndex?: number | string;

  /**
   * Type of draggable item, used for identifying item nature
   */
  itemType?: string;

  /**
   * Additional metadata to be included with the dragged item
   */
  metadata?: DraggableItemMetadata;

  /**
   * Whether the item is currently in edit mode
   */
  isEditing?: boolean;

  /**
   * Whether the item can be dragged
   */
  isDraggable?: boolean;

  /**
   * Drag mode - 'sortable' uses useSortable, 'draggable' uses useDraggable
   */
  dragMode?: DragMode;

  /**
   * Custom drag handle element, if not provided a default will be used
   */
  dragHandle?: React.ReactNode;

  /**
   * Content to display within the draggable item
   */
  children: React.ReactNode;

  /**
   * Optional action buttons to display when hovering
   */
  actionButtons?: React.ReactNode;

  /**
   * Custom styles for the container
   */
  boxStyles?: React.CSSProperties;

  /**
   * Custom class names for the container
   */
  className?: string;

  /**
   * Called when the component receives focus
   */
  onFocus?: () => void;

  /**
   * Called when the component loses focus
   */
  onBlur?: () => void;
}

/**
 * A versatile draggable/sortable item component that can be used throughout the app.
 * Supports both useSortable and useDraggable modes from dnd-kit.
 */
export const DraggableSortableItem: React.FC<DraggableSortableItemProps> = ({
  id,
  localIndex,
  itemType = 'item',
  metadata = {},
  isEditing = false,
  isDraggable = true,
  dragMode = 'sortable',
  dragHandle,
  children,
  actionButtons,
  boxStyles = {},
  className,
  onFocus,
  onBlur,
}) => {
  const [isHovering, setIsHovering] = useState(false);
  const itemRef = useRef<HTMLDivElement>(null) as React.MutableRefObject<HTMLDivElement | null>;

  // Generate a unique ID if localIndex is provided
  const itemId = localIndex !== undefined ? `${id}-${localIndex}` : id;

  // Common data object for both drag modes
  const dragData = {
    type: itemType,
    id,
    localIndex,
    metadata: {
      ...metadata,
    },
  };

  // Choose between sortable and draggable based on dragMode
  let attributes: Record<string, any> = {};
  let listeners: SyntheticListenerMap | undefined = undefined;
  let setNodeRef: (element: HTMLElement | null) => void = () => { };
  let transform: any = null;
  let transition: string | undefined = undefined;
  let isDragging = false;

  // Use the appropriate drag hook based on dragMode
  if (!isDraggable || isEditing) {
    // No drag functionality when disabled or editing
    setNodeRef = (node) => {
      if (node && itemRef.current !== node) {
        itemRef.current = node as HTMLDivElement;
      }
    };
  } else if (dragMode === 'sortable') {
    const sortable = useSortable({
      id: itemId,
      data: dragData,
    });

    attributes = sortable.attributes || {};
    listeners = sortable.listeners;
    setNodeRef = sortable.setNodeRef;
    transform = sortable.transform;
    transition = sortable.transition;
    isDragging = sortable.isDragging;
  } else {
    const draggable = useDraggable({
      id: itemId,
      data: dragData,
    });

    attributes = draggable.attributes || {};
    listeners = draggable.listeners;
    setNodeRef = draggable.setNodeRef;
    transform = draggable.transform;
    isDragging = draggable.isDragging;
    // No transition from useDraggable, so use a default
    transition = 'transform 250ms ease';
  }

  // Style for drag animation
  const style = {
    ...boxStyles,
    transform: CSS.Transform.toString(transform),
    transition: transition || '',
    opacity: isDragging ? 0.4 : 1,
    cursor: isEditing ? 'text' : isDraggable ? 'grab' : 'default',
    userSelect: 'none' as const,
    zIndex: isDragging ? 1000 : undefined,
  };

  // Default drag handle element
  const defaultDragHandle = (
    <Box
      cursor={isEditing || !isDraggable ? "default" : "grab"}
      opacity={isEditing || !isDraggable ? 0.5 : 1}
      aria-label="Drag handle"
      role="button"
      tabIndex={-1}
      userSelect="none"
      display="flex"
      alignItems="center"
    >
      ☰
    </Box>
  );

  return (
    <Box
      ref={setNodeRef}
      {...attributes}
      {...(!isEditing && isDraggable && listeners ? listeners : {})}
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
      className={className}
      onFocus={onFocus}
      onBlur={onBlur}
      data-testid={`draggable-item-${id}`}
    >
      <HStack gap={2} justify="space-between">
        <HStack gap={2} flex={1} overflow="hidden">
          {/* Drag handle */}
          {isDraggable && (dragHandle || defaultDragHandle)}

          {/* Main content */}
          <Box flex={1} overflow="hidden">
            {children}
          </Box>
        </HStack>

        {/* Action buttons */}
        {actionButtons && isHovering && !isDragging && (
          <Box onClick={(e) => e.stopPropagation()}>
            {actionButtons}
          </Box>
        )}
      </HStack>
    </Box>
  );
};