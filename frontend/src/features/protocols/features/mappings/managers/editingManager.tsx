import React, { useCallback, useEffect, useRef, useState } from 'react';
import { useNestedMapping } from '../contexts/nestedMappingContext';

interface EditableComponentProps {
  ref?: React.RefObject<HTMLElement>;
  isEditing?: boolean;
  value?: string;
  onChange?: (value: string) => void;
  onStartEdit?: () => void;
  onFinishEdit?: () => void;
  onCancelEdit?: () => void;
  isEditable?: boolean;
}

export interface EditingManagerProps {
  id: string;
  group: string | null;
  value: string;
  isEditable?: boolean;
  onValueChange?: (value: string) => void;
  children: React.ReactElement<EditableComponentProps>;
}

export const EditingManager: React.FC<EditingManagerProps> = ({
  id,
  group,
  value,
  isEditable = true,
  onValueChange,
  children
}) => {
  const {
    isEditingItem,
    startEditing,
    updateEditingValue,
    finishEditing,
    cancelEditing,
    inputRef,
    dragInfo
  } = useNestedMapping();

  const isEditing = isEditingItem(id, group);
  const [localValue, setLocalValue] = useState(value);
  const lastValueRef = useRef(value);

  useEffect(() => {
    if (value !== lastValueRef.current) {
      setLocalValue(value);
      lastValueRef.current = value;
    }
  }, [value]);

  const handleValueChange = useCallback((newValue: string) => {
    setLocalValue(newValue);
    updateEditingValue(newValue);
    onValueChange?.(newValue);
  }, [updateEditingValue, onValueChange]);

  const handleStartEditing = useCallback(() => {
    if (isEditable && !dragInfo.isDragging) {
      startEditing(id, value, group);
    }
  }, [isEditable, dragInfo.isDragging, startEditing, id, value, group]);

  const handleFinishEditing = useCallback(() => {
    finishEditing();
  }, [finishEditing]);

  const handleCancelEditing = useCallback(() => {
    setLocalValue(value);
    cancelEditing();
  }, [value, cancelEditing]);

  return React.Children.map(children, child => {
    if (!React.isValidElement(child)) return child;

    return React.cloneElement(child as React.ReactElement<EditableComponentProps>, {
      ref: inputRef,
      isEditing,
      value: isEditing ? localValue : value,
      onChange: handleValueChange,
      onStartEdit: handleStartEditing,
      onFinishEdit: handleFinishEditing,
      onCancelEdit: handleCancelEditing,
      isEditable
    });
  });
};