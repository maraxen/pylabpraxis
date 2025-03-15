import React from 'react';
import { VStack, Text } from '@chakra-ui/react';
import { Card, CardBody } from "@praxis-ui";
import { useOidc } from '../../../../oidc';
import { selectIsAdmin } from '../../../users/store/userSlice';
import UserManagement from './UserManagement';
import SystemSettings from './SystemSettings';

const AdminTab: React.FC = () => {
  const { oidcTokens } = useOidc();
  const isAdmin = selectIsAdmin(oidcTokens?.decodedIdToken);

  if (!isAdmin) {
    return (
      <Card>
        <CardBody>
          <Text color="red.500">You don't have permission to access admin settings.</Text>
        </CardBody>
      </Card>
    );
  }

  return (
    <VStack gap={6} align="stretch">
      <Card>
        <CardBody>
          <UserManagement />
        </CardBody>
      </Card>
      <Card>
        <CardBody>
          <SystemSettings />
        </CardBody>
      </Card>
    </VStack>
  );
};

export default AdminTab;