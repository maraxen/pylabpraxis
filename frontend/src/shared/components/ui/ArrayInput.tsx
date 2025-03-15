import React from 'react';
import { Box } from '@chakra-ui/react';
import {
  AutoComplete,
  AutoCompleteInput,
  AutoCompleteItem,
  AutoCompleteList,
  AutoCompleteTag,
  AutoCompleteCreatable,
} from "@choc-ui/chakra-autocomplete";


interface ArrayInputProps {
  name: string;
  value: any;
  options?: string[];
  maxLen?: number;
  restrictedOptions?: boolean;
  onChange: (name: string, value: any) => void;
  onFocus?: () => void;
  onBlur?: () => void;
  onKeyDown?: (e: React.KeyboardEvent<HTMLInputElement>) => void;
  valueRenderer?: (values: any[]) => React.ReactNode;
  onRemove?: (name: string, index: number) => void;
}

export const ArrayInput: React.FC<ArrayInputProps> = ({
  name,
  value,
  options,
  maxLen,
  restrictedOptions,
  onChange,
  onFocus,
  onBlur,
  onKeyDown,
  valueRenderer,
  onRemove,
}) => {

  const currentValues = Array.isArray(value) ? value : value ? [value] : [];
  const isConstrained = restrictedOptions && options && options.length > 0;
  const isAtMaxLength = maxLen ? currentValues.length >= maxLen : false;


  const handleRemove = (name: string, index: number) => {
    const currentValue = currentValues;
    if (Array.isArray(currentValue)) {
      onChange(name, [...currentValue.slice(0, index), ...currentValue.slice(index + 1)]);
      if (onRemove) {
        onRemove(name, index);
      }
    }
  };

  const handleSelectOption = ({ item }: { item: { value: string } }) => {
    if (currentValues.includes(item.value)) {
      return;
    }

    const newValues = [...currentValues, item.value];
    if (!maxLen || newValues.length <= maxLen) {
      onChange(name, newValues);
    }
  };


  const defaultValueRenderer = (values: any[]) => (
    values.map((val, index) => (
      <AutoCompleteTag
        key={`${val}-${index}`}
        label={String(val)}
        variant="solid"
        colorScheme="brand"
        onRemove={() => handleRemove(val, index)}
      />
    ))
  );

  return (
    <Box>
      {/* Show selected values using either custom renderer or default tags */}
      <Box mb={2} display="flex" flexWrap="wrap" gap={2}>
        {valueRenderer
          ? valueRenderer(currentValues)
          : defaultValueRenderer(currentValues)
        }
      </Box>

      <AutoComplete
        multiple
        freeSolo={!isConstrained}
        creatable={!isConstrained}
        value={currentValues}
        maxSelections={maxLen}
        openOnFocus
        isReadOnly={isAtMaxLength}
        suggestWhenEmpty={isConstrained && !isAtMaxLength}
        onSelectOption={handleSelectOption}
        onChange={(value) => {
          onChange(name, value);
        }}
      >
        <AutoCompleteInput
          placeholder={isAtMaxLength ?
            `Maximum ${maxLen} values reached` :
            `Enter values${maxLen ? ` (max ${maxLen})` : ''}`
          }
          readOnly={isAtMaxLength}
          onFocus={onFocus}
          onBlur={onBlur}
          onKeyDown={onKeyDown} // added onKeyDown
        />
        <AutoCompleteList>
          {isConstrained ? (
            options.map((opt: string | number) => (
              <AutoCompleteItem
                key={String(opt)}
                value={String(opt)}
                label={String(opt)}
                disabled={isAtMaxLength}
              >
                {String(opt)}
              </AutoCompleteItem>
            ))
          ) : (
            <AutoCompleteCreatable>
              {({ value }) => `Add "${value}"`}
            </AutoCompleteCreatable>
          )}
        </AutoCompleteList>
      </AutoComplete>
    </Box>
  );
};
