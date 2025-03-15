import React, { createContext, useContext, useState, ReactNode, useRef, useEffect, useMemo, useCallback } from 'react';
import {
  ParameterConfig,
  ValueMetadata,
  ValueData,
  GroupData,
  BaseValueProps
} from '@/shared/types/protocol';

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
  getMaxTotalValues: () => Infinity,
  getMaxValuesPerGroup: () => Infinity,
  isGroupFull: () => false,
  hasReachedMaxValues: () => false,
  createdValues: {},
  setCreatedValues: () => { },
});

// Provider props interface
export interface NestedMappingProviderProps {
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
  valueType?: string;
}

// Provider component
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
  // Extract constraints from config
  const constraints = config?.constraints || {};
  const keyConstraints = constraints.key_constraints || {};
  const valueConstraints = constraints.value_constraints || {};
  const valueType = valueConstraints?.type || 'string';

  // State for metadata tracking
  const [valueMetadataMap, setValueMetadataMap] = useState<Record<string, ValueMetadata>>({});
  const pendingMetadataUpdatesRef = useRef<Record<string, ValueMetadata>>({});

  // Input reference for focus management
  const inputRef = useRef<HTMLInputElement>(null);

  // Creation mode state
  const [creationMode, setCreationMode] = useState<string | null>(null);

  // Editing state
  const [editingState, setEditingState] = useState<EditingState>({
    id: null,
    value: '',
    group: null,
    originalValue: ''
  });

  // Helper refs
  const finishEditingInProgressRef = useRef(false);

  // Apply pending metadata updates
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
  }, []);

  // Cancel editing when dragging starts
  useEffect(() => {
    if (dragInfo.isDragging && editingState.id) {
      cancelEditing();
    }
  }, [dragInfo.isDragging, editingState.id]);

  // Get value metadata with proper typing and parameter awareness
  const getValueMetadata = useCallback((val: string | ValueData): ValueMetadata => {
    // Extract value and flags from input
    const isValueDataObject = typeof val === 'object' && val !== null;
    const value = isValueDataObject ? val.value : val;
    const explicitIsEditable = isValueDataObject ? val.isEditable : undefined;
    const explicitIsFromParam = isValueDataObject ? val.isFromParam : undefined;
    const explicitParamSource = isValueDataObject ? val.paramSource : undefined;
    const stringValue = value !== null && value !== undefined ? String(value) : '';

    // Return existing metadata if available and we don't have explicit flags that differ
    if (valueMetadataMap[stringValue] && explicitIsEditable === undefined) {
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

    let paramSource: string | undefined = explicitParamSource;
    if (!paramSource) {
      if (isFromKeyParam && keyParam) {
        paramSource = keyParam;
      } else if (isFromValueParam && valueParam) {
        paramSource = valueParam;
      }
    }

    // Determine if value is from a parameter
    const isFromParam = explicitIsFromParam !== undefined
      ? explicitIsFromParam
      : (isFromKeyParam || isFromValueParam);

    // Determine editability with proper nested constraint handling
    // Get direct creatable flags from different levels in the constraint hierarchy
    const valueCreatable = !!valueConstraints?.creatable;
    const globalCreatable = !!constraints?.creatable;

    // Get direct editable flags from different levels
    const valueEditable = valueConstraints?.editable !== undefined ? !!valueConstraints.editable : true;
    const globalEditable = constraints?.editable !== undefined ? !!constraints.editable : true;

    // Determine final isEditable flag with proper precedence:
    // 1. Explicit value takes highest precedence
    // 2. Parameter values are never editable
    // 3. Creatable flag makes values editable
    // 4. Otherwise use explicit editable flags from constraints
    const isEditable =
      explicitIsEditable !== undefined ? explicitIsEditable :
        isFromParam ? false :
          valueCreatable || globalCreatable ? true :
            valueEditable && globalEditable; // Both must be true (or undefined/default)

    // Create new metadata
    const metadata: ValueMetadata = {
      isFromParam,
      paramSource,
      isEditable,
      type: valueType
    };

    // Store in pending updates if this is a string value (not an object)
    if (!isValueDataObject) {
      pendingMetadataUpdatesRef.current[stringValue] = metadata;
    }

    return metadata;
  }, [valueMetadataMap, keyConstraints, valueConstraints, constraints, parameters, valueType]);

  // Determine creatable flags with clearer logic
  const creatable = !!constraints?.creatable;
  const creatableKey = !!keyConstraints?.creatable || creatable;
  const creatableValue = !!valueConstraints?.creatable || creatable;

  // Compute derived options for parents (groups)
  const localParentOptions = useMemo(() => {
    const options = [...effectiveParentOptions];

    // Add values from key_param if specified
    if (keyConstraints?.param && parameters?.[keyConstraints.param]?.default) {
      const paramValues = parameters[keyConstraints.param]?.default;
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

  // Compute derived options for children (values)
  const localChildOptions = useMemo(() => {
    const options = [...effectiveChildOptions];

    // Add values from value_param if specified
    if (valueConstraints?.param && parameters?.[valueConstraints.param]?.default) {
      const paramValues = parameters[valueConstraints.param]?.default;
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

  // Value type conversion helper
  const parseValue = useCallback((val: any, type: string): any => {
    if (val === null || val === undefined) return val;
    const normalizedType = type?.toLowerCase();
    switch (normalizedType) {
      case 'boolean':
      case 'bool':
        return typeof val === 'boolean' ? val : String(val).toLowerCase() === 'true';
      case 'number':
      case 'int':
      case 'integer':
      case 'float':
      case 'double': {
        const parsed = Number(val);
        return isNaN(parsed) ? 0 : parsed;
      }
      case 'string':
      case 'str':
      default:
        return String(val);
    }
  }, []);

  // Editing functions
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
    // Prevent concurrent editing operations
    if (finishEditingInProgressRef.current) {
      console.log("finishEditing already in progress, skipping duplicate call.");
      return;
    }

    finishEditingInProgressRef.current = true;
    const { id, value: newValue, group, originalValue } = editingState;

    console.log(`finishEditing called for id=${id} in group=${group} with newValue="${newValue}" (original: "${originalValue}")`);

    if (!id) {
      cancelEditing();
      finishEditingInProgressRef.current = false;
      return;
    }

    const parsedNew = parseValue(newValue, valueType);
    const parsedOriginal = parseValue(originalValue, valueType);

    if (parsedNew === parsedOriginal) {
      console.log("No change detected after parsing. Aborting update.");
      cancelEditing();
      finishEditingInProgressRef.current = false;
      return;
    }

    try {
      if (group && value[group]) {
        // Update value in group
        const groupData = value[group];
        const existingValueData = groupData.values.find((v: ValueData) => v.id === id);

        if (!existingValueData) {
          console.log("Value not found in group, aborting update");
          cancelEditing();
          finishEditingInProgressRef.current = false;
          return;
        }

        // Check if another value with the same content already exists in this group
        const valueAlreadyExists = groupData.values.some(v =>
          v.id !== id && // Not the same item
          String(v.value) === String(parsedNew) // Same value content
        );

        if (valueAlreadyExists) {
          console.log(`Value "${parsedNew}" already exists in this group, aborting update`);
          cancelEditing();
          finishEditingInProgressRef.current = false;
          return;
        }

        // Update the value in the group
        const updatedValues = groupData.values.map((valueData: ValueData) => {
          if (valueData.id === id) {
            return { ...valueData, value: parsedNew };
          }
          return valueData;
        });

        // Create updated mapping
        const updatedMapping = {
          ...value,
          [group]: { ...groupData, values: updatedValues }
        };

        // Update the Redux store
        onChange(updatedMapping);

        // Update metadata map to include the new value while preserving metadata
        setValueMetadataMap(prev => {
          const newMap = { ...prev };
          // Copy metadata from original to new value
          if (prev[originalValue]) {
            newMap[parsedNew] = { ...prev[originalValue] };
            // Keep original metadata for now (may be used elsewhere)
          }
          return newMap;
        });

      } else if (!group) {
        // Update value in available values section
        if (createdValues[id]) {
          // Check if another value with the same content already exists
          const valueAlreadyExists = Object.entries(createdValues).some(([valueId, data]) =>
            valueId !== id && // Not the same item
            String(data.value) === String(parsedNew) // Same value content
          );

          if (valueAlreadyExists) {
            console.log(`Value "${parsedNew}" already exists in available values, aborting update`);
            cancelEditing();
            finishEditingInProgressRef.current = false;
            return;
          }

          // Preserve ALL existing properties!
          const updatedCreatedValues = { ...createdValues };
          updatedCreatedValues[id] = {
            ...updatedCreatedValues[id],
            value: parsedNew
          };

          setCreatedValues(updatedCreatedValues);

          // Update metadata map to include the new value
          setValueMetadataMap(prev => {
            const newMap = { ...prev };
            // Copy metadata from original to new value
            if (prev[originalValue]) {
              newMap[parsedNew] = { ...prev[originalValue] };
            }
            return newMap;
          });

          console.log("Updated created value for", id);
        } else {
          console.log("No existing created value found for", id);
        }
      }

    } catch (err) {
      console.error("Error during finishEditing:", err);
    } finally {
      cancelEditing();
      finishEditingInProgressRef.current = false;
    }
  }, [editingState, value, onChange, valueType, cancelEditing, createdValues, setCreatedValues, parseValue]);

  const isEditingItem = useCallback((id: string, group: string | null) => {
    return editingState.id === id && editingState.group === group;
  }, [editingState.id, editingState.group]);

  // Group editability check
  const isEditable = useCallback((groupId: string): boolean => {
    // First check for explicit flags on the group
    if (value && value[groupId]) {
      const group = value[groupId];
      if (group.isEditable === false) return false;
      if (group.isEditable === true) return true;
    }

    // Then check if keys are creatable (makes groups editable)
    const creatableKey = keyConstraints.creatable || constraints.creatable;

    // Default to constraints-based editability
    return creatableKey ? true : (constraints?.editable !== false);
  }, [value, keyConstraints, constraints]);

  // Wrapper for creation methods
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

  // Wrapped setCreationMode for proper logging
  const wrappedSetCreationMode = useCallback((mode: string | null) => {
    console.log("Setting creation mode:", mode);
    setCreationMode(mode);
  }, []);

  // Value limit calculations
  const getMaxTotalValues = useCallback((): number => {
    const keyArrayLen = keyConstraints?.array_len;
    const valueArrayLen = valueConstraints?.array_len;

    // If both are specified, multiply them to get total max values
    if (keyArrayLen && valueArrayLen) {
      return keyArrayLen * valueArrayLen;
    }

    // If only one is specified
    if (keyArrayLen) return keyArrayLen;
    if (valueArrayLen) return valueArrayLen;

    // Default: no limit
    return Infinity;
  }, [keyConstraints, valueConstraints]);

  const getMaxValuesPerGroup = useCallback((): number => {
    // Use value_array_len as the limit for values per key
    return valueConstraints?.array_len || Infinity;
  }, [valueConstraints]);

  const isGroupFull = useCallback((groupId: string): boolean => {
    if (!value || !value[groupId]) return false;
    const maxPerGroup = getMaxValuesPerGroup();
    const currentCount = value[groupId].values?.length || 0;
    return currentCount >= maxPerGroup;
  }, [value, getMaxValuesPerGroup]);

  const hasReachedMaxValues = useCallback((): boolean => {
    const maxTotal = getMaxTotalValues();
    let currentTotal = 0;

    // Count all values across all groups
    Object.values(value || {}).forEach(group => {
      currentTotal += group.values?.length || 0;
    });

    return currentTotal >= maxTotal;
  }, [value, getMaxTotalValues]);

  // Create the context value with all required properties
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