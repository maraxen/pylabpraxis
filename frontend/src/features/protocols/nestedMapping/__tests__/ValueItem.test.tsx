import React from 'react';
import { render, screen, fireEvent } from '@utils/test_utils';
import { ValueItem } from '@protocols/nestedMapping/components/values/ValueItem';

// Minimal mock for draggable wrapper if needed
jest.mock('@praxis-ui', () => ({
  DraggableSortableItem: ({ children }: { children: React.ReactNode }) => <div>{children}</div>
}));

describe('ValueItem Component', () => {
  const onDeleteMock = jest.fn();
  const onEditMock = jest.fn();
  const onFocusMock = jest.fn();
  const onBlurMock = jest.fn();
  const onValueChangeMock = jest.fn();

  beforeEach(() => {
    onDeleteMock.mockClear();
    onEditMock.mockClear();
    onFocusMock.mockClear();
    onBlurMock.mockClear();
    onValueChangeMock.mockClear();
  });

  test('renders correctly with default props', () => {
    render(
      <ValueItem
        id="val1"
        value="Test Value"
        type="string"
        isEditable={true}
      />
    );
    expect(screen.getByText('Test Value')).toBeInTheDocument();
  });

  test('renders action buttons and handles edit callback', () => {
    render(
      <ValueItem
        id="val1"
        value="Editable Value"
        type="string"
        isEditable={true}
        onEdit={onEditMock}
      />
    );
    // Simulate edit button click by finding the pencil icon wrapped in a button
    const editButton = screen.getByRole('button', { name: /edit value/i });
    fireEvent.click(editButton);
    expect(onEditMock).toHaveBeenCalled();
  });

  test('calls onDelete callback when delete button is clicked', () => {
    render(
      <ValueItem
        id="val1"
        value="Test Value"
        type="string"
        isEditable={true}
        onDelete={onDeleteMock}
      />
    );
    const deleteButton = screen.getByRole('button', { name: /delete value/i });
    fireEvent.click(deleteButton);
    expect(onDeleteMock).toHaveBeenCalled();
  });

  test('passes onFocus and onBlur events to ValueDisplay', () => {
    render(
      <ValueItem
        id="val1"
        value="Focus Test"
        type="string"
        isEditable={true}
        onFocus={onFocusMock}
        onBlur={onBlurMock}
        onValueChange={onValueChangeMock}
      />
    );
    fireEvent.click(screen.getByText('Focus Test'));
    expect(onFocusMock).toHaveBeenCalled();
    // Simulate blur through keyboard event on input in ValueDisplay
    const input = screen.getByRole('textbox');
    fireEvent.keyDown(input, { key: 'Escape', code: 'Escape' });
    expect(onBlurMock).toHaveBeenCalled();
  });
});
