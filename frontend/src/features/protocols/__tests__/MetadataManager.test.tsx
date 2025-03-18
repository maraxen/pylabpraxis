import { render, renderHook, act, screen } from '@utils/test_utils';
import { MetadataManager, useValueMetadata } from '@protocols/managers/MetadataManager';

// Mock the context provider
jest.mock('../contexts/nestedMappingContext', () => ({
  useNestedMapping: jest.fn().mockReturnValue({
    localChildOptions: ['a', 'b', 100],
    valueMetadataMap: {},
    setValueMetadataMap: jest.fn(),
    getValueMetadata: jest.fn().mockImplementation((value) => {
      return {
        type: typeof value,
        isEditable: true,
        isFromParam: false,
        paramSource: undefined
      };
    })
  })
}));

// Create a wrapper component that uses the hook for testing
const TestComponent = ({ children }: { children: React.ReactNode }) => {
  return <MetadataManager>{children}</MetadataManager>;
};

// Wrapper for testing hooks with context
const createWrapper = () => {
  return ({ children }: { children: React.ReactNode }) => (
    <TestComponent>{children}</TestComponent>
  );
};

describe('MetadataManager Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  // Basic rendering tests
  describe('Rendering', () => {
    test('renders children without modification', () => {
      const { getByText } = render(
        <TestComponent>
          <div>Test Content</div>
        </TestComponent>
      );
      expect(getByText('Test Content')).toBeInTheDocument();
    });
  });

  // Effect tests
  describe('Effects', () => {
    test('initializes metadata for available options on mount', () => {
      const mockSetMetadata = jest.fn();
      // Setup mock context with specific test values
      require('../contexts/nestedMappingContext').useNestedMapping.mockReturnValueOnce({
        localChildOptions: ['value1', 'value2', 42, true],
        valueMetadataMap: {},
        setValueMetadataMap: mockSetMetadata,
        getValueMetadata: jest.fn().mockImplementation((value) => {
          const valueType = typeof value;
          return {
            type: valueType,
            isEditable: true,
            isFromParam: false
          };
        })
      });

      render(<TestComponent><div /></TestComponent>);

      // Check that setValueMetadataMap was called with correct metadata
      expect(mockSetMetadata).toHaveBeenCalledTimes(1);
      // Extract the metadata map passed to setValueMetadataMap
      const metadataMap = mockSetMetadata.mock.calls[0][0];
      // Verify values were processed
      expect(Object.keys(metadataMap)).toHaveLength(4);
      expect(metadataMap['value1']).toBeDefined();
      expect(metadataMap['value2']).toBeDefined();
      expect(metadataMap['42']).toBeDefined();
      expect(metadataMap['true']).toBeDefined();
    });

    test('updates metadata when options change', () => {
      const mockSetMetadata = jest.fn();
      const { rerender } = render(
        <TestComponent><div /></TestComponent>
      );

      // First render should have already called setValueMetadataMap once
      // Setup mock context with updated values
      require('../contexts/nestedMappingContext').useNestedMapping.mockReturnValueOnce({
        localChildOptions: ['value1', 'value3', 'newValue'],  // Changed options
        valueMetadataMap: {
          'value1': { type: 'string', isEditable: true, isFromParam: false },
          'value2': { type: 'string', isEditable: true, isFromParam: false }
        },
        setValueMetadataMap: mockSetMetadata,
        getValueMetadata: jest.fn().mockImplementation((value) => {
          const valueType = typeof value;
          return {
            type: valueType,
            isEditable: true,
            isFromParam: false
          };
        })
      });

      // Re-render with new context values
      rerender(<TestComponent><div /></TestComponent>);

      // Check that setValueMetadataMap was called again
      expect(mockSetMetadata).toHaveBeenCalledTimes(1);
      const updatedMetadata = mockSetMetadata.mock.calls[0][0];
      // Should keep 'value1', remove 'value2', add 'value3' and 'newValue'
      expect(Object.keys(updatedMetadata)).toContain('value1');
      expect(Object.keys(updatedMetadata)).toContain('value3');
      expect(Object.keys(updatedMetadata)).toContain('newValue');
      // Original value2 should be gone since it's not in localChildOptions
      expect(updatedMetadata['value2']).toBeUndefined();
    });

    test('preserves existing metadata for values that exist in both old and new options', () => {
      // Setup initial metadata map with some values
      const initialMetadata = {
        'value1': {
          type: 'string',
          isEditable: true,
          isFromParam: false,
          paramSource: 'custom-source' // Custom property to check preservation
        }
      };
      const mockSetMetadata = jest.fn();
      require('../contexts/nestedMappingContext').useNestedMapping.mockReturnValueOnce({
        localChildOptions: ['value1', 'value2'],
        valueMetadataMap: initialMetadata,
        setValueMetadataMap: mockSetMetadata,
        getValueMetadata: jest.fn().mockImplementation((_value) => {
          return {
            type: 'string',
            isEditable: true,
            isFromParam: false
          };
        })
      });

      render(<TestComponent><div /></TestComponent>);
      expect(mockSetMetadata).toHaveBeenCalledTimes(1);
      const updatedMetadata = mockSetMetadata.mock.calls[0][0];
      // Should preserve value1's custom metadata
      expect(updatedMetadata['value1']).toEqual(initialMetadata['value1']);
      expect(updatedMetadata['value1'].paramSource).toBe('custom-source');
    });

    test('handles empty options list', () => {
      const mockSetMetadata = jest.fn();
      require('../contexts/nestedMappingContext').useNestedMapping.mockReturnValueOnce({
        localChildOptions: [],
        valueMetadataMap: {},
        setValueMetadataMap: mockSetMetadata,
        getValueMetadata: jest.fn()
      });

      render(<TestComponent><div /></TestComponent>);
      expect(mockSetMetadata).toHaveBeenCalledTimes(1);
      // Should call with empty object since there are no options
      const updatedMetadata = mockSetMetadata.mock.calls[0][0];
      expect(Object.keys(updatedMetadata)).toHaveLength(0);
    });
  });

  test('renders children and updates metadata based on localChildOptions', () => {
    const mockSetValueMetadataMap = jest.fn();
    require('../contexts/nestedMappingContext').useNestedMapping.mockReturnValue({
      localChildOptions: ['a', 'b'],
      valueMetadataMap: {},
      setValueMetadataMap: mockSetValueMetadataMap,
      getValueMetadata: jest.fn().mockImplementation((val) => ({
        type: typeof val,
        isEditable: true,
        isFromParam: false,
        paramSource: undefined
      }))
    });

    render(
      <TestComponent>
        <div data-testid="content">Content</div>
      </TestComponent>
    );
    expect(mockSetValueMetadataMap).toHaveBeenCalled();
    expect(screen.getByText('Content')).toBeInTheDocument();
  });
});

describe('useValueMetadata Hook', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  // Basic hook behavior tests
  describe('Hook functionality', () => {
    test('returns metadata functions', () => {
      const contextValue = {
        valueMetadataMap: {
          'value1': { type: 'string', isEditable: true, isFromParam: false },
          'value2': { type: 'number', isEditable: false, isFromParam: true, paramSource: 'param1' }
        },
        getValueMetadata: jest.fn().mockImplementation((value) => ({
          type: typeof value,
          isEditable: false,
          isFromParam: false
        }))
      };
      require('../contexts/nestedMappingContext').useNestedMapping.mockReturnValue(contextValue);

      const { result } = renderHook(() => useValueMetadata());

      // Check that the hook returns expected functions
      expect(result.current.getMetadata).toBeInstanceOf(Function);
      expect(result.current.isEditable).toBeInstanceOf(Function);
      expect(result.current.getValueType).toBeInstanceOf(Function);
      expect(result.current.isFromParam).toBeInstanceOf(Function);
      expect(result.current.getParamSource).toBeInstanceOf(Function);
      expect(result.current.allMetadata).toBeDefined();
    });

    test('getMetadata returns correct metadata', () => {
      const mockMetadata = {
        'existingValue': { type: 'string', isEditable: true, isFromParam: false }
      };
      require('../contexts/nestedMappingContext').useNestedMapping.mockReturnValue({
        valueMetadataMap: mockMetadata,
        getValueMetadata: jest.fn().mockImplementation((_value) => ({
          type: 'string',
          isEditable: false,
          isFromParam: false,
          paramSource: undefined
        }))
      });

      const { result } = renderHook(() => useValueMetadata());

      // Should return metadata from map for existing values
      expect(result.current.getMetadata('existingValue')).toEqual(mockMetadata['existingValue']);
      // Should call getValueMetadata for new values
      expect(result.current.getMetadata('newValue')).toEqual({
        type: 'string',
        isEditable: false,
        isFromParam: false,
        paramSource: undefined
      });
    });

    test('isEditable returns correct value', () => {
      const mockMetadata = {
        'editableValue': { type: 'string', isEditable: true, isFromParam: false },
        'nonEditableValue': { type: 'string', isEditable: false, isFromParam: false }
      };
      require('../contexts/nestedMappingContext').useNestedMapping.mockReturnValue({
        valueMetadataMap: mockMetadata,
        getValueMetadata: jest.fn().mockImplementation((_value) => ({
          type: 'string',
          isEditable: false,
          isFromParam: false
        }))
      });

      const { result } = renderHook(() => useValueMetadata());
      expect(result.current.isEditable('editableValue')).toBe(true);
      expect(result.current.isEditable('nonEditableValue')).toBe(false);
    });

    test('getValueType returns correct type', () => {
      const mockMetadata = {
        'stringValue': { type: 'string', isEditable: true, isFromParam: false },
        'numberValue': { type: 'number', isEditable: true, isFromParam: false },
        'booleanValue': { type: 'boolean', isEditable: true, isFromParam: false }
      };
      require('../contexts/nestedMappingContext').useNestedMapping.mockReturnValue({
        valueMetadataMap: mockMetadata,
        getValueMetadata: jest.fn().mockImplementation((_value) => ({
          type: 'unknown',
          isEditable: true,
          isFromParam: false
        }))
      });

      const { result } = renderHook(() => useValueMetadata());
      expect(result.current.getValueType('stringValue')).toBe('string');
      expect(result.current.getValueType('numberValue')).toBe('number');
      expect(result.current.getValueType('booleanValue')).toBe('boolean');
      expect(result.current.getValueType('unknownValue')).toBe('unknown');
    });

    test('isFromParam returns correct value', () => {
      const mockMetadata = {
        'normalValue': { type: 'string', isEditable: true, isFromParam: false },
        'paramValue': { type: 'string', isEditable: false, isFromParam: true }
      };
      require('../contexts/nestedMappingContext').useNestedMapping.mockReturnValue({
        valueMetadataMap: mockMetadata,
        getValueMetadata: jest.fn().mockImplementation((_value) => ({
          type: 'string',
          isEditable: true,
          isFromParam: false
        }))
      });

      const { result } = renderHook(() => useValueMetadata());
      expect(result.current.isFromParam('normalValue')).toBe(false);
      expect(result.current.isFromParam('paramValue')).toBe(true);
    });

    test('getParamSource returns correct source', () => {
      const mockMetadata = {
        'normalValue': { type: 'string', isEditable: true, isFromParam: false, paramSource: undefined },
        'paramValue': { type: 'string', isEditable: false, isFromParam: true, paramSource: 'testParam' }
      };
      require('../contexts/nestedMappingContext').useNestedMapping.mockReturnValue({
        valueMetadataMap: mockMetadata,
        getValueMetadata: jest.fn().mockImplementation((_value) => ({
          type: 'string',
          isEditable: true,
          isFromParam: false,
          paramSource: undefined
        }))
      });

      const { result } = renderHook(() => useValueMetadata());
      expect(result.current.getParamSource('normalValue')).toBeUndefined();
      expect(result.current.getParamSource('paramValue')).toBe('testParam');
    });

    test('allMetadata returns complete metadata map', () => {
      const mockMetadata = {
        'value1': { type: 'string', isEditable: true, isFromParam: false },
        'value2': { type: 'number', isEditable: false, isFromParam: true }
      };
      require('../contexts/nestedMappingContext').useNestedMapping.mockReturnValue({
        valueMetadataMap: mockMetadata,
        getValueMetadata: jest.fn()
      });

      const { result } = renderHook(() => useValueMetadata());
      expect(result.current.allMetadata).toEqual(mockMetadata);
    });
  });

  test('returns correct metadata for existing and new values', () => {
    const mockMetadata = {
      'a': { type: 'string', isEditable: false, isFromParam: false, paramSource: 'custom' }
    };
    require('../contexts/nestedMappingContext').useNestedMapping.mockReturnValue({
      localChildOptions: ['a', 'c'],
      valueMetadataMap: mockMetadata,
      setValueMetadataMap: jest.fn(),
      getValueMetadata: jest.fn().mockImplementation((value) => ({
        type: typeof value,
        isEditable: true,
        isFromParam: false,
        paramSource: undefined
      }))
    });

    const { result } = renderHook(() => useValueMetadata());
    // existing metadata is preserved
    expect(result.current.getMetadata('a')).toEqual(mockMetadata['a']);
    // for new value, hook returns value from getValueMetadata
    expect(result.current.getMetadata('c')).toEqual({
      type: 'string',
      isEditable: true,
      isFromParam: false,
      paramSource: undefined
    });
  });
});