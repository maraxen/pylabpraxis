import React, { useRef } from 'react';
import { StringInput, DelayedField } from '@praxis-ui';

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
    <DelayedField
      value={initialValue}
      onBlur={(finalValue) => {
        if (finalValue.trim() !== '' && finalValue !== initialValue) {
          onSave(finalValue.trim());
        } else {
          onCancel();
        }
      }}
    >
      {(localValue, handleChange, handleBlur) => (
        <StringInput
          disableAutocomplete
          name="groupName"
          value={localValue}
          config={{ type: 'string' }}
          onChange={(_, val) => handleChange(val)}
          onBlur={handleBlur}
          onKeyDown={(e) => {
            if (e.key === 'Enter') {
              handleBlur();
            } else if (e.key === 'Escape') {
              onCancel();
            }
          }}
          ref={inputRef}
        />
      )}
    </DelayedField>
  );
};