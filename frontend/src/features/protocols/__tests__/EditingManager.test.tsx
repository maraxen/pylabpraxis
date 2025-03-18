import React from 'react';
import { render, screen, fireEvent, waitFor } from '@utils/test_utils';
import { EditingManager, useEditing } from '@protocols/managers/editingManager';
import { NestedMappingProvider } from '@protocols/contexts/nestedMappingContext';

const mockProviderProps = {
  config: {
    type: 'object', // <-- Added required 'type' property
    constraints: { editable: true }
  },
  parameters: {},
  value: {
    group1: {
      id: 'group1', // <-- Added group id
      name: 'Group 1', // <-- Added group name
      values: [{ id: 'test-id', value: 'init', isEditable: true, isFromParam: false }]
    }
  },
  onChange: jest.fn(),
  effectiveChildOptions: [],
  effectiveParentOptions: [],
  dragInfo: { isDragging: false, activeId: null, activeData: null, overDroppableId: null },
  createValue: jest.fn().mockReturnValue('new-id'),
  createGroup: jest.fn().mockReturnValue('new-group-id'),
  createdValues: { 'test-id': { id: 'test-id', value: 'init', isEditable: true, isFromParam: false } },
  setCreatedValues: jest.fn(),
  editingState: { id: '', value: '', group: null },
  startEditing: jest.fn(),
  updateEditingValue: jest.fn(),
  finishEditing: jest.fn(),
  cancelEditing: jest.fn(),
  valueMetadataMap: {},
  inputRef: { current: null }
};

const TestEditingComponent = () => {
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
      <div data-testid="editing-state">{JSON.stringify(editingState)}</div>
      <button onClick={() => handleStartEditing('test-id', 'init', 'group1')} data-testid="start-btn">Start Editing</button>
      <input
        ref={inputRef}
        data-testid="edit-input"
        value={getEditingValue('test-id') || ''}
        onChange={(e) => handleEditingChange(e.target.value)}
      />
      <button onClick={handleFinishEditing} data-testid="finish-btn">Finish Editing</button>
      <button onClick={handleCancelEditing} data-testid="cancel-btn">Cancel Editing</button>
    </div>
  );
};

const renderWithProviders = (ui: React.ReactElement) =>
  render(
    <NestedMappingProvider {...mockProviderProps}>
      <EditingManager>{ui}</EditingManager>
    </NestedMappingProvider>
  );

describe('EditingManager and useEditing hook', () => {
  test('renders default UI state and calls startEditing on button click', () => {
    renderWithProviders(<TestEditingComponent />);
    const startBtn = screen.getByTestId('start-btn');
    fireEvent.click(startBtn);
    expect(mockProviderProps.startEditing).toHaveBeenCalledWith('test-id', 'init', 'group1');
  });

  test('handles input change and finish editing via button and keyboard', async () => {
    renderWithProviders(<TestEditingComponent />);
    // Simulate starting editing
    fireEvent.click(screen.getByTestId('start-btn'));
    const input = screen.getByTestId('edit-input');

    // Change input value
    fireEvent.change(input, { target: { value: 'changed' } });
    expect(mockProviderProps.updateEditingValue).toHaveBeenCalledWith('changed');

    // Finish editing by button click
    fireEvent.click(screen.getByTestId('finish-btn'));
    expect(mockProviderProps.finishEditing).toHaveBeenCalled();

    // Start editing again to test keyboard event (Enter key)
    fireEvent.click(screen.getByTestId('start-btn'));
    fireEvent.keyDown(document, { key: 'Enter', code: 'Enter' });
    await waitFor(() => {
      expect(mockProviderProps.finishEditing).toHaveBeenCalledTimes(2);
    });

    // Test cancel editing by Escape key
    fireEvent.click(screen.getByTestId('start-btn'));
    fireEvent.keyDown(document, { key: 'Escape', code: 'Escape' });
    await waitFor(() => {
      expect(mockProviderProps.cancelEditing).toHaveBeenCalled();
    });
  });
});
