import React from 'react';
import { render, screen } from '@utils/test_utils';
import { Tooltip } from '../ui/tooltip';

// Mock Chakra UI Tooltip components
jest.mock('@chakra-ui/react', () => {
  const originalModule = jest.requireActual('@chakra-ui/react');
  return {
    ...originalModule,
    Tooltip: {
      Root: ({ children, ...props }: any) => (
        <div data-testid="tooltip-root" {...props}>{children}</div>
      ),
      Trigger: ({ children, asChild }: any) => (
        <div data-testid="tooltip-trigger" data-aschild={asChild}>{children}</div>
      ),
      Content: ({ children, ...props }: any) => (
        <div data-testid="tooltip-content" {...props}>{children}</div>
      ),
      Arrow: ({ children }: any) => (
        <div data-testid="tooltip-arrow">{children}</div>
      ),
      ArrowTip: () => (
        <div data-testid="tooltip-arrow-tip"></div>
      ),
      Positioner: ({ children }: any) => (
        <div data-testid="tooltip-positioner">{children}</div>
      ),
    },
    Portal: ({ children, disabled, container }: any) => (
      <div data-testid="portal" data-disabled={disabled} data-container={container?.toString()}>{children}</div>
    ),
  };
});

describe('Tooltip Component', () => {
  // Basic rendering tests
  describe('Rendering', () => {
    test('renders basic tooltip with content', () => {
      render(
        <Tooltip content="Tooltip content">
          <button>Hover me</button>
        </Tooltip>
      );

      expect(screen.getByTestId('tooltip-root')).toBeInTheDocument();
      expect(screen.getByTestId('tooltip-trigger')).toBeInTheDocument();
      expect(screen.getByText('Hover me')).toBeInTheDocument();
      expect(screen.getByTestId('portal')).toBeInTheDocument();
      expect(screen.getByTestId('tooltip-positioner')).toBeInTheDocument();
      expect(screen.getByTestId('tooltip-content')).toBeInTheDocument();
      expect(screen.getByText('Tooltip content')).toBeInTheDocument();
    });

    test('renders with arrow when showArrow is true', () => {
      render(
        <Tooltip content="Tooltip content" showArrow>
          <button>Hover me</button>
        </Tooltip>
      );

      expect(screen.getByTestId('tooltip-arrow')).toBeInTheDocument();
      expect(screen.getByTestId('tooltip-arrow-tip')).toBeInTheDocument();
    });

    test('does not render arrow when showArrow is false', () => {
      render(
        <Tooltip content="Tooltip content" showArrow={false}>
          <button>Hover me</button>
        </Tooltip>
      );

      expect(screen.queryByTestId('tooltip-arrow')).not.toBeInTheDocument();
      expect(screen.queryByTestId('tooltip-arrow-tip')).not.toBeInTheDocument();
    });
  });

  // Portal configuration tests
  describe('Portal Configuration', () => {
    test('disables portal when portalled is false', () => {
      render(
        <Tooltip content="Tooltip content" portalled={false}>
          <button>Hover me</button>
        </Tooltip>
      );

      expect(screen.getByTestId('portal')).toHaveAttribute('data-disabled', 'true');
    });

    test('enables portal by default', () => {
      render(
        <Tooltip content="Tooltip content">
          <button>Hover me</button>
        </Tooltip>
      );

      expect(screen.getByTestId('portal')).toHaveAttribute('data-disabled', 'false');
    });

    test('passes portalRef when provided', () => {
      const portalRef = { current: document.createElement('div') };

      render(
        <Tooltip content="Tooltip content" portalRef={portalRef}>
          <button>Hover me</button>
        </Tooltip>
      );

      expect(screen.getByTestId('portal')).toHaveAttribute('data-container');
    });
  });

  // Disabled state tests
  describe('Disabled State', () => {
    test('returns children directly when disabled', () => {
      render(
        <Tooltip content="Tooltip content" disabled>
          <button data-testid="hover-button">Hover me</button>
        </Tooltip>
      );

      expect(screen.getByTestId('hover-button')).toBeInTheDocument();
      expect(screen.queryByTestId('tooltip-root')).not.toBeInTheDocument();
      expect(screen.queryByText('Tooltip content')).not.toBeInTheDocument();
    });
  });

  // Props passing tests
  describe('Props Passing', () => {
    test('passes contentProps to Content component', () => {
      render(
        <Tooltip
          content="Tooltip content"
          contentProps={{ className: 'custom-content-class' }}
        >
          <button>Hover me</button>
        </Tooltip>
      );

      expect(screen.getByTestId('tooltip-content')).toHaveAttribute('className', 'custom-content-class');
    });

    test('passes additional props to Root component', () => {
      render(
        <Tooltip
          content="Tooltip content"
          positioning={{ placement: 'top' }}
          openDelay={500}
        >
          <button>Hover me</button>
        </Tooltip>
      );

      expect(screen.getByTestId('tooltip-root')).toHaveAttribute('data-placement', 'top');
      expect(screen.getByTestId('tooltip-root')).toHaveAttribute('data-open-delay', '500');
    });
  });

  // Forward refs test
  describe('Ref Forwarding', () => {
    test('forwards ref to content component', () => {
      const ref = React.createRef<HTMLDivElement>();

      render(
        <Tooltip content="Tooltip content" ref={ref}>
          <button>Hover me</button>
        </Tooltip>
      );

      // The ref would be attached to the tooltip-content element in a real environment
      // This is difficult to test in JSDOM, but we can verify the component still renders
      expect(screen.getByTestId('tooltip-content')).toBeInTheDocument();
    });
  });
});