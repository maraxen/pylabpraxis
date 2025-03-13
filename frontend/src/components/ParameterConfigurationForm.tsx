import React, { useState, useImperativeHandle, forwardRef } from 'react';
import { VStack, Badge, Box, Text, Switch } from '@chakra-ui/react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Tooltip } from '@/components/ui/tooltip';
import { Container } from '@/components/ui/container';
import { useDispatch, useSelector } from 'react-redux';
import { RootState } from '@/store';
import { updateParameterValue, removeParameterValue } from '@/store/protocolForm/slice';
import { HierarchicalMapping } from './configParams/HierarchicalMapping';
import { useToast } from '@chakra-ui/toast';
import { VisualMappingModal } from './VisualMappingDrawer'; // new file
import { StringInput } from './configParams/inputs/StringInput';
import { NumberInput } from './configParams/inputs/NumericInput';
import { BooleanInput } from './configParams/inputs/BooleanInput';
import { ArrayInput } from './configParams/inputs/ArrayInput';
import { ParameterConfig, ParameterConstraints } from './configParams/utils/parameterUtils';
import { ParameterField } from './configParams/ParameterField';

interface Props {
  parameters: Record<string, ParameterConfig>;
}

export interface ParameterConfigurationFormRef {
  saveChanges: () => void;
}

export const ParameterConfigurationForm = forwardRef<ParameterConfigurationFormRef, Props>(
  ({ parameters }, ref) => {
    console.log("ParameterConfigurationForm: parameters", parameters); // ADDED

    const dispatch = useDispatch();
    const toast = useToast();
    const parameterStates = useSelector((state: RootState) => state.protocolForm.parameters);
    const [localValues, setLocalValues] = useState<Record<string, any>>({});
    const [errorState, setErrorState] = useState<Record<string, boolean>>({}); // Track error state per parameter
    const [isVisualMappingOpen, setIsVisualMappingOpen] = useState(false);

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

    const handleTagRemove = (name: string, index: number) => {
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
          />
        ))}
        <Button
          onClick={() => setIsVisualMappingOpen(true)}
          className="outline"
          colorScheme="brand"
        >
          Open Visual Mapping
        </Button>

        {isVisualMappingOpen && (
          <VisualMappingModal
            isOpen={isVisualMappingOpen}
            onClose={() => setIsVisualMappingOpen(false)}
            parameters={parameters}
            localValues={localValues}
            onSubmit={(updatedValues) => {
              setLocalValues(updatedValues);
              setIsVisualMappingOpen(false);
            }}
          />
        )}
      </VStack>
    );
  }
);

ParameterConfigurationForm.displayName = 'ParameterConfigurationForm';
