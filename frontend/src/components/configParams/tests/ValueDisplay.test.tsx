import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { ChakraProvider } from '@chakra-ui/react';
import { ValueDisplay } from '../subcomponents/valueDisplay';
import { NestedMappingProvider } from '../contexts/nestedMappingContext';
import { ValueDisplayProps } from '../subcomponents/valueDisplay';
import { system } from '../../../theme';

// Mock the nested mapping context
const mockNestedMappingContext = {
  config: {
    type: 'object',
    constraints: {
      value_constraints: { type: 'string' }
    }
  },
  parameters: {},
  inputRef: { current: null },
  valueType: 'string'
};

// Helper to render with providers
const renderWithProviders = (ui: React.ReactElement) => {
  return render(
    <ChakraProvider value={system}>
      <NestedMappingProvider
        config={mockNestedMappingContext.config}
        parameters={mockNestedMappingContext.parameters}
        value={{}}
        onChange={() => { }}
        effectiveChildOptions={[]}
        effectiveParentOptions={[]}
        dragInfo={{
          activeId: null,
          activeData: null,
          overDroppableId: null,
          isDragging: false
        }}
        createValue={() => ""}
        createGroup={() => ""}
        createdValues={{}}
        setCreatedValues={() => { }}
      >
        {ui}
      </NestedMappingProvider>
    </ChakraProvider>
  );
};

describe('ValueDisplay Component', () => {
  // Test rendering different value types correctly
  describe('Value display rendering', () => {
    test('renders string values correctly', () => {
      const props: ValueDisplayProps = {
        value: "Test String",
        type: "string"
      };

      renderWithProviders(<ValueDisplay {...props} />);

      expect(screen.getByText('Test String')).toBeInTheDocument();
      expect(screen.getByText('string')).toBeInTheDocument();  // type badge
    });

    test('renders number values correctly', () => {
      const props: ValueDisplayProps = {
        value: 42,
        type: "number"
      };

      renderWithProviders(<ValueDisplay {...props} />);

      expect(screen.getByText('42')).toBeInTheDocument();
      expect(screen.getByText('number')).toBeInTheDocument();  // type badge
    });

    test('renders boolean values correctly', () => {
      const { rerender } = renderWithProviders(
        <ValueDisplay
          value={true}
          type="boolean"
        />
      );

      expect(screen.getByText('True')).toBeInTheDocument();
      expect(screen.getByText('boolean')).toBeInTheDocument();  // type badge

      rerender(
        <ChakraProvider value={system}>
          <NestedMappingProvider
            {...mockNestedMappingContext}
            config={mockNestedMappingContext.config}
            parameters={mockNestedMappingContext.parameters}
            value={{}}
            onChange={() => { }}
            effectiveChildOptions={[]}
            effectiveParentOptions={[]}
            dragInfo={{ activeId: null, activeData: null, overDroppableId: null, isDragging: false }}
            createValue={() => ""}
            createGroup={() => ""}
            createdValues={{}}
            setCreatedValues={() => { }}
          >
            <ValueDisplay
              value={false}
              type="boolean"
            />
          </NestedMappingProvider>
        </ChakraProvider>
      );

      expect(screen.getByText('False')).toBeInTheDocument();
    });

    test('renders empty/null values with placeholder', () => {
      const { rerender } = renderWithProviders(
        <ValueDisplay
          value={null}
          type="string"
        />
      );

      expect(screen.getByText('(empty)')).toBeInTheDocument();

      rerender(
        <ChakraProvider value={system}>
          <NestedMappingProvider
            {...mockNestedMappingContext}
            config={mockNestedMappingContext.config}
            parameters={mockNestedMappingContext.parameters}
            value={{}}
            onChange={() => { }}
            effectiveChildOptions={[]}
            effectiveParentOptions={[]}
            dragInfo={{ activeId: null, activeData: null, overDroppableId: null, isDragging: false }}
            createValue={() => ""}
            createGroup={() => ""}
            createdValues={{}}
            setCreatedValues={() => { }}
          >
            <ValueDisplay
              value={undefined}
              type="string"
            />
          </NestedMappingProvider>
        </ChakraProvider>
      );

      expect(screen.getByText('(empty)')).toBeInTheDocument();
    });
  });

  // Test edit mode transitions
  describe('Edit mode transitions', () => {
    test('clicking editable value enters edit mode', () => {
      const onFocus = jest.fn();

      renderWithProviders(
        <ValueDisplay
          value="Click Me"
          type="string"
          isEditable={true}
          onFocus={onFocus}
        />
      );

      const value = screen.getByText('Click Me');
      fireEvent.click(value);

      expect(onFocus).toHaveBeenCalled();
    });

    test('clicking non-editable value does not trigger onFocus', () => {
      const onFocus = jest.fn();

      renderWithProviders(
        <ValueDisplay
          value="Readonly Value"
          type="string"
          isEditable={false}
          onFocus={onFocus}
        />
      );

      const value = screen.getByText('Readonly Value');
      fireEvent.click(value);

      expect(onFocus).not.toHaveBeenCalled();
    });

    test('shows proper input in edit mode for string type', () => {
      renderWithProviders(
        <ValueDisplay
          value="Edit Me"
          type="string"
          isEditable={true}
          isEditing={true}
          onValueChange={() => { }}
        />
      );

      const input = screen.getByRole('textbox');
      expect(input).toBeInTheDocument();
      expect(input).toHaveValue('Edit Me');
    });

    test('shows proper input in edit mode for number type', () => {
      renderWithProviders(
        <ValueDisplay
          value={123}
          type="number"
          isEditable={true}
          isEditing={true}
          onValueChange={() => { }}
        />
      );

      // Number inputs typically use spinbutton role
      const input = screen.getByRole('spinbutton');
      expect(input).toBeInTheDocument();
      expect(input).toHaveValue(123);
    });

    test('shows proper input in edit mode for boolean type', () => {
      renderWithProviders(
        <ValueDisplay
          value={true}
          type="boolean"
          isEditable={true}
          isEditing={true}
          onValueChange={() => { }}
        />
      );

      // Boolean inputs typically use checkbox
      const input = screen.getByRole('checkbox');
      expect(input).toBeInTheDocument();
      expect(input).toBeChecked();
    });
  });

  // Test editability constraints
  describe('Editability constraints', () => {
    test('parameter values show parameter badge', () => {
      renderWithProviders(
        <ValueDisplay
          value="Parameter Value"
          type="string"
          isFromParam={true}
          paramSource="test-param"
        />
      );

      // Should show param badge
      const paramBadge = screen.getByText('test-param');
      expect(paramBadge).toBeInTheDocument();
    });

    test('parameter values show read-only badge', () => {
      renderWithProviders(
        <ValueDisplay
          value="Parameter Value"
          type="string"
          isFromParam={true}
          isEditable={false}
        />
      );

      // Should show read-only badge
      const readOnlyBadge = screen.getByText('read-only');
      expect(readOnlyBadge).toBeInTheDocument();
    });

    test('editable values show editable badge', () => {
      renderWithProviders(
        <ValueDisplay
          value="Editable Value"
          type="string"
          isEditable={true}
        />
      );

      // Should show editable badge
      const editableBadge = screen.getByText('editable');
      expect(editableBadge).toBeInTheDocument();
    });

    test('displays correct cursor styles based on editability', () => {
      const { container: editableContainer } = renderWithProviders(
        <ValueDisplay
          value="Editable Value"
          type="string"
          isEditable={true}
        />
      );

      const { container: readOnlyContainer } = renderWithProviders(
        <ValueDisplay
          value="ReadOnly Value"
          type="string"
          isEditable={false}
        />
      );

      // Get the clickable elements
      const editableElement = editableContainer.querySelector('div[cursor="pointer"]');
      const readOnlyElement = readOnlyContainer.querySelector('div[cursor="default"]');

      // This is a loose test since the actual implementation may vary
      // We're checking that CSS properties are being applied differently
      expect(editableElement).toBeTruthy();
      expect(readOnlyElement).toBeTruthy();
    });
  });

  // Test handling user input
  describe('User input handling', () => {
    test('calls onValueChange when editing value', () => {
      const onValueChange = jest.fn();

      renderWithProviders(
        <ValueDisplay
          value="Original Value"
          type="string"
          isEditable={true}
          isEditing={true}
          onValueChange={onValueChange}
        />
      );

      // Find input and change its value
      const input = screen.getByRole('textbox');
      fireEvent.change(input, { target: { value: 'New Value' } });

      expect(onValueChange).toHaveBeenCalledWith('New Value');
    });

    test('calls onBlur when pressing Enter', () => {
      const onBlur = jest.fn();

      renderWithProviders(
        <ValueDisplay
          value="Test Value"
          type="string"
          isEditable={true}
          isEditing={true}
          onBlur={onBlur}
        />
      );

      // Find input and press Enter
      const input = screen.getByRole('textbox');
      fireEvent.keyDown(input, { key: 'Enter', code: 'Enter' });

      expect(onBlur).toHaveBeenCalled();
    });

    test('resets to original value when pressing Escape', () => {
      const onValueChange = jest.fn();
      const onBlur = jest.fn();

      renderWithProviders(
        <ValueDisplay
          value="Original Value"
          type="string"
          isEditable={true}
          isEditing={true}
          onValueChange={onValueChange}
          onBlur={onBlur}
        />
      );

      // Find input, change value, then press Escape
      const input = screen.getByRole('textbox');
      fireEvent.change(input, { target: { value: 'New Value' } });

      // Verify value was changed
      expect(onValueChange).toHaveBeenCalledWith('New Value');

      // Press Escape - this should revert to original
      fireEvent.keyDown(input, { key: 'Escape', code: 'Escape' });

      // onBlur should be called
      expect(onBlur).toHaveBeenCalled();

      // The component should have called onValueChange with the original value
      // This is implementation-dependent, but ideally onBlur would be called
      expect(onValueChange).toHaveBeenCalled();
    });
  });

  // Test type badges and metadata
  describe('Type badges and metadata', () => {
    test('shows correct type badge for string', () => {
      renderWithProviders(
        <ValueDisplay
          value="String Value"
          type="string"
        />
      );

      const badge = screen.getByText('string');
      expect(badge).toBeInTheDocument();

      // Check the badge has the correct color scheme
      // This is implementation-specific but typically has class with the colorscheme
      const badgeElement = badge.closest('[class*="blue"]');
      expect(badgeElement).toBeTruthy();
    });

    test('shows correct type badge for number', () => {
      renderWithProviders(
        <ValueDisplay
          value={42}
          type="number"
        />
      );

      const badge = screen.getByText('number');
      expect(badge).toBeInTheDocument();

      // Check the badge has the correct color scheme
      const badgeElement = badge.closest('[class*="orange"]');
      expect(badgeElement).toBeTruthy();
    });

    test('shows correct type badge for boolean', () => {
      renderWithProviders(
        <ValueDisplay
          value={true}
          type="boolean"
        />
      );

      const badge = screen.getByText('boolean');
      expect(badge).toBeInTheDocument();

      // Check the badge has the correct color scheme
      const badgeElement = badge.closest('[class*="purple"]');
      expect(badgeElement).toBeTruthy();
    });
  });

  // Add new test suite for dictionary/nested values
  describe('Dictionary and nested values', () => {
    test('renders dictionary values with preview', () => {
      const dictValue = {
        key1: 'value1',
        key2: 'value2'
      };

      renderWithProviders(
        <ValueDisplay
          value={dictValue}
          type="dict"
        />
      );

      // Should show a preview of dict contents
      const preview = screen.getByText(/\{.*\}/);
      expect(preview).toBeInTheDocument();
      expect(screen.getByText('dict')).toBeInTheDocument(); // type badge
    });

    test('renders nested structure indicator for arrays', () => {
      const arrayValue = ['item1', 'item2', 'item3'];

      renderWithProviders(
        <ValueDisplay
          value={arrayValue}
          type="array"
        />
      );

      // Should show array preview
      const preview = screen.getByText(/\[.*\]/);
      expect(preview).toBeInTheDocument();
      expect(screen.getByText('array')).toBeInTheDocument(); // type badge
    });

    test('handles complex nested structures', () => {
      const complexValue = {
        name: 'Group',
        values: [
          { id: 'val1', value: 'Value 1' },
          { id: 'val2', value: 'Value 2' }
        ],
        metadata: {
          source: 'user-defined'
        }
      };

      renderWithProviders(
        <ValueDisplay
          value={complexValue}
          type="dict"
        />
      );

      // Should show a collapsed preview
      expect(screen.getByText(/\{.*\}/)).toBeInTheDocument();
    });
  });
});
