import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { ChakraProvider } from '@chakra-ui/react';
import { StringInput } from '../../../shared/components/ui/StringInput';
import { system } from '@/theme';

// Helper to render with ChakraProvider
const renderWithChakra = (ui: React.ReactElement) => {
  return render(
    <ChakraProvider value={system}>{ui}</ChakraProvider>
  );
};

describe('StringInput Component', () => {
  // Basic rendering tests
  describe('Rendering', () => {
    test('renders a basic input field', () => {
      const onChange = jest.fn();

      renderWithChakra(
        <StringInput
          name="testInput"
          value="Test Value"
          config={{ constraints: {} }}
          onChange={onChange}
        />
      );

      const input = screen.getByDisplayValue('Test Value');
      expect(input).toBeInTheDocument();
    });

    test('renders AutoComplete when options are provided', () => {
      const onChange = jest.fn();
      const options = ['Option 1', 'Option 2', 'Option 3'];

      renderWithChakra(
        <StringInput
          name="testInput"
          value=""
          config={{ constraints: { array: options } }}
          onChange={onChange}
        />
      );

      // AutoComplete should be rendered - get input field
      const input = screen.getByPlaceholderText('Select value...');
      expect(input).toBeInTheDocument();

      // Focus to open the dropdown
      fireEvent.focus(input);

      // Options would be rendered in the dropdown, but this can be tricky to test
      // without additional setup since the dropdown might be in a portal
    });

    test('disables autocomplete when disableAutocomplete prop is true', () => {
      const onChange = jest.fn();
      const options = ['Option 1', 'Option 2', 'Option 3'];

      renderWithChakra(
        <StringInput
          name="testInput"
          value="Test Value"
          config={{ constraints: { array: options } }}
          onChange={onChange}
          disableAutocomplete={true}
        />
      );

      // Should render standard input instead of AutoComplete
      const input = screen.getByDisplayValue('Test Value');
      expect(input).toBeInTheDocument();
      expect(input.tagName).toBe('INPUT'); // Standard input
    });
  });

  // Event handling tests
  describe('Event Handling', () => {
    test('calls onChange with name and new value when input changes', () => {
      const onChange = jest.fn();

      renderWithChakra(
        <StringInput
          name="testInput"
          value="Initial Value"
          config={{ constraints: {} }}
          onChange={onChange}
        />
      );

      const input = screen.getByDisplayValue('Initial Value');
      fireEvent.change(input, { target: { value: 'New Value' } });

      expect(onChange).toHaveBeenCalledWith('testInput', 'New Value');
    });

    test('calls onFocus when input is focused', () => {
      const onChange = jest.fn();
      const onFocus = jest.fn();

      renderWithChakra(
        <StringInput
          name="testInput"
          value="Test Value"
          config={{ constraints: {} }}
          onChange={onChange}
          onFocus={onFocus}
        />
      );

      const input = screen.getByDisplayValue('Test Value');
      fireEvent.focus(input);

      expect(onFocus).toHaveBeenCalled();
    });

    test('calls onBlur when input loses focus', () => {
      const onChange = jest.fn();
      const onBlur = jest.fn();

      renderWithChakra(
        <StringInput
          name="testInput"
          value="Test Value"
          config={{ constraints: {} }}
          onChange={onChange}
          onBlur={onBlur}
        />
      );

      const input = screen.getByDisplayValue('Test Value');
      fireEvent.blur(input);

      expect(onBlur).toHaveBeenCalled();
    });

    test('calls onKeyDown when key is pressed', () => {
      const onChange = jest.fn();
      const onKeyDown = jest.fn();

      renderWithChakra(
        <StringInput
          name="testInput"
          value="Test Value"
          config={{ constraints: {} }}
          onChange={onChange}
          onKeyDown={onKeyDown}
        />
      );

      const input = screen.getByDisplayValue('Test Value');
      fireEvent.keyDown(input, { key: 'Enter', code: 'Enter' });

      expect(onKeyDown).toHaveBeenCalled();
    });
  });

  // Ref forwarding test
  describe('Ref Forwarding', () => {
    test('forwards ref to input element', () => {
      const onChange = jest.fn();
      const ref = React.createRef<HTMLInputElement>();

      renderWithChakra(
        <StringInput
          name="testInput"
          value="Test Value"
          config={{ constraints: {} }}
          onChange={onChange}
          ref={ref}
        />
      );

      expect(ref.current).not.toBeNull();
      expect(ref.current?.tagName).toBe('INPUT');
      expect(ref.current?.value).toBe('Test Value');
    });
  });
});