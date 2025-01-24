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
import { authService } from '../services/auth';
import {
  LuUser,
  LuPalette,
  LuFolderCog,
  LuShieldAlert,
  LuKey
} from "react-icons/lu";
import { Card, CardBody } from '@/components/ui/card';
import { Fieldset, FieldsetContent, FieldsetLegend } from '@/components/ui/fieldset';
import { useColorMode } from '@/components/ui/color-mode';

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

const SecurityForm = React.memo(({
  onSubmit,
  currentPassword,
  setCurrentPassword,
  newPassword,
  setNewPassword,
  confirmPassword,
  setConfirmPassword,
  error
}: {
  onSubmit: (e: React.FormEvent) => void;
  currentPassword: string;
  setCurrentPassword: (value: string) => void;
  newPassword: string;
  setNewPassword: (value: string) => void;
  confirmPassword: string;
  setConfirmPassword: (value: string) => void;
  error?: string | null;
}) => {
  const handleChange = React.useCallback((setter: (value: string) => void) =>
    (e: React.ChangeEvent<HTMLInputElement>) => setter(e.target.value),
    []
  );

  return (
    <form onSubmit={onSubmit}>
      <Fieldset defaultOpen>
        <FieldsetLegend>Change Password</FieldsetLegend>
        <FieldsetContent>
          <VStack gap={4}>
            {error && (
              <Text color="red.500" fontSize="sm" width="full">
                {error}
              </Text>
            )}
            <Field label="Current Password">
              <Input
                type="password"
                value={currentPassword}
                onChange={handleChange(setCurrentPassword)}
                size="md"
                required
                {...inputStyles}
              />
            </Field>
            <Field label="New Password">
              <Input
                type="password"
                value={newPassword}
                onChange={handleChange(setNewPassword)}
                size="md"
                required
                {...inputStyles}
              />
            </Field>
            <Field label="Confirm New Password">
              <Input
                type="password"
                value={confirmPassword}
                onChange={handleChange(setConfirmPassword)}
                size="md"
                required
                {...inputStyles}
              />
            </Field>
            <Button
              type="submit"
              visual="solid"
              width="full"
              mt={2}
            >
              Change Password
            </Button>
          </VStack>
        </FieldsetContent>
      </Fieldset>
    </form>
  );
});

SecurityForm.displayName = 'SecurityForm';

interface ProfileTabProps {
  user: { username: string; avatarUrl?: string } | null;
  onAvatarChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  avatarError: string;
}

const ProfileTab = React.memo(({ user, onAvatarChange, avatarError }: ProfileTabProps) => (
  <Card>
    <CardBody>
      <Fieldset defaultOpen>
        <FieldsetLegend>Profile</FieldsetLegend>
        <FieldsetContent>
          <VStack align="start" gap={4}>
            <HStack gap={4} width="full">
              <Avatar
                size="xl"
                name={user?.username}
                src={user?.avatarUrl}
              />
              <VStack align="start" gap={2}>
                <label htmlFor="avatar-upload">
                  <Button
                    visual="outline"
                    cursor="pointer"
                    as="span"
                  >
                    Change Avatar
                  </Button>
                  <input
                    id="avatar-upload"
                    type="file"
                    accept="image/*"
                    style={{ display: 'none' }}
                    onChange={onAvatarChange}
                  />
                </label>
                {avatarError && (
                  <Text color="red.500" fontSize="sm">
                    {avatarError}
                  </Text>
                )}
                <Text fontSize="sm" color="brand.500">
                  Supported formats: JPEG, PNG, GIF (max. 5MB)
                </Text>
              </VStack>
            </HStack>
          </VStack>
        </FieldsetContent>
      </Fieldset>
    </CardBody>
  </Card>
));

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
  const [currentPassword, setCurrentPassword] = React.useState('');
  const [newPassword, setNewPassword] = React.useState('');
  const [confirmPassword, setConfirmPassword] = React.useState('');
  const [error, setError] = React.useState<string | null>(null);
  const toast = useToast();

  const validatePasswords = React.useCallback(() => {
    if (newPassword.length < 8) {
      setError('New password must be at least 8 characters');
      return false;
    }
    if (newPassword !== confirmPassword) {
      setError('Passwords do not match');
      return false;
    }
    setError(null);
    return true;
  }, [newPassword, confirmPassword]);

  const handleSubmit = React.useCallback((e: React.FormEvent) => {
    e.preventDefault();
    if (!validatePasswords()) return;

    // TODO: Implement actual password change
    toast({
      title: 'Password Changed',
      description: 'Your password has been updated successfully.',
      status: 'success',
      duration: 3000,
      isClosable: true,
    });

    // Clear form
    setCurrentPassword('');
    setNewPassword('');
    setConfirmPassword('');
  }, [validatePasswords, toast]);

  return (
    <Card>
      <CardBody>
        <SecurityForm
          onSubmit={handleSubmit}
          currentPassword={currentPassword}
          setCurrentPassword={setCurrentPassword}
          newPassword={newPassword}
          setNewPassword={setNewPassword}
          confirmPassword={confirmPassword}
          setConfirmPassword={setConfirmPassword}
          error={error}
        />
      </CardBody>
    </Card>
  );
});

const AdminTab = React.memo(() => (
  <Card>
    <CardBody>
      <Fieldset>
        <FieldsetLegend>Admin Settings</FieldsetLegend>
        <FieldsetContent>
          <Text>Admin-only settings will go here</Text>
        </FieldsetContent>
      </Fieldset>
    </CardBody>
  </Card>
));

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
  const [selectedTab, setSelectedTab] = React.useState('profile');
  const [user, setUser] = React.useState<{ username: string; is_admin: boolean; avatarUrl?: string } | null>(null);
  const [directories, setDirectories] = React.useState<string[]>([]);
  const [avatarError, setAvatarError] = React.useState<string>('');
  const { colorMode } = useColorMode();

  React.useEffect(() => {
    const fetchUser = async () => {
      const userData = await authService.getCurrentUser();
      setUser(userData);
    };
    const fetchDirectories = async () => {
      // TODO: Implement API call to fetch directories
      // For now, using mock data
      setDirectories(['/path/to/protocols', '/another/path']);
    };

    fetchUser();
    fetchDirectories();
  }, []);

  const handleTabChange = React.useCallback((details: { value: string }) => {
    setSelectedTab(details.value);
  }, []);

  const handleAvatarChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Validate file size
    if (file.size > MAX_FILE_SIZE) {
      setAvatarError('File size must be less than 5MB');
      return;
    }

    // Validate file type
    if (!ALLOWED_FILE_TYPES.includes(file.type)) {
      setAvatarError('Please upload a valid image file (JPEG, PNG, or GIF)');
      return;
    }

    try {
      // Create a FormData object
      const formData = new FormData();
      formData.append('avatar', file);

      // TODO: Implement API call to upload avatar
      console.log('Uploading avatar:', file);

      // Clear any previous errors
      setAvatarError('');
    } catch (error) {
      setAvatarError('Failed to upload avatar');
    }
  };

  const themeOptions = createListCollection({
    items: [
      { label: 'Use System Settings', value: 'system' },
      { label: 'Light Mode', value: 'light' },
      { label: 'Dark Mode', value: 'dark' }
    ],
  });

  const tabContent = React.useMemo(() => ({
    profile: (
      <ProfileTab
        user={user}
        onAvatarChange={handleAvatarChange}
        avatarError={avatarError}
      />
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
    user, handleAvatarChange, avatarError,
    directories, handleRemoveDirectory, handleAddDirectory,
  ]);

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
          <TabTrigger value="profile">
            <LuUser size={16} />
            Profile
          </TabTrigger>
          <TabTrigger value="appearance">
            <LuPalette size={16} />
            Appearance
          </TabTrigger>
          <TabTrigger value="protocols">
            <LuFolderCog size={16} />
            Protocols
          </TabTrigger>
          <TabTrigger value="security">
            <LuKey size={16} />
            Security
          </TabTrigger>
          {user?.is_admin && (
            <TabTrigger value="admin">
              <LuShieldAlert size={16} />
              Admin
            </TabTrigger>
          )}
        </TabList>
        <TabRenderer tabContent={tabContent} selectedTab={selectedTab} />
      </Tabs>
    </Box>
  );
};
