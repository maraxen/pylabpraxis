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

    const renderParameterInput = (name: string, config: ParameterConfig) => {
      console.log(`Rendering input for ${name} with config:`, config); // ADDED
      const value = getValue(name);
      const type = typeof config.type === 'function' ? (config.type as Function).name.toLowerCase() : config.type;

      switch (type) {
        case 'bool':
        case 'boolean':
          return (
            <BooleanInput
              name={name}
              value={value}
              config={config}
              onChange={handleParameterChange}
            />
          );

        case 'array':
          return (
            <ArrayInput
              name={name}
              value={value}
              config={config}
              onChange={handleParameterChange}
            />
          );

        case 'dict': {
          const currentValue = value || {};

          return (
            <Tooltip
              showArrow
              content='Mapping parameter.'
            >
              <Box>
                <HierarchicalMapping
                  name={name}
                  value={currentValue}
                  config={config} // Pass the entire config
                  onChange={(newValue) => {
                    handleParameterChange(name, newValue);
                  }}
                />
              </Box>
            </Tooltip>
          );
        }

        case 'float':
        case 'integer':
        case 'number':
          return (
            <NumberInput
              name={name}
              value={value}
              config={config}
              onChange={handleParameterChange}
            />
          );

        case 'str':
        case 'string':
          return (
            <StringInput
              name={name}
              value={value}
              config={config}
              onChange={handleParameterChange}
            />
          );

        default:
          return (
            <Input
              value={value}
              onChange={(e) => handleParameterChange(name, e.target.value)}
            />
          );
      }
    };

    return (
      <VStack gap={6} width="100%">
        {Object.entries(parameters).map(([name, config]) => (
          <Container
            key={`param-field-${name}`}
            solid
            maxW="container.md"
            p={4}
            role="group"
            _hover={{
              transform: 'translateY(-1px)',
              boxShadow: 'sm',
            }}
            {...(errorState[name] ? {
              border: "2px solid #E53E3E",
              animation: `shake` // Reference the animation token
            } : {})}
          >
            <VStack align="stretch" gap={2}>
              <Box>
                <Text
                  fontSize="lg"
                  fontWeight="semibold"
                  color={{ base: "brand.500", _dark: "brand.200" }}
                  mb={1}
                >
                  {name}
                  {config.required && (
                    <Badge ml={2} colorScheme="brand" variant="outline">Required</Badge>
                  )}
                  <Badge ml={2} colorScheme="brand" variant="outline">
                    {String(config.type)}
                  </Badge>
                </Text>
                {config.description && (
                  <Text
                    fontSize="sm"
                    color={{ base: "brand.500", _dark: "brand.200" }}
                    mb={3}
                  >
                    {config.description}
                  </Text>
                )}
              </Box>
              <Box width="100%">
                {renderParameterInput(name, config)}
              </Box>
            </VStack>
          </Container>
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
