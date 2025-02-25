import React from 'react';
import { Switch } from '@chakra-ui/react';

interface BooleanInputProps {
  name: string;
  value: any;
  config: any;
  onChange: (name: string, value: any) => void;
}

export const BooleanInput: React.FC<BooleanInputProps> = ({ name, value, config, onChange }) => {
  return (
    <Switch.Root
      checked={!!value}
      onCheckedChange={({ checked }) => onChange(name, checked)}
    >
      <Switch.HiddenInput />
      <Switch.Control>
        <Switch.Thumb />
      </Switch.Control>
      <Switch.Label>{name}</Switch.Label>
    </Switch.Root>
  );
};
