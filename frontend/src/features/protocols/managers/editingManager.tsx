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
    createdValues,
    value,
    config,
    creatableValue
  } = useNestedMapping();

  const handleStartEditing = useCallback((id: string, currentValue: string, group: string | null) => {
    // 1. If values are creatable, always allow editing
    if (creatableValue) {
      startEditing(id, currentValue, group);
      return true;
    }

    // 2. For unassigned values, check if they're in createdValues
    if (!group) {
      if (!createdValues[id]) {
        // Check if this value exists in valueMetadataMap
        const metadata = valueMetadataMap[currentValue];
        if (!metadata) {
          return false;
        }

        // Check if it's marked as not editable
        if (metadata.isEditable === false) {
          return false;
        }
      } else if (createdValues[id].isEditable === false) {
        // If in createdValues but marked as not editable
        return false;
      }
    } else if (group && value[group]) {
      // 3. For values in groups, check their editability
      const valueData = value[group].values.find((v: ValueData) => v.id === id);

      if (valueData) {
        // Never allow editing of parameter values
        if (valueData.isFromParam) {
          return false;
        }

        // Check explicit editability flag
        if (valueData.isEditable === false) {
          return false;
        }
      }

      // Check constraint-based editability
      const constraints = config?.constraints || {};
      const valueConstraints = constraints.value_constraints || {};

      // If explicitly not editable in constraints
      if (valueConstraints.editable === false && constraints.editable === false) {
        return false;
      }
    }

    // If we reach here, allow editing
    startEditing(id, currentValue, group);
    return true;
  }, [valueMetadataMap, startEditing, createdValues, value, config, creatableValue]);

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
