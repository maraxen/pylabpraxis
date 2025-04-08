import React from 'react';
import { Box, Flex, HStack, Text, Heading, Icon } from '@chakra-ui/react';
import { Button, Avatar, Tabs, TabList, TabTrigger } from '@praxis-ui';
import { useNavigate } from 'react-router-dom';
import {
  LuPlay,
  LuDatabase,
  LuChartArea,
  LuBook,
  LuSettings,
  LuFlaskConical,
} from "react-icons/lu";
import { useOidc } from '../../../oidc';
import { selectUserProfile } from '../../../features/users/store/userSlice';

const navItems = [
  { path: '/protocols', label: 'Run Protocols', icon: LuPlay },
  { path: '/assets', label: 'Manage Assets', icon: LuFlaskConical },
  { path: '/databases', label: 'Manage Databases', icon: LuDatabase },
  { path: '/vixn', label: 'Vixn', icon: LuChartArea },
  { path: '/docs', label: 'Documentation', icon: LuBook },
];

export const Navbar: React.FC = () => {
  const navigate = useNavigate();
  const { decodedIdToken, tokens, logout, goToAuthServer } = useOidc({ assert: "user logged in" });
  const currentPath = window.location.pathname;
  const userProfile = selectUserProfile(decodedIdToken);

  const handleLogout = () => {
    logout({ redirectTo: "current page" });
  };

  const handleProfileClick = () => {
    goToAuthServer({
      extraQueryParams: { kc_action: "UPDATE_PROFILE" }
    });
  };

  return (
    <Box bg={{ base: 'white', _dark: 'gray.800' }} shadow="sm">
      <Flex height="16" alignItems="center" px="6" justify="space-between">
        <Heading
          size="md"
          cursor="pointer"
          onClick={() => navigate('/home')}
          color={{ base: 'brand.300', _dark: 'brand.100' }}
        >
          Praxis
        </Heading>

        <HStack gap={4}>
          <HStack>
            <Text
              color={{ base: 'brand.300', _dark: 'brand.100' }}
              cursor="pointer"
              onClick={handleProfileClick}
            >
              {userProfile.username}
            </Text>
            <Avatar
              size="sm"
              name={userProfile.username}
              src={userProfile.picture}
              cursor="pointer"
              onClick={handleProfileClick}
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
