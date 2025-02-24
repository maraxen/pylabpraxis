import React from 'react';
import { VStack, Box } from '@chakra-ui/react';
import { DndContext, closestCenter, KeyboardSensor, PointerSensor, useSensor, useSensors } from '@dnd-kit/core';
import { arrayMove, SortableContext, sortableKeyboardCoordinates, verticalListSortingStrategy } from '@dnd-kit/sortable';
import { SortableItem } from './SortableItem';

interface OneToOneMappingProps {
  name: string;
  value: Record<string, any>;
  constraints: {
    key_array?: (string | number)[];
    value_array?: (string | number)[];
    key_param?: string;
    value_param?: string;
  };
  onChange: (value: Record<string, any>) => void;
}

export const OneToOneMapping: React.FC<OneToOneMappingProps> = ({
  name,
  value,
  constraints,
  onChange,
}) => {
  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );

  const handleDragEnd = (event: any) => {
    const { active, over } = event;

    if (active.id !== over.id) {
      const oldIndex = Object.keys(value).indexOf(active.id);
      const newIndex = Object.keys(value).indexOf(over.id);

      const items = Object.entries(value);
      const [reorderedItems] = arrayMove(items, oldIndex, newIndex);

      const newValue = Object.fromEntries(reorderedItems);
      onChange(newValue);
    }
  };

  return (
    <DndContext
      sensors={sensors}
      collisionDetection={closestCenter}
      onDragEnd={handleDragEnd}
    >
      <Box width="100%">
        <SortableContext
          items={Object.keys(value)}
          strategy={verticalListSortingStrategy}
        >
          <VStack gap={2}>
            {Object.entries(value).map(([key, val]) => (
              <SortableItem
                key={key}
                id={key}
                keyValue={key}
                value={val}
                keyOptions={constraints.key_array?.map(item => String(item))}
                valueOptions={constraints.value_array?.map(item => String(item))}
                onKeyChange={(newKey) => {
                  const newValue = { ...value };
                  delete newValue[key];
                  newValue[newKey] = val;
                  onChange(newValue);
                }}
                onValueChange={(newVal) => {
                  onChange({ ...value, [key]: newVal });
                }}
              />
            ))}
          </VStack>
        </SortableContext>
      </Box>
    </DndContext>
  );
};
