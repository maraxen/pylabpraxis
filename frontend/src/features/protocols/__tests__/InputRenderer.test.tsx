import { render, screen, fireEvent } from '@utils/test_utils';
import { InputRenderer } from '@protocols/components/common/InputRenderer';

describe('InputRenderer Component', () => {
  test('renders string input when no options provided', () => {
    const onChange = jest.fn();
    render(
      <InputRenderer
        name="stringTest"
        value="abc"
        config={{ type: 'string', constraints: {} }}
        onChange={onChange}
      />
    );
    const input = screen.getByTestId('string-input');
    expect(input).toBeInTheDocument();
    fireEvent.change(input, { target: { value: 'new string' } });
    // onChange should be called with name and new value.
    expect(onChange).toHaveBeenCalledWith('stringTest', 'new string');
  });

  test('renders number input and handles changes', () => {
    const onChange = jest.fn();
    render(
      <InputRenderer
        name="numberTest"
        value={10}
        config={{ type: 'number', constraints: { min_value: 0, max_value: 100 } }}
        onChange={onChange}
      />
    );
    const numberInput = screen.getByTestId('number-input');
    expect(numberInput).toBeInTheDocument();
    fireEvent.change(numberInput, { target: { value: '25' } });
    expect(onChange).toHaveBeenCalledWith('numberTest', 25);
  });

  test('renders boolean input and toggles value', () => {
    const onChange = jest.fn();
    render(
      <InputRenderer
        name="booleanTest"
        value={false}
        config={{ type: 'boolean', constraints: {} }}
        onChange={onChange}
      />
    );
    const checkbox = screen.getByTestId('boolean-checkbox');
    expect(checkbox).toBeInTheDocument();
    expect(checkbox).not.toBeChecked();
    fireEvent.click(checkbox);
    expect(onChange).toHaveBeenCalledWith('booleanTest', true);
  });

  test('renders array input when options are provided', () => {
    const onChange = jest.fn();
    render(
      <InputRenderer
        name="arrayTest"
        value={['one']}
        config={{ type: 'string', constraints: { array: ['one', 'two', 'three'] } }}
        onChange={onChange}
      />
    );
    const arrInput = screen.getByTestId('array-input');
    expect(arrInput).toBeInTheDocument();
    // Simulate change by updating the value string (the real control splits string by ",")
    const field = screen.getByTestId('array-input-field');
    fireEvent.change(field, { target: { value: 'one,two' } });
    expect(onChange).toHaveBeenCalledWith('arrayTest', ['one', 'two']);
  });

  test('renders dict input by delegating to HierarchicalMapping', () => {
    const onChange = jest.fn();
    render(
      <InputRenderer
        name="dictTest"
        value={{ key: 'value' }}
        config={{ type: 'dict', constraints: {} }}
        onChange={onChange}
      />
    );
    // Check that HierarchicalMapping is rendered as part of the dict input.
    expect(screen.getByTestId('hierarchical-mapping')).toBeInTheDocument();
  });
});
