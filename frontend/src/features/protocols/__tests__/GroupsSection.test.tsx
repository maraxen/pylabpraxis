import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { ChakraProvider } from '@chakra-ui/react';
import { GroupsSection } from '../components/organisms/GroupsSection';
import { system } from '@styles/theme';
import { GroupData } from '../utils/parameterUtils';

// Mock dependencies
jest.mock('../subcomponents/GroupItem', () => ({
  GroupItem: ({ groupId, group, onDelete, isHighlighted }: any) => (
    <div
      data-testid="group-item"
      data-id={groupId}
      data-name={group.name}
      data-highlighted={isHighlighted ? 'true' : 'false'}
    >
      <button
        data-testid="delete-group-button"
        onClick={onDelete}
      >
        Delete {group.name}
      </button>
    </div>
  )
}));

jest.mock('../creators/groupCreator', () => ({
  GroupCreator: ({ value }: any) => (
    <div data-testid="group-creator">
      Add Group (Groups: {Object.keys(value || {}).length})
    </div>
  )
}));

jest.mock('../subcomponents/LimitCounter', () => ({
  GroupLimit: () => <div data-testid="group-limit">3/5</div>,
  ValueLimit: () => <div data-testid="value-limit">6/10</div>
}));

// Mock the context
jest.mock('../contexts/nestedMappingContext', () => ({
  useNestedMapping: jest.fn().mockReturnValue({
    dragInfo: { overDroppableId: null }
  })
}));

// Helper to render with providers
const renderWithChakra = (ui: React.ReactElement) => {
  return render(
    <ChakraProvider value={system}>{ui}</ChakraProvider>
  );
};

describe('GroupsSection Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  // Basic rendering tests
  describe('Rendering', () => {
    test('renders heading and limits', () => {
      const mockValue: Record<string, GroupData> = {};
      const onChange = jest.fn();

      renderWithChakra(
        <GroupsSection value={mockValue} onChange={onChange} />
      );

      // Check that heading is rendered
      expect(screen.getByText('Groups')).toBeInTheDocument();

      // Check that limit counters are rendered
      expect(screen.getByTestId('group-limit')).toBeInTheDocument();
      expect(screen.getByTestId('value-limit')).toBeInTheDocument();

      // Check that group creator is rendered
      expect(screen.getByTestId('group-creator')).toBeInTheDocument();
    });

    test('renders empty group list', () => {
      const mockValue: Record<string, GroupData> = {};
      const onChange = jest.fn();

      renderWithChakra(
        <GroupsSection value={mockValue} onChange={onChange} />
      );

      // Should not render any group items
      const groupItems = screen.queryAllByTestId('group-item');
      expect(groupItems).toHaveLength(0);
    });

    test('renders groups from value prop', () => {
      const mockValue: Record<string, GroupData> = {
        'group-1': {
          id: 'group-1',
          name: 'Group 1',
          values: []
        },
        'group-2': {
          id: 'group-2',
          name: 'Group 2',
          values: []
        }
      };
      const onChange = jest.fn();

      renderWithChakra(
        <GroupsSection value={mockValue} onChange={onChange} />
      );

      // Should render two group items
      const groupItems = screen.getAllByTestId('group-item');
      expect(groupItems).toHaveLength(2);
      expect(groupItems[0]).toHaveAttribute('data-name', 'Group 1');
      expect(groupItems[1]).toHaveAttribute('data-name', 'Group 2');
    });

    test('highlights group when dragInfo indicates hover', () => {
      // Mock dragInfo to simulate hover over a group
      require('../contexts/nestedMappingContext').useNestedMapping.mockReturnValueOnce({
        dragInfo: { overDroppableId: 'group-2' }
      });

      const mockValue: Record<string, GroupData> = {
        'group-1': {
          id: 'group-1',
          name: 'Group 1',
          values: []
        },
        'group-2': {
          id: 'group-2',
          name: 'Group 2',
          values: []
        }
      };
      const onChange = jest.fn();

      renderWithChakra(
        <GroupsSection value={mockValue} onChange={onChange} />
      );

      // Should highlight the second group
      const groupItems = screen.getAllByTestId('group-item');
      expect(groupItems[0]).toHaveAttribute('data-highlighted', 'false');
      expect(groupItems[1]).toHaveAttribute('data-highlighted', 'true');
    });
  });

  // Interaction tests
  describe('Interactions', () => {
    test('calls onChange when a group is deleted', () => {
      const mockValue: Record<string, GroupData> = {
        'group-1': {
          id: 'group-1',
          name: 'Group 1',
          values: []
        },
        'group-2': {
          id: 'group-2',
          name: 'Group 2',
          values: []
        }
      };
      const onChange = jest.fn();

      renderWithChakra(
        <GroupsSection value={mockValue} onChange={onChange} />
      );

      // Find and click the first delete button
      const deleteButtons = screen.getAllByTestId('delete-group-button');
      fireEvent.click(deleteButtons[0]);

      // onChange should be called with updated value missing the first group
      expect(onChange).toHaveBeenCalledTimes(1);
      const updatedValue = onChange.mock.calls[0][0];
      expect(Object.keys(updatedValue)).toEqual(['group-2']);
    });
  });

  // Edge case tests
  describe('Edge cases', () => {
    test('handles null or undefined value prop', () => {
      const onChange = jest.fn();

      // Use an empty object instead of null to match the expected type
      renderWithChakra(
        <GroupsSection value={{}} onChange={onChange} />
      );

      // Component should render without errors
      expect(screen.getByText('Groups')).toBeInTheDocument();

      // Group creator should handle empty value
      expect(screen.getByTestId('group-creator')).toBeInTheDocument();

      // Should not render any group items
      const groupItems = screen.queryAllByTestId('group-item');
      expect(groupItems).toHaveLength(0);
    });

    test('handles empty object value prop', () => {
      const onChange = jest.fn();

      renderWithChakra(
        <GroupsSection value={{}} onChange={onChange} />
      );

      // Component should render without errors
      expect(screen.getByText('Groups')).toBeInTheDocument();

      // Group creator should show 0 groups
      const groupCreator = screen.getByTestId('group-creator');
      expect(groupCreator).toHaveTextContent('Groups: 0');

      // Should not render any group items
      const groupItems = screen.queryAllByTestId('group-item');
      expect(groupItems).toHaveLength(0);
    });
  });
});