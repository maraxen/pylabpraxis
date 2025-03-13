import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ChakraProvider } from '@chakra-ui/react';
import { ValueCreator } from '../creators/ValueCreator';
import { system } from '@/theme';

// Mock dependencies
jest.mock('@choc-ui/chakra-autocomplete', () => ({
  AutoComplete: ({ children, onSelectOption, creatable }: any) => (
    <div data-testid="auto-complete" data-creatable={creatable}>
      {children}
      <button
        data-testid="mock-select-option"
        onClick={() => onSelectOption({ item: { value: 'selected-value' } })}
      >
        Select Value
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
      {children({ value: 'new-value' })}
    </div>
  )
}));

// Mock input components
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

jest.mock('../inputs/BooleanInput', () => ({
  BooleanInput: ({ name, value, onChange }: any) => (
    <div data-testid="boolean-input">
      <input
        type="checkbox"
        checked={value}
        onChange={() => onChange(name, !value)}
        data-testid="boolean-checkbox"
      />
      <label>{name}</label>
    </div>
  )
}));

// Mock storage utils
jest.mock('../utils/storageUtils', () => ({
  clearExcessStorage: jest.fn()
}));

// Mock the context
jest.mock('../contexts/nestedMappingContext', () => ({
  useNestedMapping: jest.fn().mockReturnValue({
    localChildOptions: ['value1', 'value2', 42, true],
    creationMode: null,
    setCreationMode: jest.fn(),
    creatableValue: true,
    createValue: jest.fn().mockReturnValue('new-value-id'),
    valueType: 'string',
    config: {
      constraints: {
        creatable: true,
        key_constraints: { type: 'string' },
        value_constraints: { type: 'string' }
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

describe('ValueCreator Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  // Basic rendering tests
  describe('Rendering', () => {
    test('renders button when not in creation mode', () => {
      renderWithChakra(
        <ValueCreator value={{}} />
      );

      // Should render the "Add Value" button
      const button = screen.getByText('Add Value');
      expect(button).toBeInTheDocument();
    });

    test('disables button when not creatable', () => {
      // Mock context to make values not creatable
      require('../contexts/nestedMappingContext').useNestedMapping.mockReturnValueOnce({
        ...require('../contexts/nestedMappingContext').useNestedMapping(),
        creatableValue: false,
        config: { constraints: {} }
      });

      renderWithChakra(
        <ValueCreator value={{}} />
      );

      // Button should be disabled
      const button = screen.getByText('Add Value');
      expect(button).toBeDisabled();
    });

    test('renders autocomplete when in creation mode with string type and available options', () => {
      // Mock context with creation mode = 'value'
      require('../contexts/nestedMappingContext').useNestedMapping.mockReturnValueOnce({
        ...require('../contexts/nestedMappingContext').useNestedMapping(),
        creationMode: 'value',
        valueType: 'string',
        localChildOptions: ['option1', 'option2']
      });

      renderWithChakra(
        <ValueCreator value={{}} />
      );

      // Should render autocomplete components
      expect(screen.getByTestId('auto-complete')).toBeInTheDocument();
      expect(screen.getByTestId('auto-complete-input')).toBeInTheDocument();
      expect(screen.getByText('Cancel')).toBeInTheDocument();
    });

    test('renders string input when in creation mode with no available options', () => {
      // Mock context with creation mode = 'value' and no options
      require('../contexts/nestedMappingContext').useNestedMapping.mockReturnValueOnce({
        ...require('../contexts/nestedMappingContext').useNestedMapping(),
        creationMode: 'value',
        valueType: 'string',
        localChildOptions: []
      });

      renderWithChakra(
        <ValueCreator value={{}} />
      );

      // Should render string input
      expect(screen.getByTestId('string-input')).toBeInTheDocument();
      expect(screen.getByText('Create')).toBeInTheDocument();
      expect(screen.getByText('Cancel')).toBeInTheDocument();
    });

    test('renders number input when in creation mode with number type', () => {
      // Mock context with creation mode = 'value' and number type
      require('../contexts/nestedMappingContext').useNestedMapping.mockReturnValueOnce({
        ...require('../contexts/nestedMappingContext').useNestedMapping(),
        creationMode: 'value',
        valueType: 'number',
        localChildOptions: []
      });

      renderWithChakra(
        <ValueCreator value={{}} />
      );

      // Should render number input
      expect(screen.getByTestId('number-input')).toBeInTheDocument();
      expect(screen.getByText('Create')).toBeInTheDocument();
      expect(screen.getByText('Cancel')).toBeInTheDocument();
    });

    test('renders boolean input when in creation mode with boolean type', () => {
      // Mock context with creation mode = 'value' and boolean type
      require('../contexts/nestedMappingContext').useNestedMapping.mockReturnValueOnce({
        ...require('../contexts/nestedMappingContext').useNestedMapping(),
        creationMode: 'value',
        valueType: 'boolean',
        localChildOptions: []
      });

      renderWithChakra(
        <ValueCreator value={{}} />
      );

      // Should render boolean input
      expect(screen.getByTestId('boolean-input')).toBeInTheDocument();
      expect(screen.getByText('Create')).toBeInTheDocument();
      expect(screen.getByText('Cancel')).toBeInTheDocument();
    });

    test('filters out values already in groups from available options', () => {
      // Mock context with creation mode = 'value'
      require('../contexts/nestedMappingContext').useNestedMapping.mockReturnValueOnce({
        ...require('../contexts/nestedMappingContext').useNestedMapping(),
        creationMode: 'value',
        valueType: 'string',
        localChildOptions: ['used-value', 'available-value']
      });

      // Value that is already in a group
      const mockGroups = {
        'group1': {
          id: 'group1',
          name: 'Group 1',
          values: [{ id: 'value1', value: 'used-value' }]
        }
      };

      renderWithChakra(
        <ValueCreator value={mockGroups} />
      );

      // Should only show available-value in the list
      const items = screen.getAllByTestId('auto-complete-item');
      expect(items).toHaveLength(1);
      expect(items[0]).toHaveTextContent('available-value');
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
        <ValueCreator value={{}} />
      );

      // Click the Add Value button
      const button = screen.getByText('Add Value');
      fireEvent.click(button);

      // setCreationMode should be called with 'value'
      expect(mockSetCreationMode).toHaveBeenCalledWith('value');
    });

    test('calls createValue and setCreationMode when an option is selected', () => {
      const mockCreateValue = jest.fn().mockReturnValue('new-id');
      const mockSetCreationMode = jest.fn();

      require('../contexts/nestedMappingContext').useNestedMapping.mockReturnValueOnce({
        ...require('../contexts/nestedMappingContext').useNestedMapping(),
        creationMode: 'value',
        createValue: mockCreateValue,
        setCreationMode: mockSetCreationMode
      });

      renderWithChakra(
        <ValueCreator value={{}} />
      );

      // Click the mock "Select Value" button
      const selectButton = screen.getByTestId('mock-select-option');
      fireEvent.click(selectButton);

      // createValue should be called with the selected value
      expect(mockCreateValue).toHaveBeenCalledWith('selected-value');
      // setCreationMode should be called with null
      expect(mockSetCreationMode).toHaveBeenCalledWith(null);
    });

    test('calls setCreationMode(null) when Cancel is clicked', () => {
      const mockSetCreationMode = jest.fn();

      require('../contexts/nestedMappingContext').useNestedMapping.mockReturnValueOnce({
        ...require('../contexts/nestedMappingContext').useNestedMapping(),
        creationMode: 'value',
        setCreationMode: mockSetCreationMode
      });

      renderWithChakra(
        <ValueCreator value={{}} />
      );

      // Click the Cancel button
      const cancelButton = screen.getByText('Cancel');
      fireEvent.click(cancelButton);

      // setCreationMode should be called with null
      expect(mockSetCreationMode).toHaveBeenCalledWith(null);
    });

    test('creates value with string input', () => {
      const mockCreateValue = jest.fn().mockReturnValue('new-id');
      const mockSetCreationMode = jest.fn();
      const mockClearExcessStorage = require('../utils/storageUtils').clearExcessStorage;

      require('../contexts/nestedMappingContext').useNestedMapping.mockReturnValueOnce({
        ...require('../contexts/nestedMappingContext').useNestedMapping(),
        creationMode: 'value',
        createValue: mockCreateValue,
        setCreationMode: mockSetCreationMode,
        valueType: 'string',
        localChildOptions: []
      });

      renderWithChakra(
        <ValueCreator value={{}} />
      );

      // Enter a string value
      const input = screen.getByTestId('string-input');
      fireEvent.change(input, { target: { value: 'new-string-value' } });

      // Click Create button
      const createButton = screen.getByText('Create');
      fireEvent.click(createButton);

      // clearExcessStorage should be called first
      expect(mockClearExcessStorage).toHaveBeenCalled();

      // createValue should be called with the entered string
      expect(mockCreateValue).toHaveBeenCalledWith('new-string-value');

      // setCreationMode should be called with null
      expect(mockSetCreationMode).toHaveBeenCalledWith(null);
    });

    test('creates value with number input', () => {
      const mockCreateValue = jest.fn().mockReturnValue('new-id');
      const mockSetCreationMode = jest.fn();

      require('../contexts/nestedMappingContext').useNestedMapping.mockReturnValueOnce({
        ...require('../contexts/nestedMappingContext').useNestedMapping(),
        creationMode: 'value',
        createValue: mockCreateValue,
        setCreationMode: mockSetCreationMode,
        valueType: 'number',
        localChildOptions: []
      });

      renderWithChakra(
        <ValueCreator value={{}} />
      );

      // Enter a number value
      const input = screen.getByTestId('number-input');
      fireEvent.change(input, { target: { value: '42' } });

      // Click Create button
      const createButton = screen.getByText('Create');
      fireEvent.click(createButton);

      // createValue should be called with the entered number (converted to string)
      // Note: The ValueCreator forces values to be treated as strings
      expect(mockCreateValue).toHaveBeenCalledWith('42');

      // setCreationMode should be called with null
      expect(mockSetCreationMode).toHaveBeenCalledWith(null);
    });

    test('creates value with boolean input', () => {
      const mockCreateValue = jest.fn().mockReturnValue('new-id');
      const mockSetCreationMode = jest.fn();

      require('../contexts/nestedMappingContext').useNestedMapping.mockReturnValueOnce({
        ...require('../contexts/nestedMappingContext').useNestedMapping(),
        creationMode: 'value',
        createValue: mockCreateValue,
        setCreationMode: mockSetCreationMode,
        valueType: 'boolean',
        localChildOptions: []
      });

      renderWithChakra(
        <ValueCreator value={{}} />
      );

      // Toggle the boolean to true
      const checkbox = screen.getByTestId('boolean-checkbox');
      fireEvent.click(checkbox);

      // Click Create button
      const createButton = screen.getByText('Create');
      fireEvent.click(createButton);

      // createValue should be called with 'true' (as string)
      expect(mockCreateValue).toHaveBeenCalledWith('true');

      // setCreationMode should be called with null
      expect(mockSetCreationMode).toHaveBeenCalledWith(null);
    });
  });

  // Edge case tests
  describe('Edge cases', () => {
    test('does not create value when input is empty', () => {
      const mockCreateValue = jest.fn();
      const mockSetCreationMode = jest.fn();

      require('../contexts/nestedMappingContext').useNestedMapping.mockReturnValueOnce({
        ...require('../contexts/nestedMappingContext').useNestedMapping(),
        creationMode: 'value',
        createValue: mockCreateValue,
        setCreationMode: mockSetCreationMode
      });

      renderWithChakra(
        <ValueCreator value={{}} />
      );

      // Leave input empty
      const input = screen.getByTestId('string-input');
      fireEvent.change(input, { target: { value: '' } });

      // Click Create button
      const createButton = screen.getByText('Create');
      fireEvent.click(createButton);

      // createValue should not be called for empty input
      expect(mockCreateValue).not.toHaveBeenCalled();
    });

    test('shows error when createValue returns no ID', () => {
      jest.spyOn(console, 'error').mockImplementation(() => { });
      jest.spyOn(window, 'alert').mockImplementation(() => { });

      const mockCreateValue = jest.fn().mockReturnValue(null);

      require('../contexts/nestedMappingContext').useNestedMapping.mockReturnValueOnce({
        ...require('../contexts/nestedMappingContext').useNestedMapping(),
        creationMode: 'value',
        createValue: mockCreateValue
      });

      renderWithChakra(
        <ValueCreator value={{}} />
      );

      // Enter a value
      const input = screen.getByTestId('string-input');
      fireEvent.change(input, { target: { value: 'test-value' } });

      // Click Create button
      const createButton = screen.getByText('Create');
      fireEvent.click(createButton);

      // Should log an error to console
      expect(console.error).toHaveBeenCalledWith(
        expect.stringContaining("Failed to create value")
      );

      // Should show an alert
      expect(window.alert).toHaveBeenCalledWith(
        expect.stringContaining("Unable to create value")
      );
    });

    test('shows error when createValue throws exception', () => {
      jest.spyOn(console, 'error').mockImplementation(() => { });
      jest.spyOn(window, 'alert').mockImplementation(() => { });

      const mockCreateValue = jest.fn().mockImplementation(() => {
        throw new Error("Test error");
      });

      require('../contexts/nestedMappingContext').useNestedMapping.mockReturnValueOnce({
        ...require('../contexts/nestedMappingContext').useNestedMapping(),
        creationMode: 'value',
        createValue: mockCreateValue
      });

      renderWithChakra(
        <ValueCreator value={{}} />
      );

      // Enter a value
      const input = screen.getByTestId('string-input');
      fireEvent.change(input, { target: { value: 'test-value' } });

      // Click Create button
      const createButton = screen.getByText('Create');
      fireEvent.click(createButton);

      // Should log an error to console
      expect(console.error).toHaveBeenCalledWith(
        "Error in value creation:",
        expect.any(Error)
      );

      // Should show an alert
      expect(window.alert).toHaveBeenCalledWith(
        expect.stringContaining("An error occurred while creating the value")
      );
    });

    test('handles different value type aliases correctly', () => {
      // Test different type aliases for number
      ['number', 'int', 'integer', 'float', 'double'].forEach(typeAlias => {
        jest.clearAllMocks();

        require('../contexts/nestedMappingContext').useNestedMapping.mockReturnValueOnce({
          ...require('../contexts/nestedMappingContext').useNestedMapping(),
          creationMode: 'value',
          valueType: typeAlias
        });

        const { unmount } = renderWithChakra(
          <ValueCreator value={{}} />
        );

        // Should render number input for all number type aliases
        expect(screen.getByTestId('number-input')).toBeInTheDocument();

        unmount();
      });

      // Test different type aliases for boolean
      ['boolean', 'bool'].forEach(typeAlias => {
        jest.clearAllMocks();

        require('../contexts/nestedMappingContext').useNestedMapping.mockReturnValueOnce({
          ...require('../contexts/nestedMappingContext').useNestedMapping(),
          creationMode: 'value',
          valueType: typeAlias
        });

        const { unmount } = renderWithChakra(
          <ValueCreator value={{}} />
        );

        // Should render boolean input for all boolean type aliases
        expect(screen.getByTestId('boolean-input')).toBeInTheDocument();

        unmount();
      });
    });
  });
});