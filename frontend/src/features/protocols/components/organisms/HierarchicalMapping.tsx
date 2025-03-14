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

type HierarchicalMappingProps = {
  name: string;
  value: any;
  config: any; // ParameterConfig with optional methods isEditable/getEditable and defaultValues
  onChange: (newValue: any) => void;
  parameters?: Record<string, ParameterConfig>;
};

/**
 * HierarchicalMapping component that renders a mapping interface with groups and values
 * This version only supports the new nested constraint structure (key_constraints/value_constraints)
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

  // Get nested constraints
  const keyConstraints = constraints.key_constraints || {};
  const valueConstraints = constraints.value_constraints || {};

  // We're removing the parent property and using a simpler approach:
  // Just assume keys are in groups and values go in groups
  // We can infer relationships from the structure

  // Extract type information directly from nested constraints
  const keyType = keyConstraints.type || 'string';
  const valueType = valueConstraints.type || 'string';

  // Extract editability flags from nested constraints
  const isKeyEditable = !!keyConstraints.editable || !!constraints.editable;
  const isValueEditable = !!valueConstraints.editable || !!constraints.editable;

  // Extract creatability flags from nested constraints
  const creatable = !!constraints.creatable;
  const creatableKey = !!keyConstraints.creatable || creatable;
  const creatableValue = !!valueConstraints.creatable || creatable;

  // Configure sensors for drag and drop
  const sensors = useDndSensors();

  // UI and drag state
  const [activeId, setActiveId] = useState<string | null>(null);
  const [activeData, setActiveData] = useState<any>(null);
  const [overDroppableId, setOverDroppableId] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [valueLocations, setValueLocations] = useState<Record<string, string | null>>({});
  const [createdValues, setCreatedValues] = useState<Record<string, ValueData>>({});

  // Initialize mapping with each node having an _editable flag from config if provided.
  const [mapping, setMapping] = React.useState(() => {
    // Deep-clone function that also sets _editable flags
    const cloneMapping = (obj: any): any => {
      if (typeof obj !== 'object' || obj === null) return obj;
      // Force newObj to be a Record<string, any>
      const newObj = {} as Record<string, any>;
      Object.keys(obj).forEach((key: string) => {
        const defaultEditable = config?.constraints?.editable !== false;
        if (typeof obj[key] === 'object' && obj[key] !== null) {
          newObj[key] = {
            ...cloneMapping(obj[key]),
            _editable: ((config as any).isEditable && typeof (config as any).isEditable === 'function'
              ? (config as any).isEditable(key)
              : defaultEditable)
          };
        } else {
          newObj[key] = {
            value: obj[key],
            _editable: ((config as any).isEditable && typeof (config as any).isEditable === 'function'
              ? (config as any).isEditable(key)
              : defaultEditable)
          };
        }
      });
      return newObj;
    };
    return cloneMapping(value || {});
  });

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
          isEditable: isKeyEditable
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
              type: valueType,
              isEditable: isValueEditable
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
        type: valueType, // Simplified - always use valueType for values
        isEditable: isValueEditable
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
        isEditable: creatableKey ? true : isKeyEditable  // Force editable if creatableKey is true
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

        // Find the value being moved to preserve its properties
        const draggedValueData = sourceGroup.values.find(v => v.id === draggedId);
        if (!draggedValueData) {
          setActiveId(null);
          setActiveData(null);
          removeDragStyles();
          return;
        }

        // Update createdValues to include this value for the available section
        setCreatedValues(prev => ({
          ...prev,
          [draggedId]: draggedValueData
        }));

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
          // From available values - use existing data in createdValues to preserve properties
          draggedValueData = createdValues[draggedId];

          // If not in createdValues, create from active data but preserve metadata
          if (!draggedValueData) {
            const draggedValue = active.data.current?.value;
            const metadata = active.data.current?.metadata || {};

            if (draggedValue !== undefined) {
              draggedValueData = {
                id: draggedId,
                value: draggedValue,
                type: metadata.type || valueType,
                isEditable: metadata.isEditable !== undefined ? metadata.isEditable : isValueEditable
              };
            }
          }
        } else {
          // From another group - find original value to preserve properties
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
        } else {
          // If from available values, remove from createdValues
          setCreatedValues(prev => {
            const { [draggedId]: _, ...rest } = prev;
            return rest;
          });
        }

        // Add to target group - preserve all original properties
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

  // Get array options directly from nested constraints - simplified
  const keyArray = keyConstraints.array || [];
  const valueArray = valueConstraints.array || [];

  // Get parameter references from nested constraints
  const keyParam = keyConstraints.param;
  const valueParam = valueConstraints.param;

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

  // Determine effective options based on structure
  const effectiveParentOptions = keyArray.length > 0 ? keyArray : keyParamValues;
  const effectiveChildOptions = valueArray.length > 0 ? valueArray : valueParamValues;

  // Pack drag info for context
  const dragInfo = {
    activeId,
    activeData,
    overDroppableId,
    isDragging
  };

  // Update a specific key’s value without affecting its _editable state.
  const updateValueAtKey = (key: string, newVal: any) => {
    setMapping((prev: Record<string, any>) => {
      const newMapping = { ...prev, [key]: { ...prev[key], value: newVal } };
      onChange(newMapping);
      return newMapping;
    });
  };

  // Fix drop handling to preserve dropped item’s _editable state.
  const handleDrop = (droppedItem: any, targetKey: string) => {
    setMapping((prev: Record<string, any>) => {
      const newMapping = { ...prev };
      if (!newMapping[targetKey])
        newMapping[targetKey] = { id: targetKey, name: targetKey, values: [], isEditable: true };
      // Determine if target group is editable
      const targetEditable = newMapping[targetKey].isEditable !== false;
      console.log(`Dropping value into group "${targetKey}" (editable: ${targetEditable}). Dropped item _editable: ${droppedItem._editable}`);
      newMapping[targetKey] = {
        ...newMapping[targetKey],
        ...droppedItem,
        // Force dropped values to be editable if the group is editable
        _editable: targetEditable ? true : (droppedItem._editable !== undefined ? droppedItem._editable : false)
      };
      onChange(newMapping);
      return newMapping;
    });
  };

  // Helper to get current value; if missing, uses config.defaultValues.
  const getKeyValue = (key: string) => {
    return mapping[key]?.name ?? (config?.default ? config.default[key] : '');
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
                    type={activeData?.metadata?.type || valueType} // Simplified
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
export const HierarchicalMapping: React.FC<HierarchicalMappingProps> = (props) => {
  return <HierarchicalMappingImpl {...props} />;
};
