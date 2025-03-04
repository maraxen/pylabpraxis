import React, { createContext, useContext, useState, ReactNode, useRef, useEffect } from 'react';
import { ParameterConfig, GroupData, ValueData, ValueMetadata } from '../utils/parameterUtils';

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
  isParentKey: boolean;
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
  isParentKey: true,
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
  createValue,
  createGroup
}) => {
  const constraints = config?.constraints || {};
  const isParentKey = constraints?.parent === 'key';
  const valueType = constraints?.value_type || 'string';

  // Metadata state
  const [valueMetadataMap, setValueMetadataMap] = useState<Record<string, ValueMetadata>>({});

  // Share a ref to the input field for focus management
  const inputRef = useRef<HTMLInputElement>(null);

  // Get value metadata helper
  const getValueMetadata = (val: string | ValueData): ValueMetadata => {
    // If ValueData object is passed, extract the value
    const value = typeof val === 'object' && val !== null ? val.value : val;
    const stringValue = value !== null && value !== undefined ? String(value) : '';

    // Return existing metadata if available
    if (valueMetadataMap[stringValue]) {
      return valueMetadataMap[stringValue];
    }

    // Check if the value comes from parameters
    const keyParam = constraints?.key_param;
    const valueParam = constraints?.value_param;

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

    // Store the metadata for future use
    setValueMetadataMap(prev => ({ ...prev, [stringValue]: metadata }));

    return metadata;
  };

  // Fix the creatable flags to check both creatable and specific flags
  const creatable = !!constraints?.creatable;
  const creatableKey = creatable || !!constraints?.creatable_key;
  const creatableValue = creatable || !!constraints?.creatable_value;

  // Local state for creation mode
  const [creationMode, setCreationMode] = useState<string | null>(null);

  // Add additional child and parent options from the existing values and groups
  const localParentOptions = [...effectiveParentOptions];
  const localChildOptions = [...effectiveChildOptions];

  // Add existing group names to parent options if not already there
  if (value && typeof value === 'object') {
    Object.values(value).forEach(group => {
      if (group && group.name && !localParentOptions.includes(group.name)) {
        localParentOptions.push(group.name);
      }
    });

    // Add existing values to child options if not already there
    Object.values(value).forEach(group => {
      if (group && group.values && Array.isArray(group.values)) {
        group.values.forEach(valueData => {
          if (valueData && valueData.value !== undefined && !localChildOptions.includes(valueData.value)) {
            localChildOptions.push(valueData.value);
          }
        });
      }
    });
  }

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
  }, [dragInfo.isDragging]);

  // Start editing a value
  const startEditing = (id: string, currentValue: string, group: string | null) => {
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
  };

  // Update the value being edited
  const updateEditingValue = (newValue: string) => {
    setEditingState(prev => ({
      ...prev,
      value: newValue
    }));
  };

  // Cancel editing
  const cancelEditing = () => {
    setEditingState({
      id: null,
      value: '',
      group: null,
      originalValue: ''
    });
  };

  // Finish editing and apply changes
  const finishEditing = () => {
    const { id, value: newValue, group, originalValue } = editingState;

    // If no changes or no ID, just cancel
    if (!id) {
      cancelEditing();
      return;
    }

    // If no changes, just cancel
    if (newValue === originalValue) {
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

      // Update metadata
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

    // Reset editing state
    cancelEditing();
  };

  // Check if a specific item is currently being edited
  const isEditingItem = (id: string, group: string | null) => {
    return editingState.id === id && editingState.group === group;
  };

  return (
    <NestedMappingContext.Provider
      value={{
        config,
        parameters,
        value,
        onChange,
        effectiveChildOptions,
        effectiveParentOptions,
        localChildOptions,
        localParentOptions,
        isParentKey,
        valueType,
        creatableKey,
        creatableValue,
        creationMode,
        setCreationMode,
        createValue,
        createGroup,
        valueMetadataMap,
        setValueMetadataMap,
        getValueMetadata,
        dragInfo,
        // Editing functionality
        editingState,
        startEditing,
        updateEditingValue,
        finishEditing,
        cancelEditing,
        isEditingItem,
        inputRef,
      }}
    >
      {children}
    </NestedMappingContext.Provider>
  );
};

// Hook for using the context
export const useNestedMapping = () => useContext(NestedMappingContext);
