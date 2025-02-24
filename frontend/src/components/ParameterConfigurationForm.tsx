import React, { useRef, useState, useImperativeHandle, forwardRef } from 'react';
import { VStack, Group, Badge, Box, Text, Switch } from '@chakra-ui/react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { NumberInputField, NumberInputRoot } from "@/components/ui/number-input";
import {
  AutoComplete,
  AutoCompleteInput,
  AutoCompleteItem,
  AutoCompleteList,
  AutoCompleteTag,
  AutoCompleteCreatable,
} from "@choc-ui/chakra-autocomplete";
import { Container } from '@/components/ui/container';
import { useDispatch, useSelector } from 'react-redux';
import { RootState } from '@/store';
import { updateParameterValue, removeParameterValue } from '@/store/protocolForm/slice';
import { OneToOneMapping } from './mappings/OneToOneMapping';
import { HierarchicalMapping } from './mappings/HierarchicalMapping';
import { useToast } from '@chakra-ui/toast';
import { CssKeyframes } from '@chakra-ui/react';

interface ParameterConstraints {
  min_value?: number;
  max_value?: number;
  step?: number;
  array?: Array<string | number>;  // Keep array instead of enum
  array_len?: number;  // Keep array_len instead of enum_len
  key_type?: string;
  value_type?: string;
  key_array?: Array<string | number>;
  value_array?: Array<string | number>;
  key_array_len?: number;
  value_array_len?: number;
  key_min_len?: number;
  key_max_len?: number;
  value_min_len?: number;
  value_max_len?: number;
  key_param?: string;
  value_param?: string;
  hierarchical?: boolean;
  parent?: 'key' | 'value';
}

interface ParameterConfig {
  type: 'string' | 'number' | 'boolean' | 'array' | 'dict' | 'integer' | 'float';
  required?: boolean;
  default?: any;
  description?: string;
  constraints?: ParameterConstraints;
}

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
      const value = getValue(name);
      const type = typeof config.type === 'function' ? (config.type as Function).name.toLowerCase() : config.type;

      // Helper function to get referenced parameter constraints
      const getReferencedParams = (config: ParameterConfig) => {
        const { key_param, value_param } = config.constraints || {};
        return {
          keyConfig: key_param ? parameters[key_param] : null,
          valueConfig: value_param ? parameters[value_param] : null
        };
      };

      switch (type) {
        case 'bool':
        case 'boolean':
          return (
            <Switch.Root
              checked={!!value}
              onCheckedChange={({ checked }) => handleParameterChange(name, checked)}
            >
              <Switch.HiddenInput />
              <Switch.Control>
                <Switch.Thumb />
              </Switch.Control>
              <Switch.Label>{name}</Switch.Label>
            </Switch.Root>
          );

        case 'array': {
          const { array: options = [], array_len: maxLen } = config.constraints || {};
          const isConstrained = options.length > 0;
          const currentValues = Array.isArray(value) ? value : value ? [value] : [];
          const isAtMaxLength = maxLen ? currentValues.length >= maxLen : false;

          const handleSelectOption = ({ item }: { item: { value: string } }) => {
            if (currentValues.includes(item.value)) {
              toast({
                title: 'Duplicate value',
                description: 'This value is already selected.',
                status: 'warning',
                duration: 3000,
                isClosable: true,
              });
              setErrorState(prev => ({ ...prev, [name]: true }));
              return;
            }

            const newValues = [...currentValues, item.value];
            if (!maxLen || newValues.length <= maxLen) {
              handleParameterChange(name, newValues);
              setErrorState(prev => ({ ...prev, [name]: false })); // Clear error on success
            }
          };

          return (
            <Box>
              {/* Show selected values as tags */}
              <Box mb={2} display="flex" flexWrap="wrap" gap={2}>
                {currentValues.map((val, index) => (
                  <AutoCompleteTag
                    key={`${val}-${index}`}
                    label={String(val)}
                    variant="solid"
                    colorScheme="brand"
                    onRemove={() => handleTagRemove(name, index)}
                  />
                ))}
              </Box>

              <AutoComplete
                multiple
                freeSolo={!isConstrained}
                creatable={!isConstrained}
                value={currentValues}
                maxSelections={maxLen}
                openOnFocus
                isReadOnly={isAtMaxLength}
                suggestWhenEmpty={isConstrained && !isAtMaxLength}
                onSelectOption={handleSelectOption}
                onChange={(value) => {
                  console.log('onChange:', value);
                  handleParameterChange(name, value);
                }}
              >
                <AutoCompleteInput
                  placeholder={isAtMaxLength ?
                    `Maximum ${maxLen} values reached` :
                    `Enter values${maxLen ? ` (max ${maxLen})` : ''}`
                  }
                  readOnly={isAtMaxLength}
                />
                <AutoCompleteList>
                  {isConstrained ? (
                    options.map((opt) => (
                      <AutoCompleteItem
                        key={String(opt)}
                        value={String(opt)}
                        label={String(opt)}
                        disabled={isAtMaxLength}
                      >
                        {String(opt)}
                      </AutoCompleteItem>
                    ))
                  ) : (
                    <AutoCompleteCreatable>
                      {({ value }) => `Add "${value}"`}
                    </AutoCompleteCreatable>
                  )}
                </AutoCompleteList>
              </AutoComplete>
            </Box>
          );
        }

        case 'dict': {
          const {
            hierarchical,
            parent,
            key_array,
            value_array,
            key_param,
            value_param,
            value_array_len
          } = config.constraints || {};

          const currentValue = value || {};

          if (hierarchical && parent) {
            return (
              <HierarchicalMapping
                name={name}
                value={currentValue}
                constraints={{
                  hierarchical,
                  parent,
                  key_array,
                  value_array,
                  key_param,
                  value_param,
                  value_array_len
                }}
                onChange={(newValue) => handleParameterChange(name, newValue)}
              />
            );
          }

          return (
            <OneToOneMapping
              name={name}
              value={currentValue}
              constraints={{
                key_array,
                value_array,
                key_param,
                value_param
              }}
              onChange={(newValue) => handleParameterChange(name, newValue)}
            />
          );
        }

        case 'float':
        case 'integer':
        case 'number': {
          const min = config.constraints?.min_value ?? -Infinity;
          const max = config.constraints?.max_value ?? Infinity;
          const step = config.constraints?.step ?? (type === 'float' ? 0.1 : 1);

          const handleNumberChange = (val: string | number) => {
            if (val === '') {
              handleParameterChange(name, '');
              return;
            }

            let numValue = typeof val === 'string' ? parseFloat(val) : val;

            // Validate the number
            if (isNaN(numValue)) return;
            if (numValue < min) numValue = min;
            if (numValue > max) numValue = max;

            // For integers, round the value
            if (type === 'integer') {
              numValue = Math.round(numValue);
            }

            console.log('Number change:', { name, value: numValue, type });
            handleParameterChange(name, numValue);
          };

          return (
            <NumberInputRoot
              value={String(value)}
              onValueChange={({ value }) => handleNumberChange(value)}
              min={min}
              max={max}
              step={step}
              width="full"
            >
              <NumberInputField />
            </NumberInputRoot>
          );
        }

        case 'str':
        case 'string': {
          const { array: options } = config.constraints || {};
          if (options) {
            return (
              <AutoComplete
                value={value}
                onChange={(val) => handleParameterChange(name, val)}
              >
                <AutoCompleteInput placeholder="Select value..." />
                <AutoCompleteList>
                  {options.map((opt) => (
                    <AutoCompleteItem key={String(opt)} value={String(opt)}>
                      {String(opt)}
                    </AutoCompleteItem>
                  ))}
                </AutoCompleteList>
              </AutoComplete>
            );
          }
          return (
            <Input
              value={value}
              onChange={(e) => handleParameterChange(name, e.target.value)}
            />
          );
        }

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
      </VStack>
    );
  }
);

ParameterConfigurationForm.displayName = 'ParameterConfigurationForm';
