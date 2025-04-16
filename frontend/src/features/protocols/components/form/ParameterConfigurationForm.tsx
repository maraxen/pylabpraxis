import React, { forwardRef, useImperativeHandle } from 'react';
import { VStack } from '@chakra-ui/react';
import { useForm, Controller } from 'react-hook-form';

import { ParameterField } from '../common/ParameterField';
import { ParameterConfig } from '@shared/types';

export interface ParameterConfigurationFormRef {
  save: () => void;
  getValues: () => Record<string, any>;
}

interface Props {
  parameters: Record<string, ParameterConfig>;
  initialValues?: Record<string, any>;
  onSave?: (data: Record<string, any>) => void;
}

export const ParameterConfigurationForm = forwardRef<ParameterConfigurationFormRef, Props>(
  ({ parameters, initialValues = {}, onSave }, ref) => {

    // Deep merge defaults with initialValues
    const mergedDefaults: Record<string, any> = {};

    for (const [name, config] of Object.entries(parameters)) {
      const defaultVal = config.default;
      const initialVal = initialValues[name];

      if (initialVal !== undefined) {
        mergedDefaults[name] = initialVal;
      } else if (defaultVal !== undefined) {
        mergedDefaults[name] = defaultVal;
      } else {
        mergedDefaults[name] = undefined;
      }
    }

    const { control, handleSubmit, getValues } = useForm({
      defaultValues: mergedDefaults,
    });

    useImperativeHandle(ref, () => ({
      save: () => {
        handleSubmit((data) => {
          onSave?.(data);
        })();
      },
      getValues: () => getValues(),
    }));

    return (
      <VStack gap={6} width="100%">
        {Object.entries(parameters).map(([name, config]) => (
          <Controller
            key={name}
            name={name}
            control={control}
            defaultValue={initialValues[name] ?? config.default}
            render={({ field }) => (
              <ParameterField
                name={name}
                config={config}
                value={field.value}
                onChange={(n, v) => field.onChange(v)}
                onRemove={(n, idx) => {
                  const currentValue = field.value;
                  if (Array.isArray(currentValue)) {
                    const newValue = [
                      ...currentValue.slice(0, idx),
                      ...currentValue.slice(idx + 1),
                    ];
                    field.onChange(newValue);
                  }
                }}
                parameters={parameters} // pass parameters for option propagation
              />
            )}
          />
        ))}
      </VStack>
    );
  }
);

ParameterConfigurationForm.displayName = 'ParameterConfigurationForm';