import React, { Component, ErrorInfo, ReactNode } from 'react';
import {
  Box,
  Heading,
  Text,
  Button,
  VStack,
  Container,
  Code,
  HStack,
} from '@chakra-ui/react';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
    errorInfo: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    return {
      hasError: true,
      error,
      errorInfo: null,
    };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Uncaught error:', error, errorInfo);
    this.setState({
      error,
      errorInfo,
    });
  }

  private handleReset = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
    });
  };

  private handleReload = () => {
    window.location.reload();
  };

  public render() {
    if (this.state.hasError) {
      return (
        <Box minH="100vh" bg="gray.50" py={10}>
          <Container maxW="container.md">
            <VStack gap={6} align="stretch">
              <Heading color="red.500">Something went wrong</Heading>

              <Box bg="white" p={6} borderRadius="lg" shadow="sm">
                <Text mb={4}>
                  An error occurred while rendering this page. Please try again or contact support if the problem persists.
                </Text>

                <VStack align="stretch" gap={4}>
                  {this.state.error && (
                    <Box>
                      <Text fontWeight="bold" mb={2}>Error:</Text>
                      <Code p={3} borderRadius="md" variant="subtle">
                        {this.state.error.toString()}
                      </Code>
                    </Box>
                  )}

                  {this.state.errorInfo?.componentStack && (
                    <Box>
                      <Text fontWeight="bold" mb={2}>Stack Trace:</Text>
                      <Code p={3} borderRadius="md" variant="subtle" display="block" whiteSpace="pre-wrap">
                        {this.state.errorInfo.componentStack}
                      </Code>
                    </Box>
                  )}

                  <HStack gap={4} mt={4}>
                    <Button
                      variant="solid"
                      color={{ base: 'white', _dark: 'brand.50' }}
                      bg={{ base: 'brand.300', _dark: 'brand.600' }}
                      _hover={{
                        bg: { base: 'brand.400', _dark: 'brand.500' },
                      }}
                      onClick={this.handleReset}
                    >
                      Try Again
                    </Button>
                    <Button
                      variant="outline"
                      color={{ base: 'brand.300', _dark: 'brand.100' }}
                      borderColor={{ base: 'brand.300', _dark: 'brand.100' }}
                      _hover={{
                        color: { base: 'white', _dark: 'brand.50' },
                        bg: { base: 'brand.300', _dark: 'brand.800' },
                      }}
                      onClick={this.handleReload}
                    >
                      Reload Page
                    </Button>
                  </HStack>
                </VStack>
              </Box>
            </VStack>
          </Container>
        </Box>
      );
    }

    return this.props.children;
  }
}
