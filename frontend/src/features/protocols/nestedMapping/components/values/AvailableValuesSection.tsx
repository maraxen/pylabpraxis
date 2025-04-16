import React from 'react';
import { Box, Heading, VStack, Text, HStack } from '@chakra-ui/react';
import { DroppableArea } from '@praxis-ui';
import { ValueItem } from './ValueItem';
import { ValueCreator } from './ValueCreator';
import { useNestedMapping } from '@features/protocols/contexts/nestedMappingContext';
import { ValueData } from '@shared/types/protocol';

interface AvailableValuesSectionProps {
  value: Record<string, any>;
  editingValueId: string | null;
  setEditingValueId: React.Dispatch<React.SetStateAction<string | null>>;
}

export const AvailableValuesSection: React.FC<AvailableValuesSectionProps> = ({ value, editingValueId, setEditingValueId }) => {
  const {
    dragInfo,
    createdValues,
    effectiveChildOptions,
    creatableValue,
    creationMode
  } = useNestedMapping();

  // Get available values as an array of ValueData objects
  // Merge createdValues with constraint-defined options (effectiveChildOptions)
  const createdValueList: ValueData[] = Object.values(createdValues);

  // Build a Set of existing primitive values for quick deduplication
  const existingValuesSet = new Set(
    createdValueList.map((v) => (v?.value !== undefined && v?.value !== null ? JSON.stringify(v.value) : 'null'))
  );

  const constraintValues: ValueData[] = (effectiveChildOptions || []).map((val: any) => {
    const key = val !== undefined && val !== null ? JSON.stringify(val) : 'null';
    return {
      id: `constraint_${key}`, // deterministic id for constraint values
      value: val,
      type: typeof val,
      isEditable: false,
    };
  }).filter((v) => !existingValuesSet.has(JSON.stringify(v.value)));

  const availableValues: ValueData[] = [...createdValueList, ...constraintValues];

  // Check if we're currently in value creation mode
  const isCreatingValue = creationMode === 'value';

  return (
    <Box>
      <VStack align="stretch" gap={4}>
        <HStack justifyContent="space-between">
          <Heading size="sm" mb={2}>Available Values</Heading>
          {/* Only show ValueCreator when not already in creation mode */}
          {!isCreatingValue && <ValueCreator value={availableValues} />}
        </HStack>

        <DroppableArea
          id="available-values"
          isOver={dragInfo.overDroppableId === 'available-values'}
          isDragging={dragInfo.isDragging}
          defaultFull={false}
        >
          {/* Show Creator UI when in value creation mode */}
          {isCreatingValue && (
            <ValueCreator value={availableValues} />
          )}

          {/* Render available values */}
          {availableValues.length > 0 ? (
            <VStack align="stretch" gap={2}>
              {availableValues.map((item: ValueData) => (
                <ValueItem
                  key={item.id}
                  id={item.id}
                  value={item.value}
                  type={item.type || 'string'}
                  dragMode="draggable"
                  isEditable={item.isEditable}
                  alwaysDraggable={true}
                  isEditing={editingValueId === item.id}
                  onEdit={() => setEditingValueId(item.id)}
                  onBlur={() => setEditingValueId(null)}
                  onValueChange={(newVal) => {
                    // Update createdValues directly
                    createdValues[item.id].value = newVal;
                  }}
                />
              ))}
            </VStack>
          ) : (
            !isCreatingValue && (
              <Box py={8} textAlign="center">
                <Text color="gray.500">
                  {creatableValue
                    ? "No available values. Click 'Add Value' to create one."
                    : "No available values."}
                </Text>
              </Box>
            )
          )}
        </DroppableArea>
      </VStack>
    </Box>
  );
};