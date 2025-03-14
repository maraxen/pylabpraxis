// filepath: /Users/mar/MIT Dropbox/Marielle Russo/PLR_workspace/pylabpraxis/frontend/src/features/protocols/components/form/ParameterField.tsx
import React, { useCallback } from 'react';
import { Text, Badge, Box } from '@chakra-ui/react';
import { Container, StringInput, NumberInput, BooleanInput, ArrayInput, DelayedField } from '@praxis-ui';
import { useDispatch, useSelector } from 'react-redux';
import { HierarchicalMapping } from '../../features/mappings/components/HierarchicalMapping';
import { ParameterConfig } from "@protocols/types/protocol";

interface ParameterFieldProps {
  name: string;
  config: ParameterConfig;
  value: any;
  onChange: (name: string, value: any) => void;
}

const ParameterFieldComponent: React.FC<ParameterFieldProps> = ({ name, config, value, onChange }) => {
  const renderInput = useCallback(() => {
    const type = typeof config.type === 'function'
      ? (config.type as Function).name.toLowerCase()
      : config.type;

    // Check if a constraints.array is provided for string type
    const hasOptions = type === 'string' &&
      config.constraints?.array &&
      Array.isArray(config.constraints.array) &&
      config.constraints.array.length > 0;

    switch (type) {
      case 'boolean':
      case 'bool':
        return <BooleanInput name={name} value={value} onChange={onChange} />;
      case 'array':
        return <ArrayInput
          name={name}
          value={value}
          options={config.constraints?.array}
          maxLen={config.constraints?.array_len}
          restrictedOptions={config.constraints?.creatable}
          onChange={onChange} />;
      case 'dict':
        return (
          <HierarchicalMapping
            name={name}
            value={value}
            config={config}
            onChange={(newMapping) => onChange(name, newMapping)}
          />
        );
      case 'number':
      case 'int':
      case 'integer':
      case 'float':
        return (
          <DelayedField value={value} onBlur={(finalValue) => onChange(name, finalValue)}>
            {(localValue, handleChange, handleBlur) => (
              <NumberInput
                name={name}
                value={localValue}
                onChange={(_, newVal) => handleChange(newVal)}
                onBlur={handleBlur}
                maximum={config.constraints?.max_value}
                minimum={config.constraints?.min_value}
                step_size={config.constraints?.step}
                numeric_type={type === 'integer' ? 'integer' : 'float'}
              />
            )}
          </DelayedField>
        );
      case 'string':
      case 'str':
      default:
        if (hasOptions) {
          // For a string parameter with an array constraint, use ArrayInput to display options.
          return (
            <DelayedField value={value} onBlur={(finalValue) => onChange(name, finalValue)}>
              {(localValue, handleChange, handleBlur) => (
                <ArrayInput
                  name={name}
                  value={localValue}
                  options={config.constraints?.array}
                  maxLen={1}
                  restrictedOptions={config.constraints?.creatable}
                  onChange={(_, newVal) => handleChange(newVal)}
                  onBlur={handleBlur}
                />
              )}
            </DelayedField>
          );
        } else {
          return (
            <DelayedField value={value} onBlur={(finalValue) => onChange(name, finalValue)}>
              {(localValue, handleChange, handleBlur) => (
                <StringInput
                  disableAutocomplete
                  name={name}
                  value={localValue || ''}
                  onChange={(_, newVal) => handleChange(newVal)}
                  onBlur={handleBlur}
                />
              )}
            </DelayedField>
          );
        }
    }
  }, [name, config, value, onChange]);

  return (
    <Container solid maxW="container.md" p={4}>
      <Box mb={2}>
        <Text fontSize="lg" fontWeight="semibold">
          {name}
          {config.required && <Badge ml={2} colorScheme="brand" variant="outline">Required</Badge>}
          <Badge ml={2} colorScheme="brand" variant="outline">
            {String(config.type)}
          </Badge>
        </Text>
        {config.description && (
          <Text fontSize="sm" mb={3}>
            {config.description}
          </Text>
        )}
      </Box>
      <Box>
        {renderInput()}
      </Box>
    </Container>
  );
};

export const ParameterField = React.memo(ParameterFieldComponent);