import React from 'react';
import {
  Box,
  Heading,
  VStack,
  Text,
  HStack,
  createListCollection,
  Input
} from '@chakra-ui/react';
import { useToast } from "@chakra-ui/toast";
import { Avatar } from "@/components/ui/avatar";
import { Button } from '@/components/ui/button';
import { Field } from '@/components/ui/field';
import { Tabs, TabList, TabTrigger, TabContent } from '@/components/ui/tabs';
import {
  LuUser,
  LuPalette,
  LuFolderCog,
  LuShieldAlert,
  LuKey,
  LuUserPlus,
  LuUsers,
  LuDatabase,
  LuActivity
} from "react-icons/lu";
import { Card, CardBody } from '@/components/ui/card';
import { Fieldset, FieldsetContent, FieldsetLegend } from '@/components/ui/fieldset';
import { useColorMode } from '@/components/ui/color-mode';
import { useSelector } from 'react-redux';
import { RootState } from '../store';
import { useOidc } from '../oidc';
import { selectUserProfile, selectIsAdmin } from '../store/userSlice';

const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5MB
const ALLOWED_FILE_TYPES = ['image/jpeg', 'image/png', 'image/gif'];

const inputStyles = {
  width: '98%',  // Keep your current width
  margin: '0 auto',  // Add this to center the input
  display: 'block',  // Add this to ensure proper block layout
  border: '1px solid',
  borderColor: { base: 'brand.100', _dark: 'brand.700' },
  bg: { base: 'white', _dark: 'whiteAlpha.50' },
  _hover: {
    borderColor: { base: 'brand.200', _dark: 'brand.600' },
  },
  _focus: {
    zIndex: 1,
    borderColor: { base: 'brand.300', _dark: 'brand.500' },
    boxShadow: '0 0 0 3px var(--chakra-colors-brand-300)',
  },
}

const ProfileTab = React.memo(() => {
  const { goToAuthServer, backFromAuthServer } = useOidc({ assertUserLoggedIn: true });
  const { oidcTokens } = useOidc();
  const userProfile = selectUserProfile(oidcTokens?.decodedIdToken);

  return (
    <Card>
      <CardBody>
        <Fieldset defaultOpen>
          <FieldsetLegend>Profile Management</FieldsetLegend>
          <FieldsetContent>
            <VStack align="start" gap={4}>
              <HStack gap={4} width="full">
                <Avatar
                  size="xl"
                  name={userProfile.username}
                  src={userProfile.picture}
                />
                <VStack align="start" gap={2}>
                  <Button
                    visual="outline"
                    onClick={() => goToAuthServer({
                      extraQueryParams: { kc_action: "UPDATE_PROFILE" }
                    })}
                  >
                    Edit Profile
                  </Button>
                  <Text fontSize="sm" color="gray.600">
                    Edit your profile information on Keycloak
                  </Text>
                </VStack>
              </HStack>
            </VStack>
          </FieldsetContent>
        </Fieldset>
      </CardBody>
    </Card>
  );
});

const AppearanceTab = React.memo(() => (
  <Card>
    <CardBody>
      <Fieldset>
        <FieldsetLegend>Appearance Settings</FieldsetLegend>
        <FieldsetContent>
          <Text>Additional appearance settings will be available in future updates.</Text>
        </FieldsetContent>
      </Fieldset>
    </CardBody>
  </Card>
));

interface ProtocolsTabProps {
  directories: string[];
  onRemove: (dir: string) => void;
  onAdd: () => void;
}

const ProtocolsTab = React.memo(({ directories, onRemove, onAdd }: ProtocolsTabProps) => (
  <Card>
    <CardBody>
      <Fieldset>
        <FieldsetLegend>Protocol Directories</FieldsetLegend>
        <FieldsetContent>
          <VStack align="stretch" gap={4}>
            {directories.map((dir) => (
              <HStack key={dir} justify="space-between">
                <Text>{dir}</Text>
                <Button
                  size="sm"
                  visual="ghost"
                  color={{ base: 'brand.300', _dark: 'brand.100' }}
                  _hover={{
                    color: { base: 'white', _dark: 'brand.50' },
                    bg: { base: 'brand.300', _dark: 'brand.800' },
                  }}
                  onClick={() => onRemove(dir)}
                >
                  Remove
                </Button>
              </HStack>
            ))}
            <Button
              visual="outline"
              color={{ base: 'brand.300', _dark: 'brand.100' }}
              borderColor={{ base: 'brand.300', _dark: 'brand.100' }}
              _hover={{
                color: { base: 'white', _dark: 'brand.50' },
                bg: { base: 'brand.300', _dark: 'brand.800' },
              }}
              onClick={onAdd}
            >
              Add Directory
            </Button>
          </VStack>
        </FieldsetContent>
      </Fieldset>
    </CardBody>
  </Card>
));

const SecurityTab = React.memo(() => {
  const { goToAuthServer, backFromAuthServer } = useOidc({ assertUserLoggedIn: true });

  return (
    <Card>
      <CardBody>
        <Fieldset defaultOpen>
          <FieldsetLegend>Security Settings</FieldsetLegend>
          <FieldsetContent>
            <VStack gap={4}>
              <Button
                width="full"
                visual="solid"
                onClick={() => goToAuthServer({
                  extraQueryParams: { kc_action: "UPDATE_PASSWORD" }
                })}
              >
                Change Password
              </Button>
              {backFromAuthServer?.extraQueryParams.kc_action === "UPDATE_PASSWORD" && (
                <Text color={backFromAuthServer.result.kc_action_status === "success" ? "green.500" : "gray.500"}>
                  {backFromAuthServer.result.kc_action_status === "success"
                    ? "Password successfully updated"
                    : "Password unchanged"}
                </Text>
              )}
            </VStack>
          </FieldsetContent>
        </Fieldset>
      </CardBody>
    </Card>
  );
});

const UserManagement = () => (
  <Fieldset>
    <FieldsetLegend>User Management</FieldsetLegend>
    <FieldsetContent>
      <VStack align="stretch" gap={4}>
        <Button
          visual="outline"
        >
          <LuUserPlus size={16} />
          Invite New User
        </Button>
        <Button
          visual="outline"
        >
          <LuUsers size={16} />
          Manage Users
        </Button>
      </VStack>
    </FieldsetContent>
  </Fieldset>
);

const SystemSettings = () => (
  <Fieldset>
    <FieldsetLegend>System Settings</FieldsetLegend>
    <FieldsetContent>
      <VStack align="stretch" gap={4}>
        <Button
          visual="outline"
        >
          <LuDatabase size={16} />
          Database Configuration

        </Button>
        <Button
          visual="outline"
        >
          <LuActivity size={16} />
          View System Logs
        </Button>
      </VStack>
    </FieldsetContent>
  </Fieldset>
);

const AdminTab = React.memo(() => {
  const { oidcTokens } = useOidc();
  const userProfile = selectUserProfile(oidcTokens?.decodedIdToken);
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
});

// Fix the TabRenderer to properly render content
const TabRenderer = React.memo(({ tabContent, selectedTab }: {
  tabContent: Record<string, React.ReactNode>,
  selectedTab: string
}) => (
  <Box position="relative" minH="400px" w="full" mt={4}>
    {Object.entries(tabContent).map(([key, content]) => (
      <TabContent key={key} value={key} hidden={key !== selectedTab}>
        <Box p={4}>{content}</Box>
      </TabContent>
    ))}
  </Box>
));

const handleRemoveDirectory = (dir: string) => {
  // TODO: Implement API call to remove directory
  console.log('Removing directory:', dir);
}

const handleAddDirectory = () => {
  // TODO: Implement API call to add directory
  console.log('Adding directory');
}

export const Settings: React.FC = () => {
  const { oidcTokens } = useOidc();
  const userProfile = selectUserProfile(oidcTokens?.decodedIdToken);
  const isAdmin = selectIsAdmin(oidcTokens?.decodedIdToken);
  const [selectedTab, setSelectedTab] = React.useState('profile');
  const [directories, setDirectories] = React.useState<string[]>([]);
  const [avatarError, setAvatarError] = React.useState<string>('');
  const { colorMode } = useColorMode();

  React.useEffect(() => {

    const fetchDirectories = async () => {
      // TODO: Implement API call to fetch directories
      // For now, using mock data
      setDirectories(['/path/to/protocols', '/another/path']);
    };

    fetchDirectories();
  }, []);

  const handleTabChange = React.useCallback((details: { value: string }) => {
    setSelectedTab(details.value);
  }, []);


  const themeOptions = createListCollection({
    items: [
      { label: 'Use System Settings', value: 'system' },
      { label: 'Light Mode', value: 'light' },
      { label: 'Dark Mode', value: 'dark' }
    ],
  });

  const tabContent = React.useMemo(() => ({
    profile: (
      <ProfileTab />
    ),
    appearance: <AppearanceTab />,
    protocols: (
      <ProtocolsTab
        directories={directories}
        onRemove={handleRemoveDirectory}
        onAdd={handleAddDirectory}
      />
    ),
    security: <SecurityTab />,
    admin: <AdminTab />
  }), [
    userProfile, avatarError,
    directories, handleRemoveDirectory, handleAddDirectory,
  ]);

  const tabs = [
    { value: 'profile', label: 'Profile', icon: LuUser },
    { value: 'appearance', label: 'Appearance', icon: LuPalette },
    { value: 'protocols', label: 'Protocols', icon: LuFolderCog },
    { value: 'security', label: 'Security', icon: LuKey },
    ...(isAdmin ? [{ value: 'admin', label: 'Admin', icon: LuShieldAlert }] : []),
  ];

  return (
    <Box p={6}>
      <Heading
        size="lg"
        mb={6}
        color={{ base: 'brand.300', _dark: 'brand.100' }}
      >
        Settings
      </Heading>

      <Tabs
        value={selectedTab}
        onChange={handleTabChange}
      >
        <TabList>
          {tabs.map(({ value, label, icon: Icon }) => (
            <TabTrigger key={value} value={value}>
              <Icon size={16} />
              {label}
            </TabTrigger>
          ))}
        </TabList>
        <TabRenderer tabContent={tabContent} selectedTab={selectedTab} />
      </Tabs>
    </Box>
  );
};
