import React, { useState, useEffect } from 'react';
import {
  Box,
  Heading,
  Stack,
  Text,
  Textarea,
  Alert
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
import { DynamicParamForm } from './DynamicParamForm';
import { ResourceTypeInfo, ResourceFormData, FormValues } from '../types/plr-resources';
import { createResource } from '../api/assets-api';

interface ResourceFormProps {
  resourceTypes: Record<string, ResourceTypeInfo>;
  categories: {
    Containers: string[];
    Carriers: string[];
    Tips: string[];
    Plates: string[];
    Other: string[];
  };
  onSuccess?: (name: string) => void;
}

export const ResourceForm: React.FC<ResourceFormProps> = ({
  resourceTypes,
  categories,
  onSuccess
}) => {
  const toast = useToast();
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [resourceType, setResourceType] = useState('');
  const [category, setCategory] = useState('');
  const [params, setParams] = useState<FormValues>({});
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (resourceType) {
      const defaultParams: FormValues = {};
      const typeInfo = resourceTypes[resourceType];

      if (typeInfo) {
        Object.entries(typeInfo.constructor_params).forEach(([name, param]) => {
          if (param.default !== null) {
            defaultParams[name] = param.default;
          }
        });
      }

      setParams(defaultParams);
    } else {
      setParams({});
    }
  }, [resourceType, resourceTypes]);

  const creatableResources = Object.values(resourceTypes)
    .filter(type => type.can_create_directly);

  const selectedTypeInfo = resourceType ? resourceTypes[resourceType] : null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!name.trim()) {
      setError('Resource name is required');
      return;
    }

    if (!resourceType) {
      setError('Resource type is required');
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

    const formData: ResourceFormData = {
      name,
      resourceType,
      description,
      params
    };

    try {
      setIsLoading(true);
      const result = await createResource(formData);

      toast({
        title: 'Resource created',
        description: `Successfully created resource: ${result.name}`,
        status: 'success',
        duration: 5000,
        isClosable: true,
      });

      setName('');
      setDescription('');
      setResourceType('');
      setParams({});

      if (onSuccess) {
        onSuccess(result.name);
      }
    } catch (err) {
      setError(`Failed to create resource: ${err instanceof Error ? err.message : String(err)}`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Box as="form" onSubmit={handleSubmit}>
      <Stack gap={6}>
        <Heading size="md">Add New Resource</Heading>

        {error && (
          <Alert.Root status="error">
            <Alert.Indicator />
            <Alert.Content>
              <Alert.Title>Error</Alert.Title>
              <Alert.Description>{error}</Alert.Description>
            </Alert.Content>
          </Alert.Root>
        )}

        <Stack gap={4}>
          <Field label="Resource Name" required>
            <input
              value={name}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => setName(e.target.value)}
              placeholder="Enter a unique name for the resource"
            />
          </Field>

          <Field label="Description">
            <Textarea
              value={description}
              onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setDescription(e.target.value)}
              placeholder="Enter a description for this resource"
            />
          </Field>

          <Field label="Resource Category" required>
            <SelectRoot
              value={category ? [category] : []}
              onChange={({ value }) => {
                setCategory(value[0] || '');
                setResourceType('');
              }}
              collection={{
                items: Object.entries(categories).filter(([, types]) => types.length > 0).map(([cat, types]) => ({
                  value: cat,
                  label: `${cat} (${types.length})`
                }))
              }}
            >
              <SelectValueText placeholder="Select a category" />
            </SelectRoot>
          </Field>

          {category && (
            <Field label="Resource Type" required>
              <SelectRoot
                value={resourceType ? [resourceType] : []}
                onChange={({ value }) => setResourceType(value[0] || '')}
                collection={{
                  items: categories[category as keyof typeof categories]
                    .filter(type => resourceTypes[type]?.can_create_directly)
                    .map(type => ({
                      value: type,
                      label: type
                    }))
                }}
              >
                <SelectValueText placeholder="Select a resource type" />
              </SelectRoot>
            </Field>
          )}
        </Stack>

        {selectedTypeInfo && (
          <Fieldset defaultOpen={true}>
            <FieldsetLegend>Resource Parameters</FieldsetLegend>
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
                filteredParams={['parent']}
              />
            </FieldsetContent>
          </Fieldset>
        )}

        <CustomButton
          colorScheme="blue"
          type="submit"
          loading={isLoading}
          disabled={!name || !resourceType}
        >
          Create Resource
        </CustomButton>
      </Stack>
    </Box>
  );
};