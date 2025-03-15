import React from 'react';
import { HStack, Text } from '@chakra-ui/react';

import { GroupInputField } from './GroupInputField';
import { GroupBadges } from './GroupBadges';
import { GroupValueLimit } from './GroupValueLimit';
import { GroupActions } from './GroupActions';



interface GroupHeaderProps {
  groupId: string;
  groupName: string;
  isEditingName: boolean;
  startEditingName: () => void;
  saveGroupName: (name: string) => void;
  cancelEditName: () => void;
  groupEditable: boolean;
  hasParameterValues: boolean;
  allowDelete: boolean;
  onDelete?: () => void;
  keyConstraints: Record<string, any>;
  constraints: Record<string, any>;
}

export const GroupHeader: React.FC<GroupHeaderProps> = ({
  groupId,
  groupName,
  isEditingName,
  startEditingName,
  saveGroupName,
  cancelEditName,
  groupEditable,
  hasParameterValues,
  allowDelete,
  onDelete,
  keyConstraints,
  constraints
}) => {
  return (
    <HStack justify="space-between" mb={2}>
      <HStack>
        {/* Group name with inline editing */}
        {isEditingName ? (
          <GroupInputField
            initialValue={groupName}
            onSave={saveGroupName}
            onCancel={cancelEditName}
          />
        ) : (
          <Text
            fontWeight="medium"
            cursor={groupEditable ? "pointer" : "default"}
            onClick={startEditingName}
            _hover={groupEditable ? { textDecoration: "underline" } : {}}
          >
            {groupName}
          </Text>
        )}

        {/* Group value limit */}
        <GroupValueLimit groupId={groupId} />

        {/* Group metadata badges */}
        <GroupBadges
          groupEditable={groupEditable}
          hasParameterValues={hasParameterValues}
          keyConstraints={keyConstraints}
          constraints={constraints}
        />
      </HStack>

      {/* Action buttons */}
      <GroupActions
        groupEditable={groupEditable}
        isEditingName={isEditingName}
        allowDelete={allowDelete}
        onDelete={onDelete}
        startEditingName={startEditingName}
      />
    </HStack>
  );
};