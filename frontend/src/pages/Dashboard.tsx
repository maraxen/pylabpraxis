import React from 'react';
import { Box, VStack, Heading, Button, HStack, Text } from '@chakra-ui/react';
import { useNavigate } from 'react-router-dom';
import { useOidc } from '../oidc';
import { selectUserProfile } from '../store/userSlice';

export const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const { oidcTokens } = useOidc();
  const userProfile = selectUserProfile(oidcTokens?.decodedIdToken);

  return (
    <VStack gap={4} align="stretch" maxW="container.xl" mx="auto">
      <Box bg="white" p="6" borderRadius="lg" shadow="sm" color={{ base: "brand.500", _dark: "brand.50" }}>
        <Heading size="lg" mb="6">
          Welcome to Praxis
        </Heading>
        <Text>Select an action to get started:</Text>

        <HStack mt="6" gap={4}>
          <Button colorScheme="brand">View Protocols</Button>
          {userProfile.isAdmin && (
            <Button
              colorScheme="brand"
              variant="outline"
              onClick={() => navigate('/manage-users')}
            >
              Manage Users
            </Button>
          )}
        </HStack>
      </Box>
    </VStack >
  );
};
