import React, { useMemo } from 'react';
import { Box, Text, VStack, SimpleGrid, Heading } from '@chakra-ui/react';
import { useDroppable } from '@dnd-kit/core';
import { SortableValueItem } from '../subcomponents/SortableValueItem';
import { ValueCreator } from '../creators/ValueCreator';
import { useNestedMapping } from '../contexts/nestedMappingContext';
import { GroupData, ValueData } from '../utils/parameterUtils';
import { useEditing } from '../managers/editingManager';
import { nanoid } from 'nanoid';

// Export the interface so tests can use it
export interface AvailableValuesSectionProps {
  value: Record<string, GroupData>;
}

export const AvailableValuesSection: React.FC<AvailableValuesSectionProps> = ({ value }) => {
  const {
    effectiveChildOptions,
    valueType,
    getValueMetadata,
    dragInfo,
    createdValues,
    setCreatedValues,
    creatableValue
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

  // Create a ref to persist generated IDs per available value
  const availableIdMap = React.useRef<Record<string, string>>({});

  // Track values currently in use in any group
  const usedValues = useMemo(() => {
    const values = new Set<string>();
    const ids = new Set<string>();

    Object.values(value).forEach(group => {
      if (group?.values && Array.isArray(group.values)) {
        group.values.forEach((valueData: ValueData) => {
          if (valueData?.value !== undefined) {
            values.add(String(valueData.value));
            ids.add(valueData.id);
          }
        });
      }
    });

    return { values, ids };
  }, [value]);

  // Get available values for display - solving the duplicate key issue
  const availableValues = useMemo(() => {
    const result: ValueData[] = [];
    const valuesSeen = new Set<string>();
    const idsSeen = new Set<string>(); // Track IDs to avoid duplicates

    // First, add created values that aren't in groups
    Object.values(createdValues).forEach(valueData => {
      const valueStr = String(valueData.value);
      const valueId = valueData.id;

      // Only add if not in a group and we haven't seen this ID yet
      if (!usedValues.ids.has(valueId) && !idsSeen.has(valueId)) {
        result.push(valueData);
        valuesSeen.add(valueStr);
        idsSeen.add(valueId);
      }
    });

    // Then add options from constraints that aren't used
    effectiveChildOptions.forEach(option => {
      // Skip null/undefined values and objects
      if (option === null || option === undefined || typeof option === 'object') return;

      const optionStr = String(option);
      if (!usedValues.values.has(optionStr) && !valuesSeen.has(optionStr)) {
        // Generate a persistent ID if needed
        if (!availableIdMap.current[optionStr]) {
          availableIdMap.current[optionStr] = nanoid();
        }

        const id = availableIdMap.current[optionStr];

        // Crucial check: avoid duplicate IDs
        if (idsSeen.has(id)) {
          return; // Skip this option if ID is already used
        }

        const metadata = getValueMetadata(optionStr);

        // Check if this value already exists in createdValues
        let valueData: ValueData;
        if (createdValues[id]) {
          valueData = createdValues[id];
        } else {
          valueData = {
            id,
            value: option,
            type: metadata.type || valueType,
            isFromParam: metadata.isFromParam,
            paramSource: metadata.paramSource,
            isEditable: creatableValue ? true : metadata.isEditable
          };
        }

        result.push(valueData);
        valuesSeen.add(optionStr);
        idsSeen.add(id);
      }
    });

    return result;
  }, [effectiveChildOptions, createdValues, usedValues, getValueMetadata, valueType, creatableValue]);

  // Handle deleting a value from available values
  const handleDeleteValue = (valueId: string) => {
    setCreatedValues(prev => {
      const { [valueId]: _, ...rest } = prev;
      return rest;
    });
  };

  // Sync available values to createdValues for persistence
  React.useEffect(() => {
    const updates: Record<string, ValueData> = {};
    let hasUpdates = false;

    availableValues.forEach(valueData => {
      const id = valueData.id;
      if (!createdValues[id]) {
        updates[id] = valueData;
        hasUpdates = true;
      }
    });

    if (hasUpdates) {
      setCreatedValues(prev => ({ ...prev, ...updates }));
    }
  }, [availableValues, createdValues, setCreatedValues]);

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
              {availableValues.map((valueData) => {
                // Convert value to string for display
                const valueStr = String(valueData.value);

                // Get metadata but prioritize explicit flags from the value item
                const baseMetadata = getValueMetadata(valueData.value);
                const isFromParam = valueData.isFromParam !== undefined ? valueData.isFromParam : baseMetadata.isFromParam;

                // Determine editability based on both creatable flag and metadata
                const isValueEditable = creatableValue ? true :
                  valueData.isEditable !== undefined ? valueData.isEditable : baseMetadata.isEditable;

                return (
                  <SortableValueItem
                    key={valueData.id}
                    id={valueData.id}
                    availableId={valueData.id}
                    value={valueStr}
                    type={valueData.type || valueType}
                    isFromParam={isFromParam}
                    paramSource={valueData.paramSource}
                    isEditable={isValueEditable}
                    dragMode="draggable"
                    isEditing={isEditing(valueData.id, null)}
                    onFocus={() => handleStartEditing(valueData.id, valueStr, null)}
                    onBlur={handleFinishEditing}
                    onValueChange={handleEditingChange}
                    onDelete={isValueEditable && !isFromParam ? () => handleDeleteValue(valueData.id) : undefined}
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
