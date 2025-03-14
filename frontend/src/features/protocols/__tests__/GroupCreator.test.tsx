import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ChakraProvider } from '@chakra-ui/react';
import { GroupCreator } from '../components/molecules/groupCreator';
import { system } from '@/theme';

// Mock dependencies
jest.mock('@choc-ui/chakra-autocomplete', () => ({
  AutoComplete: ({ children, onSelectOption, creatable }: any) => (
    <div data-testid="auto-complete" data-creatable={creatable}>
      {children}
      <button
        data-testid="mock-select-option"
        onClick={() => onSelectOption({ item: { value: 'selected-option' } })}
      >
        Select Option
      </button>
    </div>
  ),
  AutoCompleteInput: React.forwardRef(({ placeholder, onBlur }: any, ref: any) => (
    <input
      data-testid="auto-complete-input"
      placeholder={placeholder}
      onBlur={onBlur}
      ref={ref}
    />
  )),
  AutoCompleteList: ({ children }: any) => (
    <div data-testid="auto-complete-list">{children}</div>
  ),
  AutoCompleteItem: ({ value, children }: any) => (
    <div data-testid="auto-complete-item" data-value={value}>{children}</div>
  ),
  AutoCompleteCreatable: ({ children }: any) => (
    <div data-testid="auto-complete-creatable">
      {children({ value: 'new-group' })}
    </div>
  )
}));

// Mock the StringInput component
jest.mock('../inputs/StringInput', () => ({
  StringInput: React.forwardRef(({ name, value, onChange }: any, ref: any) => (
    <input
      data-testid="string-input"
      name={name}
      value={value}
      onChange={(e: any) => onChange(name, e.target.value)}
      ref={ref}
    />
  ))
}));

// Mock the NumberInput component
jest.mock('../inputs/NumericInput', () => ({
  NumberInput: React.forwardRef(({ name, value, onChange }: any, ref: any) => (
    <input
      data-testid="number-input"
      name={name}
      value={value}
      type="number"
      onChange={(e: any) => onChange(name, Number(e.target.value))}
      ref={ref}
    />
  ))
}));

// Mock the context
jest.mock('../contexts/nestedMappingContext', () => ({
  useNestedMapping: jest.fn().mockReturnValue({
    localParentOptions: ['group1', 'group2'],
    creationMode: null,
    setCreationMode: jest.fn(),
    creatableKey: true,
    createGroup: jest.fn(),
    valueType: 'string',
    config: {
      constraints: {
        key_constraints: { type: 'string', editable: true },
        value_constraints: { type: 'string', editable: true }
      }
    }
  })
}));

// Memoization utility mock
jest.mock('../utils/memoUtils', () => ({
  createMemoComponent: (component: any) => component
}));

// Helper to render with providers
const renderWithChakra = (ui: React.ReactElement) => {
  return render(
    <ChakraProvider value={system}>{ui}</ChakraProvider>
  );
};

describe('GroupCreator Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  // Basic rendering tests
  describe('Rendering', () => {
    test('renders button when not in creation mode', () => {
      renderWithChakra(
        <GroupCreator value={{}} />
      );

      // Should render the "Add Group" button
      const button = screen.getByText('Add Group');
      expect(button).toBeInTheDocument();
    });

    test('disables button when not creatable', () => {
      // Mock context to make groups not creatable
      require('../contexts/nestedMappingContext').useNestedMapping.mockReturnValueOnce({
        ...require('../contexts/nestedMappingContext').useNestedMapping(),
        creatableKey: false,
        config: { constraints: {} }
      });

      renderWithChakra(
        <GroupCreator value={{}} />
      );

      // Button should be disabled
      const button = screen.getByText('Add Group');
      expect(button).toBeDisabled();
    });

    test('renders autocomplete when in creation mode with string type', () => {
      // Mock context with creation mode = 'group'
      require('../contexts/nestedMappingContext').useNestedMapping.mockReturnValueOnce({
        ...require('../contexts/nestedMappingContext').useNestedMapping(),
        creationMode: 'group',
        valueType: 'string'
      });

      renderWithChakra(
        <GroupCreator value={{}} />
      );

      // Should render autocomplete components
      expect(screen.getByTestId('auto-complete')).toBeInTheDocument();
      expect(screen.getByTestId('auto-complete-input')).toBeInTheDocument();
      expect(screen.getByText('Cancel')).toBeInTheDocument();
    });

    test('renders number input when in creation mode with number type', () => {
      // Mock context with creation mode = 'group' and number type
      require('../contexts/nestedMappingContext').useNestedMapping.mockReturnValueOnce({
        ...require('../contexts/nestedMappingContext').useNestedMapping(),
        creationMode: 'group',
        valueType: 'string',
        config: {
          constraints: {
            key_constraints: { type: 'number' }
          }
        }
      });

      renderWithChakra(
        <GroupCreator value={{}} />
      );

      // Should render number input
      expect(screen.getByTestId('number-input')).toBeInTheDocument();
      expect(screen.getByText('Create')).toBeInTheDocument();
      expect(screen.getByText('Cancel')).toBeInTheDocument();
    });

    test('renders error message for unsupported boolean type', () => {
      // Mock context with boolean type
      require('../contexts/nestedMappingContext').useNestedMapping.mockReturnValueOnce({
        ...require('../contexts/nestedMappingContext').useNestedMapping(),
        creationMode: 'group',
        config: {
          constraints: {
            key_constraints: { type: 'boolean' }
          }
        }
      });

      renderWithChakra(
        <GroupCreator value={{}} />
      );

      // Should show error message
      expect(screen.getByText('Unsupported Group Type')).toBeInTheDocument();
      expect(screen.getByText('Boolean values cannot be used as group identifiers.')).toBeInTheDocument();
    });

    test('renders available options in autocomplete list', () => {
      // Mock context with creation mode = 'group'
      require('../contexts/nestedMappingContext').useNestedMapping.mockReturnValueOnce({
        ...require('../contexts/nestedMappingContext').useNestedMapping(),
        creationMode: 'group',
        localParentOptions: ['available1', 'available2']
      });

      renderWithChakra(
        <GroupCreator value={{}} />
      );

      // Check available options
      const items = screen.getAllByTestId('auto-complete-item');
      expect(items).toHaveLength(2);
      expect(items[0]).toHaveTextContent('available1');
      expect(items[1]).toHaveTextContent('available2');
    });

    test('renders creatable option when creatableKey is true', () => {
      // Mock context with creation mode = 'group' and creatableKey = true
      require('../contexts/nestedMappingContext').useNestedMapping.mockReturnValueOnce({
        ...require('../contexts/nestedMappingContext').useNestedMapping(),
        creationMode: 'group',
        creatableKey: true
      });

      renderWithChakra(
        <GroupCreator value={{}} />
      );

      // Should show the creatable option
      expect(screen.getByTestId('auto-complete-creatable')).toBeInTheDocument();
      expect(screen.getByText('Create group "new-group"')).toBeInTheDocument();
    });
  });

  // Interaction tests
  describe('Interactions', () => {
    test('calls setCreationMode when button is clicked', () => {
      const mockSetCreationMode = jest.fn();

      require('../contexts/nestedMappingContext').useNestedMapping.mockReturnValueOnce({
        ...require('../contexts/nestedMappingContext').useNestedMapping(),
        setCreationMode: mockSetCreationMode
      });

      renderWithChakra(
        <GroupCreator value={{}} />
      );

      // Click the Add Group button
      const button = screen.getByText('Add Group');
      fireEvent.click(button);

      // setCreationMode should be called with 'group'
      expect(mockSetCreationMode).toHaveBeenCalledWith('group');
    });

    test('calls createGroup when an option is selected', () => {
      const mockCreateGroup = jest.fn();
      const mockSetCreationMode = jest.fn();

      require('../contexts/nestedMappingContext').useNestedMapping.mockReturnValueOnce({
        ...require('../contexts/nestedMappingContext').useNestedMapping(),
        creationMode: 'group',
        createGroup: mockCreateGroup,
        setCreationMode: mockSetCreationMode
      });

      renderWithChakra(
        <GroupCreator value={{}} />
      );

      // Click the mock "Select Option" button
      const selectButton = screen.getByTestId('mock-select-option');
      fireEvent.click(selectButton);

      // createGroup should be called with the selected option
      expect(mockCreateGroup).toHaveBeenCalledWith('selected-option');
      // setCreationMode should be called with null
      expect(mockSetCreationMode).toHaveBeenCalledWith(null);
    });

    test('calls setCreationMode(null) when Cancel is clicked', () => {
      const mockSetCreationMode = jest.fn();

      require('../contexts/nestedMappingContext').useNestedMapping.mockReturnValueOnce({
        ...require('../contexts/nestedMappingContext').useNestedMapping(),
        creationMode: 'group',
        setCreationMode: mockSetCreationMode
      });

      renderWithChakra(
        <GroupCreator value={{}} />
      );

      // Click the Cancel button
      const cancelButton = screen.getByText('Cancel');
      fireEvent.click(cancelButton);

      // setCreationMode should be called with null
      expect(mockSetCreationMode).toHaveBeenCalledWith(null);
    });

    test('creates group with number input', async () => {
      const mockCreateGroup = jest.fn();
      const mockSetCreationMode = jest.fn();

      require('../contexts/nestedMappingContext').useNestedMapping.mockReturnValueOnce({
        ...require('../contexts/nestedMappingContext').useNestedMapping(),
        creationMode: 'group',
        createGroup: mockCreateGroup,
        setCreationMode: mockSetCreationMode,
        config: {
          constraints: {
            key_constraints: { type: 'number' }
          }
        }
      });

      renderWithChakra(
        <GroupCreator value={{}} />
      );

      // Enter a number value
      const input = screen.getByTestId('number-input');
      fireEvent.change(input, { target: { value: '42' } });

      // Click Create button
      const createButton = screen.getByText('Create');
      fireEvent.click(createButton);

      // createGroup should be called with the entered number
      expect(mockCreateGroup).toHaveBeenCalledWith(42);
      // setCreationMode should be called with null
      expect(mockSetCreationMode).toHaveBeenCalledWith(null);
    });
  });

  // Edge case tests
  describe('Edge cases', () => {
    test('does not create group when value exists already', () => {
      const mockCreateGroup = jest.fn();

      require('../contexts/nestedMappingContext').useNestedMapping.mockReturnValueOnce({
        ...require('../contexts/nestedMappingContext').useNestedMapping(),
        creationMode: 'group',
        createGroup: mockCreateGroup
      });

      // Existing value in the group
      renderWithChakra(
        <GroupCreator value={{ 'existingGroup': { id: 'existingGroup', name: 'Existing', values: [] } }} />
      );

      // Set newValue to an existing group ID
      const input = screen.getByTestId('string-input');
      fireEvent.change(input, { target: { value: 'existingGroup' } });

      // Click Create button
      const createButton = screen.getByText('Create');
      fireEvent.click(createButton);

      // createGroup should not be called for existing value
      expect(mockCreateGroup).not.toHaveBeenCalled();
    });

    test('does not create group when input is empty', () => {
      const mockCreateGroup = jest.fn();

      require('../contexts/nestedMappingContext').useNestedMapping.mockReturnValueOnce({
        ...require('../contexts/nestedMappingContext').useNestedMapping(),
        creationMode: 'group',
        createGroup: mockCreateGroup
      });

      renderWithChakra(
        <GroupCreator value={{}} />
      );

      // Leave input empty
      const input = screen.getByTestId('string-input');
      fireEvent.change(input, { target: { value: '' } });

      // Click Create button
      const createButton = screen.getByText('Create');
      fireEvent.click(createButton);

      // createGroup should not be called for empty input
      expect(mockCreateGroup).not.toHaveBeenCalled();
    });

    test('disables button when boolean type is used', () => {
      require('../contexts/nestedMappingContext').useNestedMapping.mockReturnValueOnce({
        ...require('../contexts/nestedMappingContext').useNestedMapping(),
        config: {
          constraints: {
            key_constraints: { type: 'boolean' }
          }
        }
      });

      renderWithChakra(
        <GroupCreator value={{}} />
      );

      // Button should be disabled
      const button = screen.getByText('Add Group');
      expect(button).toBeDisabled();
    });

    test('filters out existing groups from available options', () => {
      require('../contexts/nestedMappingContext').useNestedMapping.mockReturnValueOnce({
        ...require('../contexts/nestedMappingContext').useNestedMapping(),
        creationMode: 'group',
        localParentOptions: ['existing1', 'available1'],
      });

      renderWithChakra(
        <GroupCreator value={{ 'existing1': { id: 'existing1', name: 'Existing', values: [] } }} />
      );

      // Should only show available1 in the list
      const items = screen.getAllByTestId('auto-complete-item');
      expect(items).toHaveLength(1);
      expect(items[0]).toHaveTextContent('available1');
    });
  });
});