import React from 'react';
import { Box, Flex, HStack, Text, Button, Heading } from '@chakra-ui/react';
import { Avatar } from "@/components/ui/avatar"
import { useNavigate } from 'react-router-dom';
import { authService } from '../services/auth';

interface LayoutProps {
  children: React.ReactNode;
}

export const Layout: React.FC<LayoutProps> = ({ children }) => {
  const navigate = useNavigate();
  const [user, setUser] = React.useState<{ username: string; is_admin: boolean; avatarUrl?: string } | null>(null);

  React.useEffect(() => {
    const fetchUser = async () => {
      const userData = await authService.getCurrentUser();
      setUser(userData);
    };
    fetchUser();
  }, []);

  const handleLogout = () => {
    authService.logout();
    navigate('/login');
  };

  return (
    <Box minH="100vh" bg="gray.50">
      <Flex
        as="header"
        width="full"
        height="16"
        alignItems="center"
        px="6"
        bg="white"
        borderBottomWidth="1px"
        borderColor="gray.200"
        justify="space-between"
      >
        <Heading size="md" cursor="pointer" onClick={() => navigate('/')}>
          Praxis
        </Heading>
        <HStack gap={4}>
          <HStack>
            <Text>{user?.username}</Text>
            <Avatar
              size="sm"
              name={user?.username}
              src={user?.avatarUrl || undefined}
              cursor="pointer"
              onClick={() => navigate('/settings')}
            />
          </HStack>
          <Button variant="ghost" onClick={() => navigate('/settings')}>
            Settings
          </Button>
          <Button variant="outline" onClick={handleLogout}>
            Logout
          </Button>
        </HStack>
      </Flex>

      <Box as="main" p="6">
        {children}
      </Box>

      <Flex
        as="footer"
        width="full"
        height="12"
        alignItems="center"
        px="6"
        bg="white"
        borderTopWidth="1px"
        borderColor="gray.200"
        justify="space-between"
        position="fixed"
        bottom="0"
      >
        <Text fontSize="sm" color="gray.600">
          Logged in as {user?.username}
        </Text>
        <Text fontSize="sm" color="gray.600">
          System Status: OK
        </Text>
      </Flex>
    </Box>
  );
};
