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
    dragInfo
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

  // Filter out values that are already used in groups
  const usedValues = useMemo(() => {
    const used = new Set<string>();

    Object.values(value).forEach(group => {
      if (group?.values && Array.isArray(group.values)) {
        group.values.forEach((valueData: ValueData) => {
          if (valueData?.value !== undefined) {
            used.add(String(valueData.value));
          }
        });
      }
    });

    return used;
  }, [value]);

  // Available values are those in the options that aren't used in groups
  const availableValues = useMemo(() => {
    return effectiveChildOptions.filter(option => !usedValues.has(String(option)));
  }, [effectiveChildOptions, usedValues]);

  return (
    <Box>
      <VStack align="stretch" spacing={4}>
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
            <SimpleGrid columns={1} spacing={2}>
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
