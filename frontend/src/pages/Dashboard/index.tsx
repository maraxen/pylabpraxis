import React from 'react';
import { Box, VStack, Heading, Text } from '@chakra-ui/react';
import { useSelector } from 'react-redux';
import { RootState } from '../../store';

export const Dashboard: React.FC = () => {
  const user = useSelector((state: RootState) => state.auth.user);

  return (
    <VStack columnGap={6} align="stretch">
      <Box bg="white" p={6} borderRadius="lg" shadow="sm">
        <Heading size="lg" mb={4}>Welcome, {user?.username}</Heading>
        <Text>Select an action from the navigation menu to get started.</Text>
      </Box>
    </VStack>
  );
};
