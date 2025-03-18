import React from 'react';
import { Box, Heading, VStack, Text, HStack } from '@chakra-ui/react';
import { DroppableArea } from '@praxis-ui';
import { ValueItem } from './ValueItem';
import { ValueCreator } from './ValueCreator';
import { useNestedMapping } from '@features/protocols/contexts/nestedMappingContext';
import { ValueData } from '@shared/types/protocol';

interface AvailableValuesSectionProps {
  value: Record<string, any>;
}

export const AvailableValuesSection: React.FC<AvailableValuesSectionProps> = ({ value }) => {
  const {
    dragInfo,
    createdValues,
    effectiveChildOptions,
    creatableValue,
    creationMode
  } = useNestedMapping();

  // Get available values as an array of ValueData objects
  const availableValues: ValueData[] = Object.values(createdValues);

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