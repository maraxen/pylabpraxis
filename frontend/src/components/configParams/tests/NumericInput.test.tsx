import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { ChakraProvider } from '@chakra-ui/react';
import { NumberInput } from '../inputs/NumericInput';
import { system } from '@/theme';

// Mock the NumberInputRoot and NumberInputField from the UI components
jest.mock('@/components/ui/number-input', () => ({
  NumberInputRoot: ({ children, value, onValueChange, min, max, step, inputMode }: any) => (
    <div data-testid="number-input-root" data-value={value} data-min={min} data-max={max} data-step={step} data-mode={inputMode}>
      {React.cloneElement(children, {
        onChange: (e: any) => onValueChange({ value: e.target.value })
      })}
    </div>
  ),
  NumberInputField: React.forwardRef(({ onFocus, onBlur, onKeyDown, onChange }: any, ref: any) => (
    <input
      data-testid="number-input-field"
      ref={ref}
      onFocus={onFocus}
      onBlur={onBlur}
      onKeyDown={onKeyDown}
      onChange={onChange}
    />
  ))
}));

// Helper to render with ChakraProvider
const renderWithChakra = (ui: React.ReactElement) => {
  return render(
    <ChakraProvider value={system}>{ui}</ChakraProvider>
  );
};

describe('NumberInput Component', () => {
  // Basic rendering tests
  describe('Rendering', () => {
    test('renders with default props', () => {
      const onChange = jest.fn();

      renderWithChakra(
        <NumberInput
          name="testInput"
          value={42}
          config={{ type: 'number', constraints: {} }}
          onChange={onChange}
        />
      );

      const root = screen.getByTestId('number-input-root');
      expect(root).toBeInTheDocument();
      expect(root).toHaveAttribute('data-value', '42');
    });

    test('applies min and max constraints from config', () => {
      const onChange = jest.fn();

      renderWithChakra(
        <NumberInput
          name="testInput"
          value={50}
          config={{
            type: 'number',
            constraints: {
              min_value: 10,
              max_value: 100
            }
          }}
          onChange={onChange}
        />
      );

      const root = screen.getByTestId('number-input-root');
      expect(root).toHaveAttribute('data-min', '10');
      expect(root).toHaveAttribute('data-max', '100');
    });

    test('applies step from config', () => {
      const onChange = jest.fn();

      renderWithChakra(
        <NumberInput
          name="testInput"
          value={5}
          config={{
            type: 'float',
            constraints: {
              step: 0.5
            }
          }}
          onChange={onChange}
        />
      );

      const root = screen.getByTestId('number-input-root');
      expect(root).toHaveAttribute('data-step', '0.5');
    });

    test('uses correct inputMode for integer type', () => {
      const onChange = jest.fn();

      renderWithChakra(
        <NumberInput
          name="testInput"
          value={5}
          config={{
            type: 'integer',
            constraints: {}
          }}
          onChange={onChange}
        />
      );

      const root = screen.getByTestId('number-input-root');
      expect(root).toHaveAttribute('data-mode', 'numeric');
    });

    test('uses correct inputMode for float type', () => {
      const onChange = jest.fn();

      renderWithChakra(
        <NumberInput
          name="testInput"
          value={5.5}
          config={{
            type: 'float',
            constraints: {}
          }}
          onChange={onChange}
        />
      );

      const root = screen.getByTestId('number-input-root');
      expect(root).toHaveAttribute('data-mode', 'decimal');
    });
  });

  // Value handling tests
  describe('Value Handling', () => {
    test('calls onChange with parsed number value', () => {
      const onChange = jest.fn();

      renderWithChakra(
        <NumberInput
          name="testInput"
          value={10}
          config={{ type: 'number', constraints: {} }}
          onChange={onChange}
        />
      );

      const field = screen.getByTestId('number-input-field');
      fireEvent.change(field, { target: { value: '42' } });

      expect(onChange).toHaveBeenCalledWith('testInput', 42);
    });

    test('handles empty string by passing empty string to onChange', () => {
      const onChange = jest.fn();

      renderWithChakra(
        <NumberInput
          name="testInput"
          value={10}
          config={{ type: 'number', constraints: {} }}
          onChange={onChange}
        />
      );

      const field = screen.getByTestId('number-input-field');
      fireEvent.change(field, { target: { value: '' } });

      expect(onChange).toHaveBeenCalledWith('testInput', '');
    });

    test('enforces min value constraint', () => {
      const onChange = jest.fn();

      renderWithChakra(
        <NumberInput
          name="testInput"
          value={50}
          config={{
            type: 'number',
            constraints: { min_value: 10 }
          }}
          onChange={onChange}
        />
      );

      const field = screen.getByTestId('number-input-field');
      fireEvent.change(field, { target: { value: '5' } });

      expect(onChange).toHaveBeenCalledWith('testInput', 10);
    });

    test('enforces max value constraint', () => {
      const onChange = jest.fn();

      renderWithChakra(
        <NumberInput
          name="testInput"
          value={50}
          config={{
            type: 'number',
            constraints: { max_value: 100 }
          }}
          onChange={onChange}
        />
      );

      const field = screen.getByTestId('number-input-field');
      fireEvent.change(field, { target: { value: '150' } });

      expect(onChange).toHaveBeenCalledWith('testInput', 100);
    });

    test('rounds to integer for integer type', () => {
      const onChange = jest.fn();

      renderWithChakra(
        <NumberInput
          name="testInput"
          value={5}
          config={{
            type: 'integer',
            constraints: {}
          }}
          onChange={onChange}
        />
      );

      const field = screen.getByTestId('number-input-field');
      fireEvent.change(field, { target: { value: '5.7' } });

      expect(onChange).toHaveBeenCalledWith('testInput', 6);
    });
  });

  // Event handling tests
  describe('Event Handling', () => {
    test('calls onFocus when input is focused', () => {
      const onChange = jest.fn();
      const onFocus = jest.fn();

      renderWithChakra(
        <NumberInput
          name="testInput"
          value={10}
          config={{ type: 'number', constraints: {} }}
          onChange={onChange}
          onFocus={onFocus}
        />
      );

      const field = screen.getByTestId('number-input-field');
      fireEvent.focus(field);

      expect(onFocus).toHaveBeenCalled();
    });

    test('calls onBlur when input loses focus', () => {
      const onChange = jest.fn();
      const onBlur = jest.fn();

      renderWithChakra(
        <NumberInput
          name="testInput"
          value={10}
          config={{ type: 'number', constraints: {} }}
          onChange={onChange}
          onBlur={onBlur}
        />
      );

      const field = screen.getByTestId('number-input-field');
      fireEvent.blur(field);

      expect(onBlur).toHaveBeenCalled();
    });

    test('calls onKeyDown when key is pressed', () => {
      const onChange = jest.fn();
      const onKeyDown = jest.fn();

      renderWithChakra(
        <NumberInput
          name="testInput"
          value={10}
          config={{ type: 'number', constraints: {} }}
          onChange={onChange}
          onKeyDown={onKeyDown}
        />
      );

      const field = screen.getByTestId('number-input-field');
      fireEvent.keyDown(field, { key: 'Enter', code: 'Enter' });

      expect(onKeyDown).toHaveBeenCalled();
    });
  });

  // Ref forwarding test
  describe('Ref Forwarding', () => {
    test('forwards ref to input element', () => {
      const onChange = jest.fn();
      const ref = React.createRef<HTMLInputElement>();

      renderWithChakra(
        <NumberInput
          name="testInput"
          value={10}
          config={{ type: 'number', constraints: {} }}
          onChange={onChange}
          ref={ref}
        />
      );

      expect(ref.current).not.toBeNull();
      expect(ref.current).toBe(screen.getByTestId('number-input-field'));
    });
  });
});