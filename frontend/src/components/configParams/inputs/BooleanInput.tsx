import React from 'react';
import { Switch } from '@chakra-ui/react';

interface BooleanInputProps {
  name: string;
  value: any;
  config: any;
  onChange: (name: string, value: any) => void;
  onFocus?: () => void;
  onBlur?: () => void;
}

export const BooleanInput: React.FC<BooleanInputProps> = ({
  name,
  value,
  config,
  onChange,
  onFocus,
  onBlur
}) => {
  return (
    <Switch.Root
      checked={!!value}
      onCheckedChange={({ checked }) => onChange(name, checked)}
      onFocus={onFocus}
      onBlur={onBlur}
    >
      <Switch.HiddenInput />
      <Switch.Control>
        <Switch.Thumb />
      </Switch.Control>
      <Switch.Label>{name}</Switch.Label>
    </Switch.Root>
  );
};
