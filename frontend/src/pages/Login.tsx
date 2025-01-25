import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useSelector, useDispatch } from 'react-redux';
import { RootState } from '../store';
import {
  Box,
  Input,
  VStack,
  Heading,
  Text,
} from '@chakra-ui/react';
import { Fieldset, FieldsetContent, FieldsetLegend } from '@/components/ui/fieldset';
import { authService } from '../services/auth';
import { useToast } from '@chakra-ui/toast';
import { Field } from '@/components/ui/field';
import { Button } from '@/components/ui/button';
import { setUser } from '../store/authSlice';

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
};

export const Login: React.FC = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const dispatch = useDispatch();
  const toast = useToast();
  const { isAuthenticated } = useSelector((state: RootState) => state.auth);

  // Redirect if already authenticated
  useEffect(() => {
    if (isAuthenticated) {
      const from = location.state?.from?.pathname || '/';
      navigate(from, { replace: true });
    }
  }, [isAuthenticated, navigate, location]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    e.stopPropagation();

    if (isSubmitting) return;

    setIsLoading(true);
    setIsSubmitting(true);

    try {
      const response = await authService.login({ username, password });
      dispatch(setUser(response.user)); // Add this line to update auth state

      toast({
        title: 'Login successful',
        description: `Welcome back, ${response.user.username}!`,
        status: 'success',
        duration: 3000,
        isClosable: true,
      });

      // Navigation will be handled by the useEffect
    } catch (error) {
      console.error('Login error:', error);
      setIsSubmitting(false);
      setIsLoading(false);

      toast({
        title: 'Login failed',
        description: error instanceof Error ? error.message : 'Invalid username or password',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });

      // Clear password field on error
      setPassword('');
    }
  };

  // Disable form submission while processing
  const formProps = {
    onSubmit: handleSubmit,
    style: { pointerEvents: isSubmitting ? 'none' as const : 'auto' as const }
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
          <form {...formProps}>
            <Fieldset disabled={isSubmitting}>
              <FieldsetLegend>Login Credentials</FieldsetLegend>
              <FieldsetContent>
                <Field label="Username">
                  <Input
                    type="text"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    placeholder="Enter your username"
                    size="md"
                    {...inputStyles}
                  />
                </Field>
                <Field label="Password">
                  <Input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Enter your password"
                    size="md"
                    {...inputStyles}
                  />
                </Field>
              </FieldsetContent>

              <Button
                type="submit"
                colorScheme="brand"
                width="full"
                mt={4}
                loading={isLoading}
                loadingText="Signing in..."
                disabled={isSubmitting || !username || !password}
              >
                Sign In
              </Button>
            </Fieldset>
          </form>
          <Text fontSize="sm" color="gray.600" textAlign="center" mt={4}>
            Contact your administrator if you need access.
          </Text>
        </VStack>
      </Box>
    </Box>
  );
};
