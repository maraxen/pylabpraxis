import React from 'react';
import { HStack } from '@chakra-ui/react';
import { ActionButton } from '@praxis-ui';

interface GroupActionsProps {
  groupEditable: boolean;
  isEditingName: boolean;
  allowDelete: boolean;
  onDelete?: () => void;
  startEditingName: () => void;
}

export const GroupActions: React.FC<GroupActionsProps> = ({
  groupEditable,
  isEditingName,
  allowDelete,
  onDelete,
  startEditingName
}) => {
  return (
    <HStack gap={1}>
      {/* Edit group name button */}
      {!isEditingName && groupEditable && (
        <ActionButton
          action="edit"
          onClick={startEditingName}
          label="Edit group name"
          testId="edit-group-button"
          size="sm"
        />
      )}

      {/* Delete group button */}
      {allowDelete && !isEditingName && (
        <ActionButton
          action="remove"
          onClick={onDelete}
          label="Delete group"
          testId="delete-group-button"
          size="sm"
          colorScheme="red"
        />
      )}
    </HStack>
  );
};