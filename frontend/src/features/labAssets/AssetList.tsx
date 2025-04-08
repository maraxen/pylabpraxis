import React, { useState, useMemo } from 'react';
import {
  Box,
  SimpleGrid,
  Flex,
  Text,
  BoxProps,
} from '@chakra-ui/react';
import { FiSearch } from 'react-icons/fi';
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

export const AssetList: React.FC<AssetListProps> = ({
  assets,
  onAssetSelect,
  selectedAssetId,
  emptyMessage = 'No assets found',
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [filterType, setFilterType] = useState('');
  const [availabilityFilter, setAvailabilityFilter] = useState<'all' | 'available' | 'in-use'>('all');

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
      // Filter by search query
      const matchesSearch = searchQuery === '' ||
        asset.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        asset.description?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        asset.type.toLowerCase().includes(searchQuery.toLowerCase());

      // Filter by asset type
      const matchesType = filterType === '' || asset.type === filterType;

      // Filter by availability
      const matchesAvailability =
        availabilityFilter === 'all' ||
        (availabilityFilter === 'available' && asset.is_available) ||
        (availabilityFilter === 'in-use' && !asset.is_available);

      return matchesSearch && matchesType && matchesAvailability;
    });
  }, [assets, searchQuery, filterType, availabilityFilter]);

  // Handle search input change
  const handleSearchChange = (name: string, value: string) => {
    setSearchQuery(value);
  };

  // Handle key press in search input for auto-selection
  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && filteredAssets.length === 1 && onAssetSelect) {
      // If only one asset matches the search and Enter is pressed, select it
      onAssetSelect(filteredAssets[0]);
    }
  };

  // Custom search input with icon
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
      <StringInput
        name="assetSearch"
        value={searchQuery}
        options={assetNames}
        onChange={handleSearchChange}
        onKeyDown={handleKeyDown}
      />
    </Box>
  );

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

  return (
    <Box>
      <Flex mb={4} direction={{ base: 'column', md: 'row' }} gap={2}>
        {/* Search Input */}
        <SearchWrapper />

        {/* Type Filter */}
        <Box maxWidth="200px">
          <SelectRoot
            value={filterType ? [filterType] : []}
            onChange={(e) => setFilterType(e.value[0] || '')}
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
        </Box>

        {/* Availability Filter */}
        <Box maxWidth="200px">
          <SelectRoot
            value={[availabilityFilter]}
            onChange={(e) => setAvailabilityFilter(e.value[0] as any || 'all')}
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
          {availabilityFilter !== 'all' && (
            <StatusBadge
              ml={2}
              status={availabilityFilter === 'available' ? 'editable' : 'readonly'}
              label={availabilityFilter === 'available' ? 'Available' : 'In Use'}
              tooltip={`Showing ${availabilityFilter} assets`}
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