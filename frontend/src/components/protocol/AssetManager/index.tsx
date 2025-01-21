import React, { useState } from 'react';
import { Box, Heading } from '@chakra-ui/react';
import { AssetManagerProps } from './types';
import { AssetList } from './AssetList';
import { Asset } from '../../../types';

export const AssetManager: React.FC<AssetManagerProps> = ({
  assets,
  onAssetSelect,
  onAssetStatusChange,
  selectedAssetId,
  isEditable = false,
}) => {
  const [filter, setFilter] = useState<{
    type?: Asset['type'][];
    status?: Asset['status'][];
    search?: string;
  }>({});

  return (
    <Box>
      <Heading size="md" mb={4}>
        Asset Manager
      </Heading>
      <AssetList
        assets={assets}
        selectedAssetId={selectedAssetId}
        onAssetSelect={onAssetSelect}
        onAssetStatusChange={onAssetStatusChange}
        isEditable={isEditable}
        filter={filter}
      />
    </Box>
  );
};

export * from './types';
export * from './AssetCard';
export * from './AssetList';