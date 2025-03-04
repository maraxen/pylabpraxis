import React, { useState, useEffect } from 'react';
import { Box, SimpleGrid } from '@chakra-ui/react';
import {
  DndContext,
  closestCenter,
  DragOverlay,
} from '@dnd-kit/core';
import { snapCenterToCursor } from '@dnd-kit/modifiers';

// Import the context provider
import { NestedMappingProvider } from './contexts/nestedMappingContext';

// Import the section components
import { GroupsSection } from './sections/GroupsSection';
import { AvailableValuesSection } from './sections/AvailableValuesSection';

// Import the managers
import { MetadataManager } from './managers/MetadataManager';
import { EditingManager } from './managers/EditingManager';

// Import the value display for drag overlay
import { ValueDisplay } from './subcomponents/valueDisplay';

// Import utilities
import { useDndSensors, addDragStyles, removeDragStyles } from './utils/dndUtils';
import { NestedMappingProps, GroupData, SubvariablesData, ValueData, BaseValueProps, SubvariableValue } from './utils/parameterUtils';

// Helper functions for working with IDs
const generateUniqueId = (): string => {
  return crypto.randomUUID();
};

// Find a value by its content across all groups
const findValueByContent = (
  groups: Record<string, GroupData>,
  valueToFind: any
): { valueId: string, groupId: string } | null => {
  for (const [groupId, group] of Object.entries(groups)) {
    for (const valueData of group.values) {
      if (valueData.value === valueToFind) {
        return { valueId: valueData.id, groupId };
      }
    }
  }
  return null;
};

// Find a group by its name
const findGroupByName = (
  groups: Record<string, GroupData>,
  nameToFind: string
): string | null => {
  for (const [groupId, group] of Object.entries(groups)) {
    if (group.name === nameToFind) {
      return groupId;
    }
  }
  return null;
};

/**
 * HierarchicalMapping is a component that allows users to organize values into groups
 * with drag-and-drop functionality and editing capabilities.
 */
const HierarchicalMappingImpl: React.FC<NestedMappingProps> = ({
  name,
  value,
  config,
  onChange,
  parameters,
}) => {
  // Extract constraints with defaults
  const constraints = config?.constraints || {};
  const isParentKey = constraints?.parent === 'key';
  const valueType = constraints?.value_type || 'string';

  // Fix the creatable flags to check both creatable and specific flags
  const creatable = !!constraints?.creatable;
  const creatableKey = creatable || !!constraints?.creatable_key;
  const creatableValue = creatable || !!constraints?.creatable_value;

  // Configure sensors for drag and drop
  const sensors = useDndSensors();

  // Track active drag overlay item
  const [activeId, setActiveId] = useState<string | null>(null);
  const [activeData, setActiveData] = useState<any>(null);
  const [overDroppableId, setOverDroppableId] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);

  // Add state for tracking value locations
  const [valueLocations, setValueLocations] = useState<Record<string, string | null>>({});

  // Initial setup to ensure all values and groups have IDs
  useEffect(() => {
    let requiresUpdate = false;
    const updatedValue = { ...value };

    // Ensure all groups have IDs and proper structure
    Object.entries(updatedValue).forEach(([key, groupData]) => {
      // Handle case where groupData is not an object
      if (typeof groupData !== 'object' || groupData === null) {
        requiresUpdate = true;
        updatedValue[key] = {
          id: generateUniqueId(),
          name: key,
          values: [],
          isEditable: true
        };
        return;
      }

      if (!groupData.id) {
        requiresUpdate = true;
        groupData.id = generateUniqueId();
      }

      if (!groupData.name) {
        requiresUpdate = true;
        groupData.name = key;
      }

      // Initialize or convert values array
      if (!groupData.values || !Array.isArray(groupData.values)) {
        requiresUpdate = true;
        // Handle different formats of input data
        let oldValues: any[] = [];

        if (Array.isArray(groupData)) {
          oldValues = groupData;
        } else if (Array.isArray(groupData.values)) {
          oldValues = groupData.values;
        } else if (groupData.values) {
          // Handle case where values exists but isn't an array
          oldValues = [groupData.values];
        }

        groupData.values = oldValues.map(val => {
          if (typeof val === 'object' && val !== null && val.id && val.value !== undefined) {
            return val; // Already in correct format
          } else {
            // Convert to ValueData format with ID
            return {
              id: generateUniqueId(),
              value: val,
              type: valueType,
              isEditable: true
            };
          }
        });
      }
    });

    if (requiresUpdate) {
      onChange(updatedValue);
    }
  }, []);

  // Initialize value locations mapping
  useEffect(() => {
    // Track locations of all values
    const locations: Record<string, string | null> = {};

    // Map each value ID to its group ID
    Object.entries(value).forEach(([groupId, groupData]) => {
      if (groupData && Array.isArray(groupData.values)) {
        groupData.values.forEach((valueData: ValueData) => {
          locations[valueData.id] = groupId;
        });
      }
    });

    setValueLocations(locations);
  }, [value]);

  // Create a new value
  const createValue = (newVal: any): string => {
    const valueData: ValueData = {
      id: generateUniqueId(),
      value: newVal,
      type: valueType,
      isEditable: true
    };
    return valueData.id;
  };

  // Create a new group
  const createGroup = (groupName: string): string => {
    const groupId = generateUniqueId();
    const newGroup: GroupData = {
      id: groupId,
      name: groupName,
      values: [],
      isEditable: true
    };

    onChange({
      ...value,
      [groupId]: newGroup
    });

    return groupId;
  };

  // Handle drag start
  const handleDragStart = (event: any) => {
    setActiveId(String(event.active.id));
    setIsDragging(true);

    // Capture metadata for the drag overlay
    const metadata = event.active.data.current || {};
    setActiveData(metadata);

    addDragStyles();
  };

  // Handle drag over for highlighting
  const handleDragOver = (event: any) => {
    const overId = event.over?.id || null;
    setOverDroppableId(overId);
  };

  // Handle drag end with direct value manipulation
  const handleDragEnd = (event: any) => {
    setIsDragging(false);
    setOverDroppableId(null);

    // If no active or over elements, just clean up
    if (!event.active || !event.over) {
      setActiveId(null);
      setActiveData(null);
      removeDragStyles();
      return;
    }

    const { active, over } = event;
    const draggedId = String(active.id);
    const targetId = String(over.id);

    // Find the value and which group it's currently in
    let sourceGroupId = valueLocations[draggedId] || null;

    // Handle dropping to available values (removing from a group)
    if (targetId === 'available-values' && sourceGroupId) {
      const sourceGroup = value[sourceGroupId];

      // Remove from source group
      const updatedValues = sourceGroup.values.filter(v => v.id !== draggedId);

      // Create updated group
      const updatedGroup: GroupData = {
        ...sourceGroup,
        values: updatedValues
      };

      // Update value
      onChange({
        ...value,
        [sourceGroupId]: updatedGroup
      });

      // Update local tracking
      setValueLocations(prev => ({
        ...prev,
        [draggedId]: null // Set to available
      }));
    }
    // Handle dropping to a group
    else if (value[targetId] && targetId !== sourceGroupId) {
      const targetGroup = value[targetId];
      const draggedValueData = sourceGroupId ?
        value[sourceGroupId].values.find(v => v.id === draggedId) :
        null;

      if (!draggedValueData) {
        // Clean up and exit if we can't find the dragged value
        setActiveId(null);
        setActiveData(null);
        removeDragStyles();
        return;
      }

      let updatedValue = { ...value };

      // Remove from source group if it exists
      if (sourceGroupId) {
        const sourceGroup = value[sourceGroupId];
        const updatedSourceValues = sourceGroup.values.filter(v => v.id !== draggedId);

        updatedValue = {
          ...updatedValue,
          [sourceGroupId]: {
            ...sourceGroup,
            values: updatedSourceValues
          }
        };
      }

      // Add to target group
      updatedValue = {
        ...updatedValue,
        [targetId]: {
          ...targetGroup,
          values: [...targetGroup.values, draggedValueData]
        }
      };

      // Update value
      onChange(updatedValue);

      // Update local tracking
      setValueLocations(prev => ({
        ...prev,
        [draggedId]: targetId
      }));
    }

    // Clean up
    setActiveId(null);
    setActiveData(null);
    removeDragStyles();
  };

  // Prepare parent and child options based on constraints
  const parentOptions = isParentKey
    ? (constraints?.key_array || [])
    : (constraints?.value_array || []);

  const childOptions = isParentKey
    ? (constraints?.value_array || [])
    : (constraints?.key_array || []);

  // Extract parameter references from constraints
  const keyParam = constraints?.key_param;
  const valueParam = constraints?.value_param;

  // Extract parameter values with fallbacks
  const keyParamValues = keyParam && parameters?.[keyParam]?.default
    ? Array.isArray(parameters[keyParam].default)
      ? parameters[keyParam].default
      : [parameters[keyParam].default]
    : [];

  const valueParamValues = valueParam && parameters?.[valueParam]?.default
    ? Array.isArray(parameters[valueParam].default)
      ? parameters[valueParam].default
      : [parameters[valueParam].default]
    : [];

  // Get effective options based on references with fallbacks
  const effectiveParentOptions = isParentKey
    ? (parentOptions.length > 0 ? parentOptions : keyParamValues)
    : (parentOptions.length > 0 ? parentOptions : valueParamValues);

  const effectiveChildOptions = isParentKey
    ? (childOptions.length > 0 ? childOptions : valueParamValues)
    : (childOptions.length > 0 ? childOptions : keyParamValues);

  const dragInfo = {
    activeId,
    activeData,
    overDroppableId,
    isDragging
  };

  return (
    <NestedMappingProvider
      config={config}
      parameters={parameters}
      value={value}
      onChange={onChange}
      effectiveChildOptions={effectiveChildOptions}
      effectiveParentOptions={effectiveParentOptions}
      dragInfo={dragInfo}
      createValue={createValue}
      createGroup={createGroup}
    >
      <MetadataManager>
        <EditingManager>
          <DndContext
            sensors={sensors}
            collisionDetection={closestCenter}
            onDragStart={handleDragStart}
            onDragOver={handleDragOver}
            onDragEnd={handleDragEnd}
            modifiers={[snapCenterToCursor]}
          >
            <Box width="100%">
              <SimpleGrid columns={2} gap={4} width="100%">
                {/* Groups Section */}
                <GroupsSection value={value} onChange={onChange} />

                {/* Available Values Section */}
                <AvailableValuesSection value={value} />
              </SimpleGrid>
            </Box>

            {/* Drag Overlay */}
            <DragOverlay
              dropAnimation={{
                duration: 200,
                easing: 'cubic-bezier(0.18, 0.67, 0.6, 1.22)',
              }}
              modifiers={[snapCenterToCursor]}
            >
              {activeId ? (
                <ValueDisplay
                  value={activeData?.value || activeId}
                  type={activeData?.metadata?.type || valueType}
                  isFromParam={activeData?.metadata?.isFromParam}
                  paramSource={activeData?.metadata?.paramSource}
                  isEditable={activeData?.metadata?.isEditable}
                />
              ) : null}
            </DragOverlay>

            {/* Global styles for drag cursor */}
            <style>{`
              body.dragging {
                cursor: grabbing !important;
              }
              body.dragging * {
                cursor: grabbing !important;
              }
            `}</style>
          </DndContext>
        </EditingManager>
      </MetadataManager>
    </NestedMappingProvider>
  );
};

// Export the public API component
export const HierarchicalMapping: React.FC<NestedMappingProps> = (props) => {
  return <HierarchicalMappingImpl {...props} />;
};
