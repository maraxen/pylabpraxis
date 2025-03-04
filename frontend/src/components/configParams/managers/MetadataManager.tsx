import React, { useEffect, useCallback } from 'react';
import { useNestedMapping } from '../contexts/nestedMappingContext';
import { ValueMetadata } from '../utils/parameterUtils';

interface MetadataManagerProps {
  children: React.ReactNode;
}

/**
 * MetadataManager handles the metadata for all values in the hierarchical mapping,
 * including tracking sources, editability, and types.
 */
export const MetadataManager: React.FC<MetadataManagerProps> = ({ children }) => {
  const {
    localChildOptions,
    valueMetadataMap,
    setValueMetadataMap,
    getValueMetadata
  } = useNestedMapping();

  // Initialize or update metadata when values change
  useEffect(() => {
    const updateMetadata = () => {
      const updatedMetadata: Record<string, ValueMetadata> = { ...valueMetadataMap };

      // Update metadata for all available options
      localChildOptions.forEach((value) => {
        const stringValue = String(value);
        if (!updatedMetadata[stringValue]) {
          updatedMetadata[stringValue] = getValueMetadata(stringValue);
        }
      });

      // Remove metadata for options that no longer exist
      Object.keys(updatedMetadata).forEach((key) => {
        if (!localChildOptions.includes(key) && !localChildOptions.some(item => String(item) === key)) {
          delete updatedMetadata[key];
        }
      });

      setValueMetadataMap(updatedMetadata);
    };

    updateMetadata();
  }, [localChildOptions]);

  return <>{children}</>;
};

// Custom hook for accessing value metadata
export const useValueMetadata = () => {
  const { valueMetadataMap, getValueMetadata } = useNestedMapping();

  // Get metadata for a specific value
  const getMetadata = useCallback((value: string): ValueMetadata => {
    return valueMetadataMap[value] || getValueMetadata(value);
  }, [valueMetadataMap, getValueMetadata]);

  // Check if a value is editable
  const isEditable = useCallback((value: string): boolean => {
    const metadata = getMetadata(value);
    return metadata.isEditable;
  }, [getMetadata]);

  // Get the type of a value
  const getValueType = useCallback((value: string): string => {
    const metadata = getMetadata(value);
    return metadata.type;
  }, [getMetadata]);

  // Check if a value comes from a referenced parameter
  const isFromParam = useCallback((value: string): boolean => {
    const metadata = getMetadata(value);
    return metadata.isFromParam;
  }, [getMetadata]);

  // Get the source parameter name if applicable
  const getParamSource = useCallback((value: string): string | undefined => {
    const metadata = getMetadata(value);
    return metadata.paramSource;
  }, [getMetadata]);

  return {
    getMetadata,
    isEditable,
    getValueType,
    isFromParam,
    getParamSource,
    allMetadata: valueMetadataMap
  };
};
