import React, { useState, useImperativeHandle, forwardRef } from 'react';
import { VStack } from '@chakra-ui/react';
import { useToast } from '@chakra-ui/toast';
import { useDispatch, useSelector } from 'react-redux';

import { RootState } from '@/store';
import { updateParameterValue } from '@protocols/store/slice';

import { ParameterField } from '../common/ParameterField';

import { ParameterConfig } from '@shared/types';

interface Props {
  parameters: Record<string, ParameterConfig>;
}

export interface ParameterConfigurationFormRef {
  saveChanges: () => void;
}

export const ParameterConfigurationForm = forwardRef<ParameterConfigurationFormRef, Props>(
  ({ parameters }, ref) => {
    const dispatch = useDispatch();
    const toast = useToast();
    const parameterStates = useSelector((state: RootState) => state.protocolForm.parameters);
    const [localValues, setLocalValues] = useState<Record<string, any>>({});
    const [errorState, setErrorState] = useState<Record<string, boolean>>({}); // Track error state per parameter

    // Save changes to Redux store
    const saveChanges = () => {
      Object.entries(localValues).forEach(([name, value]) => {
        dispatch(updateParameterValue({ name, value }));
      });
    };

    useImperativeHandle(ref, () => ({
      saveChanges
    }));

    const handleParameterChange = (name: string, value: any) => {
      setLocalValues(prev => ({
        ...prev,
        [name]: value
      }));
    };

    const handleRemove = (name: string, index: number) => {
      const currentValue = localValues[name] || parameterStates[name]?.currentValue;
      if (Array.isArray(currentValue)) {
        setLocalValues(prev => ({
          ...prev,
          [name]: [...currentValue.slice(0, index), ...currentValue.slice(index + 1)]
        }));
      }
    };

    const getValue = (name: string) => {
      return localValues[name] !== undefined
        ? localValues[name]
        : (parameterStates[name]?.currentValue ?? parameters[name]?.default);
    };

    return (
      <VStack gap={6} width="100%">
        {Object.entries(parameters).map(([name, config]) => (
          <ParameterField
            key={name}
            name={name}
            config={config}
            value={getValue(name)}
            onChange={handleParameterChange}
            onRemove={handleRemove}
          />
        ))}
      </VStack>
    );
  }
);

ParameterConfigurationForm.displayName = 'ParameterConfigurationForm';