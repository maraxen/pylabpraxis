import React, { useState, useEffect } from 'react';
import {
  Box,
  Heading,
  Button,
  Input,
  Stack,
  Text,
  Textarea,
  Alert,
  AlertIcon,
  Select,
  useToast,
} from '@chakra-ui/react';
import { Fieldset, FieldsetContent, FieldsetLegend } from '@shared/components/ui/fieldset';
import { Field } from '@shared/components/ui/field';
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

  // Reset params and backend when machine type changes
  useEffect(() => {
    if (machineType) {
      const defaultParams: FormValues = {};
      const typeInfo = machineTypes[machineType];

      if (typeInfo) {
        // Initialize with default values
        Object.entries(typeInfo.constructor_params).forEach(([name, param]) => {
          if (param.default !== null) {
            defaultParams[name] = param.default;
          }
        });
      }

      setParams(defaultParams);
      setBackend(''); // Reset backend when machine type changes
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

    // Check if all required params are provided
    if (selectedTypeInfo) {
      const missingParams = Object.entries(selectedTypeInfo.constructor_params)
        .filter(([name, param]) => param.required && !params[name])
        .map(([name]) => name);

      if (missingParams.length > 0) {
        setError(`Missing required parameters: ${missingParams.join(', ')}`);
        return;
      }
    }

    // Prepare form data
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

      // Clear form
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
      <Stack spacing={6}>
        <Heading size="md">Add New Machine</Heading>

        {error && (
          <Alert status="error">
            <AlertIcon />
            {error}
          </Alert>
        )}

        <Stack spacing={4}>
          <Field label="Machine Name" isRequired>
            <Input
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Enter a unique name for the machine"
            />
          </Field>

          <Field label="Description">
            <Textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Enter a description for this machine"
            />
          </Field>

          <Field label="Machine Type" isRequired>
            <Select
              value={machineType}
              onChange={(e) => setMachineType(e.target.value)}
              placeholder="Select a machine type"
            >
              {Object.values(machineTypes).map(type => (
                <option key={type.name} value={type.name}>
                  {type.name}
                </option>
              ))}
            </Select>
          </Field>

          {selectedTypeInfo?.backends && selectedTypeInfo.backends.length > 0 && (
            <Field label="Backend" isRequired>
              <Select
                value={backend}
                onChange={(e) => setBackend(e.target.value)}
                placeholder="Select a backend"
              >
                {selectedTypeInfo.backends.map(backendType => (
                  <option key={backendType} value={backendType}>
                    {backendType}
                  </option>
                ))}
              </Select>
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

        <Button
          colorScheme="blue"
          type="submit"
          isLoading={isLoading}
          isDisabled={!name || !machineType || (selectedTypeInfo?.backends && selectedTypeInfo.backends.length > 0 && !backend)}
        >
          Create Machine
        </Button>
      </Stack>
    </Box>
  );
};