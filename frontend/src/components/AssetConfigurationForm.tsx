import React from 'react';
import { VStack, Group, Text, Badge } from '@chakra-ui/react';
import { Field } from '@/components/ui/field';
import {
  AutoComplete,
  AutoCompleteInput,
  AutoCompleteItem,
  AutoCompleteList,
} from "@choc-ui/chakra-autocomplete";

interface Asset {
  name: string;
  type: string;
  required: boolean;
  description?: string;
}

interface AssetOption {
  name: string;
  type: string;
  is_available: boolean;
  description?: string;
  metadata?: Record<string, any>;
  last_used?: string;
}

interface Props {
  assets: Asset[];
  availableAssets: { [key: string]: AssetOption[] };
  assetConfig: Record<string, any>;
  onAssetChange: (assetName: string, value: string) => void;
  deckFiles?: string[];
  selectedDeckFile?: string;
  onDeckFileChange?: (value: string) => void;
}

export const AssetConfigurationForm: React.FC<Props> = ({
  assets,
  availableAssets,
  assetConfig,
  onAssetChange,
  deckFiles = [],
  selectedDeckFile = '',
  onDeckFileChange,
}) => {
  return (
    <VStack gap={4} width="100%">
      {assets.map((asset) => (
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
          <AutoComplete
            value={assetConfig[asset.name] || ''}
            onChange={(value) => onAssetChange(asset.name, value)}
          >
            <AutoCompleteInput
              placeholder={`Select ${asset.name}...`}
              variant="outline"
            />
            <AutoCompleteList>
              {(availableAssets[asset.type] || []).map((item) => (
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
        </Field>
      ))}

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
};
