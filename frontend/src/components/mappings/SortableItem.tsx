import React from 'react';
import { useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import { Box, HStack } from '@chakra-ui/react';
import { AutoComplete, AutoCompleteInput, AutoCompleteItem, AutoCompleteList } from "@choc-ui/chakra-autocomplete";
import { LuGripVertical } from "react-icons/lu";


interface SortableItemProps {
  id: string;
  keyValue: string;
  value: string;
  keyOptions?: string[];
  valueOptions?: string[];
  onKeyChange: (newKey: string) => void;
  onValueChange: (newValue: string) => void;
}

export const SortableItem: React.FC<SortableItemProps> = ({
  id,
  keyValue,
  value,
  keyOptions,
  valueOptions,
  onKeyChange,
  onValueChange,
}) => {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
  } = useSortable({ id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
  };

  return (
    <Box ref={setNodeRef} style={style} width="100%">
      <HStack width="100%" gap={2}>
        <Box cursor="grab" {...attributes} {...listeners}>
          <LuGripVertical />
        </Box>

        <AutoComplete
          value={keyValue}
          openOnFocus
          suggestWhenEmpty
          onSelectOption={({ item }) => onKeyChange(item.value)}
        >
          <AutoCompleteInput placeholder="Key" />
          <AutoCompleteList>
            {keyOptions?.map((opt) => (
              <AutoCompleteItem key={opt} value={opt}>
                {opt}
              </AutoCompleteItem>
            ))}
          </AutoCompleteList>
        </AutoComplete>

        <AutoComplete
          value={value}
          openOnFocus
          suggestWhenEmpty
          onSelectOption={({ item }) => onValueChange(item.value)}
        >
          <AutoCompleteInput placeholder="Value" />
          <AutoCompleteList>
            {valueOptions?.map((opt) => (
              <AutoCompleteItem key={opt} value={opt}>
                {opt}
              </AutoCompleteItem>
            ))}
          </AutoCompleteList>
        </AutoComplete>
      </HStack>
    </Box>
  );
};
