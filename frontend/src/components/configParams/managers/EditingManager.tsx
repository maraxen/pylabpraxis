import React, { useCallback, useEffect } from 'react';
import { useNestedMapping } from '../contexts/nestedMappingContext';
import { ValueData } from '../utils/parameterUtils';

interface EditingManagerProps {
  children: React.ReactNode;
}

/**
 * EditingManager provides a centralized way to handle the editing states for values
 * in both the available values section and group sections.
 */
export const EditingManager: React.FC<EditingManagerProps> = ({ children }) => {
  const {
    editingState,
    startEditing,
    updateEditingValue,
    finishEditing,
    cancelEditing,
    valueMetadataMap,
    inputRef
  } = useNestedMapping();

  // Handle keyboard events for editing
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Only process if we're currently editing something
      if (!editingState.id) return;

      if (e.key === 'Escape') {
        e.preventDefault();
        cancelEditing();
      } else if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        finishEditing();
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [editingState, cancelEditing, finishEditing]);

  // Focus the input when editing starts
  useEffect(() => {
    if (editingState.id && inputRef.current) {
      setTimeout(() => {
        inputRef.current?.focus();
        inputRef.current?.select();
      }, 50);
    }
  }, [editingState.id, inputRef]);

  return <>{children}</>;
};

// Custom hook to use editing functionality
export const useEditing = () => {
  const {
    editingState,
    startEditing,
    updateEditingValue,
    finishEditing,
    cancelEditing,
    valueMetadataMap,
    inputRef,
    value,
    onChange,
    valueType,
    setValueMetadataMap
  } = useNestedMapping();

  const handleStartEditing = useCallback((id: string, currentValue: string, group: string | null) => {
    // Check if value is editable from metadata
    const metadata = valueMetadataMap[id] || valueMetadataMap[currentValue];
    if (metadata && !metadata.isEditable) {
      return false;
    }

    startEditing(id, currentValue, group);
    return true;
  }, [valueMetadataMap, startEditing]);

  const handleEditingChange = useCallback((newValue: string) => {
    updateEditingValue(newValue);
  }, [updateEditingValue]);

  const handleFinishEditing = useCallback(() => {
    finishEditing();
  }, [finishEditing]);

  const handleCancelEditing = useCallback(() => {
    cancelEditing();
  }, [cancelEditing]);

  const isEditing = useCallback((id: string, group: string | null = null) => {
    return editingState.id === id && editingState.group === group;
  }, [editingState]);

  const getEditingValue = useCallback((id: string) => {
    return editingState.id === id ? editingState.value : null;
  }, [editingState]);

  return {
    isEditing,
    getEditingValue,
    handleStartEditing,
    handleEditingChange,
    handleFinishEditing,
    handleCancelEditing,
    editingState,
    inputRef
  };
};
