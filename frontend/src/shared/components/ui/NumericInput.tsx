import React, { forwardRef } from 'react';
import { NumberInputField, NumberInputRoot } from "@praxis-ui";

interface NumericInputProps {
  name: string;
  value: any;
  onChange: (name: string, value: any) => void;
  onFocus?: () => void;
  onBlur?: () => void;
  onKeyDown?: (e: React.KeyboardEvent<HTMLInputElement>) => void; // new prop
  minimum?: number;
  maximum?: number;
  step_size?: number;
  numeric_type?: 'integer' | 'float';
}

export const NumericInput = forwardRef<HTMLInputElement, NumericInputProps>((props, ref) => {
  const { name, value, onChange, onFocus, onBlur, onKeyDown, minimum, maximum, step_size, numeric_type } = props;
  const min = minimum || -Infinity;
  const max = maximum || Infinity;
  const step = step_size || 1;
  const type = numeric_type || 'integer';


  const inputMode = type === 'integer' ? 'numeric' : 'decimal';

  const handleNumberChange = (val: string | number) => {
    if (val === '') {
      onChange(name, '');
      return;
    }

    let numValue = typeof val === 'string' ? parseFloat(val) : val;

    // Validate the number
    if (isNaN(numValue)) return;
    if (numValue < min) numValue = min;
    if (numValue > max) numValue = max;

    // For integers, round the value
    if (type === 'integer') {
      numValue = Math.round(numValue);
    }

    onChange(name, numValue);
  };

  return (
    <NumberInputRoot
      value={String(value)}
      onValueChange={({ value }) => handleNumberChange(value)}
      min={min}
      max={max}
      step={step}
      inputMode={inputMode}
      width="full"
    >
      <NumberInputField
        onFocus={onFocus}
        onBlur={onBlur}
        onKeyDown={onKeyDown} // added onKeyDown
        ref={ref}
      />
    </NumberInputRoot>
  );
});

NumericInput.displayName = 'NumericInput';
