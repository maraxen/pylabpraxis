import React, { useCallback } from 'react';
import { Text, Badge, Box } from '@chakra-ui/react';
import { Container } from '@/components/ui/container';
import { Input } from '@/components/ui/input';
import { useDispatch, useSelector } from 'react-redux';
import { useNestedMapping } from './contexts/nestedMappingContext';
import { StringInput } from './inputs/StringInput';
import { NumberInput } from './inputs/NumericInput';
import { BooleanInput } from './inputs/BooleanInput';
import { ArrayInput } from './inputs/ArrayInput';
import { ParameterConfig } from './utils/parameterUtils';
import { HierarchicalMapping } from './HierarchicalMapping';
import { DelayedField } from '../../shared/components/ui/forms/delayedField';

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
        return <BooleanInput name={name} value={value} config={config} onChange={onChange} />;
      case 'array':
        return <ArrayInput name={name} value={value} config={config} onChange={onChange} />;
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
                config={config}
                onChange={(_, newVal) => handleChange(newVal)}
                onBlur={handleBlur}
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
                  config={config}
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
                  config={config}
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
