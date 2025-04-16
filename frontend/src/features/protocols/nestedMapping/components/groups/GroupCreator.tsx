import React, { useState, useRef, useEffect } from 'react';
import { Box, Input, ButtonGroup } from '@chakra-ui/react';
import { Button } from '@praxis-ui';
import { useNestedMapping } from '@protocols/contexts/nestedMappingContext';
import { GroupData } from '@shared/types/protocol';
import { LuPlus } from 'react-icons/lu';

interface GroupCreatorProps {
  value: Record<string, GroupData>;
}

const GroupCreator: React.FC<GroupCreatorProps> = ({ value }) => {
  const { createGroup, creationMode, setCreationMode, creatableKey } = useNestedMapping();
  const [groupName, setGroupName] = useState('');
  const inputRef = useRef<HTMLInputElement>(null);

  // Focus the input when entering creation mode
  useEffect(() => {
    if (creationMode === 'group' && inputRef.current) {
      inputRef.current.focus();
    }
  }, [creationMode]);

  // Handle creating a new group
  const handleCreateGroup = () => {
    if (groupName.trim()) {
      const displayName = groupName.trim();

      // Check for duplicate group name
      const duplicate = Object.values(value).some(
        (group) => group.name === displayName
      );

      if (duplicate) {
        alert(`Group name "${displayName}" already exists. Please choose a unique name.`);
        return;
      }

      // Create the group with the display name
      createGroup(displayName);

      // Reset the state
      setGroupName('');
      setCreationMode(null);
    }
  };

  // If not in creation mode, just show the button
  if (creationMode !== 'group') {
    return (
      <Button
        onClick={() => setCreationMode('group')}
        disabled={!creatableKey}
        _disabled={{ opacity: 0.5, cursor: 'not-allowed' }}
      >
        <LuPlus /> Add Group
      </Button>
    );
  }

  // In creation mode, show the form
  return (
    <Box mt={2}>
      <Input
        ref={inputRef}
        value={groupName}
        onChange={(e) => setGroupName(e.target.value)}
        placeholder="Enter group name"
        mb={2}
        onKeyDown={(e) => {
          if (e.key === 'Enter') {
            handleCreateGroup();
          } else if (e.key === 'Escape') {
            setCreationMode(null);
            setGroupName('');
          }
        }}
      />
      <ButtonGroup size="sm">
        <Button onClick={handleCreateGroup}>
          Create
        </Button>
        <Button
          visual="outline"
          onClick={() => {
            setCreationMode(null);
            setGroupName('');
          }}
        >
          Cancel
        </Button>
      </ButtonGroup>
    </Box>
  );
};

export default GroupCreator;