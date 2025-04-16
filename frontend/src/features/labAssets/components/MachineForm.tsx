import React, { useState, useEffect } from 'react';
import {
  Box,
  Heading,
  Stack,
  Text,
  Textarea,
} from '@chakra-ui/react';
import { useToast } from '@chakra-ui/toast';
import {
  Field,
  Fieldset,
  FieldsetContent,
  FieldsetLegend,
  SelectRoot,
  SelectValueText,
  Button as CustomButton,
} from '@shared/components/ui';
import { Alert as ChakraAlert } from '@chakra-ui/react';
import { DynamicParamForm } from './DynamicParamForm';
import { MachineTypeInfo, MachineFormData, FormValues } from '../types/plr-resources';
import { createMachine } from '../api/assets-api';

interface MachineFormProps {
  machineTypes: Record<string, MachineTypeInfo>;
  onSuccess?: (name: string) => void;
}

export const MachineForm: React.FC<MachineFormProps> = ({
  machineTypes,
  onSuccess
}) => {
  const toast = useToast();
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [machineType, setMachineType] = useState('');
  const [backend, setBackend] = useState('');
  const [params, setParams] = useState<FormValues>({});
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (machineType) {
      const defaultParams: FormValues = {};
      const typeInfo = machineTypes[machineType];

      if (typeInfo) {
        Object.entries(typeInfo.constructor_params).forEach(([name, param]) => {
          if (param.default !== null) {
            defaultParams[name] = param.default;
          }
        });
      }

      setParams(defaultParams);
      setBackend('');
    } else {
      setParams({});
    }
  }, [machineType, machineTypes]);

  const selectedTypeInfo = machineType ? machineTypes[machineType] : null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!name.trim()) {
      setError('Machine name is required');
      return;
    }

    if (!machineType) {
      setError('Machine type is required');
      return;
    }

    if (selectedTypeInfo?.backends && selectedTypeInfo.backends.length > 0 && !backend) {
      setError('Backend selection is required');
      return;
    }

    if (selectedTypeInfo) {
      const missingParams = Object.entries(selectedTypeInfo.constructor_params)
        .filter(([key, param]) => param.required && !params[key])
        .map(([key]) => key);

      if (missingParams.length > 0) {
        setError(`Missing required parameters: ${missingParams.join(', ')}`);
        return;
      }
    }

    const formData: MachineFormData = {
      name,
      machineType,
      description,
      backend,
      params
    };

    try {
      setIsLoading(true);
      const result = await createMachine(formData);

      toast({
        title: 'Machine created',
        description: `Successfully created machine: ${result.name}`,
        status: 'success',
        duration: 5000,
        isClosable: true,
      });

      setName('');
      setDescription('');
      setMachineType('');
      setBackend('');
      setParams({});

      if (onSuccess) {
        onSuccess(result.name);
      }
    } catch (err) {
      setError(`Failed to create machine: ${err instanceof Error ? err.message : String(err)}`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Box as="form" onSubmit={handleSubmit}>
      <Stack gap={6}>
        <Heading size="md">Add New Machine</Heading>

        {error && (
          <ChakraAlert.Root status="error">
            <ChakraAlert.Indicator />
            <ChakraAlert.Content>
              <ChakraAlert.Title>Error</ChakraAlert.Title>
              <ChakraAlert.Description>{error}</ChakraAlert.Description>
            </ChakraAlert.Content>
          </ChakraAlert.Root>
        )}

        <Stack gap={4}>
          <Field label="Machine Name" required>
            <input
              value={name}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => setName(e.target.value)}
              placeholder="Enter a unique name for the machine"
            />
          </Field>

          <Field label="Description">
            <Textarea
              value={description}
              onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setDescription(e.target.value)}
              placeholder="Enter a description for this machine"
            />
          </Field>

          <Field label="Machine Type" required>
            <SelectRoot
              value={machineType ? [machineType] : []}
              onChange={({ value }) => setMachineType(value[0] || '')}
              collection={{
                items: Object.values(machineTypes).map(type => ({
                  value: type.name,
                  label: type.name
                }))
              }}
            >
              <SelectValueText placeholder="Select a machine type" />
            </SelectRoot>
          </Field>

          {selectedTypeInfo?.backends && selectedTypeInfo.backends.length > 0 && (
            <Field label="Backend" required>
              <SelectRoot
                value={backend ? [backend] : []}
                onChange={({ value }) => setBackend(value[0] || '')}
                collection={{
                  items: selectedTypeInfo.backends.map(b => ({
                    value: b,
                    label: b
                  }))
                }}
              >
                <SelectValueText placeholder="Select a backend" />
              </SelectRoot>
            </Field>
          )}
        </Stack>

        {selectedTypeInfo && (
          <Fieldset defaultOpen={true}>
            <FieldsetLegend>Machine Parameters</FieldsetLegend>
            <FieldsetContent>
              {selectedTypeInfo.doc && (
                <Text mb={4} fontSize="sm" color="gray.600">
                  {selectedTypeInfo.doc}
                </Text>
              )}
              <DynamicParamForm
                parameters={selectedTypeInfo.constructor_params}
                values={params}
                onChange={setParams}
              />
            </FieldsetContent>
          </Fieldset>
        )}

        <CustomButton
          colorScheme="blue"
          type="submit"
          loading={isLoading}
          disabled={!name || !machineType || (selectedTypeInfo?.backends && selectedTypeInfo.backends.length > 0 && !backend)}
        >
          Create Machine
        </CustomButton>
      </Stack>
    </Box>
  );
};