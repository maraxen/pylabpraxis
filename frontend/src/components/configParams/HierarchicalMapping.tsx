import React, { useState, useEffect } from 'react';
import { Box, SimpleGrid } from '@chakra-ui/react';
import {
  DndContext,
  closestCenter,
  DragOverlay,
} from '@dnd-kit/core';
import { snapCenterToCursor } from '@dnd-kit/modifiers';

// Import the context provider and other components
import { NestedMappingProvider } from './contexts/nestedMappingContext';
import { GroupsSection } from './sections/GroupsSection';
import { AvailableValuesSection } from './sections/AvailableValuesSection';
import { MetadataManager } from './managers/MetadataManager';
import { EditingManager } from './managers/editingManager';
import { DebugManager } from './managers/debugManager';
import { ValueDisplay } from './subcomponents/valueDisplay';

// Import utilities
import { useDndSensors, addDragStyles, removeDragStyles } from './utils/dndUtils';
import { NestedMappingProps, GroupData, ValueData } from './utils/parameterUtils';
import { clearExcessStorage, generateCompactId } from './utils/storageUtils';

/**
 * HierarchicalMapping component that renders a mapping interface with groups and values
 * Uses the new nested constraint structure (key_constraints/value_constraints)
 * while maintaining backward compatibility with legacy constraints
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

  // Get nested constraints with better typing
  const keyConstraints = constraints.key_constraints || {};
  const valueConstraints = constraints.value_constraints || {};

  // Determine the parent-child relationship
  const isParentKey = constraints?.parent === 'key';

  // Extract type information with proper fallbacks
  // First try the nested constraints, then fall back to legacy format
  const keyType = keyConstraints.type || constraints.key_type || 'string';
  const valueType = valueConstraints.type || constraints.value_type || 'string';

  // Extract editability flags with inheritance and priority order
  // A value is editable if it's marked as such at any level
  const isKeyEditable =
    !!keyConstraints.editable ||
    !!constraints.editable ||
    !!constraints.editable_key;

  const isValueEditable =
    !!valueConstraints.editable ||
    !!constraints.editable ||
    !!constraints.editable_value;

  // Extract creatability flags with inheritance and priority order
  // Creatable flag enables both key and value creation unless specifically disabled
  const creatable = !!constraints.creatable;
  const creatableKey =
    !!keyConstraints.creatable ||
    creatable ||
    !!constraints.creatable_key;

  const creatableValue =
    !!valueConstraints.creatable ||
    creatable ||
    !!constraints.creatable_value;

  // Configure sensors for drag and drop
  const sensors = useDndSensors();

  // UI and drag state
  const [activeId, setActiveId] = useState<string | null>(null);
  const [activeData, setActiveData] = useState<any>(null);
  const [overDroppableId, setOverDroppableId] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [valueLocations, setValueLocations] = useState<Record<string, string | null>>({});
  const [createdValues, setCreatedValues] = useState<Record<string, ValueData>>({});

  // Clear excess storage on component mount to prevent storage quota issues
  useEffect(() => {
    try {
      clearExcessStorage();
    } catch (e) {
      console.warn("Error clearing storage:", e);
    }
  }, []);

  // Initialize structure with proper IDs and formatting
  useEffect(() => {
    let requiresUpdate = false;
    const updatedValue = { ...value };

    // Ensure all groups have proper structure
    Object.entries(updatedValue).forEach(([key, groupData]) => {
      // Handle case where groupData is not properly structured
      if (typeof groupData !== 'object' || groupData === null) {
        requiresUpdate = true;
        updatedValue[key] = {
          id: generateCompactId(),
          name: key,
          values: [],
          isEditable: isKeyEditable // Use constraint-based editability
        };
        return;
      }

      if (!groupData.id) {
        requiresUpdate = true;
        groupData.id = generateCompactId();
      }

      if (!groupData.name) {
        requiresUpdate = true;
        groupData.name = key;
      }

      // Initialize values array with proper structure
      if (!groupData.values || !Array.isArray(groupData.values)) {
        requiresUpdate = true;
        // Handle different input formats
        let oldValues: any[] = [];

        if (Array.isArray(groupData)) {
          oldValues = groupData;
        } else if (Array.isArray(groupData.values)) {
          oldValues = groupData.values;
        } else if (groupData.values) {
          oldValues = [groupData.values];
        }

        // Convert all values to proper ValueData format
        groupData.values = oldValues.map(val => {
          if (typeof val === 'object' && val !== null && val.id && val.value !== undefined) {
            return val; // Already in correct format
          } else {
            // Convert to ValueData format with proper types from constraints
            return {
              id: generateCompactId(),
              value: val,
              type: isParentKey ? valueType : keyType, // Use appropriate type based on parent-child relationship
              isEditable: isValueEditable // Use constraint-based editability
            };
          }
        });
      }
    });

    if (requiresUpdate) {
      onChange(updatedValue);
    }
  }, []);

  // Track value locations for drag and drop operations
  useEffect(() => {
    const locations: Record<string, string | null> = {};

    // Map each value ID to its containing group ID
    Object.entries(value).forEach(([groupId, groupData]) => {
      if (groupData && Array.isArray(groupData.values)) {
        groupData.values.forEach((valueData: ValueData) => {
          locations[valueData.id] = groupId;
        });
      }
    });

    setValueLocations(locations);
  }, [value]);

  // Create a new value with proper typing from constraints
  const createValue = (newVal: any): string => {
    try {
      const valueId = generateCompactId('val_');

      // Create value data with constraint-based type and editability
      const valueData: ValueData = {
        id: valueId,
        value: newVal,
        type: isParentKey ? valueType : keyType, // Type depends on parent-child relationship
        isEditable: isValueEditable // Use constraint-based editability
      };

      setCreatedValues(prev => ({
        ...prev,
        [valueId]: valueData
      }));

      return valueId;
    } catch (error) {
      console.error("Error creating value:", error);
      return "";
    }
  };

  // Create a new group with proper typing from constraints
  const createGroup = (groupName: string): string => {
    try {
      const groupId = generateCompactId('group_');

      // Create group with constraint-based editability
      const newGroup: GroupData = {
        id: groupId,
        name: groupName,
        values: [],
        isEditable: isKeyEditable // Use constraint-based editability
      };

      onChange({
        ...value,
        [groupId]: newGroup
      });

      return groupId;
    } catch (error) {
      console.error("Error creating group:", error);
      try {
        clearExcessStorage();
      } catch {
        // Ignore nested error
      }
      return "";
    }
  };

  // Drag and drop handlers
  const handleDragStart = (event: any) => {
    setActiveId(String(event.active.id));
    setIsDragging(true);
    setActiveData(event.active.data.current || {});
    addDragStyles();
  };

  const handleDragOver = (event: any) => {
    const overId = event.over?.id || null;
    if (overDroppableId !== overId) {
      setOverDroppableId(overId);
    }
  };

  const handleDragEnd = (event: any) => {
    setIsDragging(false);
    setOverDroppableId(null);

    if (!event.active || !event.over) {
      setActiveId(null);
      setActiveData(null);
      removeDragStyles();
      return;
    }

    try {
      const { active, over } = event;
      const draggedId = String(active.id);
      const targetId = String(over.id);

      // Get source group of the dragged item
      let sourceGroupId = valueLocations[draggedId] || null;

      // Handle dropping to "available values" (removing from group)
      if (targetId === 'available-values' && sourceGroupId) {
        const sourceGroup = value[sourceGroupId];
        const updatedValues = sourceGroup.values.filter(v => v.id !== draggedId);

        // Update the value state
        onChange({
          ...value,
          [sourceGroupId]: {
            ...sourceGroup,
            values: updatedValues
          }
        });

        // Update tracking
        setValueLocations(prev => ({
          ...prev,
          [draggedId]: null
        }));
      }
      // Handle dropping to a group
      else if (value[targetId] && targetId !== sourceGroupId) {
        const targetGroup = value[targetId];

        // Find value data based on where it's coming from
        let draggedValueData;
        if (!sourceGroupId) {
          // From available values
          const draggedValue = active.data.current?.value;
          if (draggedValue !== undefined) {
            draggedValueData = {
              id: draggedId,
              value: draggedValue,
              type: isParentKey ? valueType : keyType, // Use constraint-based type
              isEditable: isValueEditable // Use constraint-based editability
            };
          }
        } else {
          // From another group
          draggedValueData = value[sourceGroupId].values.find(v => v.id === draggedId);
        }

        // Safety check
        if (!draggedValueData) {
          setActiveId(null);
          setActiveData(null);
          removeDragStyles();
          return;
        }

        let updatedValue = { ...value };

        // Remove from source group if needed
        if (sourceGroupId) {
          const sourceGroup = value[sourceGroupId];
          updatedValue[sourceGroupId] = {
            ...sourceGroup,
            values: sourceGroup.values.filter(v => v.id !== draggedId)
          };
        }

        // Add to target group
        updatedValue[targetId] = {
          ...targetGroup,
          values: [...targetGroup.values, draggedValueData]
        };

        // Update state
        onChange(updatedValue);
        setValueLocations(prev => ({
          ...prev,
          [draggedId]: targetId
        }));
      }
    } catch (error) {
      console.error("Error during drag operation:", error);
    }

    // Clean up
    setActiveId(null);
    setActiveData(null);
    removeDragStyles();
  };

  // Get array options from nested constraints or fall back to legacy constraints
  // Apply parent/child relationship based on isParentKey
  const parentArray = isParentKey
    ? (keyConstraints.array || constraints.key_array || [])
    : (valueConstraints.array || constraints.value_array || []);

  const childArray = isParentKey
    ? (valueConstraints.array || constraints.value_array || [])
    : (keyConstraints.array || constraints.key_array || []);

  // Get parameter references from nested constraints or fall back to legacy
  const keyParam = keyConstraints.param || constraints.key_param;
  const valueParam = valueConstraints.param || constraints.value_param;

  // Get parameter values if they exist
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

  // Determine effective options based on parent/child relationship
  const effectiveParentOptions = isParentKey
    ? (parentArray.length > 0 ? parentArray : keyParamValues)
    : (parentArray.length > 0 ? parentArray : valueParamValues);

  const effectiveChildOptions = isParentKey
    ? (childArray.length > 0 ? childArray : valueParamValues)
    : (childArray.length > 0 ? childArray : keyParamValues);

  // Pack drag info for context
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
      createdValues={createdValues}
      setCreatedValues={setCreatedValues}
    >
      <MetadataManager>
        <EditingManager>
          <DebugManager>
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
                  <GroupsSection value={value} onChange={onChange} />
                  <AvailableValuesSection value={value} />
                </SimpleGrid>
              </Box>

              {/* Drag Overlay */}
              <DragOverlay
                dropAnimation={{
                  duration: 250,
                  easing: 'cubic-bezier(0.18, 0.67, 0.6, 1.22)',
                }}
                modifiers={[snapCenterToCursor]}
              >
                {activeId ? (
                  <ValueDisplay
                    value={activeData?.value || activeId}
                    type={activeData?.metadata?.type || (isParentKey ? valueType : keyType)}
                    isFromParam={activeData?.metadata?.isFromParam}
                    paramSource={activeData?.metadata?.paramSource}
                    isEditable={activeData?.metadata?.isEditable ?? isValueEditable}
                  />
                ) : null}
              </DragOverlay>

              {/* Drag cursor styles */}
              <style>{`
                body.dragging {
                  cursor: grabbing !important;
                }
                body.dragging * {
                  cursor: grabbing !important;
                }
              `}</style>
            </DndContext>
          </DebugManager>
        </EditingManager>
      </MetadataManager>
    </NestedMappingProvider>
  );
};

// Export the public API component
export const HierarchicalMapping: React.FC<NestedMappingProps> = (props) => {
  return <HierarchicalMappingImpl {...props} />;
};
