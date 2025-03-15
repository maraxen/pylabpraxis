import React from 'react';
import { Box, Heading } from '@chakra-ui/react';
import { Tabs, TabList, TabTrigger, TabRenderer } from "@praxis-ui";
import {
  LuUser,
  LuPalette,
  LuFolderCog,
  LuShieldAlert,
  LuKey,
} from "react-icons/lu";
import { useOidc } from '../../../oidc';
import { selectIsAdmin } from '../../users/store/userSlice';

// Import tab components
import ProfileTab from '../components/profile/ProfileTab';
import AppearanceTab from '../components/appearance/AppearanceTab';
import ProtocolsTab from '../components/protocols/ProtocolsTab';
import SecurityTab from '../components/security/SecurityTab';
import AdminTab from '../components/admin/AdminTab';

export const Settings: React.FC = () => {
  const { oidcTokens } = useOidc();
  const isAdmin = selectIsAdmin(oidcTokens?.decodedIdToken);
  const [selectedTab, setSelectedTab] = React.useState('profile');
  const [directories, setDirectories] = React.useState<string[]>([]);

  React.useEffect(() => {
    const fetchDirectories = async () => {
      // TODO: Implement API call to fetch directories
      setDirectories(['/path/to/protocols', '/another/path']);
    };

    fetchDirectories();
  }, []);

  const handleTabChange = React.useCallback((details: { value: string }) => {
    setSelectedTab(details.value);
  }, []);

  const handleRemoveDirectory = (dir: string) => {
    // TODO: Implement API call to remove directory
    setDirectories(prev => prev.filter(d => d !== dir));
  };

  const handleAddDirectory = () => {
    // TODO: Implement API call to add directory
    setDirectories(prev => [...prev, '/new/path']);
  };

  const tabContent = React.useMemo(() => ({
    profile: <ProfileTab />,
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
  }), [directories]);

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
