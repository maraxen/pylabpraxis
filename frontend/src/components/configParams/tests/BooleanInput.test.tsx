import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { ChakraProvider } from '@chakra-ui/react';
import { BooleanInput } from '../inputs/BooleanInput';
import { system } from '@/theme';

// Mock the Switch component from Chakra UI
jest.mock('@chakra-ui/react', () => {
  const originalModule = jest.requireActual('@chakra-ui/react');
  return {
    ...originalModule,
    Switch: {
      Root: ({ checked, onCheckedChange, onFocus, onBlur, children }: any) => (
        <div
          data-testid="switch-root"
          role="switch"
          aria-checked={checked}
          onClick={() => onCheckedChange({ checked: !checked })}
          onFocus={onFocus}
          onBlur={onBlur}
        >
          {children}
        </div>
      ),
      HiddenInput: () => <input type="checkbox" data-testid="switch-input" hidden />,
      Control: ({ children }: any) => <div data-testid="switch-control">{children}</div>,
      Thumb: () => <div data-testid="switch-thumb" />,
      Label: ({ children }: any) => <div data-testid="switch-label">{children}</div>
    }
  };
});

// Helper to render with ChakraProvider
const renderWithChakra = (ui: React.ReactElement) => {
  return render(
    <ChakraProvider value={system}>{ui}</ChakraProvider>
  );
};

describe('BooleanInput Component', () => {
  // Basic rendering tests
  describe('Rendering', () => {
    test('renders a switch component', () => {
      const onChange = jest.fn();

      renderWithChakra(
        <BooleanInput
          name="testInput"
          value={false}
          config={{}}
          onChange={onChange}
        />
      );

      const switchRoot = screen.getByTestId('switch-root');
      const switchLabel = screen.getByTestId('switch-label');

      expect(switchRoot).toBeInTheDocument();
      expect(switchLabel).toBeInTheDocument();
      expect(switchLabel).toHaveTextContent('testInput');
    });

    test('renders with correct checked state when true', () => {
      const onChange = jest.fn();

      renderWithChakra(
        <BooleanInput
          name="testInput"
          value={true}
          config={{}}
          onChange={onChange}
        />
      );

      const switchRoot = screen.getByTestId('switch-root');
      expect(switchRoot).toHaveAttribute('aria-checked', 'true');
    });

    test('renders with correct checked state when false', () => {
      const onChange = jest.fn();

      renderWithChakra(
        <BooleanInput
          name="testInput"
          value={false}
          config={{}}
          onChange={onChange}
        />
      );

      const switchRoot = screen.getByTestId('switch-root');
      expect(switchRoot).toHaveAttribute('aria-checked', 'false');
    });
  });

  // Event handling tests
  describe('Event Handling', () => {
    test('calls onChange with name and toggled value when clicked', () => {
      const onChange = jest.fn();

      renderWithChakra(
        <BooleanInput
          name="testInput"
          value={false}
          config={{}}
          onChange={onChange}
        />
      );

      const switchRoot = screen.getByTestId('switch-root');
      fireEvent.click(switchRoot);

      expect(onChange).toHaveBeenCalledWith('testInput', true);
    });

    test('toggles from true to false when clicked', () => {
      const onChange = jest.fn();

      renderWithChakra(
        <BooleanInput
          name="testInput"
          value={true}
          config={{}}
          onChange={onChange}
        />
      );

      const switchRoot = screen.getByTestId('switch-root');
      fireEvent.click(switchRoot);

      expect(onChange).toHaveBeenCalledWith('testInput', false);
    });

    test('handles null/undefined value as false', () => {
      const onChange = jest.fn();

      renderWithChakra(
        <BooleanInput
          name="testInput"
          value={null}
          config={{}}
          onChange={onChange}
        />
      );

      const switchRoot = screen.getByTestId('switch-root');
      expect(switchRoot).toHaveAttribute('aria-checked', 'false');

      fireEvent.click(switchRoot);
      expect(onChange).toHaveBeenCalledWith('testInput', true);
    });

    test('calls onFocus when switch is focused', () => {
      const onChange = jest.fn();
      const onFocus = jest.fn();

      renderWithChakra(
        <BooleanInput
          name="testInput"
          value={false}
          config={{}}
          onChange={onChange}
          onFocus={onFocus}
        />
      );

      const switchRoot = screen.getByTestId('switch-root');
      fireEvent.focus(switchRoot);

      expect(onFocus).toHaveBeenCalled();
    });

    test('calls onBlur when switch loses focus', () => {
      const onChange = jest.fn();
      const onBlur = jest.fn();

      renderWithChakra(
        <BooleanInput
          name="testInput"
          value={false}
          config={{}}
          onChange={onChange}
          onBlur={onBlur}
        />
      );

      const switchRoot = screen.getByTestId('switch-root');
      fireEvent.blur(switchRoot);

      expect(onBlur).toHaveBeenCalled();
    });
  });

  // Edge case tests
  describe('Edge Cases', () => {
    test('handles truthy non-boolean values as true', () => {
      const onChange = jest.fn();

      renderWithChakra(
        <BooleanInput
          name="testInput"
          value="true" // string value rather than boolean
          config={{}}
          onChange={onChange}
        />
      );

      const switchRoot = screen.getByTestId('switch-root');
      expect(switchRoot).toHaveAttribute('aria-checked', 'true');
    });

    test('handles falsy non-boolean values as false', () => {
      const onChange = jest.fn();

      renderWithChakra(
        <BooleanInput
          name="testInput"
          value="" // empty string, falsy value
          config={{}}
          onChange={onChange}
        />
      );

      const switchRoot = screen.getByTestId('switch-root');
      expect(switchRoot).toHaveAttribute('aria-checked', 'false');
    });
  });
});