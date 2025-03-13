import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { ChakraProvider } from '@chakra-ui/react';
import { ParameterField } from '../ParameterField';
import { system } from '@/theme';

// Mock Redux
jest.mock('react-redux', () => ({
  useDispatch: jest.fn(),
  useSelector: jest.fn()
}));

// Mock the DelayedField component for simplified testing
jest.mock('../delayedField', () => ({
  DelayedField: ({ value, onBlur, children }: any) => {
    const renderProps = children(value, (newVal: any) => { }, () => onBlur(value));
    return <div data-testid="delayed-field">{renderProps}</div>;
  }
}));

// Mock the StringInput component
jest.mock('../inputs/StringInput', () => ({
  StringInput: ({ name, value, onChange, onBlur }: any) => (
    <input
      data-testid="string-input"
      name={name}
      value={value || ''}
      onChange={(e: any) => onChange(name, e.target.value)}
      onBlur={onBlur}
    />
  )
}));

// Mock the NumberInput component
jest.mock('../inputs/NumericInput', () => ({
  NumberInput: ({ name, value, onChange, onBlur }: any) => (
    <input
      data-testid="number-input"
      name={name}
      type="number"
      value={value || 0}
      onChange={(e: any) => onChange(name, Number(e.target.value))}
      onBlur={onBlur}
    />
  )
}));

// Mock the BooleanInput component
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

// Mock the ArrayInput component
jest.mock('../inputs/ArrayInput', () => ({
  ArrayInput: ({ name, value, onChange, onBlur }: any) => (
    <div data-testid="array-input">
      <input
        value={Array.isArray(value) ? value.join(',') : value || ''}
        onChange={(e: any) => onChange(name, e.target.value.split(','))}
        onBlur={onBlur}
        data-testid="array-input-field"
      />
    </div>
  )
}));

// Mock the hierarchical mapping component
jest.mock('../HierarchicalMapping', () => ({
  HierarchicalMapping: ({ name, value, onChange }: any) => (
    <div data-testid="hierarchical-mapping">
      <button
        data-testid="mapping-change-button"
        onClick={() => onChange({ newKey: 'newValue' })}
      >
        Change Mapping
      </button>
      <pre>{JSON.stringify(value)}</pre>
    </div>
  )
}));

// Mock the context
jest.mock('../contexts/nestedMappingContext', () => ({
  useNestedMapping: jest.fn().mockReturnValue({})
}));

// Helper to render with providers
const renderWithChakra = (ui: React.ReactElement) => {
  return render(
    <ChakraProvider value={system}>{ui}</ChakraProvider>
  );
};

describe('ParameterField Component', () => {
  // Basic rendering tests
  describe('Rendering', () => {
    test('renders with string parameter type', () => {
      const onChange = jest.fn();
      const config = {
        type: 'string',
        description: 'A test string parameter',
        required: true,
        constraints: {}
      };

      renderWithChakra(
        <ParameterField
          name="testParam"
          config={config}
          value="test value"
          onChange={onChange}
        />
      );

      // Check that the parameter name and description are rendered
      expect(screen.getByText('testParam')).toBeInTheDocument();
      expect(screen.getByText('A test string parameter')).toBeInTheDocument();

      // Check for required badge
      expect(screen.getByText('Required')).toBeInTheDocument();

      // Check for type badge
      expect(screen.getByText('string')).toBeInTheDocument();

      // Check that the string input is rendered
      expect(screen.getByTestId('string-input')).toBeInTheDocument();
    });

    test('renders with number parameter type', () => {
      const onChange = jest.fn();
      const config = {
        type: 'number',
        description: 'A test number parameter',
        required: false,
        constraints: {}
      };

      renderWithChakra(
        <ParameterField
          name="testNumber"
          config={config}
          value={42}
          onChange={onChange}
        />
      );

      expect(screen.getByText('testNumber')).toBeInTheDocument();
      expect(screen.getByText('A test number parameter')).toBeInTheDocument();
      expect(screen.getByText('number')).toBeInTheDocument();

      // No required badge should be present
      expect(screen.queryByText('Required')).not.toBeInTheDocument();

      // Check that the number input is rendered
      expect(screen.getByTestId('delayed-field')).toBeInTheDocument();
      expect(screen.getByTestId('number-input')).toBeInTheDocument();
    });

    test('renders with boolean parameter type', () => {
      const onChange = jest.fn();
      const config = {
        type: 'boolean',
        description: 'A test boolean parameter',
        required: false,
        constraints: {}
      };

      renderWithChakra(
        <ParameterField
          name="testBoolean"
          config={config}
          value={true}
          onChange={onChange}
        />
      );

      expect(screen.getByText('testBoolean')).toBeInTheDocument();
      expect(screen.getByText('boolean')).toBeInTheDocument();

      // Check that the boolean input is rendered
      expect(screen.getByTestId('boolean-input')).toBeInTheDocument();
      expect(screen.getByTestId('boolean-checkbox')).toBeChecked();
    });

    test('renders with array parameter type', () => {
      const onChange = jest.fn();
      const config = {
        type: 'array',
        description: 'A test array parameter',
        required: false,
        constraints: {}
      };

      renderWithChakra(
        <ParameterField
          name="testArray"
          config={config}
          value={['one', 'two', 'three']}
          onChange={onChange}
        />
      );

      expect(screen.getByText('testArray')).toBeInTheDocument();
      expect(screen.getByText('array')).toBeInTheDocument();

      // Check that the array input is rendered
      expect(screen.getByTestId('array-input')).toBeInTheDocument();
    });

    test('renders with dict parameter type', () => {
      const onChange = jest.fn();
      const config = {
        type: 'dict',
        description: 'A test dictionary parameter',
        required: false,
        constraints: {}
      };

      renderWithChakra(
        <ParameterField
          name="testDict"
          config={config}
          value={{ key: 'value' }}
          onChange={onChange}
        />
      );

      expect(screen.getByText('testDict')).toBeInTheDocument();
      expect(screen.getByText('dict')).toBeInTheDocument();

      // Check that the hierarchical mapping is rendered
      expect(screen.getByTestId('hierarchical-mapping')).toBeInTheDocument();
    });

    test('renders string input with array options', () => {
      const onChange = jest.fn();
      const config = {
        type: 'string',
        description: 'A test string with options',
        required: false,
        constraints: {
          array: ['option1', 'option2', 'option3']
        }
      };

      renderWithChakra(
        <ParameterField
          name="testStringOptions"
          config={config}
          value="option1"
          onChange={onChange}
        />
      );

      expect(screen.getByText('testStringOptions')).toBeInTheDocument();
      expect(screen.getByTestId('delayed-field')).toBeInTheDocument();
      expect(screen.getByTestId('array-input')).toBeInTheDocument();
    });
  });

  // Interaction tests
  describe('Interactions', () => {
    test('calls onChange when string input changes', () => {
      const onChange = jest.fn();
      const config = {
        type: 'string',
        description: 'A test string parameter',
        constraints: {}
      };

      renderWithChakra(
        <ParameterField
          name="testParam"
          config={config}
          value="initial value"
          onChange={onChange}
        />
      );

      const input = screen.getByTestId('string-input');
      fireEvent.blur(input);

      // onChange should be called with the correct name and value
      expect(onChange).toHaveBeenCalled();
    });

    test('calls onChange when hierarchical mapping changes', () => {
      const onChange = jest.fn();
      const config = {
        type: 'dict',
        description: 'A test dictionary parameter',
        constraints: {}
      };

      renderWithChakra(
        <ParameterField
          name="testDict"
          config={config}
          value={{ oldKey: 'oldValue' }}
          onChange={onChange}
        />
      );

      // Click the mapping change button to trigger a change
      const changeButton = screen.getByTestId('mapping-change-button');
      fireEvent.click(changeButton);

      // onChange should be called with correct name and new mapping
      expect(onChange).toHaveBeenCalledWith('testDict', { newKey: 'newValue' });
    });
  });

  // Type handling tests
  describe('Type handling', () => {
    test('handles function as type parameter', () => {
      const onChange = jest.fn();

      // Create a function type (a class constructor is a function)
      class TestClass { }

      const config = {
        type: TestClass,
        description: 'A test parameter with function type',
        constraints: {}
      };

      renderWithChakra(
        <ParameterField
          name="functionTypeParam"
          config={config}
          value="test value"
          onChange={onChange}
        />
      );

      // Should show the function name in lowercase
      expect(screen.getByText('testclass')).toBeInTheDocument();

      // Default to string input for unknown types
      expect(screen.getByTestId('string-input')).toBeInTheDocument();
    });

    test('handles string type aliases', () => {
      const onChange = jest.fn();
      const config = {
        type: 'str', // 'str' is an alias for 'string'
        description: 'A test string with alias type',
        constraints: {}
      };

      renderWithChakra(
        <ParameterField
          name="stringAliasParam"
          config={config}
          value="test value"
          onChange={onChange}
        />
      );

      expect(screen.getByText('str')).toBeInTheDocument();
      expect(screen.getByTestId('string-input')).toBeInTheDocument();
    });

    test('handles integer type aliases', () => {
      const onChange = jest.fn();
      const config = {
        type: 'int', // 'int' is an alias for 'number'
        description: 'A test integer with alias type',
        constraints: {}
      };

      renderWithChakra(
        <ParameterField
          name="intAliasParam"
          config={config}
          value={42}
          onChange={onChange}
        />
      );

      expect(screen.getByText('int')).toBeInTheDocument();
      expect(screen.getByTestId('delayed-field')).toBeInTheDocument();
      expect(screen.getByTestId('number-input')).toBeInTheDocument();
    });

    test('handles bool type alias', () => {
      const onChange = jest.fn();
      const config = {
        type: 'bool', // 'bool' is an alias for 'boolean'
        description: 'A test boolean with alias type',
        constraints: {}
      };

      renderWithChakra(
        <ParameterField
          name="boolAliasParam"
          config={config}
          value={false}
          onChange={onChange}
        />
      );

      expect(screen.getByText('bool')).toBeInTheDocument();
      expect(screen.getByTestId('boolean-input')).toBeInTheDocument();
    });
  });
});