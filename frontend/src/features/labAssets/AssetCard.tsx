import React from 'react';
import {
  Box,
  Stack,
  Heading,
  Text,
  Badge,
  MenuRoot,
  MenuTrigger,
  MenuContent,
  MenuItem,
  IconButton,
} from '@chakra-ui/react';
import { FiMoreVertical } from 'react-icons/fi';
import { AssetCardProps } from './types';
import type { MouseEvent } from 'react';

const statusColors = {
  available: 'green',
  in_use: 'orange',
  offline: 'red',
} as const;

export const AssetCard: React.FC<AssetCardProps> = ({
  asset,
  isSelected,
  onSelect,
  onStatusChange,
  isEditable = false,
}) => {
  const handleMenuClick = (e: MouseEvent) => {
    e.stopPropagation();
  };

  return (
    <Box
      cursor="pointer"
      onClick={() => onSelect?.(asset)}
      borderWidth={isSelected ? '2px' : '1px'}
      borderColor={isSelected ? 'blue.500' : 'gray.200'}
      _hover={{ shadow: 'md' }}
      p={4}
      borderRadius="md"
      bg="white"
    >
      <Stack gap={3}>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Heading size="sm">{asset.name}</Heading>
          {isEditable && (
            <MenuRoot>
              <MenuTrigger>
                <IconButton
                  variant="ghost"
                  size="sm"
                  aria-label="Options"
                  onClick={handleMenuClick}><FiMoreVertical /></IconButton>
              </MenuTrigger>
              <MenuContent onClick={handleMenuClick}>
                <MenuItem value="available" onClick={() => onStatusChange?.('available')}>
                  Set Available
                </MenuItem>
                <MenuItem value="in_use" onClick={() => onStatusChange?.('in_use')}>
                  Set In Use
                </MenuItem>
                <MenuItem value="offline" onClick={() => onStatusChange?.('offline')}>
                  Set Offline
                </MenuItem>
              </MenuContent>
            </MenuRoot>
          )}
        </Box>

        <Stack direction="row" gap={2}>
          <Badge>{asset.type}</Badge>
          {asset.status && (
            <Badge colorScheme={statusColors[asset.status]}>
              {asset.status.replace('_', ' ')}
            </Badge>
          )}
        </Stack>

        <Text fontSize="sm" color="gray.600">
          {asset.description}
        </Text>

        {asset.resource && (
          <Box>
            <Text fontSize="sm" fontWeight="bold">
              Resource Details:
            </Text>
            <Text fontSize="sm">Type: {asset.resource.type}</Text>
            {asset.resource.max_volume && (
              <Text fontSize="sm">Max Volume: {asset.resource.max_volume}µL</Text>
            )}
            {asset.resource.capacity && (
              <Text fontSize="sm">Capacity: {asset.resource.capacity}</Text>
            )}
          </Box>
        )}
      </Stack>
    </Box>
  );
};