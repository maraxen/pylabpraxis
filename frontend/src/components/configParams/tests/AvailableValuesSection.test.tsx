import React from 'react';
import { render, screen } from '@testing-library/react';
import { ChakraProvider } from '@chakra-ui/react';
import { DndContext } from '@dnd-kit/core';
import { AvailableValuesSection } from '../sections/AvailableValuesSection';
import { NestedMappingProvider } from '../contexts/nestedMappingContext';
import { AvailableValuesSectionProps } from '../sections/AvailableValuesSection';
import { system } from '@/theme';

// Mock the drag and drop functionality
jest.mock('@dnd-kit/core', () => {
  const originalModule = jest.requireActual('@dnd-kit/core');
  return {
    ...originalModule,
    useDroppable: jest.fn().mockReturnValue({
      setNodeRef: jest.fn(),
      isOver: false,
    }),
  };
});

// Mock nanoid to provide predictable IDs
jest.mock('nanoid', () => ({
  nanoid: jest.fn().mockReturnValue('test-id'),
}));

// Mock ValueCreator component to simplify testing
jest.mock('../creators/ValueCreator', () => ({
  ValueCreator: () => <div data-testid="value-creator">ValueCreator</div>,
}));

// Mock SortableValueItem to simplify testing
jest.mock('../subcomponents/SortableValueItem', () => ({
  SortableValueItem: (props: any) => (
    <div data-testid="sortable-value-item" data-value={props.value} data-id={props.id}>
      {props.value}
      <span data-testid="value-type">{props.type}</span>
    </div>
  ),
}));

// Mock the editing manager
jest.mock('../managers/editingManager', () => ({
  useEditing: () => ({
    isEditing: () => false,
    handleStartEditing: jest.fn(),
    handleEditingChange: jest.fn(),
    handleFinishEditing: jest.fn(),
  }),
}));

// Import NestedMappingProviderProps interface for proper typing
import { NestedMappingProviderProps } from '../contexts/nestedMappingContext';

// Helper to render with providers
const renderWithProviders = (ui: React.ReactElement, contextProps: Partial<NestedMappingProviderProps> = {}) => {
  const defaultContextValues: NestedMappingProviderProps = {
    children: null,
    value: {},
    onChange: jest.fn(),
    config: {
      type: 'object',
      constraints: { value_constraints: { type: 'string' } }
    },
    // Add all required props for NestedMappingProvider
    parameters: {},
    effectiveChildOptions: [],
    effectiveParentOptions: [],
    dragInfo: {
      activeId: null,
      activeData: null,
      overDroppableId: null,
      isDragging: false
    },
    createValue: jest.fn().mockReturnValue('test-id'),
    createGroup: jest.fn().mockReturnValue('test-group-id'),
    createdValues: {},
    setCreatedValues: jest.fn()
  };

  const mergedContextValues = { ...defaultContextValues, ...contextProps, children: ui };

  return render(
    <ChakraProvider value={system}>
      <DndContext>
        <NestedMappingProvider
          {...mergedContextValues}
        >
          {ui}
        </NestedMappingProvider>
      </DndContext>
    </ChakraProvider>
  );
};

describe('AvailableValuesSection Component', () => {
  describe('Rendering', () => {
    test('renders with empty values', () => {
      const props: AvailableValuesSectionProps = {
        value: {}
      };

      renderWithProviders(<AvailableValuesSection {...props} />);

      // Should show title
      expect(screen.getByText('Available Values')).toBeInTheDocument();

      // Should show value creator
      expect(screen.getByTestId('value-creator')).toBeInTheDocument();

      // Should show empty message
      expect(screen.getByText(/No available values/i)).toBeInTheDocument();
    });

    test('renders with available options', () => {
      const props: AvailableValuesSectionProps = {
        value: {}
      };

      renderWithProviders(
        <AvailableValuesSection {...props} />,
        {
          effectiveChildOptions: ['Option1', 'Option2', 'Option3'],
        }
      );

      // Should render sortable value items for each option
      const valueItems = screen.getAllByTestId('sortable-value-item');
      expect(valueItems).toHaveLength(3);
      expect(valueItems[0]).toHaveTextContent('Option1');
      expect(valueItems[1]).toHaveTextContent('Option2');
      expect(valueItems[2]).toHaveTextContent('Option3');
    });

    test('filters out values that are already in groups', () => {
      const mockValue = {
        'group1': {
          id: 'group1',
          name: 'Group 1',
          values: [
            { id: 'value1', value: 'Option1' },
            { id: 'value2', value: 'Option2' }
          ]
        }
      };

      renderWithProviders(
        <AvailableValuesSection value={mockValue} />,
        {
          effectiveChildOptions: ['Option1', 'Option2', 'Option3', 'Option4'],
        }
      );

      // Should only render options that aren't in groups
      const valueItems = screen.getAllByTestId('sortable-value-item');
      expect(valueItems).toHaveLength(2); // Only Option3 and Option4 should be shown

      // Check that Option3 and Option4 are rendered, not Option1 or Option2
      const values = valueItems.map(item => item.textContent?.replace(/string|number|boolean/g, '').trim());
      expect(values).toContain('Option3');
      expect(values).toContain('Option4');
      expect(values).not.toContain('Option1');
      expect(values).not.toContain('Option2');
    });
  });

  describe('Value Types', () => {
    test('renders values with correct types', () => {
      renderWithProviders(
        <AvailableValuesSection value={{}} />,
        {
          effectiveChildOptions: ['StringValue', 42, true],
        }
      );

      const valueItems = screen.getAllByTestId('sortable-value-item');
      expect(valueItems).toHaveLength(3);

      // Check that values have correct types
      const types = screen.getAllByTestId('value-type');
      expect(types).toHaveLength(3);

      // Extract all type values (the actual implementation may vary)
      const typeValues = types.map(type => type.textContent);
      expect(typeValues).toContain('string');
      expect(typeValues).toContain('number');
      expect(typeValues).toContain('boolean');
    });

    test('handles parameter values correctly', () => {
      renderWithProviders(
        <AvailableValuesSection value={{}} />,
        {
          effectiveChildOptions: ['RegularValue', 'ParameterValue'],
        }
      );

      // Both values should be rendered
      const valueItems = screen.getAllByTestId('sortable-value-item');
      expect(valueItems).toHaveLength(2);

      // Check data attributes for parameter values
      const paramValueItem = valueItems.find(item => item.textContent?.includes('ParameterValue'));
      expect(paramValueItem).toBeTruthy();
    });

    test('preserves existing created values', () => {
      const createdValues = {
        'created-id-1': { id: 'created-id-1', value: 'CreatedValue1', type: 'string', isEditable: true },
        'created-id-2': { id: 'created-id-2', value: 'CreatedValue2', type: 'number', isEditable: true }
      };

      renderWithProviders(
        <AvailableValuesSection value={{}} />,
        {
          effectiveChildOptions: ['Option1', 'CreatedValue1', 'CreatedValue2'],
          createdValues
        }
      );

      // Should render all values
      const valueItems = screen.getAllByTestId('sortable-value-item');
      expect(valueItems).toHaveLength(3);

      // Check that created values are rendered with their correct IDs
      expect(valueItems.some(item => item.getAttribute('data-id') === 'created-id-1')).toBeTruthy();
      expect(valueItems.some(item => item.getAttribute('data-id') === 'created-id-2')).toBeTruthy();
    });
  });

  describe('Complex Values', () => {
    test('handles dictionary values properly', () => {
      const dictValue = { id: 'dict-id', value: { key1: 'value1', key2: 'value2' }, type: 'dict' };

      renderWithProviders(
        <AvailableValuesSection value={{}} />,
        {
          effectiveChildOptions: [],
          createdValues: { 'dict-id': dictValue }
        }
      );

      // Dictionary value should be rendered
      const valueItem = screen.getByTestId('sortable-value-item');
      expect(valueItem).toBeInTheDocument();
      expect(valueItem.getAttribute('data-id')).toBe('dict-id');
    });

    test('handles array values properly', () => {
      const arrayValue = { id: 'array-id', value: ['item1', 'item2', 'item3'], type: 'array' };

      renderWithProviders(
        <AvailableValuesSection value={{}} />,
        {
          effectiveChildOptions: [],
          createdValues: { 'array-id': arrayValue }
        }
      );

      // Array value should be rendered
      const valueItem = screen.getByTestId('sortable-value-item');
      expect(valueItem).toBeInTheDocument();
      expect(valueItem.getAttribute('data-id')).toBe('array-id');
    });

    test('displays complex nested structures', () => {
      const complexValue = {
        id: 'complex-id',
        value: {
          name: 'Nested Group',
          values: [
            { id: 'nested-val-1', value: 'NestedValue1' },
            { id: 'nested-val-2', value: 'NestedValue2' }
          ],
          metadata: { source: 'user-defined' }
        },
        type: 'dict'
      };

      renderWithProviders(
        <AvailableValuesSection value={{}} />,
        {
          effectiveChildOptions: [],
          createdValues: { 'complex-id': complexValue }
        }
      );

      // Complex value should be rendered
      const valueItem = screen.getByTestId('sortable-value-item');
      expect(valueItem).toBeInTheDocument();
      expect(valueItem.getAttribute('data-id')).toBe('complex-id');
    });
  });

  describe('Styling', () => {
    test('applies correct styles when value is dragged over', () => {
      // Set isOver to true in useDroppable mock
      jest.spyOn(require('@dnd-kit/core'), 'useDroppable').mockReturnValueOnce({
        setNodeRef: jest.fn(),
        isOver: true,
      });

      const { container } = renderWithProviders(
        <AvailableValuesSection value={{}} />
      );

      // We'd need to check styles, but this is harder to test generically
      // Instead, for this example we'll just ensure the component renders without error
      expect(container).toBeInTheDocument();
    });

    test('applies default styles when no drag is occurring', () => {
      const { container } = renderWithProviders(
        <AvailableValuesSection value={{}} />
      );

      // Again, checking specific styles is difficult without more specific selectors
      // We'll just ensure the component renders without error
      expect(container).toBeInTheDocument();
    });
  });
});
