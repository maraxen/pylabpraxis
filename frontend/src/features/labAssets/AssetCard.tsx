import React from 'react';
import {
  Flex,
  Text,
  Icon
} from '@chakra-ui/react';
import { LuFlaskConical, LuCpu, LuCircleCheck, LuCircleX } from 'react-icons/lu';
import { CardContainer, Tooltip, StatusBadge } from '@praxis-ui';
import { Asset } from './types/asset';

interface AssetCardProps {
  asset: Asset;
  isSelected?: boolean;
  onSelect?: (asset: Asset) => void;
}

export const AssetCard: React.FC<AssetCardProps> = ({
  asset,
  isSelected = false,
  onSelect
}) => {
  // Determine asset icon based on type
  const getAssetIcon = () => {
    if (asset.type.toLowerCase().includes('machine')) {
      return LuCpu;
    }
    return LuFlaskConical;
  };

  const handleClick = () => {
    if (onSelect) {
      onSelect(asset);
    }
  };

  return (
    <CardContainer
      isHighlighted={isSelected}
      isActive={false}
      isDragging={false}
      cursor={onSelect ? 'pointer' : 'default'}
      onClick={handleClick}
      transition="all 0.2s"
      _hover={{
        transform: 'translateY(-2px)',
      }}
    >
      <Flex justify="space-between" align="center" mb={3}>
        <Flex align="center">
          <Icon as={getAssetIcon()} boxSize={5} color="blue.500" mr={2} />
          <Text fontWeight="bold" fontSize="md" truncate maxWidth="150px">
            {asset.name}
          </Text>
        </Flex>
        <StatusBadge
          status={asset.is_available ? 'editable' : 'readonly'}
          label={asset.is_available ? 'Available' : 'In Use'}
          tooltip={asset.is_available ? 'This asset is available for use' : 'This asset is currently in use'}
        />
      </Flex>

      <Text fontSize="sm" color="gray.500" mb={3} truncate>
        Type: {asset.type}
      </Text>

      {asset.description && (
        <Text fontSize="sm" lineClamp={2} mb={3}>
          {asset.description}
        </Text>
      )}

      <Flex justify="flex-start" mt={2}>
        <Tooltip content={asset.is_available ? 'Available for use' : 'Currently in use'}>
          <Flex align="center">
            <Icon
              as={asset.is_available ? LuCircleCheck : LuCircleX}
              color={asset.is_available ? 'green.500' : 'red.500'}
              mr={1}
            />
            <Text fontSize="xs" color={asset.is_available ? 'green.500' : 'red.500'}>
              {asset.is_available ? 'Available' : 'In Use'}
            </Text>
          </Flex>
        </Tooltip>
      </Flex>
    </CardContainer>
  );
};