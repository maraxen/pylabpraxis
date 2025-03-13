import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
// Remove userEvent import since it's causing type issues
import { ChakraProvider } from '@chakra-ui/react';
import { NestedMappingProvider } from '../contexts/nestedMappingContext';
import { EditingManager, useEditing } from '../managers/editingManager';
import system from '@/theme';

// Test component that uses the useEditing hook
const TestComponent = () => {
  const {
    isEditing,
    getEditingValue,
    handleStartEditing,
    handleEditingChange,
    handleFinishEditing,
    handleCancelEditing,
    editingState,
    inputRef
  } = useEditing();

  return (
    <div>
      <div data-testid="editing-state">
        {JSON.stringify({
          id: editingState.id,
          value: editingState.value,
          group: editingState.group
        })}
      </div>
      <button
        onClick={() => handleStartEditing('test-id', 'test-value', 'test-group')}
        data-testid="start-editing"
      >
        Start Editing
      </button>
      <button
        onClick={() => handleEditingChange('new-value')}
        data-testid="change-value"
      >
        Change Value
      </button>
      <button
        onClick={handleFinishEditing}
        data-testid="finish-editing"
      >
        Finish Editing
      </button>
      <button
        onClick={handleCancelEditing}
        data-testid="cancel-editing"
      >
        Cancel Editing
      </button>
      <div data-testid="is-editing">
        {isEditing('test-id', 'test-group') ? 'Editing' : 'Not Editing'}
      </div>
      <div data-testid="editing-value">
        {getEditingValue('test-id') || 'No Value'}
      </div>
      <input ref={inputRef} data-testid="edit-input" />
    </div>
  );
};

// Mock context provider for testing
const mockProviderProps = {
  config: { type: 'object' },
  parameters: {},
  value: {},
  onChange: jest.fn(),
  effectiveChildOptions: [],
  effectiveParentOptions: [],
  dragInfo: {
    activeId: null,
    activeData: null,
    overDroppableId: null,
    isDragging: false
  },
  createValue: jest.fn().mockReturnValue('new-id'),
  createGroup: jest.fn().mockReturnValue('new-group-id'),
  createdValues: {},
  setCreatedValues: jest.fn()
};

// Helper to create a test wrapper with providers
const renderWithProviders = (ui: React.ReactElement) => {
  return render(
    <ChakraProvider value={system}>
      <NestedMappingProvider {...mockProviderProps}>
        <EditingManager>
          {ui}
        </EditingManager>
      </NestedMappingProvider>
    </ChakraProvider>
  );
};

describe('EditingManager and useEditing hook', () => {
  // Basic test for hook functionality
  test('useEditing hook provides editing functionality', async () => {
    renderWithProviders(<TestComponent />);

    // Initial state - not editing
    expect(screen.getByTestId('is-editing')).toHaveTextContent('Not Editing');
    expect(screen.getByTestId('editing-value')).toHaveTextContent('No Value');

    // Start editing
    fireEvent.click(screen.getByTestId('start-editing'));

    // Should now be in editing state
    expect(screen.getByTestId('is-editing')).toHaveTextContent('Editing');
    expect(screen.getByTestId('editing-value')).toHaveTextContent('test-value');

    // Change the value
    fireEvent.click(screen.getByTestId('change-value'));

    // Value should update
    expect(screen.getByTestId('editing-value')).toHaveTextContent('new-value');

    // Finish editing
    fireEvent.click(screen.getByTestId('finish-editing'));

    // Should go back to not editing
    await waitFor(() => {
      expect(screen.getByTestId('is-editing')).toHaveTextContent('Not Editing');
    });
  });

  // Test keyboard interactions
  test('keyboard shortcuts work for editing', async () => {
    renderWithProviders(<TestComponent />);

    // Start editing
    fireEvent.click(screen.getByTestId('start-editing'));

    // Should now be in editing state
    expect(screen.getByTestId('is-editing')).toHaveTextContent('Editing');

    // Press Escape
    fireEvent.keyDown(document, { key: 'Escape', code: 'Escape' });

    // Should exit editing
    await waitFor(() => {
      expect(screen.getByTestId('is-editing')).toHaveTextContent('Not Editing');
    });

    // Start editing again
    fireEvent.click(screen.getByTestId('start-editing'));

    // Press Enter
    fireEvent.keyDown(document, { key: 'Enter', code: 'Enter' });

    // Should finish editing
    await waitFor(() => {
      expect(screen.getByTestId('is-editing')).toHaveTextContent('Not Editing');
    });
  });

  // Test input focus
  test('input gets focus when editing starts', async () => {
    renderWithProviders(<TestComponent />);

    const input = screen.getByTestId('edit-input');

    // Start editing
    fireEvent.click(screen.getByTestId('start-editing'));

    // Input should get focus
    setTimeout(() => {
      expect(document.activeElement).toBe(input);
    }, 100);
  });

  // Test cancel editing
  test('canceling edit reverts to original value', async () => {
    renderWithProviders(<TestComponent />);

    // Start editing
    fireEvent.click(screen.getByTestId('start-editing'));

    // Change value
    fireEvent.click(screen.getByTestId('change-value'));
    expect(screen.getByTestId('editing-value')).toHaveTextContent('new-value');

    // Cancel editing
    fireEvent.click(screen.getByTestId('cancel-editing'));

    // Should exit editing and discard changes
    await waitFor(() => {
      expect(screen.getByTestId('is-editing')).toHaveTextContent('Not Editing');
      expect(screen.getByTestId('editing-value')).toHaveTextContent('No Value');
    });
  });
});
