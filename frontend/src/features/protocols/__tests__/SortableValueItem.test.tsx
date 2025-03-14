import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { ChakraProvider } from '@chakra-ui/react';
import { DndContext } from '@dnd-kit/core';
import { SortableValueItem } from '../components/molecules/SortableValueItem';
import { SortableValueItemProps } from '../components/molecules/SortableValueItem';
import { system } from '../../../theme';

// Mock the drag-and-drop functionality since we're not testing that directly
jest.mock('@dnd-kit/core', () => {
  const originalModule = jest.requireActual('@dnd-kit/core');
  return {
    ...originalModule,
    useDraggable: jest.fn().mockReturnValue({
      attributes: {},
      listeners: {},
      setNodeRef: jest.fn(),
      transform: null,
      isDragging: false,
    }),
  };
});

jest.mock('@dnd-kit/sortable', () => {
  const originalModule = jest.requireActual('@dnd-kit/sortable');
  return {
    ...originalModule,
    useSortable: jest.fn().mockReturnValue({
      attributes: {},
      listeners: {},
      setNodeRef: jest.fn(),
      transform: null,
      transition: 'transform 250ms',
      isDragging: false,
    }),
  };
});

// Helper to render with providers
const renderWithProviders = (ui: React.ReactElement) => {
  return render(
    <ChakraProvider value={system}>
      <DndContext>
        {ui}
      </DndContext>
    </ChakraProvider>
  );
};

describe('SortableValueItem Component', () => {
  // Basic rendering tests
  describe('Rendering', () => {
    test('renders string value correctly', () => {
      const props: SortableValueItemProps = {
        id: "test-id",
        value: "Test String"
      };

      renderWithProviders(<SortableValueItem {...props} />);

      expect(screen.getByText('Test String')).toBeInTheDocument();
      expect(screen.getByText('string')).toBeInTheDocument(); // type badge
    });

    test('renders with custom type', () => {
      const props: SortableValueItemProps = {
        id: "test-id",
        value: 42,
        type: "number"
      };

      renderWithProviders(<SortableValueItem {...props} />);

      expect(screen.getByText('42')).toBeInTheDocument();
      expect(screen.getByText('number')).toBeInTheDocument(); // type badge
    });

    test('renders with parameter source badge', () => {
      renderWithProviders(
        <SortableValueItem
          id="test-id"
          value="Parameter Value"
          isFromParam={true}
          paramSource="test-param"
        />
      );

      expect(screen.getByText('Parameter Value')).toBeInTheDocument();
      expect(screen.getByText('test-param')).toBeInTheDocument();
    });

    test('renders with read-only badge when not editable', () => {
      renderWithProviders(
        <SortableValueItem
          id="test-id"
          value="Readonly Value"
          isEditable={false}
        />
      );

      expect(screen.getByText('Readonly Value')).toBeInTheDocument();
      expect(screen.getByText('read-only')).toBeInTheDocument();
    });
  });

  // Interaction tests
  describe('Interactions', () => {
    test('calls onDelete when delete button is clicked', () => {
      const onDelete = jest.fn();

      const { container } = renderWithProviders(
        <SortableValueItem
          id="test-id"
          value="Deletable Value"
          onDelete={onDelete}
        />
      );

      // Hover to show the delete button
      const itemBox = container.firstChild;
      if (itemBox) {
        fireEvent.mouseEnter(itemBox);
      }

      // Find and click the delete button
      const deleteButton = screen.getByLabelText('Delete value');
      fireEvent.click(deleteButton);

      expect(onDelete).toHaveBeenCalled();
    });

    test('calls onFocus when value is clicked', () => {
      const onFocus = jest.fn();

      renderWithProviders(
        <SortableValueItem
          id="test-id"
          value="Focusable Value"
          onFocus={onFocus}
        />
      );

      // Find and click the value
      const valueText = screen.getByText('Focusable Value');
      fireEvent.click(valueText);

      expect(onFocus).toHaveBeenCalled();
    });

    test('does not call onFocus for non-editable values', () => {
      const onFocus = jest.fn();

      renderWithProviders(
        <SortableValueItem
          id="test-id"
          value="Readonly Value"
          isEditable={false}
          onFocus={onFocus}
        />
      );

      // Find and click the value
      const valueText = screen.getByText('Readonly Value');
      fireEvent.click(valueText);

      expect(onFocus).not.toHaveBeenCalled();
    });

    test('edit button is not shown for non-editable values', () => {
      const onEdit = jest.fn();

      const { container } = renderWithProviders(
        <SortableValueItem
          id="test-id"
          value="Readonly Value"
          isEditable={false}
          onEdit={onEdit}
        />
      );

      // Hover to potentially show action buttons
      const itemBox = container.firstChild;
      if (itemBox) {
        fireEvent.mouseEnter(itemBox);
      }

      // Try to find edit button - should not be present
      const editButton = screen.queryByLabelText('Edit value');
      expect(editButton).not.toBeInTheDocument();
    });
  });

  // Handle different drag modes
  describe('Drag modes', () => {
    test('uses draggable mode when specified', () => {
      const { container } = renderWithProviders(
        <SortableValueItem
          id="test-id"
          value="Draggable Value"
          dragMode="draggable"
        />
      );

      // This is more of an implementation detail, so we're just checking that it renders
      expect(container.firstChild).toBeInTheDocument();
      expect(screen.getByText('Draggable Value')).toBeInTheDocument();
    });

    test('uses sortable mode by default', () => {
      const { container } = renderWithProviders(
        <SortableValueItem
          id="test-id"
          value="Sortable Value"
        />
      );

      expect(container.firstChild).toBeInTheDocument();
      expect(screen.getByText('Sortable Value')).toBeInTheDocument();
    });
  });

  // Test dictionary/nested value rendering
  describe('Dictionary and nested values', () => {
    test('renders dictionary value with proper format', () => {
      const dictValue = {
        name: 'Test Group',
        values: [
          { id: 'val1', value: 'Value 1' },
          { id: 'val2', value: 'Value 2' }
        ]
      };

      renderWithProviders(
        <SortableValueItem
          id="test-id"
          value={dictValue}
          type="dict"
        />
      );

      // Should render the value through ValueDisplay
      // The specific rendering depends on ValueDisplay implementation,
      // but we should see at least a collapsed representation
      const valueText = screen.getByText(/\{.*\}/);
      expect(valueText).toBeInTheDocument();
    });

    test('renders array value with proper format', () => {
      const arrayValue = ['item1', 'item2', 'item3'];

      renderWithProviders(
        <SortableValueItem
          id="test-id"
          value={arrayValue}
          type="array"
        />
      );

      // Should render array preview
      const valueText = screen.getByText(/\[.*\]/);
      expect(valueText).toBeInTheDocument();
    });
  });
});
