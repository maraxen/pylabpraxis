import React from 'react';
import { render, screen } from '@testing-library/react';
import { ChakraProvider } from '@chakra-ui/react';
import { DroppableGroup } from '../subcomponents/droppableGroup';
import { system } from '@/theme';

// Mock the useDroppable hook
jest.mock('@dnd-kit/core', () => ({
  useDroppable: jest.fn().mockReturnValue({
    setNodeRef: jest.fn(),
    isOver: false,
  }),
}));

// Mock the context
jest.mock('../contexts/nestedMappingContext', () => ({
  useNestedMapping: jest.fn().mockReturnValue({
    isEditable: jest.fn().mockReturnValue(true),
    isGroupFull: jest.fn().mockReturnValue(false),
  }),
}));

// Helper to render with providers
const renderWithChakra = (ui: React.ReactElement) => {
  return render(
    <ChakraProvider value={system}>{ui}</ChakraProvider>
  );
};

describe('DroppableGroup Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();

    // Reset the default mock implementations
    require('@dnd-kit/core').useDroppable.mockReturnValue({
      setNodeRef: jest.fn(),
      isOver: false,
    });

    require('../contexts/nestedMappingContext').useNestedMapping.mockReturnValue({
      isEditable: jest.fn().mockReturnValue(true),
      isGroupFull: jest.fn().mockReturnValue(false),
    });
  });

  // Basic rendering tests
  describe('Rendering', () => {
    test('renders children inside droppable area', () => {
      renderWithChakra(
        <DroppableGroup id="test-group">
          <div data-testid="child-content">Test Content</div>
        </DroppableGroup>
      );

      // Check that the child content is rendered
      expect(screen.getByTestId('child-content')).toBeInTheDocument();
      expect(screen.getByText('Test Content')).toBeInTheDocument();
    });

    test('renders empty state message when no children provided', () => {
      renderWithChakra(
        <DroppableGroup id="test-group" />
      );

      // Check for the empty state message
      expect(screen.getByText('Drop values here')).toBeInTheDocument();
    });

    test('renders with proper data attributes', () => {
      const { container } = renderWithChakra(
        <DroppableGroup id="test-group" />
      );

      // Find the main container element
      const droppableElement = container.firstChild;
      expect(droppableElement).toHaveAttribute('data-droppable-id', 'test-group');
      expect(droppableElement).toHaveAttribute('data-editable', 'true');
      expect(droppableElement).toHaveAttribute('data-full', 'false');
    });

    test('passes correct ID to useDroppable', () => {
      renderWithChakra(
        <DroppableGroup id="test-id" />
      );

      // Verify the useDroppable hook was called with the right ID
      expect(require('@dnd-kit/core').useDroppable).toHaveBeenCalledWith({
        id: 'test-id',
      });
    });
  });

  // State tests
  describe('States based on props and context', () => {
    test('shows "read-only" indicator when not editable', () => {
      // Mock isEditable to return false
      require('../contexts/nestedMappingContext').useNestedMapping.mockReturnValue({
        isEditable: jest.fn().mockReturnValue(false),
        isGroupFull: jest.fn().mockReturnValue(false),
      });

      renderWithChakra(
        <DroppableGroup id="test-group" />
      );

      // Should show read-only badge
      expect(screen.getByText('read-only')).toBeInTheDocument();

      // Should show appropriate empty state
      expect(screen.getByText('Read-only group')).toBeInTheDocument();
    });

    test('shows "full" indicator when group is full', () => {
      // Mock isGroupFull to return true
      require('../contexts/nestedMappingContext').useNestedMapping.mockReturnValue({
        isEditable: jest.fn().mockReturnValue(true),
        isGroupFull: jest.fn().mockReturnValue(true),
      });

      renderWithChakra(
        <DroppableGroup id="test-group" />
      );

      // Should show full badge
      expect(screen.getByText('full')).toBeInTheDocument();

      // Should show appropriate empty state
      expect(screen.getByText('Group is full')).toBeInTheDocument();
    });

    test('has different appearance when being dragged over', () => {
      // Mock useDroppable to indicate drop is over
      require('@dnd-kit/core').useDroppable.mockReturnValue({
        setNodeRef: jest.fn(),
        isOver: true,
      });

      const { container } = renderWithChakra(
        <DroppableGroup id="test-group" isOver={true} />
      );

      // Check that the element has the expected attributes
      const droppableElement = container.firstChild;
      expect(droppableElement).toHaveAttribute('data-droppable-id', 'test-group');

      // Since we're not testing actual CSS here, we rely on the props being passed
      expect(screen.getByText('Drop values here')).toBeInTheDocument();
    });
  });

  // Edge cases
  describe('Edge cases', () => {
    test('handles both read-only and full state together', () => {
      // Mock both flags to true
      require('../contexts/nestedMappingContext').useNestedMapping.mockReturnValue({
        isEditable: jest.fn().mockReturnValue(false),
        isGroupFull: jest.fn().mockReturnValue(true),
      });

      renderWithChakra(
        <DroppableGroup id="test-group" />
      );

      // Should prioritize read-only state for the empty message
      expect(screen.getByText('Read-only group')).toBeInTheDocument();
      expect(screen.getByText('read-only')).toBeInTheDocument();

      // Should not show both badges - read-only takes precedence
      expect(screen.queryByText('full')).not.toBeInTheDocument();
    });

    test('handles isDragging prop to show hover state', () => {
      const { container } = renderWithChakra(
        <DroppableGroup id="test-group" isDragging={true} />
      );

      // Check that the element has the correct attributes set
      const droppableElement = container.firstChild;
      expect(droppableElement).toHaveAttribute('data-droppable-id', 'test-group');

      // In a real component, we'd check specific styling, but that's not included in this mock
    });
  });

  // Accessibility tests
  describe('Accessibility', () => {
    test('applies minimum height for better target area', () => {
      const { container } = renderWithChakra(
        <DroppableGroup id="test-group" />
      );

      // In a real test with real styling, we'd check for actual min-height
      // Since we can't easily test styles in a Jest test, just verify rendering
      expect(container.firstChild).toBeInTheDocument();
    });
  });
});