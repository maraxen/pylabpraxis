import React, { useMemo } from 'react';
import {
  Box,
  SimpleGrid,
  Input,
  Stack,
  FormControl,
  FormLabel,
} from '@chakra-ui/react';
import {
  SelectRoot,
  SelectTrigger,
  SelectContent,
  SelectItem,
  SelectValueText,
} from '@chakra-ui/react';
import { AssetListProps } from './types';
import { AssetCard } from './AssetCard';
import { Asset, AssetType } from '../../../types';
import type { ChangeEvent } from 'react';

type FilterUpdate = {
  type?: AssetType;
  status?: Asset['status'];
  search?: string;
};

export const AssetList: React.FC<AssetListProps> = ({
  assets,
  selectedAssetId,
  onAssetSelect,
  onAssetStatusChange,
  isEditable = false,
  filter,
}) => {
  const filteredAssets = useMemo(() => {
    return assets.filter((asset) => {
      if (filter?.type && !filter.type.includes(asset.type)) {
        return false;
      }
      if (filter?.status && asset.status && !filter.status.includes(asset.status)) {
        return false;
      }
      if (filter?.search) {
        const searchLower = filter.search.toLowerCase();
        return (
          asset.name.toLowerCase().includes(searchLower) ||
          asset.description.toLowerCase().includes(searchLower)
        );
      }
      return true;
    });
  }, [assets, filter]);

  const handleFilterChange = (update: Partial<FilterUpdate>) => {
    if (filter) {
      onAssetSelect?.({ ...filter, ...update } as unknown as Asset);
    }
  };

  return (
    <Stack gap={4}>
      <Stack direction={{ base: 'column', md: 'row' }} gap={4}>
        <FormControl>
          <FormLabel>Search</FormLabel>
          <Input
            placeholder="Search assets..."
            value={filter?.search || ''}
            onChange={(e: ChangeEvent<HTMLInputElement>) =>
              handleFilterChange({ search: e.target.value })
            }
          />
        </FormControl>
        <FormControl>
          <FormLabel>Type</FormLabel>
          <SelectRoot
            value={filter?.type?.[0] || ''}
            onValueChange={(value) =>
              handleFilterChange({
                type: value as AssetType,
              })
            }
          >
            <SelectTrigger>
              <SelectValueText placeholder="All types" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="machine">Machine</SelectItem>
              <SelectItem value="liquid_handler">Liquid Handler</SelectItem>
              <SelectItem value="resource">Resource</SelectItem>
            </SelectContent>
          </SelectRoot>
        </FormControl>
        <FormControl>
          <FormLabel>Status</FormLabel>
          <SelectRoot
            value={filter?.status?.[0] || ''}
            onValueChange={(value) =>
              handleFilterChange({
                status: value as Asset['status'],
              })
            }
          >
            <SelectTrigger>
              <SelectValueText placeholder="All statuses" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="available">Available</SelectItem>
              <SelectItem value="in_use">In Use</SelectItem>
              <SelectItem value="offline">Offline</SelectItem>
            </SelectContent>
          </SelectRoot>
        </FormControl>
      </Stack>

      <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} gap={4}>
        {filteredAssets.map((asset) => (
          <AssetCard
            key={asset.id}
            asset={asset}
            isSelected={asset.id === selectedAssetId}
            onSelect={onAssetSelect}
            onStatusChange={(status) => onAssetStatusChange?.(asset.id, status)}
            isEditable={isEditable}
          />
        ))}
      </SimpleGrid>
    </Stack>
  );
};