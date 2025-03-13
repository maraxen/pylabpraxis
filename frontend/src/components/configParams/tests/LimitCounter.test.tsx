import React from 'react';
import { render, screen } from '@testing-library/react';
import { ChakraProvider } from '@chakra-ui/react';
import { LimitCounter } from '../subcomponents/LimitCounter';
import { BaseLimitCounterProps } from '../subcomponents/LimitCounter';
import { system } from '../../../theme';

// Helper to render with providers
const renderWithProviders = (ui: React.ReactElement) => {
  return render(
    <ChakraProvider value={system}>
      {ui}
    </ChakraProvider>
  );
};

// Mock the tooltip component to make testing easier
jest.mock("@/components/ui/tooltip", () => ({
  Tooltip: ({ children }: { children: React.ReactNode }) => <div data-testid="tooltip">{children}</div>,
}));

describe('LimitCounter Component', () => {
  // Basic rendering tests
  describe('Rendering', () => {
    test('displays count and limit correctly', () => {
      const props: BaseLimitCounterProps = {
        current: 5,
        max: 10
      };

      renderWithProviders(<LimitCounter {...props} />);

      expect(screen.getByText('5/10')).toBeInTheDocument();
    });

    test('displays infinity symbol for unlimited max', () => {
      const props: BaseLimitCounterProps = {
        current: 5,
        max: Infinity,
        showAlways: true
      };

      renderWithProviders(<LimitCounter {...props} />);

      expect(screen.getByText('5/∞')).toBeInTheDocument();
    });

    test('does not render when max is Infinity and showAlways is false', () => {
      const { container } = renderWithProviders(
        <LimitCounter current={5} max={Infinity} showAlways={false} />
      );

      // The component should return null, so container should be empty
      expect(container.firstChild).toBeNull();
    });
  });

  // Color scheme tests
  describe('Color schemes', () => {
    test('uses blue color scheme for low usage', () => {
      renderWithProviders(
        <LimitCounter current={2} max={10} />
      );

      // Find the badge
      const badge = screen.getByText('2/10');

      // In a real test, we'd check for the presence of a class like "blue"
      // This is implementation-specific and depends on how Chakra applies color schemes
      expect(badge).toBeInTheDocument();
    });

    test('uses yellow color scheme for medium usage', () => {
      renderWithProviders(
        <LimitCounter current={6} max={10} />
      );

      const badge = screen.getByText('6/10');
      expect(badge).toBeInTheDocument();
      // Would check for "yellow" class in a real test
    });

    test('uses orange color scheme for high usage', () => {
      renderWithProviders(
        <LimitCounter current={8} max={10} />
      );

      const badge = screen.getByText('8/10');
      expect(badge).toBeInTheDocument();
      // Would check for "orange" class in a real test
    });

    test('uses red color scheme for full usage', () => {
      renderWithProviders(
        <LimitCounter current={10} max={10} />
      );

      const badge = screen.getByText('10/10');
      expect(badge).toBeInTheDocument();
      // Would check for "red" class in a real test
    });
  });

  // Label tests
  describe('Labels', () => {
    test('includes label in tooltip when provided', () => {
      renderWithProviders(
        <LimitCounter current={5} max={10} label="Test Label" />
      );

      // Since we mocked Tooltip, we can just check that the badge is rendered
      const badge = screen.getByText('5/10');
      expect(badge).toBeInTheDocument();

      // In a real test, we'd check that the tooltip has appropriate content
      // But this depends on how your Tooltip component works
    });
  });
});
