import { render, screen, fireEvent } from '@utils/test_utils';
import { SubvariableInput } from '@protocols/nestedMapping/components/values/SubvariableInput';

describe('SubvariableInput Component', () => {
  const onChangeMock = jest.fn();

  beforeEach(() => {
    onChangeMock.mockClear();
  });

  test('renders correctly with default props', () => {
    render(<SubvariableInput name="test" value="initial" config={{ type: 'string' }} onChange={onChangeMock} />);
    expect(screen.getByDisplayValue('initial')).toBeInTheDocument();
  });

  test('handles input change and calls onChange on blur', () => {
    render(<SubvariableInput name="test" value="initial" config={{ type: 'string' }} onChange={onChangeMock} />);
    const input = screen.getByRole('textbox');
    fireEvent.focus(input);
    fireEvent.change(input, { target: { value: 'changed' } });
    fireEvent.blur(input);
    expect(onChangeMock).toHaveBeenCalledWith('changed');
  });
});
