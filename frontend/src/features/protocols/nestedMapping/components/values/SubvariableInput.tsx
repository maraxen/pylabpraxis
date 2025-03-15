import React, { useState, useEffect, useRef } from 'react';
import { InputRenderer } from '../../../components/common/InputRenderer';
import { SubvariableConfig } from '@/features/protocols/types/protocol';

interface SubvariableInputProps {
  name: string;
  value: any;
  config: SubvariableConfig;
  onChange: (newValue: any) => void;
}

export const SubvariableInput: React.FC<SubvariableInputProps> = ({ name, value, config, onChange }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [localValue, setLocalValue] = useState(value);
  const inputRef = useRef<HTMLInputElement>(null);

  // Sync localValue with parent value when not editing
  useEffect(() => {
    if (!isEditing) {
      setLocalValue(value);
    }
  }, [value, isEditing]);

  // Focus input when editing starts
  useEffect(() => {
    if (isEditing && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isEditing]);

  const handleChange = (name: string, newValue: any) => {
    setLocalValue(newValue);
  };

  const handleFocus = () => {
    setIsEditing(true);
  };

  const handleBlur = () => {
    setIsEditing(false);
    onChange(localValue);
  };

  return (
    <InputRenderer
      name={name}
      value={isEditing ? localValue : value}
      config={config}
      onChange={handleChange}
      onFocus={handleFocus}
      onBlur={handleBlur}
      inputRef={inputRef}
    />
  );
};
