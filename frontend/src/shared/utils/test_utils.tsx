import { ReactElement, ReactNode } from 'react';
import { render, RenderOptions } from '@testing-library/react';
import { ChakraProvider } from '@chakra-ui/react';
import system from '@styles/theme'; // Your system import path

// Define the wrapper props with proper typing
interface AllProvidersProps {
  children: ReactNode;
}


// Create a wrapper component with proper typing
const AllProviders = ({ children }: AllProvidersProps) => (
  <ChakraProvider value={system} >
    {children}
  </ChakraProvider>
);

// Custom render function with proper TypeScript types
const customRender = (
  ui: ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>
) => render(ui, { wrapper: AllProviders, ...options });

// Export everything from testing library
export * from '@testing-library/react';

// Export the custom render function
export { customRender as render };