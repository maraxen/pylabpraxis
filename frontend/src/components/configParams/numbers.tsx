import React from 'react';
import { NumberInputField, NumberInputRoot } from "@/components/ui/number-input";

interface NumberInputProps {
  name: string;
  value: any;
  config: any;
  onChange: (name: string, value: any) => void;
}

export const NumberInput: React.FC<NumberInputProps> = ({ name, value, config, onChange }) => {
  const type = config.type;
  const min = config.constraints?.min_value ?? -Infinity;
  const max = config.constraints?.max_value ?? Infinity;
  const step = config.constraints?.step ?? (type === 'float' ? 0.1 : 1);

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
      width="full"
    >
      <NumberInputField />
    </NumberInputRoot>
  );
};
