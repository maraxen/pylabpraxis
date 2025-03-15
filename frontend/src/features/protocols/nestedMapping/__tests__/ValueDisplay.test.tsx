import { render, screen, fireEvent } from '@utils/test_utils';
import { ValueDisplay } from '@protocols/nestedMapping/components/values/ValueDisplay';

describe('ValueDisplay Component', () => {
  test('renders string value correctly with type badge', () => {
    render(<ValueDisplay value="Test String" type="string" />);
    expect(screen.getByText('Test String')).toBeInTheDocument();
    expect(screen.getByText('string')).toBeInTheDocument();
  });

  test('renders boolean value correctly', () => {
    render(<ValueDisplay value={true} type="boolean" />);
    expect(screen.getByText('True')).toBeInTheDocument();
    expect(screen.getByText('boolean')).toBeInTheDocument();
  });

  test('renders (empty) placeholder for null/undefined values', () => {
    render(<ValueDisplay value={null} type="string" />);
    expect(screen.getByText(/\(empty\)/i)).toBeInTheDocument();
  });

  test('enters edit mode when clicked (if editable)', () => {
    const onFocus = jest.fn();
    render(<ValueDisplay value="Click Me" type="string" isEditable onFocus={onFocus} />);
    fireEvent.click(screen.getByText('Click Me'));
    expect(onFocus).toHaveBeenCalled();
  });

  test('shows input and handles save/cancel in edit mode', () => {
    const onValueChange = jest.fn();
    const onBlur = jest.fn();
    render(
      <ValueDisplay
        value="Edit Me"
        type="string"
        isEditable
        isEditing
        onValueChange={onValueChange}
        onBlur={onBlur}
      />
    );
    // Check input exists with initial value
    const input = screen.getByRole('textbox');
    expect(input).toHaveValue('Edit Me');
    // Simulate change and Enter key
    fireEvent.change(input, { target: { value: 'New Value' } });
    fireEvent.keyDown(input, { key: 'Enter', code: 'Enter' });
    expect(onValueChange).toHaveBeenCalledWith('New Value');
    // For Escape, we reset back without saving
    fireEvent.change(input, { target: { value: 'Another Value' } });
    fireEvent.keyDown(input, { key: 'Escape', code: 'Escape' });
    expect(onBlur).toHaveBeenCalled();
  });
});
