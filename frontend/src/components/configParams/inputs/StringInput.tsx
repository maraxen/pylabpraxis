import React, { forwardRef } from 'react';
import { Input } from '@/components/ui/input';
import { AutoComplete, AutoCompleteInput, AutoCompleteItem, AutoCompleteList } from "@choc-ui/chakra-autocomplete";

interface StringInputProps {
  name: string;
  value: any;
  config: any;
  onChange: (name: string, value: any) => void;
  onFocus?: () => void;
  onBlur?: () => void;
}

export const StringInput = forwardRef<HTMLInputElement, StringInputProps>((props, ref) => {
  const { name, value, config, onChange, onFocus, onBlur } = props;
  const { array: options } = config.constraints || {};

  if (options) {
    return (
      <AutoComplete
        value={value}
        onChange={(val) => onChange(name, val)}
      >
        <AutoCompleteInput
          placeholder="Select value..."
          onFocus={onFocus}
          onBlur={onBlur}
          ref={ref as any}
        />
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
      onFocus={onFocus}
      onBlur={onBlur}
      ref={ref}
    />
  );
});

StringInput.displayName = 'StringInput';
