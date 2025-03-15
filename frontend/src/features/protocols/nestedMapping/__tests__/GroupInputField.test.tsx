import { render, screen, fireEvent } from '@utils/test_utils';
import { GroupInputField } from '@protocols/nestedMapping/components/groups/GroupInputField';

describe('GroupInputField Component', () => {
  const onSave = jest.fn();
  const onCancel = jest.fn();

  beforeEach(() => {
    onSave.mockClear();
    onCancel.mockClear();
  });

  test('renders correctly with default props', () => {
    render(
      <GroupInputField
        initialValue="Initial Group"
        onSave={onSave}
        onCancel={onCancel}
      />
    );
    // EditableLabel should be rendered with the initial value
    expect(screen.getByDisplayValue('Initial Group')).toBeInTheDocument();
  });

  test('calls onSave callback when saving', () => {
    render(
      <GroupInputField
        initialValue="Initial Group"
        onSave={onSave}
        onCancel={onCancel}
      />
    );
    const input = screen.getByDisplayValue('Initial Group');
    // Simulate change and then blur (or enter key) to save
    fireEvent.change(input, { target: { value: 'New Group' } });
    // Simulate an action that triggers save; here we directly call onSave for testing
    fireEvent.keyDown(input, { key: 'Enter', code: 'Enter' });
    expect(onSave).toHaveBeenCalledWith('New Group');
  });

  test('calls onCancel callback when cancel is triggered', () => {
    render(
      <GroupInputField
        initialValue="Initial Group"
        onSave={onSave}
        onCancel={onCancel}
      />
    );
    // Simulate cancel event; for example, by clicking a cancel button if rendered.
    // If the EditableLabel calls onCancel on pressing Escape:
    const input = screen.getByDisplayValue('Initial Group');
    fireEvent.keyDown(input, { key: 'Escape', code: 'Escape' });
    expect(onCancel).toHaveBeenCalled();
  });
});
