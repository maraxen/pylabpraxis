import React from 'react';
import { Box, Flex, HStack, Text, Button, Heading } from '@chakra-ui/react';
import { Avatar } from "@/components/ui/avatar"
import { useNavigate } from 'react-router-dom';
import { authService } from '../services/auth';
import {
  LuPlay,
  LuDatabase,
  LuChartArea,
  LuBook
} from "react-icons/lu";
import { useAppDispatch, useAppSelector } from '../hooks/redux';
import {
  logout,
  selectUserProfile,
  selectIsAuthenticated,
  selectIsLoading,
  selectErrors
} from '../store/userSlice';
import { LoadingOverlay } from './LoadingOverlay';

interface LayoutProps {
  children: React.ReactNode;
}

export const Layout: React.FC<LayoutProps> = ({ children }) => {
  const navigate = useNavigate();
  const dispatch = useAppDispatch();
  const { username, isAdmin, avatarUrl } = useAppSelector(selectUserProfile);
  const isAuthenticated = useAppSelector(selectIsAuthenticated);
  const isLoading = useAppSelector(selectIsLoading);
  const errors = useAppSelector(selectErrors);

  const handleLogout = () => {
    dispatch(logout());
    navigate('/login');
  };

  const navItems = [
    { path: '/protocols', label: 'Run Protocols', icon: LuPlay },
    { path: '/databases', label: 'Manage Databases', icon: LuDatabase },
    { path: '/vixn', label: 'Vixn', icon: LuChartArea },
    { path: '/docs', label: 'Documentation', icon: LuBook },
  ];

  const currentPath = window.location.pathname;

  return (
    <Box minH="100vh" bg={{ base: 'white', _dark: 'gray.900' }}>
      {isLoading && <LoadingOverlay />}
      <Flex
        direction="column"
        width="full"
        bg={{ base: 'white', _dark: 'gray.800' }}
        borderBottomWidth="1px"
        borderColor={{ base: 'brand.100', _dark: 'brand.700' }}
      >
        <Flex
          height="16"
          alignItems="center"
          px="6"
          justify="space-between"
        >
          <Heading
            size="md"
            cursor="pointer"
            onClick={() => navigate('/')}
            color={{ base: 'brand.300', _dark: 'brand.100' }}
            _hover={{ color: { base: 'brand.400', _dark: 'brand.50' } }}
          >
            Praxis
          </Heading>
          <HStack gap={4}>
            <HStack>
              <Text color={{ base: 'brand.300', _dark: 'brand.100' }}>{username}</Text>
              <Avatar
                size="sm"
                name={username}
                src={avatarUrl}
                cursor="pointer"
                onClick={() => navigate('/settings')}
              />
            </HStack>
            <Button
              variant="ghost"
              color={{ base: 'brand.300', _dark: 'brand.100' }}
              _hover={{
                color: { base: 'white', _dark: 'brand.50' },
                bg: { base: 'brand.300', _dark: 'brand.800' },
              }}
              onClick={() => navigate('/settings')}
            >
              Settings
            </Button>
            <Button
              variant="outline"
              color={{ base: 'brand.300', _dark: 'brand.100' }}
              borderColor={{ base: 'brand.300', _dark: 'brand.100' }}
              _hover={{
                color: { base: 'white', _dark: 'brand.50' },
                bg: { base: 'brand.300', _dark: 'brand.800' },
                borderColor: { base: 'brand.300', _dark: 'brand.100' }
              }}
              onClick={handleLogout}
            >
              Logout
            </Button>
          </HStack>
        </Flex>

        <HStack px="6" height="12" gap={8}>
          {navItems.map(({ path, label, icon: Icon }) => (
            <Button
              key={path}
              variant="ghost"
              size="sm"
              onClick={() => navigate(path)}
              color={currentPath === path
                ? { base: 'brand.300', _dark: 'brand.100' }
                : { base: 'brand.600', _dark: 'brand.300' }
              }
              _hover={{
                color: { base: 'white', _dark: 'brand.50' },
                bg: { base: 'brand.300', _dark: 'brand.800' },
              }}
            >
              <Icon size={20} />
              {label}
            </Button>
          ))}
        </HStack>
      </Flex>

      {errors.fetchUser && (
        <Text
          color={{ base: 'red.500', _dark: 'red.300' }}
          fontSize="sm"
          px={6}
        >
          Error: {errors.fetchUser}
        </Text>
      )}

      <Box
        as="main"
        p="6"
        bg={{ base: 'gray.50', _dark: 'gray.900' }}
      >
        {children}
      </Box>

      <Flex
        as="footer"
        width="full"
        height="12"
        alignItems="center"
        px="6"
        bg={{ base: 'white', _dark: 'gray.800' }}
        borderTopWidth="1px"
        borderColor={{ base: 'brand.100', _dark: 'brand.700' }}
        justify="space-between"
        position="fixed"
        bottom="0"
      >
        <Text
          fontSize="sm"
          color={{ base: 'brand.300', _dark: 'brand.100' }}
        >
          Logged in as {username}
        </Text>
        <Text
          fontSize="sm"
          color={{ base: 'brand.300', _dark: 'brand.100' }}
        >
          System Status: OK
        </Text>
      </Flex>
    </Box>
  );
};
