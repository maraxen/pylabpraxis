import React, { useMemo } from 'react';
import { Box, Text, VStack, SimpleGrid, Heading } from '@chakra-ui/react';
import { useDroppable } from '@dnd-kit/core';
import { SortableValueItem } from '../subcomponents/SortableValueItem';
import { ValueCreator } from '../creators/ValueCreator';
import { useNestedMapping } from '../contexts/nestedMappingContext';
import { GroupData, ValueData } from '../utils/parameterUtils';
import { useEditing } from '../managers/editingManager';

interface AvailableValuesSectionProps {
  value: Record<string, GroupData>;
}

export const AvailableValuesSection: React.FC<AvailableValuesSectionProps> = ({ value }) => {
  const {
    effectiveChildOptions,
    valueType,
    getValueMetadata,
    dragInfo,
    createdValues // Add this line to get createdValues from context
  } = useNestedMapping();

  const {
    isEditing,
    handleStartEditing,
    handleEditingChange,
    handleFinishEditing
  } = useEditing();

  // Setup droppable for the available values section
  const { setNodeRef, isOver } = useDroppable({
    id: 'available-values',
  });

  // Update the availableValues memo to properly track and display values
  const availableValues = useMemo(() => {
    // Start with options from constraints
    const allOptions = [...effectiveChildOptions];

    // Track all values that are in groups to avoid duplicates
    const usedValues = new Set<string>();

    // Track value IDs to their display values for lookups
    const valueIdMap = new Map<string, string>();

    // Collect all values that are in groups
    Object.values(value).forEach(group => {
      if (group?.values && Array.isArray(group.values)) {
        group.values.forEach((valueData: ValueData) => {
          if (valueData?.value !== undefined) {
            usedValues.add(String(valueData.value));
            valueIdMap.set(valueData.id, String(valueData.value));
          }
        });
      }
    });

    // Add created values that aren't assigned to groups
    const createdValuesList: any[] = [];
    Object.values(createdValues).forEach(valueData => {
      if (!valueIdMap.has(valueData.id) && !usedValues.has(String(valueData.value))) {
        createdValuesList.push(valueData.value);
      }
    });

    // Combine all available options into one list, deduplicating and filtering
    const uniqueOptions = new Set([...allOptions, ...createdValuesList]);
    const combined = Array.from(uniqueOptions).filter(option => !usedValues.has(String(option)));

    return combined;
  }, [effectiveChildOptions, createdValues, value]);

  return (
    <Box>
      <VStack align="stretch" gap={4}>
        <Box px={1}>
          <Heading size="sm" mb={2}>Available Values</Heading>
          <ValueCreator value={value} />
        </Box>

        <Box
          ref={setNodeRef}
          borderWidth={1}
          borderRadius="md"
          p={3}
          bg={isOver || dragInfo.overDroppableId === 'available-values' ? "blue.50" : "gray.50"}
          _dark={{
            bg: isOver || dragInfo.overDroppableId === 'available-values' ? "blue.900" : "gray.800"
          }}
          borderColor={isOver || dragInfo.overDroppableId === 'available-values' ? "blue.400" : "gray.200"}
          transition="all 0.2s"
          minHeight="100px"
        >
          {availableValues.length > 0 ? (
            <SimpleGrid columns={1} gap={2}>
              {availableValues.map((availableValue, index) => {
                const valueStr = String(availableValue);
                const metadata = getValueMetadata(valueStr);
                const availableId = `available-${index}-${valueStr}`;

                return (
                  <SortableValueItem
                    key={availableId}
                    id={valueStr}
                    availableId={availableId}
                    value={valueStr}
                    type={metadata.type || valueType}
                    isFromParam={metadata.isFromParam}
                    paramSource={metadata.paramSource}
                    isEditable={metadata.isEditable}
                    dragMode="draggable"
                    isEditing={isEditing(availableId, null)}
                    onFocus={() => handleStartEditing(availableId, valueStr, null)}
                    onBlur={handleFinishEditing}
                    onValueChange={handleEditingChange}
                  />
                );
              })}
            </SimpleGrid>
          ) : (
            <Text color="gray.500" textAlign="center" py={4}>
              No available values. Add values or drop items here to remove from groups.
            </Text>
          )}
        </Box>
      </VStack>
    </Box>
  );
};
