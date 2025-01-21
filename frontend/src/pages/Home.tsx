import React from 'react';
import { Box, VStack, Heading, Button, HStack, Text } from '@chakra-ui/react';
import { useNavigate } from 'react-router-dom';
import { authService } from '../services/auth';

export const Home: React.FC = () => {
  const navigate = useNavigate();
  const [user, setUser] = React.useState<{ username: string; is_admin: boolean } | null>(null);

  React.useEffect(() => {
    const fetchUser = async () => {
      const userData = await authService.getCurrentUser();
      setUser(userData);
    };
    fetchUser();
  }, []);

  return (
    <VStack gap={4} align="stretch" maxW="container.xl" mx="auto">
      <Box bg="white" p="6" borderRadius="lg" shadow="sm">
        <Heading size="lg" mb="6">
          Welcome to Praxis
        </Heading>
        <Text>Select an action to get started:</Text>

        <HStack mt="6" gap={4}>
          <Button colorScheme="brand">View Protocols</Button>
          {user?.is_admin && (
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
    </VStack>
  );
};
