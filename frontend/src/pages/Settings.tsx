import React from 'react';
import {
  Box,
  Heading,
  VStack,
  Input,
  Fieldset,
  Text,
  HStack,
  Card,
  createListCollection,
  Tabs
} from '@chakra-ui/react';
import { Avatar } from "@/components/ui/avatar"
import { Button } from '@/components/ui/button';
import { Field } from '@/components/ui/field';
import {
  SelectContent,
  SelectItem,
  SelectRoot,
  SelectTrigger,
  SelectValueText,
} from '@/components/ui/select';
import { authService } from '../services/auth';
import {
  LuUser,
  LuPalette,
  LuFolderCog,
  LuShieldAlert,
  LuKey
} from "react-icons/lu";

const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5MB
const ALLOWED_FILE_TYPES = ['image/jpeg', 'image/png', 'image/gif'];

export const Settings: React.FC = () => {
  const [currentPassword, setCurrentPassword] = React.useState('');
  const [newPassword, setNewPassword] = React.useState('');
  const [confirmPassword, setConfirmPassword] = React.useState('');
  const [currentTheme, setCurrentTheme] = React.useState(localStorage.getItem('theme') || 'system');
  const [user, setUser] = React.useState<{ username: string; is_admin: boolean; avatarUrl?: string } | null>(null);
  const [directories, setDirectories] = React.useState<string[]>([]);
  const [avatarError, setAvatarError] = React.useState<string>('');

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

  const handlePasswordChange = (e: React.FormEvent) => {
    e.preventDefault();
    // TODO: Implement password change logic
    console.log('Password change requested');
  };

  const handleThemeChange: React.FormEventHandler<HTMLDivElement> = (event) => {
    const values = (event.target as any).value;
    const value = Array.isArray(values) ? values[0] : values;
    setCurrentTheme(value);
    localStorage.setItem('theme', value);
    document.documentElement.setAttribute('data-theme', value);
  };

  const handleAddDirectory = () => {
    // TODO: Implement directory selection
    console.log('Add directory clicked');
  };

  const handleRemoveDirectory = (dir: string) => {
    // TODO: Implement directory removal
    console.log('Remove directory:', dir);
  };

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

  const renderProfileTab = () => (
    <Card.Root>
      <Card.Body>
        <Fieldset.Root>
          <Fieldset.Legend>Profile</Fieldset.Legend>
          <Fieldset.Content>
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
                      variant="outline"
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
                      onChange={handleAvatarChange}
                    />
                  </label>
                  {avatarError && (
                    <Text color="red.500" fontSize="sm">
                      {avatarError}
                    </Text>
                  )}
                  <Text fontSize="sm" color="gray.600">
                    Supported formats: JPEG, PNG, GIF (max. 5MB)
                  </Text>
                </VStack>
              </HStack>
            </VStack>
          </Fieldset.Content>
        </Fieldset.Root>
      </Card.Body>
    </Card.Root>
  );

  const renderAppearanceTab = () => (
    <Card.Root>
      <Card.Body>
        <Fieldset.Root>
          <Fieldset.Legend>Theme Settings</Fieldset.Legend>
          <Fieldset.Content>
            <Field label="Theme">
              <SelectRoot
                collection={themeOptions}
                value={[currentTheme]}
                onChange={handleThemeChange}
              >
                <SelectTrigger>
                  <SelectValueText placeholder="Select theme" />
                </SelectTrigger>
                <SelectContent>
                  {themeOptions.items.map((theme) => (
                    <SelectItem key={theme.value} item={theme}>
                      {theme.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </SelectRoot>
            </Field>
          </Fieldset.Content>
        </Fieldset.Root>
      </Card.Body>
    </Card.Root>
  );

  const renderProtocolsTab = () => (
    <Card.Root>
      <Card.Body>
        <Fieldset.Root>
          <Fieldset.Legend>Protocol Directories</Fieldset.Legend>
          <Fieldset.Content>
            <VStack align="stretch" gap={4}>
              {directories.map((dir) => (
                <HStack key={dir} justify="space-between">
                  <Text>{dir}</Text>
                  <Button
                    size="sm"
                    variant="ghost"
                    color={{ base: 'brand.300', _dark: 'brand.100' }}
                    _hover={{
                      color: { base: 'white', _dark: 'brand.50' },
                      bg: { base: 'brand.300', _dark: 'brand.800' },
                    }}
                    onClick={() => handleRemoveDirectory(dir)}
                  >
                    Remove
                  </Button>
                </HStack>
              ))}
              <Button
                variant="outline"
                color={{ base: 'brand.300', _dark: 'brand.100' }}
                borderColor={{ base: 'brand.300', _dark: 'brand.100' }}
                _hover={{
                  color: { base: 'white', _dark: 'brand.50' },
                  bg: { base: 'brand.300', _dark: 'brand.800' },
                }}
                onClick={handleAddDirectory}
              >
                Add Directory
              </Button>
            </VStack>
          </Fieldset.Content>
        </Fieldset.Root>
      </Card.Body>
    </Card.Root>
  );

  const renderSecurityTab = () => (
    <Card.Root>
      <Card.Body>
        <form onSubmit={handlePasswordChange}>
          <Fieldset.Root>
            <Fieldset.Legend>Change Password</Fieldset.Legend>
            <Fieldset.Content>
              <VStack gap={4}>
                <Field label="Current Password">
                  <Input
                    type="password"
                    value={currentPassword}
                    onChange={(e) => setCurrentPassword(e.target.value)}
                  />
                </Field>
                <Field label="New Password">
                  <Input
                    type="password"
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                  />
                </Field>
                <Field label="Confirm New Password">
                  <Input
                    type="password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                  />
                </Field>
              </VStack>
            </Fieldset.Content>
            <Button
              type="submit"
              colorScheme="brand"
              mt={4}
              alignSelf="flex-start"
            >
              Update Password
            </Button>
          </Fieldset.Root>
        </form>
      </Card.Body>
    </Card.Root>
  );

  const renderAdminTab = () => (
    <Card.Root>
      <Card.Body>
        <Fieldset.Root>
          <Fieldset.Legend>Admin Settings</Fieldset.Legend>
          <Fieldset.Content>
            <Text>Admin-only settings will go here</Text>
          </Fieldset.Content>
        </Fieldset.Root>
      </Card.Body>
    </Card.Root>
  );

  return (
    <Box p={6}>
      <Heading size="lg" mb={6}>Settings</Heading>

      <Tabs.Root defaultValue="profile">
        <Tabs.List>
          <Tabs.Trigger value="profile">
            <LuUser />
            Profile
          </Tabs.Trigger>
          <Tabs.Trigger value="appearance">
            <LuPalette />
            Appearance
          </Tabs.Trigger>
          <Tabs.Trigger value="protocols">
            <LuFolderCog />
            Protocols
          </Tabs.Trigger>
          <Tabs.Trigger value="security">
            <LuKey />
            Security
          </Tabs.Trigger>
          <Tabs.Trigger value="admin" disabled={!user?.is_admin}>
            <LuShieldAlert />
            Admin
          </Tabs.Trigger>
        </Tabs.List>

        <Box pt={6}>
          <Tabs.Content value="profile">
            {renderProfileTab()}
          </Tabs.Content>

          <Tabs.Content value="appearance">
            {renderAppearanceTab()}
          </Tabs.Content>

          <Tabs.Content value="protocols">
            {renderProtocolsTab()}
          </Tabs.Content>

          <Tabs.Content value="security">
            {renderSecurityTab()}
          </Tabs.Content>

          <Tabs.Content value="admin">
            {user?.is_admin && renderAdminTab()}
          </Tabs.Content>
        </Box>
      </Tabs.Root>
    </Box>
  );
};
