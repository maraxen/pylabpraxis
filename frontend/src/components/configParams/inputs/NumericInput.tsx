import React, { forwardRef } from 'react';
import { NumberInputField, NumberInputRoot } from "@/components/ui/number-input";

interface NumberInputProps {
  name: string;
  value: any;
  config: any;
  onChange: (name: string, value: any) => void;
  onFocus?: () => void;
  onBlur?: () => void;
}

export const NumberInput = forwardRef<HTMLInputElement, NumberInputProps>((props, ref) => {
  const { name, value, config, onChange, onFocus, onBlur } = props;
  const type = config.type;
  const min = config.constraints?.min_value ?? -Infinity;
  const max = config.constraints?.max_value ?? Infinity;
  const step = config.constraints?.step ?? (type === 'float' ? 0.1 : 1);
  const inputMode = type === 'integer' ? 'numeric' : 'decimal';
  const formatOptions = {};

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
        ref={ref}
      />
    </NumberInputRoot>
  );
});

NumberInput.displayName = 'NumberInput';
