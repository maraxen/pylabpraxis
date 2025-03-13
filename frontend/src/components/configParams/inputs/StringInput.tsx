import React, { forwardRef } from 'react';
import { Input } from '@/components/ui/input';
import { AutoComplete, AutoCompleteInput, AutoCompleteItem, AutoCompleteList } from "@choc-ui/chakra-autocomplete";

interface StringInputProps {
  name: string;
  value: any;
  config: any;
  disableAutocomplete?: boolean;  // <-- new prop
  onChange: (name: string, value: any) => void;
  onFocus?: () => void;
  onBlur?: () => void;
  onKeyDown?: (e: React.KeyboardEvent<HTMLInputElement>) => void; // new prop
}

export const StringInput = forwardRef<HTMLInputElement, StringInputProps>((props, ref) => {
  const { name, value, config, disableAutocomplete, onChange, onFocus, onBlur, onKeyDown } = props;
  const { array: options } = config.constraints || {};

  // If disableAutocomplete is true, always use plain Input
  if (!disableAutocomplete && options) {
    return (
      <AutoComplete
        value={value}
        onChange={(val) => onChange(name, val)}
      >
        <AutoCompleteInput
          placeholder="Select value..."
          onFocus={onFocus}
          onBlur={onBlur}
          onKeyDown={onKeyDown} // added onKeyDown
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
      onKeyDown={onKeyDown} // added onKeyDown
      ref={ref}
    />
  );
});

StringInput.displayName = 'StringInput';
