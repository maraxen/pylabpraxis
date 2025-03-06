import React, { createContext, useContext, useState, ReactNode, useRef, useEffect, useMemo, useCallback } from 'react';
import { ParameterConfig, GroupData, ValueData, ValueMetadata, NestedConstraint } from '../utils/parameterUtils';

// Editing state interface
interface EditingState {
  id: string | null;
  value: string;
  group: string | null;
  originalValue: string;
}

// Define the context type
interface NestedMappingContextType {
  // Configuration
  config: ParameterConfig;
  parameters?: Record<string, ParameterConfig>;

  // Values
  value: Record<string, GroupData>;
  onChange: (value: any) => void;

  // Options for groups and values
  effectiveChildOptions: any[];
  effectiveParentOptions: any[];
  localChildOptions: any[];
  localParentOptions: any[];

  // Type information
  valueType: string;

  // Creation flags
  creatableKey: boolean;
  creatableValue: boolean;

  // Creation mode
  creationMode: string | null;
  setCreationMode: (mode: string | null) => void;

  // Creation methods
  createValue: (value: any) => string;
  createGroup: (name: string) => string;

  // Metadata for values
  valueMetadataMap: Record<string, ValueMetadata>;
  setValueMetadataMap: (metadata: Record<string, ValueMetadata>) => void;
  getValueMetadata: (value: string | ValueData) => ValueMetadata;

  // Group editability check
  isEditable: (groupId: string) => boolean;

  // Drag and drop info
  dragInfo: {
    activeId: string | null;
    activeData: any;
    overDroppableId: string | null;
    isDragging: boolean;
  };

  // Editing functionality
  editingState: EditingState;
  startEditing: (id: string, value: string, group: string | null) => void;
  updateEditingValue: (value: string) => void;
  finishEditing: () => void;
  cancelEditing: () => void;
  isEditingItem: (id: string, group: string | null) => boolean;
  inputRef: React.RefObject<HTMLInputElement>;

  // Value limits
  getMaxTotalValues: () => number;
  getMaxValuesPerGroup: () => number;
  isGroupFull: (groupId: string) => boolean;
  hasReachedMaxValues: () => boolean;

  // Track created but unassigned values
  createdValues: Record<string, ValueData>;
  setCreatedValues: React.Dispatch<React.SetStateAction<Record<string, ValueData>>>;
}

// Create the context with default values
const NestedMappingContext = createContext<NestedMappingContextType>({
  config: { type: 'object' },
  value: {},
  onChange: () => { },
  effectiveChildOptions: [],
  effectiveParentOptions: [],
  localChildOptions: [],
  localParentOptions: [],
  valueType: 'string',
  creatableKey: false,
  creatableValue: false,
  creationMode: null,
  setCreationMode: () => { },
  createValue: () => '',
  createGroup: () => '',
  valueMetadataMap: {},
  setValueMetadataMap: () => { },
  getValueMetadata: () => ({ isFromParam: false, isEditable: true, type: 'string' }),
  isEditable: () => true,
  dragInfo: {
    activeId: null,
    activeData: null,
    overDroppableId: null,
    isDragging: false
  },
  // Default editing state
  editingState: {
    id: null,
    value: '',
    group: null,
    originalValue: ''
  },
  startEditing: () => { },
  updateEditingValue: () => { },
  finishEditing: () => { },
  cancelEditing: () => { },
  isEditingItem: () => false,
  inputRef: { current: null },
  // Value limits
  getMaxTotalValues: () => Infinity,
  getMaxValuesPerGroup: () => Infinity,
  isGroupFull: () => false,
  hasReachedMaxValues: () => false,
  // Track created but unassigned values
  createdValues: {},
  setCreatedValues: () => { },
});

// Provider component
interface NestedMappingProviderProps {
  children: ReactNode;
  config: ParameterConfig;
  parameters?: Record<string, ParameterConfig>;
  value: Record<string, GroupData>;
  onChange: (value: any) => void;
  effectiveChildOptions: any[];
  effectiveParentOptions: any[];
  dragInfo: {
    activeId: string | null;
    activeData: any;
    overDroppableId: string | null;
    isDragging: boolean;
  };
  createValue: (value: any) => string;
  createGroup: (name: string) => string;
  createdValues: Record<string, ValueData>;
  setCreatedValues: React.Dispatch<React.SetStateAction<Record<string, ValueData>>>;
}

export const NestedMappingProvider: React.FC<NestedMappingProviderProps> = ({
  children,
  config,
  parameters,
  value,
  onChange,
  effectiveChildOptions,
  effectiveParentOptions,
  dragInfo,
  createValue: createValueProp,
  createGroup: createGroupProp,
  createdValues,
  setCreatedValues
}) => {
  const constraints = config?.constraints || {};
  const keyConstraints = constraints.key_constraints || {};
  const valueConstraints = constraints.value_constraints || {};
  const valueType = valueConstraints?.type || 'string';

  // Metadata state
  const [valueMetadataMap, setValueMetadataMap] = useState<Record<string, ValueMetadata>>({});

  // Share a ref to the input field for focus management
  const inputRef = useRef<HTMLInputElement>(null);

  // Add this ref to track pending metadata updates
  const pendingMetadataUpdatesRef = useRef<Record<string, ValueMetadata>>({});

  // Apply pending metadata updates using useEffect
  useEffect(() => {
    const pendingUpdates = pendingMetadataUpdatesRef.current;
    if (Object.keys(pendingUpdates).length > 0) {
      setValueMetadataMap(prev => ({
        ...prev,
        ...pendingUpdates
      }));
      // Clear the pending updates
      pendingMetadataUpdatesRef.current = {};
    }
  });

  // Memoize functions to prevent unnecessary re-renders
  const getValueMetadata = useCallback((val: string | ValueData): ValueMetadata => {
    // If ValueData object is passed, extract the value
    const value = typeof val === 'object' && val !== null ? val.value : val;
    const stringValue = value !== null && value !== undefined ? String(value) : '';

    // Return existing metadata if available
    if (valueMetadataMap[stringValue]) {
      return valueMetadataMap[stringValue];
    }

    // Check if the value comes from parameters
    const keyParam = keyConstraints?.param;
    const valueParam = valueConstraints?.param;

    const isFromKeyParam = keyParam && parameters?.[keyParam]?.default &&
      (Array.isArray(parameters[keyParam].default)
        ? parameters[keyParam].default.some((v: any) => String(v) === stringValue)
        : String(parameters[keyParam].default) === stringValue);

    const isFromValueParam = valueParam && parameters?.[valueParam]?.default &&
      (Array.isArray(parameters[valueParam].default)
        ? parameters[valueParam].default.some((v: any) => String(v) === stringValue)
        : String(parameters[valueParam].default) === stringValue);

    let paramSource: string | undefined = undefined;
    if (isFromKeyParam && keyParam) {
      paramSource = keyParam;
    } else if (isFromValueParam && valueParam) {
      paramSource = valueParam;
    }

    // Create new metadata if not found
    const metadata: ValueMetadata = {
      isFromParam: isFromKeyParam || isFromValueParam,
      paramSource,
      isEditable: true, // Default to editable
      type: valueType
    };

    // Instead of updating state directly during render, store in pending updates
    pendingMetadataUpdatesRef.current[stringValue] = metadata;

    return metadata;
  }, [valueMetadataMap, constraints, parameters, valueType]);

  // Fix the creatable flags to check both creatable and specific flags
  const creatable = !!constraints?.creatable;
  const creatableKey = !!keyConstraints?.creatable || creatable;
  const creatableValue = !!valueConstraints?.creatable || creatable;

  // Local state for creation mode
  const [creationMode, setCreationMode] = useState<string | null>(null);

  // Memoize derived values
  const localParentOptions = useMemo(() => {
    const options = [...effectiveParentOptions];

    // Add values from key_param if specified
    if (keyConstraints?.param && parameters?.[keyConstraints.param]?.default) {
      const paramValues = parameters[keyConstraints.param].default;
      if (Array.isArray(paramValues)) {
        paramValues.forEach(val => {
          if (!options.includes(val)) {
            options.push(val);
          }
        });
      } else if (paramValues !== undefined && !options.includes(paramValues)) {
        options.push(paramValues);
      }
    }

    // Add existing group names to parent options if not already there
    if (value && typeof value === 'object') {
      Object.values(value).forEach(group => {
        if (group && group.name && !options.includes(group.name)) {
          options.push(group.name);
        }
      });
    }

    return options;
  }, [effectiveParentOptions, keyConstraints, parameters, value]);

  const localChildOptions = useMemo(() => {
    const options = [...effectiveChildOptions];

    // Add values from value_param if specified
    if (valueConstraints?.param && parameters?.[valueConstraints.param]?.default) {
      const paramValues = parameters[valueConstraints.param].default;
      if (Array.isArray(paramValues)) {
        paramValues.forEach(val => {
          if (!options.includes(val)) {
            options.push(val);
          }
        });
      } else if (paramValues !== undefined && !options.includes(paramValues)) {
        options.push(paramValues);
      }
    }

    // Add existing values to child options if not already there
    if (value && typeof value === 'object') {
      Object.values(value).forEach(group => {
        if (group && group.values && Array.isArray(group.values)) {
          group.values.forEach(valueData => {
            if (valueData && valueData.value !== undefined && !options.includes(valueData.value)) {
              options.push(valueData.value);
            }
          });
        }
      });
    }

    return options;
  }, [effectiveChildOptions, valueConstraints, parameters, value]);

  // Editing state
  const [editingState, setEditingState] = useState<EditingState>({
    id: null,
    value: '',
    group: null,
    originalValue: ''
  });

  // Prevent editing during dragging
  useEffect(() => {
    if (dragInfo.isDragging && editingState.id) {
      cancelEditing();
    }
  }, [dragInfo.isDragging, editingState.id]);

  // Memoize editing functions
  const startEditing = useCallback((id: string, currentValue: string, group: string | null) => {
    // Check if the value is editable
    const metadata = valueMetadataMap[id] || valueMetadataMap[currentValue];
    if (metadata && !metadata.isEditable) {
      return;
    }

    // Can't edit during dragging
    if (dragInfo.isDragging) {
      return;
    }

    setEditingState({
      id,
      value: currentValue,
      group,
      originalValue: currentValue
    });
  }, [valueMetadataMap, dragInfo.isDragging]);

  const updateEditingValue = useCallback((newValue: string) => {
    setEditingState(prev => ({
      ...prev,
      value: newValue
    }));
  }, []);

  const cancelEditing = useCallback(() => {
    setEditingState({
      id: null,
      value: '',
      group: null,
      originalValue: ''
    });
  }, []);

  const finishEditing = useCallback(() => {
    const { id, value: newValue, group, originalValue } = editingState;

    // If no changes or no ID, just cancel
    if (!id || newValue === originalValue) {
      cancelEditing();
      return;
    }

    // If editing a value in a group
    if (group && value[group]) {
      const groupData = value[group];
      const updatedValues = groupData.values.map((valueData: ValueData) => {
        if (valueData.id === id) {
          return {
            ...valueData,
            value: newValue
          };
        }
        return valueData;
      });

      // Update the group
      onChange({
        ...value,
        [group]: {
          ...groupData,
          values: updatedValues
        }
      });

      // Update metadata - retain the ID but update the value
      setValueMetadataMap(prev => {
        const metadata = { ...(prev[originalValue] || { type: valueType, isEditable: true, isFromParam: false }) };
        const newMap = { ...prev };

        // If value text changed, update the key in metadata map
        if (originalValue !== newValue) {
          delete newMap[originalValue];
        }

        newMap[newValue] = metadata;
        return newMap;
      });
    }
    // Handle editing available values
    else if (!group) {
      // Find if this is a created value that we're editing
      const createdValueEntry = Object.entries(createdValues).find(([_, valueData]) => valueData.id === id);

      if (createdValueEntry) {
        const [createdValueId, createdValueData] = createdValueEntry;

        // Update the created value in our state
        setCreatedValues(prev => {
          const updated = { ...prev };
          updated[createdValueId] = {
            ...createdValueData,
            value: newValue
          };
          return updated;
        });

        // Also update metadata
        setValueMetadataMap(prev => {
          const metadata = { ...(prev[originalValue] || { type: valueType, isEditable: true, isFromParam: false }) };
          const newMap = { ...prev };

          if (originalValue !== newValue) {
            delete newMap[originalValue];
          }

          newMap[newValue] = metadata;
          return newMap;
        });
      }
    }

    // Reset editing state
    cancelEditing();
  }, [editingState, value, onChange, valueType, cancelEditing, createdValues, setCreatedValues]);

  const isEditingItem = useCallback((id: string, group: string | null) => {
    return editingState.id === id && editingState.group === group;
  }, [editingState.id, editingState.group]);

  // Update isEditable function to check for editability flags in constraints
  const isEditable = useCallback((groupId: string): boolean => {
    // First check if the group exists and has explicit editability flag
    if (value && value[groupId]) {
      const group = value[groupId];
      // If explicitly set to false, respect that
      if (group.isEditable === false) return false;
      // If explicitly set to true, allow editing
      if (group.isEditable === true) return true;
    }

    // Check constraints for editability flags
    const editableByConstraint =
      !!constraints?.editable;

    return editableByConstraint;
  }, [value, constraints]);

  // Wrap the creation methods to ensure they work in the optimized context
  const createValue = useCallback((newVal: any): string => {
    try {
      console.log("Creating value in context:", newVal);
      return createValueProp(newVal);
    } catch (error) {
      console.error("Error in context while creating value:", error);
      return "";
    }
  }, [createValueProp]);

  const createGroup = useCallback((groupName: string): string => {
    try {
      console.log("Creating group in context:", groupName);
      return createGroupProp(groupName);
    } catch (error) {
      console.error("Error in context while creating group:", error);
      return "";
    }
  }, [createGroupProp]);

  // Fix the setCreationMode function to ensure proper updates
  const wrappedSetCreationMode = useCallback((mode: string | null) => {
    console.log("Setting creation mode:", mode);
    setCreationMode(mode);
  }, []);

  // Calculate the maximum total values based on constraints
  const getMaxTotalValues = useCallback((): number => {
    const keyArrayLen = constraints?.key_constraints?.array_len;
    const valueArrayLen = constraints?.value_constraints?.array_len;

    // If both are specified, multiply them to get total max values
    if (keyArrayLen && valueArrayLen) {
      return keyArrayLen * valueArrayLen;
    }

    // If only one is specified
    if (keyArrayLen) return keyArrayLen;
    if (valueArrayLen) return valueArrayLen;

    // Default: no limit
    return Infinity;
  }, [constraints]);

  // Calculate the maximum values per group
  const getMaxValuesPerGroup = useCallback((): number => {
    // Use value_array_len as the limit for values per key
    return constraints?.value_constraints?.array_len || Infinity;
  }, [constraints]);

  // Check if a group has reached its maximum values
  const isGroupFull = useCallback((groupId: string): boolean => {
    if (!value || !value[groupId]) return false;

    const maxPerGroup = getMaxValuesPerGroup();
    const currentCount = value[groupId].values?.length || 0;

    return currentCount >= maxPerGroup;
  }, [value, getMaxValuesPerGroup]);

  // Check if we've reached the total maximum values
  const hasReachedMaxValues = useCallback((): boolean => {
    const maxTotal = getMaxTotalValues();
    let currentTotal = 0;

    // Count all values across all groups
    Object.values(value || {}).forEach(group => {
      currentTotal += group.values?.length || 0;
    });

    return currentTotal >= maxTotal;
  }, [value, getMaxTotalValues]);

  // Memoize the context value to avoid unnecessary re-renders
  const contextValue = useMemo(() => ({
    config,
    parameters,
    value,
    onChange,
    effectiveChildOptions,
    effectiveParentOptions,
    localChildOptions,
    localParentOptions,
    valueType,
    creatableKey,
    creatableValue,
    creationMode,
    setCreationMode: wrappedSetCreationMode,
    createValue,
    createGroup,
    valueMetadataMap,
    setValueMetadataMap,
    getValueMetadata,
    isEditable,
    dragInfo,
    // Editing functionality
    editingState,
    startEditing,
    updateEditingValue,
    finishEditing,
    cancelEditing,
    isEditingItem,
    inputRef,
    // Value limits
    getMaxTotalValues,
    getMaxValuesPerGroup,
    isGroupFull,
    hasReachedMaxValues,
    // Track created but unassigned values
    createdValues,
    setCreatedValues,
  }), [
    config, parameters, value, onChange,
    effectiveChildOptions, effectiveParentOptions,
    localChildOptions, localParentOptions, valueType, creatableKey, creatableValue,
    creationMode, wrappedSetCreationMode, createValue, createGroup,
    valueMetadataMap, setValueMetadataMap, getValueMetadata, isEditable,
    dragInfo, editingState,
    startEditing, updateEditingValue, finishEditing, cancelEditing, isEditingItem,
    getMaxTotalValues, getMaxValuesPerGroup, isGroupFull, hasReachedMaxValues,
    createdValues, setCreatedValues
  ]);

  return (
    <NestedMappingContext.Provider value={contextValue}>
      {children}
    </NestedMappingContext.Provider>
  );
};

// Hook for using the context
export const useNestedMapping = () => useContext(NestedMappingContext);
