import React from 'react';
import { Box, VStack, SimpleGrid, Text, Heading, HStack } from '@chakra-ui/react';
import { GroupItem } from '../molecules/GroupItem';
import { GroupCreator } from '../molecules/groupCreator';
import { useNestedMapping } from '../contexts/nestedMappingContext';
import { GroupData } from '../../utils/parameterUtils';
import { GroupLimit, ValueLimit } from '../../../../shared/components/ui/LimitCounter';

interface GroupsSectionProps {
  value: Record<string, GroupData>;
  onChange: (value: Record<string, GroupData>) => void;
}

export const GroupsSection: React.FC<GroupsSectionProps> = ({ value, onChange }) => {
  const { dragInfo } = useNestedMapping();

  // Handle deleting a group
  const handleDeleteGroup = (groupId: string) => {
    const { [groupId]: _, ...rest } = value;
    onChange(rest);
  };

  // Sort groups by name
  const sortedGroups = Object.entries(value);

  return (
    <Box>
      <VStack align="stretch" gap={4}>
        <Box px={1}>
          <HStack justifyContent="space-between" mb={2}>
            <Heading size="sm">Groups</Heading>

            <HStack gap={2}>
              <GroupLimit />
              <ValueLimit />
            </HStack>
          </HStack>

          <GroupCreator value={value} />
        </Box>

        {sortedGroups.length > 0 ? (
          <SimpleGrid columns={1} gap={4}>
            {sortedGroups.map(([groupId, group]) => (
              <GroupItem
                key={groupId}
                groupId={groupId}
                group={group}
                onDelete={() => handleDeleteGroup(groupId)}
                isHighlighted={dragInfo.overDroppableId === groupId}
              />
            ))}
          </SimpleGrid>
        ) : (
          <Box py={8} textAlign="center">
            <Text color="gray.500">
              No groups defined. Create a group to organize your values.
            </Text>
          </Box>
        )}
      </VStack>
    </Box>
  );
};
