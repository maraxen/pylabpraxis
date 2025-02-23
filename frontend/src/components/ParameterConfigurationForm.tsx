import React from 'react';
import { VStack, Group, Badge, Box, Text, Switch } from '@chakra-ui/react';
import { Field } from '@/components/ui/field';
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

interface ParameterConstraints {
  min_value?: number;
  max_value?: number;
  step?: number;
  enum?: (string | number)[];
  enum_len?: number;
  key_type?: string;
  value_type?: string;
  key_enum?: string[];
  value_enum?: Array<string | number>;
  key_enum_len?: number;
  value_enum_len?: number;
  key_min_len?: number;
  key_max_len?: number;
  value_min_len?: number;
  value_max_len?: number;
  key_param?: string;
  value_param?: string;
}

interface ParameterConfig {
  type: 'string' | 'number' | 'boolean' | 'array' | 'dict';  // Updated to match backend mapping
  required?: boolean;
  default?: any;
  description?: string;
  constraints?: ParameterConstraints;
}

interface Props {
  parameters: Record<string, ParameterConfig>;
  parameterValues: Record<string, any>;
  onParameterChange: (name: string, value: any) => void;
}

export const ParameterConfigurationForm: React.FC<Props> = ({
  parameters,
  parameterValues,
  onParameterChange,
}) => {
  const renderParameterInput = (name: string, config: ParameterConfig) => {
    const value = parameterValues[name] ?? config.default;
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
            onCheckedChange={(checked) => onParameterChange(name, checked)}
          >
            <Switch.Control>
              <Switch.Thumb />
            </Switch.Control>
          </Switch.Root>
        );

      case 'array':  // Handle array type (previously 'enum')
        const options = config.constraints?.enum || [];
        const maxLen = config.constraints?.enum_len;
        const isConstrained = options.length > 0;

        return (
          <AutoComplete
            multiple
            value={Array.isArray(value) ? value : [value].filter(Boolean)}
            onChange={(values) => {
              const finalValues = Array.isArray(values) ? values : [values];
              if (maxLen && finalValues.length > maxLen) {
                return; // Don't update if exceeding max length
              }
              onParameterChange(name, finalValues);
            }}
          >
            <AutoCompleteInput placeholder={`Enter values${maxLen ? ` (max ${maxLen})` : ''}`} />
            <AutoCompleteList>
              {isConstrained ? (
                options.map((opt) => (
                  <AutoCompleteItem key={String(opt)} value={String(opt)}>
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
        );

      case 'dict':
        const { key_enum, value_enum, key_enum_len, value_enum_len, key_param, value_param } = config.constraints || {};
        const currentDict = (value || {}) as Record<string, any>;

        // Get referenced parameter configurations if they exist
        const { keyConfig, valueConfig } = getReferencedParams(config);

        // Use constraints from referenced parameters if available
        const effectiveKeyEnum = keyConfig?.constraints?.enum || key_enum || [];
        const effectiveValueEnum = valueConfig?.constraints?.enum || value_enum || [];
        const effectiveKeyEnumLen = keyConfig?.constraints?.enum_len || key_enum_len;
        const effectiveValueEnumLen = valueConfig?.constraints?.enum_len || value_enum_len;

        // Determine if values should be arrays based on referenced value parameter type
        const isArrayValue = valueConfig?.type === 'array' ||  // Check referenced param type
          config.constraints?.value_type === 'array';  // Check direct constraint

        return (
          <VStack gap={2} width="100%">
            {Object.entries(currentDict).map(([dictKey, dictVal], idx) => (
              <Group key={idx} gap={2} width="100%" alignItems="flex-start">
                <AutoComplete
                  value={dictKey}
                  onChange={(newKey) => {
                    const newDict = { ...currentDict };
                    delete newDict[dictKey];
                    newDict[newKey] = dictVal;
                    onParameterChange(name, newDict);
                  }}
                >
                  <AutoCompleteInput placeholder="Key" />
                  <AutoCompleteList>
                    {effectiveKeyEnum?.map((k) => (
                      <AutoCompleteItem key={k} value={k}>
                        {k}
                      </AutoCompleteItem>
                    ))}
                  </AutoCompleteList>
                </AutoComplete>

                {isArrayValue ? (
                  <AutoComplete
                    multiple
                    value={Array.isArray(dictVal) ? dictVal : [dictVal].filter(Boolean)}
                    onChange={(newVals) => {
                      const finalValues = Array.isArray(newVals) ? newVals : [newVals];
                      if (effectiveValueEnumLen && finalValues.length > effectiveValueEnumLen) {
                        return;
                      }
                      onParameterChange(name, {
                        ...currentDict,
                        [dictKey]: finalValues
                      });
                    }}
                  >
                    <AutoCompleteInput placeholder={`Values (max ${effectiveValueEnumLen || '∞'})`} />
                    <AutoCompleteList>
                      {(effectiveValueEnum?.length > 0) && (
                        effectiveValueEnum.map((v: string | number) => (
                          <AutoCompleteItem key={String(v)} value={String(v)}>
                            {String(v)}
                          </AutoCompleteItem>
                        ))
                      )}
                    </AutoCompleteList>
                  </AutoComplete>
                ) : (
                  <Input
                    value={String(dictVal)}
                    onChange={(e) => onParameterChange(name, {
                      ...currentDict,
                      [dictKey]: e.target.value
                    })}
                    placeholder="Value"
                  />
                )}
              </Group>
            ))}
            <Button
              size="sm"
              onClick={() => {
                if (effectiveKeyEnumLen && Object.keys(currentDict).length >= effectiveKeyEnumLen) {
                  return;
                }
                onParameterChange(name, {
                  ...currentDict,
                  '': isArrayValue ? [] : ''
                });
              }}
            >
              Add Key-Value Pair
            </Button>
          </VStack>
        );

      case 'float':
      case 'int':
      case 'number':
        const min = config.constraints?.min_value ?? -Infinity;
        const max = config.constraints?.max_value ?? Infinity;
        const step = config.constraints?.step ?? (type === 'float' ? 0.1 : 1);

        return (
          <NumberInputRoot
            value={value}
            onChange={(val) => onParameterChange(name, Number(val))}
            min={min}
            max={max}
            step={step}
            width="full"
          >
            <NumberInputField />
          </NumberInputRoot>
        );

      case 'str':
      case 'string':
        if (config.constraints?.enum) {
          return (
            <AutoComplete
              value={value}
              onChange={(val) => onParameterChange(name, val)}
            >
              <AutoCompleteInput placeholder="Select value..." />
              <AutoCompleteList>
                {config.constraints.enum.map((opt) => (
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
            onChange={(e) => onParameterChange(name, e.target.value)}
          />
        );

      default:
        return (
          <Input
            value={value}
            onChange={(e) => onParameterChange(name, e.target.value)}
          />
        );
    }
  };

  return (
    <VStack gap={4} width="100%">
      {Object.entries(parameters).map(([name, config]) => (
        <Field
          key={`param-field-${name}`}
          label={
            <Group gap={2}>
              {name}
              {config.required && <Badge colorPalette="red">Required</Badge>}
              <Badge colorPalette="gray">{String(config.type)}</Badge>
              {config.constraints?.enum_len && (
                <Badge colorPalette="blue">Max {config.constraints.enum_len}</Badge>
              )}
            </Group>
          }
          required={config.required}
          helperText={config.description}
        >
          {renderParameterInput(name, config)}
        </Field>
      ))}
    </VStack>
  );
};
