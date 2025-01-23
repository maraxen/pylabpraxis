import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Input,
  VStack,
  Heading,
  Text,
  Fieldset,
} from '@chakra-ui/react';
import { useToast } from '@chakra-ui/toast';
import { Field } from '@/components/ui/field';
import { Button } from '@/components/ui/button';
import { useAppDispatch, useAppSelector } from '../hooks/redux';
import { loginUser, selectError } from '../store/userSlice';

// Keep authService for type definitions and potential direct usage
import type { LoginCredentials } from '../services/auth';

export const Login: React.FC = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();
  const toast = useToast();
  const dispatch = useAppDispatch();
  const error = useAppSelector(selectError);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    const credentials: LoginCredentials = { username, password };

    try {
      await dispatch(loginUser(credentials)).unwrap();
      toast({
        title: 'Login successful',
        description: `Welcome back!`,
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
      navigate('/');
    } catch (err) {
      toast({
        title: 'Login failed',
        description: error || 'An error occurred during login',
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
        <VStack gap={4} align="stretch">
          <Heading textAlign="center" mb={6}>
            Login to Praxis
          </Heading>
          <form onSubmit={handleSubmit}>
            <Fieldset.Root>
              <Fieldset.Legend>Login Credentials</Fieldset.Legend>
              <Fieldset.HelperText>
                Please enter your credentials below
              </Fieldset.HelperText>
              <Fieldset.Content>
                {error && (
                  <Text color="red.500" mb={4} fontSize="sm">
                    {error}
                  </Text>
                )}
                <Field label="Username">
                  <Input
                    type="text"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    placeholder="Enter your username"
                  />
                </Field>
                <Field label="Password">
                  <Input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Enter your password"
                  />
                </Field>
              </Fieldset.Content>

              <Button
                type="submit"
                variant="solid"
                width="full"
                mt={4}
                loading={isLoading}
                loadingText="Signing in..."
                color={{ base: 'white', _dark: 'brand.50' }}
                bg={{ base: 'brand.300', _dark: 'brand.600' }}
                _hover={{
                  bg: { base: 'brand.400', _dark: 'brand.500' },
                }}
              >
                Sign In
              </Button>
            </Fieldset.Root>
          </form>
          <Text fontSize="sm" color="gray.600" textAlign="center" mt={4}>
            Contact your administrator if you need access.
          </Text>
        </VStack>
      </Box>
    </Box>
  );
};