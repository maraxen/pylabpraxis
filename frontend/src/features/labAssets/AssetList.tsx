import React, { useMemo } from 'react';
import {
  Box,
  SimpleGrid,
  Flex,
  Text,
  BoxProps,
} from '@chakra-ui/react';
import { FiSearch } from 'react-icons/fi';
import { useForm, Controller } from 'react-hook-form';
import { AssetCard } from './AssetCard';
import { StringInput } from '@shared/components/ui/StringInput';
import { StatusBadge } from '@shared/components/ui/StatusBadge';
import { SelectRoot, SelectTrigger, SelectContent, SelectItem, SelectValueText } from '@shared/components/ui/select';
import { Asset } from './types/asset';

interface AssetListProps {
  assets: Asset[];
  onAssetSelect?: (asset: Asset) => void;
  selectedAssetId?: string;
  emptyMessage?: string;
}

interface FilterFormValues {
  searchQuery: string;
  filterType: string;
  availability: 'all' | 'available' | 'in-use';
}

export const AssetList: React.FC<AssetListProps> = ({
  assets,
  onAssetSelect,
  selectedAssetId,
  emptyMessage = 'No assets found',
}) => {
  const { control, watch } = useForm<FilterFormValues>({
    defaultValues: {
      searchQuery: '',
      filterType: '',
      availability: 'all',
    },
  });

  const { searchQuery, filterType, availability } = watch();

  // Extract unique asset types for the filter dropdown
  const assetTypes = useMemo(() => {
    const types = new Set<string>();
    assets.forEach(asset => types.add(asset.type));
    return Array.from(types);
  }, [assets]);

  // Extract unique asset names for autocomplete
  const assetNames = useMemo(() => {
    return assets.map(asset => asset.name);
  }, [assets]);

  // Filter assets based on search query, type and availability
  const filteredAssets = useMemo(() => {
    return assets.filter(asset => {
      const matchesSearch = searchQuery === '' ||
        asset.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        asset.description?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        asset.type.toLowerCase().includes(searchQuery.toLowerCase());

      const matchesType = filterType === '' || asset.type === filterType;

      const matchesAvailability =
        availability === 'all' ||
        (availability === 'available' && asset.is_available) ||
        (availability === 'in-use' && !asset.is_available);

      return matchesSearch && matchesType && matchesAvailability;
    });
  }, [assets, searchQuery, filterType, availability]);

  // Handle Enter key to select if only one asset matches
  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && filteredAssets.length === 1 && onAssetSelect) {
      onAssetSelect(filteredAssets[0]);
    }
  };

  // Convert asset types to the format expected by SelectRoot
  const assetTypeOptions = assetTypes.map(type => ({
    value: type,
    label: type
  }));

  // Convert availability options to the format expected by SelectRoot
  const availabilityOptions = [
    { value: 'all', label: 'All Status' },
    { value: 'available', label: 'Available' },
    { value: 'in-use', label: 'In Use' }
  ];

  // Search input with icon
  const SearchWrapper = (props: BoxProps) => (
    <Box position="relative" flex={1} {...props}>
      <Box
        position="absolute"
        left="3"
        top="50%"
        transform="translateY(-50%)"
        zIndex={1}
        pointerEvents="none"
      >
        <FiSearch color="gray.300" />
      </Box>
      <Controller
        name="searchQuery"
        control={control}
        render={({ field }) => (
          <StringInput
            name="assetSearch"
            value={field.value}
            options={assetNames}
            onChange={(_, val) => field.onChange(val)}
            onKeyDown={handleKeyDown}
          />
        )}
      />
    </Box>
  );

  return (
    <Box>
      <Flex mb={4} direction={{ base: 'column', md: 'row' }} gap={2}>
        {/* Search Input */}
        <SearchWrapper />

        {/* Type Filter */}
        <Box maxWidth="200px">
          <Controller
            name="filterType"
            control={control}
            render={({ field }) => (
              <SelectRoot
                value={field.value ? [field.value] : []}
                onChange={(e) => field.onChange(e.value[0] || '')}
                collection={{ items: [{ value: '', label: 'All Types' }, ...assetTypeOptions] }}
                size="md"
              >
                <SelectTrigger>
                  <SelectValueText placeholder="All Types" />
                </SelectTrigger>
                <SelectContent>
                  {[{ value: '', label: 'All Types' }, ...assetTypeOptions].map(item => (
                    <SelectItem key={item.value} item={item} />
                  ))}
                </SelectContent>
              </SelectRoot>
            )}
          />
        </Box>

        {/* Availability Filter */}
        <Box maxWidth="200px">
          <Controller
            name="availability"
            control={control}
            render={({ field }) => (
              <SelectRoot
                value={[field.value]}
                onChange={(e) => field.onChange(e.value[0] as any || 'all')}
                collection={{ items: availabilityOptions }}
                size="md"
              >
                <SelectTrigger>
                  <SelectValueText />
                </SelectTrigger>
                <SelectContent>
                  {availabilityOptions.map(item => (
                    <SelectItem key={item.value} item={item} />
                  ))}
                </SelectContent>
              </SelectRoot>
            )}
          />
        </Box>
      </Flex>

      <Box mb={2}>
        <Text fontSize="sm" color="gray.500">
          Showing {filteredAssets.length} out of {assets.length} assets
          {filterType && (
            <StatusBadge
              ml={2}
              status="type"
              label={`Type: ${filterType}`}
              tooltip={`Filtering by ${filterType} assets`}
            />
          )}
          {availability !== 'all' && (
            <StatusBadge
              ml={2}
              status={availability === 'available' ? 'editable' : 'readonly'}
              label={availability === 'available' ? 'Available' : 'In Use'}
              tooltip={`Showing ${availability} assets`}
            />
          )}
        </Text>
      </Box>

      {filteredAssets.length > 0 ? (
        <SimpleGrid columns={{ base: 1, md: 2, lg: 3, xl: 4 }} gap={4}>
          {filteredAssets.map((asset) => (
            <AssetCard
              key={asset.id || asset.name}
              asset={asset}
              isSelected={selectedAssetId === asset.id || selectedAssetId === asset.name}
              onSelect={onAssetSelect}
            />
          ))}
        </SimpleGrid>
      ) : (
        <Flex justify="center" align="center" minHeight="200px" bg="gray.50" borderRadius="md">
          <Text color="gray.500">{emptyMessage}</Text>
        </Flex>
      )}
    </Box>
  );
};