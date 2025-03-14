import React from 'react';
import { Text } from '@chakra-ui/react';
import { DelayedField } from './delayedField';
import { StringInput } from './StringInput';

interface EditableLabelProps {
  value: string;
  isEditable: boolean;
  isEditing: boolean;
  onEdit: () => void;
  onSave: (newValue: string) => void;
  onCancel: () => void;
  fontWeight?: string;
  placeholder?: string;
  disableAutocomplete?: boolean;
  testId?: string;
}

/**
 * A generic editable label component that toggles between display text and editable input
 */
export const EditableLabel: React.FC<EditableLabelProps> = ({
  value,
  isEditable,
  isEditing,
  onEdit,
  onSave,
  onCancel,
  fontWeight = "medium",
  placeholder = "",
  disableAutocomplete = true,
  testId = "editable-label"
}) => {
  return isEditing ? (
    <DelayedField
      value={value}
      onBlur={(finalValue) => {
        if (finalValue.trim() !== '' && finalValue !== value) {
          onSave(finalValue.trim());
        } else {
          onCancel();
        }
      }}
      data-testid={`${testId}-input`}
    >
      {(localValue, handleChange, handleBlur) => (
        <StringInput
          disableAutocomplete={disableAutocomplete}
          name="editableField"
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
        />
      )}
    </DelayedField>
  ) : (
    <Text
      fontWeight={fontWeight}
      cursor={isEditable ? "pointer" : "default"}
      onClick={isEditable ? onEdit : undefined}
      _hover={isEditable ? { textDecoration: "underline" } : {}}
      data-testid={`${testId}-text`}
    >
      {value || placeholder}
    </Text>
  );
};