import {
  KeyboardSensor,
  MouseSensor,
  TouchSensor,
  useSensor,
  useSensors,
} from '@dnd-kit/core';

/**
 * Configure and return the standard set of drag and drop sensors
 */
export const useDndSensors = () => {
  const mouseSensor = useSensor(MouseSensor, {
    activationConstraint: {
      distance: 10,
    },
  });

  const touchSensor = useSensor(TouchSensor, {
    activationConstraint: {
      delay: 250,
      tolerance: 5,
    },
  });

  const keyboardSensor = useSensor(KeyboardSensor);

  return useSensors(mouseSensor, touchSensor, keyboardSensor);
};

/**
 * Add dragging styles to the body for better UX
 */
export const addDragStyles = () => {
  document.body.classList.add('dragging');
  // Also add a style tag if it doesn't exist
  if (!document.getElementById('drag-styles')) {
    const styleTag = document.createElement('style');
    styleTag.id = 'drag-styles';
    styleTag.innerHTML = `
      body.dragging {
        cursor: grabbing !important;
      }
      body.dragging * {
        cursor: grabbing !important;
      }
      .droppable-highlight {
        background-color: rgba(66, 153, 225, 0.1);
        border-color: rgba(66, 153, 225, 0.8) !important;
      }
    `;
    document.head.appendChild(styleTag);
  }
};

/**
 * Remove dragging styles from the body
 */
export const removeDragStyles = () => {
  document.body.classList.remove('dragging');
};

/**
 * Get drop animation configuration
 */
export const getDropAnimation = () => {
  return {
    duration: 200,
    easing: 'cubic-bezier(0.18, 0.67, 0.6, 1.22)',
  };
};

export const getGroupId = (droppableId: string | null): string | null => {
  if (!droppableId) return null;
  const parts = droppableId.split('-');
  return parts.length > 1 ? parts[1] : parts[0];
};

export const isValueDraggable = (value: any, metadata: any): boolean => {
  if (!value || !metadata) return false;

  // Values from parameters are not draggable
  if (metadata.isFromParam) return false;

  // Check if value is editable based on metadata
  return metadata.isEditable !== false;
};

export const isGroupAcceptingDrops = (groupId: string, value: any): boolean => {
  if (!value || !value[groupId]) return false;
  const group = value[groupId];
  return group.isEditable !== false;
};