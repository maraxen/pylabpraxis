import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Button,
  Input,
  VStack,
  Heading,
  Text,
} from '@chakra-ui/react';
import { FormControl, FormLabel } from '@chakra-ui/form-control';
import { authService } from '../services/auth';
import { useToast } from '@chakra-ui/toast';
export const Login: React.FC = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();
  const toast = useToast();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      await authService.login({ username, password });
      const user = await authService.getCurrentUser();

      toast({
        title: 'Login successful',
        description: `Welcome back, ${user?.username}!`,
        status: 'success',
        duration: 3000,
        isClosable: true,
      });

      navigate('/');
    } catch (error) {
      toast({
        title: 'Login failed',
        description: 'Invalid username or password',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Box
      minH="100vh"
      display="flex"
      alignItems="center"
      justifyContent="center"
      bg="gray.50"
    >
      <Box
        p={8}
        maxWidth="400px"
        borderWidth={1}
        borderRadius={8}
        boxShadow="lg"
        bg="white"
        width="90%"
      >
        <VStack align="stretch">
          <Heading textAlign="center" mb={6}>
            Login to PLR
          </Heading>
          <form onSubmit={handleSubmit}>
            <VStack>
              <FormControl isRequired>
                <FormLabel>Username</FormLabel>
                <Input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="Enter your username"
                />
              </FormControl>
              <FormControl isRequired>
                <FormLabel>Password</FormLabel>
                <Input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Enter your password"
                />
              </FormControl>
              <Button loading>  </Button>
              <Button
                type="submit"
                colorScheme="blue"
                width="full"
                mt={4}
                loadingText="Signing in..."
              >
                Sign In
              </Button>
            </VStack>
          </form>
          <Text fontSize="sm" color="gray.600" textAlign="center" mt={4}>
            Contact your administrator if you need access.
          </Text>
        </VStack>
      </Box>
    </Box>
  );
};