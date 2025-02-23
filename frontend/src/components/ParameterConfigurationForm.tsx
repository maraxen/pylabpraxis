import React from 'react';
import { VStack, Group, Badge, Box } from '@chakra-ui/react';
import { Field } from '@/components/ui/field';
import { Input } from '@/components/ui/input';
import { Slider } from '@/components/ui/slider';
import { Switch } from '@chakra-ui/react';
import {
  SelectRoot,
  SelectItem,
  SelectContent,
  SelectTrigger,
  SelectValueText
} from "@/components/ui/select";
import { createListCollection } from '@chakra-ui/react';
import type { ValueChangeDetails } from '@zag-js/slider';
import { NumberInputField, NumberInputRoot } from "@/components/ui/number-input";
import {
  AutoComplete,
  AutoCompleteInput,
  AutoCompleteItem,
  AutoCompleteList,
  AutoCompleteTag,
  AutoCompleteCreatable,
} from "@choc-ui/chakra-autocomplete";

interface ParameterConfig {
  type: 'string' | 'number' | 'boolean' | 'enum';
  required?: boolean;
  default?: any;
  description?: string;
  isFloat?: boolean;  // Add this to distinguish float vs int
  constraints?: {
    min?: number;
    max?: number;
    step?: number;
    options?: string[];
  };
}

interface Props {
  parameters: Record<string, ParameterConfig>;
  parameterValues: Record<string, any>;
  onParameterChange: (name: string, value: any) => void;
}

export const ParameterConfigurationForm: React.FC<Props> = ({
  parameters = {},
  parameterValues,
  onParameterChange,
}) => {
  const renderParameterInput = (name: string, config: ParameterConfig) => {
    console.log(`[Parameter Debug] Rendering parameter:`, {
      name,
      config,
      currentValue: parameterValues[name],
      defaultValue: config.default,
      constraints: config.constraints,
      type: config.type
    });

    switch (config.type) {
      case 'number':
        const min = config.constraints?.min ?? 0;
        const max = config.constraints?.max ?? 100;
        const step = config.constraints?.step ?? (config.isFloat ? 0.1 : 1);
        const value = parameterValues[name] ?? config.default ?? min;

        console.log(`Number parameter details:`, {
          min, max, step, value
        });

        return (
          <NumberInputRoot
            value={value}
            onChange={(val) => {
              console.log(`NumberInput change:`, { name, val });
              onParameterChange(name, Number(val));
            }}
            min={min}
            max={max}
            step={step}
            width="full"
          >
            <NumberInputField />
          </NumberInputRoot>
        );

      case 'boolean':
        const boolValue = parameterValues[name] ?? config.default ?? false;
        return (
          <Switch.Root
            checked={boolValue}
            onCheckedChange={(checked) => onParameterChange(name, checked)}
          >
            <Switch.HiddenInput />
            <Switch.Control>
              <Switch.Thumb />
            </Switch.Control>
            <Switch.Label>{name}</Switch.Label>
          </Switch.Root>
        );

      case 'enum':
        const currentValues = Array.isArray(parameterValues[name])
          ? parameterValues[name]
          : parameterValues[name] !== undefined && parameterValues[name] !== null
            ? [parameterValues[name]]
            : [];

        console.log(`[Parameter Debug] Enum parameter details:`, {
          name,
          currentValues,
          rawValue: parameterValues[name],
          options: config.constraints?.options
        });

        return (
          <AutoComplete
            multiple
            creatable
            rollNavigation
            defaultValues={currentValues}
            onChange={(values) => {
              console.log(`[Parameter Debug] AutoComplete onChange event:`, {
                name,
                values,
                isArray: Array.isArray(values),
                type: typeof values
              });
              onParameterChange(name, values);
            }}
          >
            <AutoCompleteInput
              placeholder={`Select or create ${name}...`}
              variant="outline"
            >
              {({ tags }) => (
                <Group gap={2}>
                  {tags.map((tag, tid) => (
                    <Badge
                      key={tid}
                      colorPalette="brand"
                      variant="solid"
                      px={2}
                      py={1}
                      borderRadius="md"
                      fontSize="sm"
                      display="flex"
                      alignItems="center"
                      gap={2}
                    >
                      {String(tag.label)}
                      <Box
                        as="span"
                        cursor="pointer"
                        onClick={(e) => {
                          e.stopPropagation();
                          tag.onRemove();
                        }}
                        opacity={0.7}
                        _hover={{ opacity: 1 }}
                        ml={1}
                      >
                        ×
                      </Box>
                    </Badge>
                  ))}
                </Group>
              )}
            </AutoCompleteInput>
            <AutoCompleteList>
              {(config.constraints?.options || []).map((option) => (
                <AutoCompleteItem
                  key={`${name}::${option}`}
                  value={option}
                  label={option}
                  textTransform="capitalize"
                >
                  {option}
                </AutoCompleteItem>
              ))}
              <AutoCompleteCreatable>
                {({ value }) => `Add "${value}"`}
              </AutoCompleteCreatable>
            </AutoCompleteList>
          </AutoComplete>
        );

      default:
        return (
          <Input
            value={parameterValues[name] ?? config.default}
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
              <Badge colorPalette="gray">{config.type}</Badge>
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
