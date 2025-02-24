import React from 'react';
import { VStack, Box, Button } from '@chakra-ui/react';
import { AutoComplete, AutoCompleteInput, AutoCompleteItem, AutoCompleteList, AutoCompleteTag } from "@choc-ui/chakra-autocomplete";

interface HierarchicalMappingProps {
  name: string;
  value: Record<string, any[]>;
  constraints: {
    hierarchical: boolean;
    parent: 'key' | 'value';
    key_array?: (string | number)[];
    value_array?: (string | number)[];
    key_param?: string;
    value_param?: string;
    value_array_len?: number;
  };
  onChange: (value: Record<string, any[]>) => void;
}

export const HierarchicalMapping: React.FC<HierarchicalMappingProps> = ({
  name,
  value,
  constraints,
  onChange,
}) => {
  const isParentKey = constraints.parent === 'key';
  const parentOptions = isParentKey ? constraints.key_array : constraints.value_array;
  const childOptions = isParentKey ? constraints.value_array : constraints.key_array;

  return (
    <VStack gap={4} width="100%">
      {Object.entries(value).map(([parentVal, children]) => (
        <Box key={parentVal} width="100%" p={4} borderWidth={1} borderRadius="md">
          <AutoComplete
            value={parentVal}
            openOnFocus
            suggestWhenEmpty
            onSelectOption={({ item }) => {
              if (item.value === parentVal) return;
              const newValue = { ...value };
              delete newValue[parentVal];
              newValue[item.value] = children;
              onChange(newValue);
            }}
          >
            <AutoCompleteInput placeholder="Select parent..." />
            <AutoCompleteList>
              {parentOptions?.map((opt) => (
                <AutoCompleteItem key={opt} value={opt}>
                  {opt}
                </AutoCompleteItem>
              ))}
            </AutoCompleteList>
          </AutoComplete>

          <Box mt={2}>
            <AutoComplete
              multiple
              value={children}
              maxSelections={constraints.value_array_len}
              openOnFocus
              suggestWhenEmpty
              onSelectOption={({ item }) => {
                const newChildren = [...children, item.value];
                if (!constraints.value_array_len ||
                  newChildren.length <= constraints.value_array_len) {
                  onChange({
                    ...value,
                    [parentVal]: newChildren
                  });
                }
              }}
            >
              <AutoCompleteInput
                placeholder={`Add children (max ${constraints.value_array_len || '∞'})`}
              />
              <AutoCompleteList>
                {childOptions?.map((opt) => (
                  <AutoCompleteItem key={opt} value={opt}>
                    {opt}
                  </AutoCompleteItem>
                ))}
              </AutoCompleteList>
            </AutoComplete>

            <Box mt={2} display="flex" flexWrap="wrap" gap={2}>
              {children.map((child, idx) => (
                <AutoCompleteTag
                  key={`${child}-${idx}`}
                  label={child}
                  onRemove={() => {
                    const newChildren = [...children];
                    newChildren.splice(idx, 1);
                    onChange({
                      ...value,
                      [parentVal]: newChildren
                    });
                  }}
                />
              ))}
            </Box>
          </Box>
        </Box>
      ))}

      <Button
        onClick={() => {
          const newParent = `new-${Object.keys(value).length}`;
          onChange({
            ...value,
            [newParent]: []
          });
        }}
      >
        Add New Group
      </Button>
    </VStack>
  );
};
