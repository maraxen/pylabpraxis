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
  config: any;
  onChange: (name: string, value: any) => void;
}

export const ArrayInput: React.FC<ArrayInputProps> = ({ name, value, config, onChange }) => {
  const { array: options = [], array_len: maxLen } = config.constraints || {};
  const isConstrained = options.length > 0;
  const currentValues = Array.isArray(value) ? value : value ? [value] : [];
  const isAtMaxLength = maxLen ? currentValues.length >= maxLen : false;

  const handleTagRemove = (name: string, index: number) => {
    const currentValue = currentValues;
    if (Array.isArray(currentValue)) {
      onChange(name, [...currentValue.slice(0, index), ...currentValue.slice(index + 1)]);
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

  return (
    <Box>
      {/* Show selected values as tags */}
      <Box mb={2} display="flex" flexWrap="wrap" gap={2}>
        {currentValues.map((val, index) => (
          <AutoCompleteTag
            key={`${val}-${index}`}
            label={String(val)}
            variant="solid"
            colorScheme="brand"
            onRemove={() => handleTagRemove(name, index)}
          />
        ))}
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
