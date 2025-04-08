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
  Select
} from '@chakra-ui/react';
import { useToast } from ;
import { Fieldset, FieldsetContent, FieldsetLegend } from '@shared/components/ui/fieldset';
import { Field } from '@shared/components/ui/field';
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

  // Reset params when resource type changes
  useEffect(() => {
    if (resourceType) {
      const defaultParams: FormValues = {};
      const typeInfo = resourceTypes[resourceType];

      if (typeInfo) {
        // Initialize with default values
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

  // Filter the list of resource types to only those that can be created directly
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

      // Clear form
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
      <Stack spacing={6}>
        <Heading size="md">Add New Resource</Heading>

        {error && (
          <Alert status="error">
            <AlertIcon />
            {error}
          </Alert>
        )}

        <Stack spacing={4}>
          <Field label="Resource Name" isRequired>
            <Input
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Enter a unique name for the resource"
            />
          </Field>

          <Field label="Description">
            <Textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Enter a description for this resource"
            />
          </Field>

          <Field label="Resource Category" isRequired>
            <Select
              value={category}
              onChange={(e) => {
                setCategory(e.target.value);
                setResourceType(''); // Reset resource type when category changes
              }}
              placeholder="Select a category"
            >
              {Object.entries(categories).map(([category, types]) => (
                types.length > 0 && (
                  <option key={category} value={category}>
                    {category} ({types.length})
                  </option>
                )
              ))}
            </Select>
          </Field>

          {category && (
            <Field label="Resource Type" isRequired>
              <Select
                value={resourceType}
                onChange={(e) => setResourceType(e.target.value)}
                placeholder="Select a resource type"
              >
                {categories[category as keyof typeof categories]
                  .filter(type => resourceTypes[type]?.can_create_directly)
                  .map(type => (
                    <option key={type} value={type}>
                      {type}
                    </option>
                  ))}
              </Select>
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
                filteredParams={['parent']} // Filter out parent parameter
              />
            </FieldsetContent>
          </Fieldset>
        )}

        <Button
          colorScheme="blue"
          type="submit"
          isLoading={isLoading}
          isDisabled={!name || !resourceType}
        >
          Create Resource
        </Button>
      </Stack>
    </Box>
  );
};