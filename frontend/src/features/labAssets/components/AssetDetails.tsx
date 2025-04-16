import React from 'react';
import {
  Box,
  Heading,
  Text,
  Flex,
  Icon,
  Accordion,
  Grid,
} from '@chakra-ui/react';
import { Separator } from '@chakra-ui/react';
import { LuFlaskConical, LuCpu, LuCircleCheck, LuCircleX } from 'react-icons/lu';
import { ActionButton } from "@praxis-ui";
import { StatusBadge } from '@shared/components/ui/StatusBadge';
import { Asset, DetailedAsset } from '../types/asset';

const cardBg = 'white'; // Define card background color
const borderColor = 'gray.200'; // Define border color
const headingColor = 'gray.700'; // Define heading color

interface AssetDetailsProps {
  asset: DetailedAsset;
  onEdit?: (asset: Asset) => void;
  onDelete?: (asset: Asset) => void;
}

export const AssetDetails: React.FC<AssetDetailsProps> = ({
  asset,
  onEdit,
  onDelete
}) => {

  // Determine asset icon based on type
  const AssetIcon = asset.type.toLowerCase().includes('machine') ? LuCpu : LuFlaskConical;

  const renderObjectProperties = (obj: Record<string, any>, depth: number = 0) => {
    if (!obj || typeof obj !== 'object' || Array.isArray(obj)) {
      return <Text>{JSON.stringify(obj)}</Text>;
    }

    return (
      <Box pl={depth > 0 ? 4 : 0}>
        {Object.entries(obj).map(([key, value]) => {
          const isObject = value !== null && typeof value === 'object' && !Array.isArray(value);

          return (
            <Box key={key} mb={2}>
              <Text fontWeight="medium">{key}:</Text>
              {isObject ? (
                renderObjectProperties(value, depth + 1)
              ) : (
                <Text pl={2} fontSize="sm">
                  {Array.isArray(value)
                    ? JSON.stringify(value)
                    : String(value)
                  }
                </Text>
              )}
            </Box>
          );
        })}
      </Box>
    );
  };

  return (
    <Box
      bg={cardBg}
      borderWidth="1px"
      borderStyle="solid"
      borderColor={borderColor}
      borderRadius="lg"
      overflow="hidden"
      p={6}
      shadow="md"
    >
      <Flex justifyContent="space-between" alignItems="center" mb={4}>
        <Flex alignItems="center">
          <Icon as={AssetIcon} boxSize={6} color={headingColor} mr={3} />
          <Heading size="lg" color={headingColor}>{asset.name}</Heading>
        </Flex>
        <StatusBadge
          status={asset.is_available ? 'editable' : 'readonly'}
          label={asset.is_available ? 'Available' : 'In Use'}
          tooltip={asset.is_available ? 'This asset is available for use' : 'This asset is currently in use'}
        />
      </Flex>

      {asset.description && (
        <Text fontSize="md" mb={5} fontStyle="italic">
          {asset.description}
        </Text>
      )}

      <Grid templateColumns={{ base: '1fr', md: 'repeat(2, 1fr)' }} gap={4} mb={5}>
        <Flex align="center">
          <Text fontWeight="bold" mr={2}>Type:</Text>
          <Text>{asset.type}</Text>
        </Flex>

        <Flex align="center">
          <Text fontWeight="bold" mr={2}>Status:</Text>
          <Flex align="center">
            <Icon
              as={asset.is_available ? LuCircleCheck : LuCircleX}
              color={asset.is_available ? 'green.500' : 'red.500'}
              mr={1}
            />
            <Text>{asset.is_available ? 'Available' : 'In Use'}</Text>
          </Flex>
        </Flex>

        {asset.lock_expires_at && !asset.is_available && (
          <Flex align="center">
            <Text fontWeight="bold" mr={2}>Lock Expires:</Text>
            <Text>{new Date(asset.lock_expires_at).toLocaleString()}</Text>
          </Flex>
        )}

        {asset.created_at && (
          <Flex align="center">
            <Text fontWeight="bold" mr={2}>Created:</Text>
            <Text>{new Date(asset.created_at).toLocaleString()}</Text>
          </Flex>
        )}

        {asset.updated_at && (
          <Flex align="center">
            <Text fontWeight="bold" mr={2}>Last Updated:</Text>
            <Text>{new Date(asset.updated_at).toLocaleString()}</Text>
          </Flex>
        )}
      </Grid>

      <Separator my={5} />

      {/* Updated Accordion section following Chakra UI documentation */}
      <Accordion.Root collapsible defaultValue={["metadata"]}>
        <Accordion.Item value="metadata">
          <Accordion.ItemTrigger>
            <Box as="span" flex="1" textAlign="left">
              <Heading size="md">Metadata</Heading>
            </Box>
            <Accordion.ItemIndicator />
          </Accordion.ItemTrigger>
          <Accordion.ItemContent>
            <Accordion.ItemBody>{renderObjectProperties(asset.metadata)}</Accordion.ItemBody>
          </Accordion.ItemContent>
        </Accordion.Item>
        {asset.plr_serialized && (
          <Accordion.Item value="plr_serialized">
            <Accordion.ItemTrigger>
              <Box as="span" flex="1" textAlign="left">
                <Heading size="md">PyLabRobot Configuration</Heading>
              </Box>
              <Accordion.ItemIndicator />
            </Accordion.ItemTrigger>
            <Accordion.ItemContent>
              <Accordion.ItemBody>{renderObjectProperties(asset.plr_serialized)}</Accordion.ItemBody>
            </Accordion.ItemContent>
          </Accordion.Item>
        )}
      </Accordion.Root>

      <Flex justifyContent="flex-end" mt={6} gap={4}>
        {onEdit && (
          <ActionButton
            action="edit"
            size="md"
            onClick={() => onEdit(asset)}
            testId="edit-asset-button"
          />
        )}

        {onDelete && (
          <ActionButton
            action="remove"
            size="md"
            colorScheme="red"
            onClick={() => onDelete(asset)}
            testId="delete-asset-button"
          />
        )}
      </Flex>
    </Box>
  );
};

export default AssetDetails;