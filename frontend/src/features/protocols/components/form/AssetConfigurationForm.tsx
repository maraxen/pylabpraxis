import React, { forwardRef, useImperativeHandle } from 'react';
import { VStack, Text, Badge, Group } from '@chakra-ui/react';
import { Field } from '@praxis-ui';
import {
  AutoComplete,
  AutoCompleteInput,
  AutoCompleteItem,
  AutoCompleteList,
} from "@choc-ui/chakra-autocomplete";
import { useForm, Controller } from 'react-hook-form';

import { Asset, AssetOption } from '@protocols/types/protocol';

export interface AssetConfigurationFormRef {
  save: () => void;
  getValues: () => Record<string, any>;
}

interface Props {
  assets: Asset[];
  availableAssets?: Record<string, AssetOption[]>;
  deckFiles?: string[];
  selectedDeckFile?: string;
  onDeckFileChange?: (value: string) => void;
  initialValues?: Record<string, any>;
  onSave?: (data: Record<string, any>) => void;
}

export const AssetConfigurationForm = forwardRef<AssetConfigurationFormRef, Props>(({
  assets,
  availableAssets = {},
  deckFiles = [],
  selectedDeckFile = '',
  onDeckFileChange,
  initialValues = {},
  onSave,
}, ref) => {
  const { control, handleSubmit, getValues, reset } = useForm({
    defaultValues: initialValues,
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
    <VStack gap={4} width="100%">
      {assets.map((asset) => {
        const options = availableAssets[asset.type] || [];
        return (
          <Field
            key={`asset-field-${asset.name}`}
            label={
              <Group gap={2}>
                {asset.name}
                {asset.required && <Badge colorPalette="red">Required</Badge>}
                <Badge colorPalette="gray">{asset.type}</Badge>
              </Group>
            }
            required={asset.required}
            helperText={asset.description}
          >
            <Controller
              control={control}
              name={asset.name}
              render={({ field }) => (
                <AutoComplete
                  value={field.value || ''}
                  onChange={field.onChange}
                >
                  <AutoCompleteInput
                    placeholder={`Select ${asset.name}...`}
                    variant="outline"
                  />
                  <AutoCompleteList>
                    {options.map((item) => (
                      <AutoCompleteItem
                        key={`${asset.type}::${item.name}`}
                        value={item.name}
                        disabled={!item.is_available}
                        label={`${item.name}${item.description ? ` - ${item.description}` : ''}`}
                      >
                        <Group gap={2} width="100%" justify="space-between">
                          <Text>{item.name}</Text>
                          <Group gap={2}>
                            {!item.is_available && (
                              <Badge colorPalette="yellow">In Use</Badge>
                            )}
                            {item.metadata?.location && (
                              <Badge colorPalette="blue">{item.metadata.location}</Badge>
                            )}
                            {item.last_used && (
                              <Text fontSize="sm" color="gray.500">
                                Last used: {new Date(item.last_used).toLocaleDateString()}
                              </Text>
                            )}
                          </Group>
                        </Group>
                      </AutoCompleteItem>
                    ))}
                  </AutoCompleteList>
                </AutoComplete>
              )}
            />
          </Field>
        );
      })}

      <Field
        label={
          <Group gap={2}>
            Base Deck Layout
            <Badge colorPalette="red">Required</Badge>
          </Group>
        }
        required
        helperText="Select the base deck layout for this protocol run"
      >
        <AutoComplete
          value={selectedDeckFile}
          onChange={(value) => onDeckFileChange?.(value)}
        >
          <AutoCompleteInput
            placeholder="Select deck layout..."
            variant="outline"
          />
          <AutoCompleteList>
            {deckFiles.map((file) => (
              <AutoCompleteItem
                key={file}
                value={file}
                textTransform="capitalize"
              >
                {file}
              </AutoCompleteItem>
            ))}
          </AutoCompleteList>
        </AutoComplete>
      </Field>
    </VStack>
  );
});

AssetConfigurationForm.displayName = 'AssetConfigurationForm';