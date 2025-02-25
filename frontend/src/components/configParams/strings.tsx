import React from 'react';
import { Input } from '@/components/ui/input';
import { AutoComplete, AutoCompleteInput, AutoCompleteItem, AutoCompleteList } from "@choc-ui/chakra-autocomplete";

interface StringInputProps {
  name: string;
  value: any;
  config: any;
  onChange: (name: string, value: any) => void;
}

export const StringInput: React.FC<StringInputProps> = ({ name, value, config, onChange }) => {
  const { array: options } = config.constraints || {};
  if (options) {
    return (
      <AutoComplete
        value={value}
        onChange={(val) => onChange(name, val)}
      >
        <AutoCompleteInput placeholder="Select value..." />
        <AutoCompleteList>
          {options.map((opt: string | number) => (
            <AutoCompleteItem key={String(opt)} value={String(opt)}>
              {String(opt)}
            </AutoCompleteItem>
          ))}
        </AutoCompleteList>
      </AutoComplete>
    );
  }
  return (
    <Input
      value={value}
      onChange={(e) => onChange(name, e.target.value)}
    />
  );
};
