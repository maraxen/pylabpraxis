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
import { authService } from '../services/auth';
import { useToast } from '@chakra-ui/toast';
import { Field } from '@/components/ui/field';
import { Button } from '@/components/ui/button';

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
        <VStack gap={4} align="stretch">
          <Heading textAlign="center" mb={6}>
            Login to PLR
          </Heading>
          <form onSubmit={handleSubmit}>
            <Fieldset.Root>
              <Fieldset.Legend>Login Credentials</Fieldset.Legend>
              <Fieldset.HelperText>
                Please enter your credentials below
              </Fieldset.HelperText>
              <Fieldset.Content>
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
                colorScheme="brand"
                width="full"
                mt={4}
                loadingText="Signing in..."
                loading={isLoading}
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