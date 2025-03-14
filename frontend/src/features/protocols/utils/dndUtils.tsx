import {
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors
} from '@dnd-kit/core';
import { sortableKeyboardCoordinates } from '@dnd-kit/sortable';

/**
 * Configure and return the standard set of drag and drop sensors
 */
export const useDndSensors = () => {
  return useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 5, // Minimum dragging distance before a drag starts
      }
    }),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );
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
