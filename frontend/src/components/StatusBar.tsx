import { HStack, Text, Box } from '@chakra-ui/react';
import { useSelector } from 'react-redux';
import { RootState } from '../store';
import { ColorModeButton } from './ui/color-mode';

export const StatusBar = () => {
  const user = useSelector((state: RootState) => state.auth.user);

  return (
    <Box
      position="fixed"
      bottom={0}
      left={0}
      right={0}
      height="8"
      bg={{ base: 'white', _dark: 'gray.800' }}
      borderTop="1px"
      borderColor={{ base: 'gray.200', _dark: 'gray.700' }}
      px={4}
      zIndex={100}
    >
      <HStack h="full" justify="space-between">
        <Text fontSize="sm" color={{ base: 'gray.600', _dark: 'gray.400' }}>
          Logged in as {user?.username}
        </Text>
        <HStack gap={4}>
          <Text fontSize="sm" color={{ base: 'gray.600', _dark: 'gray.400' }}>
            Version 0.1.0
          </Text>
          <ColorModeButton />
        </HStack>
      </HStack>
    </Box>
  );
};
