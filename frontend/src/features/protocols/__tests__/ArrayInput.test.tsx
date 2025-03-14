import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { ChakraProvider } from '@chakra-ui/react';
import { ArrayInput } from '../../../shared/components/ui/ArrayInput';
import { system } from '@/theme';

// Mock the AutoComplete components
jest.mock('@choc-ui/chakra-autocomplete', () => ({
  AutoComplete: ({ children, multiple, freeSolo, value, onChange, onSelectOption }: any) => (
    <div data-testid="autocomplete" data-multiple={multiple} data-freesolo={freeSolo} data-value={JSON.stringify(value)}>
      {React.Children.map(children, child => {
        if (child.type.displayName === 'AutoCompleteInput') {
          return React.cloneElement(child, {
            onSelectItem: (item: any) => onSelectOption({ item }),
            onChange: (e: any) => onChange(e.target.value)
          });
        }
        return child;
      })}
    </div>
  ),
  AutoCompleteInput: React.forwardRef(
    ({ placeholder, readOnly, onFocus, onBlur, onKeyDown, onChange, onSelectItem }: any, ref: any) => (
      <input
        data-testid="autocomplete-input"
        placeholder={placeholder}
        readOnly={readOnly}
        ref={ref}
        onFocus={onFocus}
        onBlur={onBlur}
        onKeyDown={onKeyDown}
        onChange={onChange}
        onSelect={(e: any) => onSelectItem && onSelectItem({ value: e.target.value })}
      />
    )
  ),
  AutoCompleteList: ({ children }: any) => <div data-testid="autocomplete-list">{children}</div>,
  AutoCompleteItem: ({ value, children, disabled }: any) => (
    <div data-testid="autocomplete-item" data-value={value} data-disabled={disabled}>
      {children}
    </div>
  ),
  AutoCompleteTag: ({ label, onRemove }: any) => (
    <div data-testid="autocomplete-tag" onClick={onRemove}>
      {label}
    </div>
  ),
  AutoCompleteCreatable: ({ children }: any) => (
    <div data-testid="autocomplete-creatable">
      {typeof children === 'function' ? children({ value: 'New Value' }) : children}
    </div>
  )
}));

// Helper to render with ChakraProvider
const renderWithChakra = (ui: React.ReactElement) => {
  return render(
    <ChakraProvider value={system}>{ui}</ChakraProvider>
  );
};

describe('ArrayInput Component', () => {
  // Basic rendering tests
  describe('Rendering', () => {
    test('renders with empty array value', () => {
      const onChange = jest.fn();

      renderWithChakra(
        <ArrayInput
          name="testInput"
          value={[]}
          config={{ constraints: {} }}
          onChange={onChange}
        />
      );

      const autocomplete = screen.getByTestId('autocomplete');
      const input = screen.getByTestId('autocomplete-input');

      expect(autocomplete).toBeInTheDocument();
      expect(input).toBeInTheDocument();
      expect(autocomplete).toHaveAttribute('data-value', '[]');
    });

    test('renders with predefined array values', () => {
      const onChange = jest.fn();
      const value = ['Item 1', 'Item 2'];

      renderWithChakra(
        <ArrayInput
          name="testInput"
          value={value}
          config={{ constraints: {} }}
          onChange={onChange}
        />
      );

      const tags = screen.getAllByTestId('autocomplete-tag');
      expect(tags).toHaveLength(2);
      expect(tags[0]).toHaveTextContent('Item 1');
      expect(tags[1]).toHaveTextContent('Item 2');
    });

    test('renders with constrained options', () => {
      const onChange = jest.fn();
      const options = ['Option 1', 'Option 2', 'Option 3'];

      renderWithChakra(
        <ArrayInput
          name="testInput"
          value={[]}
          config={{ constraints: { array: options } }}
          onChange={onChange}
        />
      );

      // Focus to trigger dropdown display
      const input = screen.getByTestId('autocomplete-input');
      fireEvent.focus(input);

      // In a real component, options would be displayed in a dropdown
      const list = screen.getByTestId('autocomplete-list');
      expect(list).toBeInTheDocument();

      // Options should be rendered (in our mock)
      const items = screen.getAllByTestId('autocomplete-item');
      expect(items).toHaveLength(3);
      expect(items[0]).toHaveAttribute('data-value', 'Option 1');
      expect(items[1]).toHaveAttribute('data-value', 'Option 2');
      expect(items[2]).toHaveAttribute('data-value', 'Option 3');
    });

    test('renders with max length constraint', () => {
      const onChange = jest.fn();
      const value = ['Item 1', 'Item 2'];

      renderWithChakra(
        <ArrayInput
          name="testInput"
          value={value}
          config={{ constraints: { array_len: 2 } }}
          onChange={onChange}
        />
      );

      const input = screen.getByTestId('autocomplete-input');
      expect(input).toHaveAttribute('placeholder', 'Maximum 2 values reached');
      expect(input).toHaveAttribute('readOnly', '');
    });

    test('shows non-readonly input when under max length', () => {
      const onChange = jest.fn();
      const value = ['Item 1'];

      renderWithChakra(
        <ArrayInput
          name="testInput"
          value={value}
          config={{ constraints: { array_len: 2 } }}
          onChange={onChange}
        />
      );

      const input = screen.getByTestId('autocomplete-input');
      expect(input).toHaveAttribute('placeholder', 'Enter values (max 2)');
      expect(input).not.toHaveAttribute('readOnly');
    });

    test('renders creatable option when not constrained', () => {
      const onChange = jest.fn();

      renderWithChakra(
        <ArrayInput
          name="testInput"
          value={[]}
          config={{ constraints: {} }}
          onChange={onChange}
        />
      );

      // Focus to trigger dropdown display
      const input = screen.getByTestId('autocomplete-input');
      fireEvent.focus(input);

      // Creatable option should be present
      const creatable = screen.getByTestId('autocomplete-creatable');
      expect(creatable).toBeInTheDocument();
      expect(creatable).toHaveTextContent('Add "New Value"');
    });

    test('does not render creatable option when constrained', () => {
      const onChange = jest.fn();
      const options = ['Option 1', 'Option 2'];

      renderWithChakra(
        <ArrayInput
          name="testInput"
          value={[]}
          config={{ constraints: { array: options } }}
          onChange={onChange}
        />
      );

      // Focus to trigger dropdown display
      const input = screen.getByTestId('autocomplete-input');
      fireEvent.focus(input);

      // Creatable option should not be present
      const creatables = screen.queryAllByTestId('autocomplete-creatable');
      expect(creatables).toHaveLength(0);
    });
  });

  // Interaction tests
  describe('Interactions', () => {
    test('calls onChange when a value is selected', () => {
      const onChange = jest.fn();
      const options = ['Option 1', 'Option 2', 'Option 3'];

      renderWithChakra(
        <ArrayInput
          name="testInput"
          value={[]}
          config={{ constraints: { array: options } }}
          onChange={onChange}
        />
      );

      // Get the autocomplete input
      const input = screen.getByTestId('autocomplete-input');

      // Simulate selecting an item (using our mock's onSelect)
      fireEvent.select(input, { target: { value: 'Option 1' } });

      // onChange should be called with the name and the new array
      expect(onChange).toHaveBeenCalledWith('testInput', ['Option 1']);
    });

    test('does not add duplicate values', () => {
      const onChange = jest.fn();
      const value = ['Option 1'];
      const options = ['Option 1', 'Option 2', 'Option 3'];

      renderWithChakra(
        <ArrayInput
          name="testInput"
          value={value}
          config={{ constraints: { array: options } }}
          onChange={onChange}
        />
      );

      // Get the autocomplete input
      const input = screen.getByTestId('autocomplete-input');

      // Simulate selecting an item that already exists
      fireEvent.select(input, { target: { value: 'Option 1' } });

      // onChange should not be called since the value already exists
      expect(onChange).not.toHaveBeenCalled();
    });

    test('calls onChange when tag is removed', () => {
      const onChange = jest.fn();
      const value = ['Item 1', 'Item 2'];

      renderWithChakra(
        <ArrayInput
          name="testInput"
          value={value}
          config={{ constraints: {} }}
          onChange={onChange}
        />
      );

      // Get the tags
      const tags = screen.getAllByTestId('autocomplete-tag');

      // Click on the first tag to remove it
      fireEvent.click(tags[0]);

      // onChange should be called with the remaining items
      expect(onChange).toHaveBeenCalledWith('testInput', ['Item 2']);
    });

    test('respects max length constraint when adding items', () => {
      const onChange = jest.fn();
      const value = ['Item 1', 'Item 2'];

      renderWithChakra(
        <ArrayInput
          name="testInput"
          value={value}
          config={{ constraints: { array_len: 2 } }}
          onChange={onChange}
        />
      );

      // Get the autocomplete input
      const input = screen.getByTestId('autocomplete-input');

      // Try to add a third item
      fireEvent.select(input, { target: { value: 'Item 3' } });

      // onChange should not be called since we're at max length
      expect(onChange).not.toHaveBeenCalled();
    });
  });

  // Event handling tests
  describe('Event Handling', () => {
    test('calls onFocus when input is focused', () => {
      const onChange = jest.fn();
      const onFocus = jest.fn();

      renderWithChakra(
        <ArrayInput
          name="testInput"
          value={[]}
          config={{ constraints: {} }}
          onChange={onChange}
          onFocus={onFocus}
        />
      );

      const input = screen.getByTestId('autocomplete-input');
      fireEvent.focus(input);

      expect(onFocus).toHaveBeenCalled();
    });

    test('calls onBlur when input loses focus', () => {
      const onChange = jest.fn();
      const onBlur = jest.fn();

      renderWithChakra(
        <ArrayInput
          name="testInput"
          value={[]}
          config={{ constraints: {} }}
          onChange={onChange}
          onBlur={onBlur}
        />
      );

      const input = screen.getByTestId('autocomplete-input');
      fireEvent.blur(input);

      expect(onBlur).toHaveBeenCalled();
    });

    test('calls onKeyDown when key is pressed', () => {
      const onChange = jest.fn();
      const onKeyDown = jest.fn();

      renderWithChakra(
        <ArrayInput
          name="testInput"
          value={[]}
          config={{ constraints: {} }}
          onChange={onChange}
          onKeyDown={onKeyDown}
        />
      );

      const input = screen.getByTestId('autocomplete-input');
      fireEvent.keyDown(input, { key: 'Enter', code: 'Enter' });

      expect(onKeyDown).toHaveBeenCalled();
    });
  });

  // Edge case tests
  describe('Edge Cases', () => {
    test('handles non-array value by converting to array', () => {
      const onChange = jest.fn();
      const value = 'Single Value'; // Non-array value

      renderWithChakra(
        <ArrayInput
          name="testInput"
          value={value}
          config={{ constraints: {} }}
          onChange={onChange}
        />
      );

      // Should render a single tag for the non-array value
      const tags = screen.getAllByTestId('autocomplete-tag');
      expect(tags).toHaveLength(1);
      expect(tags[0]).toHaveTextContent('Single Value');
    });

    test('handles null/undefined value as empty array', () => {
      const onChange = jest.fn();

      renderWithChakra(
        <ArrayInput
          name="testInput"
          value={null}
          config={{ constraints: {} }}
          onChange={onChange}
        />
      );

      // Should not render any tags
      const tags = screen.queryAllByTestId('autocomplete-tag');
      expect(tags).toHaveLength(0);
    });
  });
});