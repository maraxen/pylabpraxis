import React from 'react';
import {
  Box,
  Heading,
  VStack,
  Button,
  Table,
} from '@chakra-ui/react';

export const ManageUsers: React.FC = () => {
  return (
    <Box p={6}>
      <VStack align="stretch" gap={6}>
        <Heading size="lg">Manage Users</Heading>
        <Button colorScheme="brand" alignSelf="flex-start">
          Add New User
        </Button>
        <Table.Root variant={"outline"}>
          <Table.Header>
            <Table.Row>
              <Table.ColumnHeader>Username</Table.ColumnHeader>
              <Table.ColumnHeader>Status</Table.ColumnHeader>
              <Table.ColumnHeader>Actions</Table.ColumnHeader>
            </Table.Row>
          </Table.Header>
          <Table.Body>
            <Table.Row>
              <Table.Cell>example_user</Table.Cell>
              <Table.Cell>Active</Table.Cell>
              <Table.Cell>
                <Button size="sm" variant="outline">
                  Edit
                </Button>
              </Table.Cell>
            </Table.Row>
          </Table.Body>
        </Table.Root>
      </VStack>
    </Box>
  );
};
