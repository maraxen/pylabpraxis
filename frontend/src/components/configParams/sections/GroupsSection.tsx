import React from 'react';
import { Box, VStack, SimpleGrid, Text, Heading } from '@chakra-ui/react';
import { GroupItem } from '../subcomponents/GroupItem';
import { GroupCreator } from '../creators/GroupCreator';
import { useNestedMapping } from '../contexts/nestedMappingContext';
import { GroupData } from '../utils/parameterUtils';

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
  const sortedGroups = Object.entries(value).sort((a, b) => {
    const nameA = a[1].name?.toLowerCase() || '';
    const nameB = b[1].name?.toLowerCase() || '';
    return nameA.localeCompare(nameB);
  });

  return (
    <Box>
      <VStack align="stretch" spacing={4}>
        <Box px={1}>
          <Heading size="sm" mb={2}>Groups</Heading>

          <GroupCreator value={value} />
        </Box>

        {sortedGroups.length > 0 ? (
          <SimpleGrid columns={1} spacing={4}>
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
