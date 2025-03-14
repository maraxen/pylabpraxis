import React from 'react';
import { VStack, Button } from '@chakra-ui/react';
import { Fieldset, FieldsetContent, FieldsetLegend } from "@atoms";
import { LuUserPlus, LuUsers } from "react-icons/lu";

const UserManagement: React.FC = () => (
  <Fieldset>
    <FieldsetLegend>User Management</FieldsetLegend>
    <FieldsetContent>
      <VStack align="stretch" gap={4}>
        <Button visual="outline">
          <LuUserPlus size={16} />
          Invite New User
        </Button>
        <Button visual="outline">
          <LuUsers size={16} />
          Manage Users
        </Button>
      </VStack>
    </FieldsetContent>
  </Fieldset>
);

export default UserManagement;