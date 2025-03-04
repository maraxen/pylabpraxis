import React, { useState, useRef, useCallback, useEffect } from 'react';
import { VStack, Box, IconButton, SimpleGrid, Heading, Badge, Text, useForceUpdate } from '@chakra-ui/react';
import { AutoComplete, AutoCompleteInput, AutoCompleteItem, AutoCompleteList, AutoCompleteCreatable } from "@choc-ui/chakra-autocomplete";
import { LuX, LuPlus } from "react-icons/lu";
import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  useDroppable,
  useDraggable,
  UniqueIdentifier,
  DragOverlay,
  defaultDropAnimation,
} from '@dnd-kit/core';
import {
  arrayMove,
  SortableContext,
  sortableKeyboardCoordinates,
  verticalListSortingStrategy,
  useSortable,
} from '@dnd-kit/sortable';
import { snapCenterToCursor } from '@dnd-kit/modifiers';
import { Button } from '@/components/ui/button';
import { CSS } from '@dnd-kit/utilities';
import { StringInput } from './inputs/StringInput';
import { NumberInput } from './inputs/NumericInput';
import { BooleanInput } from './inputs/BooleanInput';
import { ArrayInput } from './Lists';
import {
  ParameterConfig,
  ParameterConstraints,
  SubvariableConfig,
  SubvariablesData,
  HierarchicalMappingProps,
  DragState,
  SortableItemProps
} from './interfaces';
import { DraggableValue } from './subcomponents/draggableValue';
import { SortableItem } from './subcomponents/sortableItem';
import { ValueDisplay } from './subcomponents/valueDisplay';
import { DroppableGroup } from './subcomponents/droppableGroup';
import { SubvariableInput } from './inputs/SubvariableInput';

const NestedMapping: React.FC<HierarchicalMappingProps> = ({
  name,
  value,
  config,
  onChange,
  parameters,
}) => {
  // Use useForceUpdate hook to trigger re-renders
  const forceUpdate = useForceUpdate ? useForceUpdate() : () => { };

  const constraints = config?.constraints;
  const isParentKey = constraints?.parent === 'key';
  const creatable = !!constraints?.creatable;
  const creatableKey = creatable || !!(constraints?.key_param && !constraints?.key_array);
  const creatableValue = creatable || !!(constraints?.value_param && !constraints?.value_array);

  // Get parent and child options
  const parentOptions = isParentKey
    ? (constraints?.key_array || [])
    : (constraints?.value_array || []);

  const childOptions = isParentKey
    ? (constraints?.value_array || [])
    : (constraints?.key_array || []);

  // Track child values from referenced parameters
  const keyParam = constraints?.key_param;
  const valueParam = constraints?.value_param;

  // Fix: Properly access the parameter values with proper fallbacks
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

  // Fix: Get the actual options based on references with fallbacks for empty arrays
  const effectiveParentOptions = isParentKey
    ? (parentOptions.length > 0 ? parentOptions : keyParamValues)
    : (parentOptions.length > 0 ? parentOptions : valueParamValues);

  const effectiveChildOptions = isParentKey
    ? (childOptions.length > 0 ? childOptions : valueParamValues)
    : (childOptions.length > 0 ? childOptions : keyParamValues);

  const subvariables = constraints?.subvariables || {};
  const keyType = constraints?.key_type || 'string';
  const valueType = constraints?.value_type || 'string';

  // Fix: Improve state tracking for available options
  const [localChildOptions, setLocalChildOptions] = useState<string[]>([]);
  const [localParentOptions, setLocalParentOptions] = useState<string[]>([]);

  // Track editing state to prevent focus issues
  const [editingState, setEditingState] = useState<{
    id: string | null;
    value: string;
    group: string | null;
  }>({
    id: null,
    value: '',
    group: null
  });

  // Track location of all values (available or in which group)
  const [valueLocations, setValueLocations] = useState<Record<string, string | null>>({});

  // Fix: Improved initialization from all sources when parameters change
  useEffect(() => {
    // Process child options
    const processedChildOptions = new Set<string>();

    // Add from static arrays
    if (Array.isArray(effectiveChildOptions)) {
      effectiveChildOptions.forEach(opt =>
        processedChildOptions.add(String(opt))
      );
    }

    // Add from current value structure (captures any dynamic/created values)
    Object.entries(value || {}).forEach(([_, groupValues]) => {
      const values = Array.isArray(groupValues)
        ? groupValues
        : (groupValues as SubvariablesData)?.values || [];

      values.forEach(val => processedChildOptions.add(String(val)));
    });

    // Update local options state
    setLocalChildOptions(Array.from(processedChildOptions));

    // Initialize locations mapping
    const initialLocations: Record<string, string | null> = {};

    // First mark all as available
    processedChildOptions.forEach(val => {
      initialLocations[val] = null; // null = available
    });

    // Then update with actual locations from current value
    Object.entries(value || {}).forEach(([group, groupValues]) => {
      const values = Array.isArray(groupValues)
        ? groupValues
        : (groupValues as SubvariablesData)?.values || [];

      values.forEach(val => {
        initialLocations[val] = group;
      });
    });

    setValueLocations(initialLocations);

    // Process parent options similarly
    const processedParentOptions = new Set<string>();

    if (Array.isArray(effectiveParentOptions)) {
      effectiveParentOptions.forEach(opt =>
        processedParentOptions.add(String(opt))
      );
    }

    // Add existing groups from value
    Object.keys(value || {}).forEach(key =>
      processedParentOptions.add(key)
    );

    setLocalParentOptions(Array.from(processedParentOptions));

  }, [effectiveChildOptions, effectiveParentOptions, parameters, value]);

  // Standard state variables
  const [dragState, setDragState] = useState<DragState>({ active: null, over: null });
  const [isDragging, setIsDragging] = useState(false);
  const [activeId, setActiveId] = useState<string | null>(null);
  const [activeData, setActiveData] = useState<any>(null);
  const [creationMode, setCreationMode] = useState<'group' | 'value' | null>(null);

  // Add a state for tracking metadata of all values
  const [valueMetadataMap, setValueMetadataMap] = useState<Record<string, any>>({});

  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 5,
      }
    }),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );

  // Fix: Enhanced metadata tracking with proper read-only state
  useEffect(() => {
    const metadataMap: Record<string, any> = {};

    // Include all available options and handle read-only state
    if (Array.isArray(localChildOptions)) {
      localChildOptions.forEach((opt) => {
        const metadata = getValueMetadata(String(opt));
        metadataMap[String(opt)] = {
          ...metadata,
          type: valueType
        };
      });
    }

    // Also process options that might already be in the value
    Object.values(value || {}).forEach((groupData) => {
      const children = Array.isArray(groupData)
        ? groupData
        : (groupData as any)?.values || [];

      children.forEach((child: string) => {
        if (!metadataMap[child]) {
          const metadata = getValueMetadata(String(child));
          metadataMap[String(child)] = {
            ...metadata,
            type: valueType
          };
        }
      });
    });

    setValueMetadataMap(metadataMap);
  }, [localChildOptions, valueType, parameters, value]);

  // Fix drag start handler
  const handleDragStart = (event: any) => {
    // Cancel any ongoing editing
    setEditingState({
      id: null,
      value: '',
      group: null
    });

    setIsDragging(true);
    setDragState({ active: event.active.id, over: null });
    setActiveId(String(event.active.id));

    // Make sure we capture all the metadata from the dragged item
    const metadata = event.active.data.current?.metadata || {};
    setActiveData({
      ...metadata,
      type: metadata.type || valueType,
    });

    // Add class to control cursor
    document.body.classList.add('dragging');
  };

  const handleDragOver = (event: any) => {
    setDragState({
      active: dragState.active,
      over: event.over?.id || null
    });
  };

  // Enhance drag end to handle both adding to groups AND removing from groups
  const handleDragEnd = (event: any) => {
    setIsDragging(false);
    setDragState({ active: null, over: null });
    document.body.classList.remove('dragging');

    if (!event.active || !event.over) {
      setActiveId(null);
      setActiveData(null);
      return;
    }

    const { active, over } = event;
    const draggedId = String(active.id);
    const targetId = String(over.id);

    // Fix: Don't allow dragging read-only values
    const draggedMetadata = valueMetadataMap[draggedId];
    if (draggedMetadata && !draggedMetadata.isEditable) {
      setActiveId(null);
      setActiveData(null);
      return;
    }

    // Handle moving back to available values
    if (targetId === 'available-values') {
      // Get the current location of the dragged item
      const currentLocation = valueLocations[draggedId];

      // If it's not already available and is in a group
      if (currentLocation) {
        // Remove from the current group
        const currentGroup = value[currentLocation];
        if (!currentGroup) {
          setActiveId(null);
          setActiveData(null);
          return;
        }

        const currentValues = Array.isArray(currentGroup)
          ? currentGroup
          : (currentGroup as SubvariablesData).values;

        const newValues = currentValues.filter(v => v !== draggedId);

        // Update the group
        const hasSubvariables = Object.keys(subvariables).length > 0;
        const updatedGroup = hasSubvariables
          ? { ...(currentGroup as SubvariablesData), values: newValues }
          : newValues;

        // Update the value object
        onChange({
          ...value,
          [currentLocation]: updatedGroup
        });

        // Update location tracking
        setValueLocations(prev => ({
          ...prev,
          [draggedId]: null // null = available
        }));
      }
    }
    // Handle adding to a group
    else if (value[targetId] !== undefined) {
      const targetGroup = value[targetId];

      // Get current values of target group
      const currentValues = Array.isArray(targetGroup)
        ? targetGroup
        : (targetGroup as SubvariablesData)?.values || [];

      // Skip if already in this group
      if (currentValues.includes(draggedId)) {
        setActiveId(null);
        setActiveData(null);
        return;
      }

      // Get the current location of the dragged item
      const currentLocation = valueLocations[draggedId];

      // If it's in another group, remove it from that group first
      if (currentLocation && currentLocation !== targetId) {
        const sourceGroup = value[currentLocation];
        if (sourceGroup) {
          const sourceValues = Array.isArray(sourceGroup)
            ? sourceGroup
            : (sourceGroup as SubvariablesData).values;

          const newSourceValues = sourceValues.filter(v => v !== draggedId);

          // Update source group
          const hasSubvariables = Object.keys(subvariables).length > 0;
          const updatedSourceGroup = hasSubvariables
            ? { ...(sourceGroup as SubvariablesData), values: newSourceValues }
            : newSourceValues;

          // Create new values object with the updated source group
          const newValueObj = {
            ...value,
            [currentLocation]: updatedSourceGroup
          };

          // Now add to target group
          const newTargetValues = [...currentValues, draggedId];
          const updatedTargetGroup = hasSubvariables
            ? { ...(targetGroup as SubvariablesData), values: newTargetValues }
            : newTargetValues;

          // Update the full value object
          onChange({
            ...newValueObj,
            [targetId]: updatedTargetGroup
          });
        }
      }
      // If it's in available values, simply add it to the target group
      else if (!currentLocation || currentLocation === null) {
        // Add to target group
        const newValues = [...currentValues, draggedId];

        // Create the updated value object
        const hasSubvariables = Object.keys(subvariables).length > 0;
        const updatedGroup = hasSubvariables
          ? { ...(targetGroup as SubvariablesData), values: newValues }
          : newValues;

        // Call onChange with the updated value
        onChange({
          ...value,
          [targetId]: updatedGroup
        });
      }

      // Update location tracking
      setValueLocations(prev => ({
        ...prev,
        [draggedId]: targetId
      }));
    }

    setActiveId(null);
    setActiveData(null);
    forceUpdate();
  };

  // Fix focus issue during value editing
  const handleStartEditing = (id: string, currentValue: string, group: string | null) => {
    // Check if this item is editable
    const metadata = valueMetadataMap[id];
    if (metadata && !metadata.isEditable) {
      return;
    }

    setEditingState({
      id,
      value: currentValue,
      group
    });
  };

  const handleEditingChange = (newValue: string) => {
    setEditingState(prev => ({
      ...prev,
      value: newValue
    }));
  };

  const handleFinishEditing = () => {
    const { id, value: newValue, group } = editingState;

    if (id && newValue && newValue !== id) {
      // If editing a value in a group
      if (group) {
        const currentGroup = value[group];
        if (!currentGroup) return;

        const currentValues = Array.isArray(currentGroup)
          ? currentGroup
          : (currentGroup as SubvariablesData).values;

        const newValues = currentValues.map(v => v === id ? newValue : v);

        // Update the group
        const hasSubvariables = Object.keys(subvariables).length > 0;
        const updatedGroup = hasSubvariables
          ? { ...(currentGroup as SubvariablesData), values: newValues }
          : newValues;

        // Update the value object
        onChange({
          ...value,
          [group]: updatedGroup
        });

        // Update location tracking and metadata
        setValueLocations(prev => {
          const newLocations = { ...prev };
          delete newLocations[id];
          newLocations[newValue] = group;
          return newLocations;
        });

        setValueMetadataMap(prev => {
          const newMap = { ...prev };
          const metadata = prev[id] || { type: valueType };
          delete newMap[id];
          newMap[newValue] = metadata;
          return newMap;
        });

        // Update localChildOptions
        setLocalChildOptions(prev => {
          const newOptions = [...prev];
          const index = newOptions.indexOf(id);
          if (index >= 0) {
            newOptions[index] = newValue;
          } else {
            newOptions.push(newValue);
          }
          return newOptions;
        });
      }
      // If editing a value in available values
      else {
        // Update localChildOptions
        setLocalChildOptions(prev => {
          const newOptions = [...prev];
          const index = newOptions.indexOf(id);
          if (index >= 0) {
            newOptions[index] = newValue;
          } else {
            newOptions.push(newValue);
          }
          return newOptions;
        });

        // Update location tracking and metadata
        setValueLocations(prev => {
          const newLocations = { ...prev };
          delete newLocations[id];
          newLocations[newValue] = null;
          return newLocations;
        });

        setValueMetadataMap(prev => {
          const newMap = { ...prev };
          const metadata = prev[id] || { type: valueType };
          delete newMap[id];
          newMap[newValue] = metadata;
          return newMap;
        });
      }

      // Update real array too if possible
      if (Array.isArray(childOptions)) {
        const index = childOptions.indexOf(id);
        if (index >= 0) {
          childOptions[index] = newValue;
        }
      }

      // Update constraints to trigger UI update
      if (config.constraints) {
        if (isParentKey && Array.isArray(config.constraints.value_array)) {
          const index = config.constraints.value_array.indexOf(id);
          if (index >= 0) {
            config.constraints.value_array[index] = newValue;
          }
        } else if (!isParentKey && Array.isArray(config.constraints.key_array)) {
          const index = config.constraints.key_array.indexOf(id);
          if (index >= 0) {
            config.constraints.key_array[index] = newValue;
          }
        }
      }
    }

    // Reset editing state
    setEditingState({
      id: null,
      value: '',
      group: null
    });
  };

  // Improved value creation to track locations
  const handleValueCreation = (valueName: string) => {
    if (!valueName.trim()) return;

    // Check if value exists in any group or available values
    if (valueLocations[valueName]) return;

    // Add to localChildOptions
    if (!localChildOptions.includes(valueName)) {
      const updatedOptions = [...localChildOptions, valueName];
      setLocalChildOptions(updatedOptions);

      // Update real array too if possible
      if (Array.isArray(childOptions) && !childOptions.includes(valueName)) {
        childOptions.push(valueName);
      }

      // Update constraints to trigger UI update
      if (config.constraints) {
        if (isParentKey && Array.isArray(config.constraints.value_array)) {
          config.constraints.value_array = [...config.constraints.value_array, valueName];
        } else if (!isParentKey && Array.isArray(config.constraints.key_array)) {
          config.constraints.key_array = [...config.constraints.key_array, valueName];
        }
      }

      // Update metadata
      setValueMetadataMap(prev => ({
        ...prev,
        [valueName]: {
          type: valueType,
          isFromParam: false,
          isEditable: true
        }
      }));

      // Update location tracking
      setValueLocations(prev => ({
        ...prev,
        [valueName]: null // null = available values
      }));
    }

    setCreationMode(null);
    forceUpdate();
  };

  // Improved group creation to work with subvariables
  const handleCreateGroup = (newGroupName: string) => {
    if (!newGroupName?.trim() || value[newGroupName]) {
      return;
    }

    // Update localParentOptions
    if (!localParentOptions.includes(newGroupName)) {
      setLocalParentOptions([...localParentOptions, newGroupName]);

      // Update original array too
      if (Array.isArray(parentOptions) && !parentOptions.includes(newGroupName)) {
        parentOptions.push(newGroupName);
      }

      // Update constraints
      if (config.constraints) {
        if (isParentKey && Array.isArray(config.constraints.key_array)) {
          config.constraints.key_array = [...config.constraints.key_array, newGroupName];
        } else if (!isParentKey && Array.isArray(config.constraints.value_array)) {
          config.constraints.value_array = [...config.constraints.value_array, newGroupName];
        }
      }
    }

    // Create new group with proper subvariables
    const hasSubvariables = Object.keys(subvariables || {}).length > 0;
    const newGroup = hasSubvariables
      ? {
        values: [],
        ...Object.fromEntries(
          Object.entries(subvariables).map(([k, config]) => [k, (config as any).default])
        )
      }
      : [];

    onChange({
      ...value,
      [newGroupName]: newGroup
    });
  };

  // Fix: Enhanced metadata retrieval with better parameter checking
  const getValueMetadata = (value: string) => {
    const { key_param, value_param, creatable } = constraints || {};


    // Check if value is from a referenced parameter with proper type checking
    const isFromKeyParam = key_param && parameters?.[key_param]?.default &&
      (Array.isArray(parameters[key_param].default)
        ? parameters[key_param].default.some((v: any) => String(v) === String(value))
        : String(parameters[key_param].default) === String(value));

    const isFromValueParam = value_param && parameters?.[value_param]?.default &&
      (Array.isArray(parameters[value_param].default)
        ? parameters[value_param].default.some((v: any) => String(v) === String(value))
        : String(parameters[value_param].default) === String(value));

    let paramSource: string | undefined = undefined;
    if (isFromKeyParam && key_param) {
      paramSource = key_param;
    } else if (isFromValueParam && value_param) {
      paramSource = value_param;
    }

    const isEditable = !!creatable;

    return {
      isFromParam: isFromKeyParam || isFromValueParam,
      paramSource: paramSource,
      isEditable: isEditable
    };
  };

  // Fix: Helper to remove values with proper read-only validation
  const handleRemoveFromGroup = (parentVal: string, child: string) => {
    // Check if item is editable
    const metadata = valueMetadataMap[child];
    if (metadata && !metadata.isEditable) {
      return;
    }

    const currentData = value[parentVal];
    const currentValues = Array.isArray(currentData) ? currentData : (currentData as SubvariablesData).values;
    const newValues = currentValues.filter(c => c !== child);

    onChange({
      ...value,
      [parentVal]: Object.keys(subvariables).length > 0
        ? { ...(currentData as SubvariablesData), values: newValues }
        : newValues
    });

    // Update location tracking
    setValueLocations(prev => ({
      ...prev,
      [child]: null // null = available values
    }));

    forceUpdate();
  };

  // Dropzone for available values
  const { setNodeRef: setAvailableValuesRef } = useDroppable({
    id: 'available-values',
    data: {
      type: 'available-values',
      accepts: ['value']
    }
  });

  const renderSubvariableInput = (subVarName: string, subVarConfig: SubvariableConfig, parentVal: string) => {
    const currentData = value[parentVal] as SubvariablesData;
    const subVarValue = currentData[subVarName];

    const handleSubvariableChange = (newValue: any) => {
      const updatedValue = {
        ...value,
        [parentVal]: {
          ...currentData,
          [subVarName]: newValue,
        },
      };
      onChange(updatedValue);
    };

    return (
      <SubvariableInput
        name={subVarName}
        value={subVarValue}
        config={subVarConfig}
        onChange={handleSubvariableChange}
      />
    );
  };

  return (
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
          <Box borderWidth={1} borderRadius="md" p={4} display="flex" flexDirection="column" bg="brand.50" _dark={{ bg: "brand.900" }}>
            <Heading size="sm" mb={4} color="brand.500" _dark={{ color: "brand.200" }}>Groups</Heading>
            <VStack gap={2} flex="1" minHeight="200px" overflowY="auto">
              {Object.entries(value).map(([parentVal, parentData]) => {
                const children = Array.isArray(parentData)
                  ? parentData
                  : (parentData as SubvariablesData)?.values || [];

                return (
                  <Box
                    key={parentVal}
                    width="100%"
                    borderWidth={1}
                    borderRadius="md"
                    p={4}
                    bg="brand.100"
                    _dark={{ bg: "brand.800" }}
                    position="relative"
                    className="group"
                  >
                    <Box
                      display="flex"
                      justifyContent="space-between"
                      alignItems="center"
                      mb={2}
                    >
                      <Heading size="xs" color="brand.600" _dark={{ color: "brand.300" }}>{parentVal}</Heading>

                      <IconButton
                        aria-label="Remove Group"
                        size="xs"
                        onClick={() => {
                          // Update locations for all values in this group
                          children.forEach(child => {
                            setValueLocations(prev => ({
                              ...prev,
                              [child]: null // null = available values
                            }));
                          });

                          const newValue = { ...value };
                          delete newValue[parentVal];
                          onChange(newValue);
                        }}
                        opacity={0}
                        _groupHover={{ opacity: 1 }}
                        transition="opacity 0.2s"
                        position="absolute"
                        top={2}
                        right={2}
                      >
                        <LuX />
                      </IconButton>
                    </Box>
                    <Box p={2} display="flex" flexDirection="column" gap={2} minHeight="100px">
                      <DroppableGroup
                        id={parentVal}
                        isOver={dragState.over === parentVal}
                        isDragging={isDragging}
                      >
                        {children.map((child) => {
                          // Get metadata for this value
                          const metadata = valueMetadataMap[child] || {
                            type: valueType,
                            isFromParam: false,
                            isEditable: true
                          };

                          // Is this value currently being edited?
                          const isEditing = editingState.id === child && editingState.group === parentVal;

                          return (
                            <Box key={child} width="100%">
                              <SortableItem
                                id={child}
                                value={isEditing ? editingState.value : child}
                                keyValue={parentVal}
                                type={metadata.type || valueType}
                                isFromParam={metadata.isFromParam}
                                paramSource={metadata.paramSource}
                                isEditable={metadata.isEditable}
                                isEditing={isEditing}
                                onFocus={() => {
                                  if (metadata.isEditable) {
                                    handleStartEditing(child, child, parentVal);
                                  }
                                }}
                                onValueChange={(newValue: any) => {
                                  handleEditingChange(newValue);
                                }}
                                onBlur={handleFinishEditing}
                                onRemove={() => handleRemoveFromGroup(parentVal, child)}
                              />
                            </Box>
                          );
                        })}
                      </DroppableGroup>

                      {/* Fix: Improved subvariables rendering */}
                      {!Array.isArray(parentData) && Object.entries(subvariables).length > 0 && (
                        <Box mt={4} p={3} borderWidth="1px" borderRadius="md" bg="gray.50" _dark={{ bg: "gray.700" }}>
                          <Heading size="xs" mb={3} color="brand.500">Subvariables</Heading>
                          <VStack gap={3} align="stretch">
                            {Object.entries(subvariables).map(([subVarName, subVarConfig]) => {
                              const currentData = value[parentVal] as SubvariablesData;
                              const subVarValue = currentData[subVarName];
                              return (
                                <Box key={subVarName}>
                                  <Text fontSize="sm" fontWeight="medium" mb={1}>{subVarName}</Text>
                                  {renderSubvariableInput(subVarName, subVarConfig as SubvariableConfig, parentVal)}
                                </Box>
                              );
                            })}
                          </VStack>
                        </Box>
                      )}
                    </Box>
                  </Box>
                );
              })}

              {/* No groups placeholder */}
              {Object.keys(value).length === 0 && (
                <Box
                  width="100%"
                  height="100px"
                  borderWidth={1}
                  borderStyle="dashed"
                  borderRadius="md"
                  display="flex"
                  alignItems="center"
                  justifyContent="center"
                >
                  <Text color="brand.500" _dark={{ color: "brand.300" }}>No groups created yet</Text>
                </Box>
              )}
            </VStack>

            {/* Group creation with AutoComplete */}
            <Box mt={4}>
              {creationMode !== 'group' ? (
                <Button
                  onClick={() => setCreationMode('group')}
                  disabled={!creatableKey}
                  _disabled={{ opacity: 0.5, cursor: 'not-allowed' }}
                >
                  <LuPlus /> Add Group
                </Button>
              ) : (
                <Box width="100%" borderWidth={1} borderRadius="md" p={4} bg="white" _dark={{ bg: "gray.700" }}>
                  <AutoComplete
                    openOnFocus
                    suggestWhenEmpty
                    creatable={creatableKey}
                    onSelectOption={(item) => {
                      if (!item?.item?.value) return;
                      const groupName = item.item.value.trim();
                      if (!groupName || value[groupName]) return;
                      handleCreateGroup(groupName);
                      setCreationMode(null);
                    }}
                  >
                    <AutoCompleteInput
                      placeholder="Enter group name..."
                      autoFocus
                      onBlur={() => setTimeout(() => setCreationMode(null), 200)}
                    />
                    <AutoCompleteList>
                      {localParentOptions.length > 0 ? (
                        localParentOptions
                          .filter(opt => !value[opt])
                          .map((opt) => (
                            <AutoCompleteItem key={opt} value={opt}>
                              {opt}
                            </AutoCompleteItem>
                          ))
                      ) : null}
                      {creatableKey && (
                        <AutoCompleteCreatable>
                          {({ value }) => `Create group "${value}"`}
                        </AutoCompleteCreatable>
                      )}
                    </AutoCompleteList>
                  </AutoComplete>
                  <Button
                    size="sm"
                    mt={2}
                    visual="outline"
                    onClick={() => setCreationMode(null)}
                  >
                    Cancel
                  </Button>
                </Box>
              )}
            </Box>
          </Box>

          {/* Available Values Section */}
          <Box borderWidth={1} borderRadius="md" p={4} display="flex" flexDirection="column" bg="brand.50" _dark={{ bg: "brand.900" }}>
            <Heading size="sm" mb={4} color="brand.500" _dark={{ color: "brand.200" }}>Available Values</Heading>
            <Box flex="1" overflowY="auto" minHeight="200px">
              <SortableContext items={localChildOptions} strategy={verticalListSortingStrategy}>
                <VStack ref={setAvailableValuesRef} align="stretch" gap={2}>
                  {/* Fix: Use localChildOptions for rendering */}
                  {localChildOptions
                    .filter((opt) =>
                      !Object.values(value || {}).some((groupValues: any) => {
                        if (!groupValues) return false;
                        const values = Array.isArray(groupValues)
                          ? groupValues
                          : (groupValues.values || []);
                        return Array.isArray(values) && values.includes(String(opt));
                      })
                    )
                    .map((opt) => {
                      // Use cached metadata
                      const metadata = valueMetadataMap[String(opt)] || getValueMetadata(String(opt));

                      // Is this value currently being edited?
                      const isEditing = editingState.id === String(opt) && editingState.group === null;

                      return (
                        <DraggableValue
                          key={opt}
                          id={String(opt)}
                          value={isEditing ? editingState.value : String(opt)}
                          type={metadata.type || valueType}
                          isFromParam={metadata.isFromParam}
                          paramSource={metadata.paramSource}
                          isEditable={metadata.isEditable}
                          isEditing={isEditing}
                          onFocus={() => {
                            if (metadata.isEditable) {
                              handleStartEditing(String(opt), String(opt), null);
                            }
                          }}
                          onValueChange={(newValue: any) => {
                            handleEditingChange(newValue);
                          }}
                          onBlur={handleFinishEditing}
                        />
                      );
                    })}
                </VStack>
              </SortableContext>
            </Box>

            {/* Value creation with fixed AutoComplete */}
            <Box mt={4}>
              {creationMode !== 'value' ? (
                <Button
                  onClick={() => setCreationMode('value')}
                  disabled={!creatableValue}
                  _disabled={{ opacity: 0.5, cursor: 'not-allowed' }}
                >
                  <LuPlus /> Add Value
                </Button>
              ) : (
                <Box width="100%" borderWidth={1} borderRadius="md" p={4} bg="white" _dark={{ bg: "gray.700" }}>
                  <AutoComplete
                    openOnFocus
                    suggestWhenEmpty
                    creatable={creatableValue}
                    onSelectOption={(item) => {
                      if (!item?.item?.value) return;
                      handleValueCreation(item.item.value);
                    }}
                  >
                    <AutoCompleteInput
                      placeholder="Enter value name..."
                      autoFocus
                      onBlur={() => setTimeout(() => setCreationMode(null), 200)}
                    />
                    <AutoCompleteList>
                      {localChildOptions
                        .filter(opt =>
                          !Object.values(value || {}).some((groupValues: any) => {
                            if (!groupValues) return false;
                            const values = Array.isArray(groupValues)
                              ? groupValues
                              : (groupValues.values || []);
                            return values?.includes(opt);
                          })
                        )
                        .map((opt) => (
                          <AutoCompleteItem key={opt} value={opt}>
                            {opt}
                          </AutoCompleteItem>
                        ))}
                      {creatableValue && (
                        <AutoCompleteCreatable>
                          {({ value }) => `Create value "${value}"`
                          }
                        </AutoCompleteCreatable>
                      )}
                    </AutoCompleteList>
                  </AutoComplete>
                  <Button
                    size="sm"
                    mt={2}
                    visual="outline"
                    onClick={() => setCreationMode(null)}
                  >
                    Cancel
                  </Button>
                </Box>
              )}
            </Box>
          </Box>
        </SimpleGrid>
      </Box>

      {/* Fix: Improved drag overlay */}
      <DragOverlay
        dropAnimation={{
          duration: 200,
          easing: 'cubic-bezier(0.18, 0.67, 0.6, 1.22)',
        }}
        modifiers={[snapCenterToCursor]}
      >
        {activeId ? (
          <ValueDisplay
            value={activeId}
            type={activeData?.type || valueType}
            isFromParam={activeData?.isFromParam}
            paramSource={activeData?.paramSource}
            isEditable={activeData?.isEditable}
          />
        ) : null}
      </DragOverlay>

      {/* Add global styles for better drag handling */}
      <style>{`
        body.dragging {
          cursor: grabbing !important;
        }
        body.dragging * {
          cursor: grabbing !important;
        }
      `}</style>

    </DndContext >

  );
};

export const HierarchicalMapping: React.FC<HierarchicalMappingProps> = ({
  name,
  value,
  config,
  onChange,
  parameters,
}) => {
  return (
    <NestedMapping
      name={name}
      value={value}
      config={config}
      onChange={onChange}
      parameters={parameters}
    />
  );
};
