import React, { useRef } from 'react';
import { EditableLabel } from '@praxis-ui';

interface GroupInputFieldProps {
  initialValue: string;
  onSave: (value: string) => void;
  onCancel: () => void;
}

export const GroupInputField: React.FC<GroupInputFieldProps> = ({
  initialValue,
  onSave,
  onCancel
}) => {
  const inputRef = useRef<HTMLInputElement>(null);

  return (
    <EditableLabel
      value={initialValue}
      isEditable
      isEditing
      onEdit={() => inputRef.current?.focus()}
      onSave={onSave}
      onCancel={onCancel}
      testId="group-input-field"
    />
  );
};