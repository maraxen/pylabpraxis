import React, { useMemo } from 'react';
import { Stack } from '@chakra-ui/react';

// Import shared UI components
import { Field } from '@shared/components/ui/field';
import { StringInput } from '@shared/components/ui/StringInput';
import { ArrayInput } from '@shared/components/ui/ArrayInput';
import { BooleanInput } from '@shared/components/ui/BooleanInput';
import { NumericInput } from '@shared/components/ui/NumericInput';

import { ParameterInfo, ParameterValue, FormValues } from '../types/plr-resources';

interface DynamicParamFormProps {
  parameters: Record<string, ParameterInfo>;
  values: FormValues;
  onChange: (values: FormValues) => void;
  filteredParams?: string[];
}

export const DynamicParamForm: React.FC<DynamicParamFormProps> = ({
  parameters,
  values,
  onChange,
  filteredParams = [],
}) => {
  // Filter out any parameters that should be excluded
  const visibleParams = useMemo(() => {
    return Object.entries(parameters)
      .filter(([name]) => !filteredParams.includes(name))
      .sort((a, b) => {
        // Show required parameters first
        if (a[1].required && !b[1].required) return -1;
        if (!a[1].required && b[1].required) return 1;
        // Then sort alphabetically
        return a[0].localeCompare(b[0]);
      });
  }, [parameters, filteredParams]);

  const handleValueChange = (name: string, value: ParameterValue) => {
    const newValues = {
      ...values,
      [name]: value
    };
    onChange(newValues);
  };

  // Detect if parameter type is an array
  const isArrayType = (type: string): boolean => {
    return type.includes('List') ||
      type.includes('list') ||
      type.includes('[]') ||
      type.includes('Array');
  };

  // Detect if parameter type is numeric
  const isNumericType = (type: string): boolean => {
    return type.includes('int') ||
      type.includes('float') ||
      type.includes('double') ||
      type.includes('number');
  };

  // Detect if parameter type is boolean
  const isBooleanType = (type: string): boolean => {
    return type.includes('bool');
  };

  // Render appropriate input based on parameter type
  const renderInput = (name: string, param: ParameterInfo) => {
    const value = values[name] ?? param.default;

    if (isBooleanType(param.type)) {
      return (
        <BooleanInput
          name={name}
          value={Boolean(value)}
          onChange={handleValueChange}
        />
      );
    }

    if (isArrayType(param.type)) {
      return (
        <ArrayInput
          name={name}
          value={Array.isArray(value) ? value : value ? [value] : []}
          onChange={handleValueChange}
        />
      );
    }

    if (isNumericType(param.type)) {
      return (
        <NumericInput
          name={name}
          value={value}
          onChange={handleValueChange}
          numeric_type={param.type.includes('int') ? 'integer' : 'float'}
        />
      );
    }

    // Default to string input
    return (
      <StringInput
        name={name}
        value={value}
        onChange={handleValueChange}
      />
    );
  };

  return (
    <Stack gap={4}>
      {visibleParams.map(([name, param]) => (
        <Field
          key={name}
          label={`${name}${param.required ? ' *' : ''}`}
          helperText={param.description || `Type: ${param.type}`}
          required={param.required}
        >
          {renderInput(name, param)}
        </Field>
      ))}
    </Stack>
  );
};