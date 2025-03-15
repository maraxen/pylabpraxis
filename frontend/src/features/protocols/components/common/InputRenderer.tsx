import React, { forwardRef } from 'react';
import {
  StringInput,
  DelayedField,
  NumericInput,
  BooleanInput,
  ArrayInput
} from '@praxis-ui';
import { HierarchicalMapping } from '@protocols/nestedMapping/components/HierarchicalMapping';
import { BaseConstraintProps } from '@protocols/types/protocol'

export interface InputConfig {
  type?: string;
  constraints?: BaseConstraintProps;
  required?: boolean;
  description?: string;
}

export interface InputRendererProps {
  name: string;
  value: any;
  config: InputConfig;
  onChange: (name: string, value: any) => void;
  onFocus?: () => void;
  onBlur?: () => void;
  onKeyDown?: (e: React.KeyboardEvent<HTMLInputElement>) => void;
  inputRef?: React.RefObject<HTMLInputElement>;
  useDelayed?: boolean;
  valueRenderer?: (values: any[]) => React.ReactNode;
  onRemove?: (name: string, index: number) => void;
}

export const InputRenderer: React.FC<InputRendererProps> = ({
  name,
  value,
  config,
  onChange,
  onFocus,
  onBlur,
  onKeyDown,
  inputRef,
  useDelayed = false,
  valueRenderer,
  onRemove
}) => {
  // Normalize the type
  const normalizedType = typeof config.type === 'function'
    ? (config.type as Function).name.toLowerCase()
    : (config.type?.toLowerCase() || 'string');

  // Extract constraints for easier access
  const constraints = config.constraints || {};

  // Check if we have options for array inputs
  const options = constraints.array;
  const maxLen = constraints.array_len;
  const restrictedOptions = !constraints.creatable;

  // The actual input component to render
  const renderInputComponent = (
    localValue: any,
    handleChange: (name: string, value: any) => void,
    handleBlur?: () => void
  ) => {
    switch (normalizedType) {
      case 'boolean':
      case 'bool':
        return (
          <BooleanInput
            name={name}
            value={localValue}
            onChange={handleChange}
            onFocus={onFocus}
            onBlur={handleBlur || onBlur}
          />
        );

      case 'array':
        return (
          <ArrayInput
            name={name}
            value={localValue}
            options={options}
            maxLen={maxLen}
            restrictedOptions={restrictedOptions}
            onChange={handleChange}
            onFocus={onFocus}
            onBlur={handleBlur || onBlur}
            onKeyDown={onKeyDown}
            valueRenderer={valueRenderer}
            onRemove={onRemove}
          />
        );

      case 'dict':
      case 'object':
        return (
          <HierarchicalMapping
            name={name}
            value={localValue}
            config={config}
            onChange={(newMapping) => handleChange(name, newMapping)}
          />
        );

      case 'number':
      case 'int':
      case 'integer':
      case 'float':
      case 'double':
        return (
          <NumericInput
            name={name}
            value={localValue}
            onChange={handleChange}
            onFocus={onFocus}
            onBlur={handleBlur || onBlur}
            onKeyDown={onKeyDown}
            minimum={constraints.min_value}
            maximum={constraints.max_value}
            step_size={constraints.step}
            numeric_type={
              normalizedType === 'integer' || normalizedType === 'int'
                ? 'integer'
                : 'float'
            }
            ref={inputRef}
          />
        );

      case 'string':
      case 'str':
      default:
        // Check if we should use an array input with a single selection
        if (options && options.length > 0) {
          return (
            <ArrayInput
              name={name}
              value={localValue}
              options={options}
              maxLen={1} // Set to 1 for single-selection behavior
              restrictedOptions={restrictedOptions}
              onChange={handleChange}
              onFocus={onFocus}
              onBlur={handleBlur || onBlur}
              onKeyDown={onKeyDown}
              valueRenderer={valueRenderer}
              onRemove={onRemove}
            />
          );
        } else {
          return (
            <StringInput
              name={name}
              value={localValue || ''}
              options={options}
              disableAutocomplete={true}
              onChange={handleChange}
              onFocus={onFocus}
              onBlur={handleBlur || onBlur}
              onKeyDown={onKeyDown}
              ref={inputRef}
            />
          );
        }
    }
  };

  // If we want delayed updates (to avoid frequent state changes while typing)
  if (useDelayed) {
    return (
      <DelayedField
        value={value}
        onBlur={(finalValue) => {
          onChange(name, finalValue);
          onBlur?.();
        }}
      >
        {(localValue, handleChange, handleBlur) =>
          renderInputComponent(
            localValue,
            (_name, newVal) => handleChange(newVal),
            handleBlur
          )
        }
      </DelayedField>
    );
  }

  // Direct rendering without delay
  return renderInputComponent(value, onChange, onBlur);
};