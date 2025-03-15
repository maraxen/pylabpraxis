import React from 'react';
import { HStack } from '@chakra-ui/react';
import { StatusBadge } from '@praxis-ui';

interface GroupBadgesProps {
  groupEditable: boolean;
  hasParameterValues: boolean;
  keyConstraints?: Record<string, any>;
  constraints?: Record<string, any>;
}

export const GroupBadges: React.FC<GroupBadgesProps> = ({
  groupEditable,
  hasParameterValues,
  keyConstraints,
  constraints
}) => {
  // Display the type badge if available
  const keyType = keyConstraints?.type
    ? String(keyConstraints.type).toLowerCase()
    : 'string';

  return (
    <HStack gap={1}>
      {/* Editable status badge */}
      <StatusBadge
        status={groupEditable ? 'editable' : 'readonly'}
        variant="subtle"
        size="sm"
      />

      {/* Parameter values badge */}
      {hasParameterValues && (
        <StatusBadge
          status="parameter"
          variant="subtle"
          size="sm"
          tooltip="Contains parameter-driven values"
        />
      )}

      {/* Type badge if specified */}
      {keyType && keyType !== 'string' && (
        <StatusBadge
          status="type"
          label={keyType}
          variant="subtle"
          size="sm"
          tooltip={`Group key type: ${keyType}`}
        />
      )}

      {/* Show constraints badge if constraints are applied */}
      {constraints && Object.keys(constraints).length > 0 && (
        <StatusBadge
          status="type"
          label="constrained"
          variant="subtle"
          size="sm"
          colorScheme="purple"
          tooltip="This group has constraints on its values"
        />
      )}
    </HStack>
  );
};