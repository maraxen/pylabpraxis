import React, { useState, useEffect, useRef } from 'react';
import { Input } from '@atoms/input';
import { StringInput as ConfigStringInput } from '../../../../shared/components/ui/StringInput';
import { NumberInput as ConfigNumberInput } from '../../../../shared/components/ui/NumericInput';
import { BooleanInput as ConfigBooleanInput } from '../../../../shared/components/ui/BooleanInput';
import { ArrayInput as ConfigArrayInput } from '../../../../shared/components/ui/ArrayInput';
import {
  SubvariableConfig,
} from '../../utils/parameterUtils';

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

  const type = typeof config.type === 'function' ? (config.type as Function).name.toLowerCase() : config.type;

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

  const handleDirectChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setLocalValue(e.target.value);
  };

  const handleDirectBlur = () => {
    setIsEditing(false);
    onChange(localValue);
  };

  switch (type) {
    case 'bool':
    case 'boolean':
      return (
        <ConfigBooleanInput
          name={name}
          value={isEditing ? localValue : value}
          config={config}
          onChange={handleChange}
          onFocus={handleFocus}
          onBlur={handleBlur}
        />
      );
    case 'array':
      return (
        <ConfigArrayInput
          name={name}
          value={isEditing ? localValue : value}
          config={config}
          onChange={handleChange}
          onFocus={handleFocus}
          onBlur={handleBlur}
        />
      );
    case 'float':
    case 'integer':
    case 'number':
      return (
        <ConfigNumberInput
          name={name}
          value={isEditing ? localValue : value}
          config={config}
          onChange={handleChange}
          onFocus={handleFocus}
          onBlur={handleBlur}
          ref={inputRef}
        />
      );
    case 'str':
    case 'string':
      return (
        <ConfigStringInput
          name={name}
          value={isEditing ? localValue : value}
          config={config}
          onChange={handleChange}
          onFocus={handleFocus}
          onBlur={handleBlur}
          ref={inputRef}
        />
      );
    default:
      return (
        <Input
          value={isEditing ? localValue : value}
          onChange={handleDirectChange}
          onFocus={handleFocus}
          onBlur={handleDirectBlur}
          ref={inputRef}
        />
      );
  }
};
