import React from 'react';
import { Box, Flex, HStack, Text, Heading, Icon } from '@chakra-ui/react';
import { Button } from './ui/button';
import { Avatar } from "./ui/avatar"
import { useNavigate } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { logout } from '../store/authSlice';
import { RootState } from '../store';
import {
  LuPlay,
  LuDatabase,
  LuChartArea,
  LuBook,
  LuSettings,
} from "react-icons/lu";
import { Tabs, TabList, TabTrigger } from './ui/tabs';

const navItems = [
  { path: '/protocols', label: 'Run Protocols', icon: LuPlay },
  { path: '/databases', label: 'Manage Databases', icon: LuDatabase },
  { path: '/vixn', label: 'Vixn', icon: LuChartArea },
  { path: '/docs', label: 'Documentation', icon: LuBook },
];

export const Navbar: React.FC = () => {
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const user = useSelector((state: RootState) => state.auth.user);
  const currentPath = window.location.pathname;

  const handleLogout = () => {
    dispatch(logout());
    navigate('/login', { replace: true });
  };

  return (
    <Box bg={{ base: 'white', _dark: 'gray.800' }} shadow="sm">
      <Flex height="16" alignItems="center" px="6" justify="space-between">
        <Heading
          size="md"
          cursor="pointer"
          onClick={() => navigate('/')}
          color={{ base: 'brand.300', _dark: 'brand.100' }}
        >
          Praxis
        </Heading>

        <HStack gap={4}>
          <HStack>
            <Text color={{ base: 'brand.300', _dark: 'brand.100' }}>
              {user?.username}
            </Text>
            <Avatar
              size="sm"
              name={user?.username}
              src={user?.picture}
              cursor="pointer"
              onClick={() => navigate('/settings')}
            />
          </HStack>
          <Button
            visual="ghost"
            size="sm"
            onClick={() => navigate('/settings')}
          >
            <Icon as={LuSettings} boxSize={4} marginRight={2} />
            Settings
          </Button>
          <Button
            visual="outline"
            size="sm"
            onClick={handleLogout}
          >
            Logout
          </Button>
        </HStack>
      </Flex>

      <Tabs value={currentPath} onChange={(details) => navigate(details.value)}>
        <TabList>
          {navItems.map(({ path, label, icon: Icon }) => (
            <TabTrigger key={path} value={path}>
              <Icon size={16} />
              {label}
            </TabTrigger>
          ))}
        </TabList>
      </Tabs>
    </Box>
  );
};
