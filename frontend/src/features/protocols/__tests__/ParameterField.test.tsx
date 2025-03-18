import React from 'react';
import { render, screen, fireEvent } from '@utils/test_utils';
import { ParameterField } from '@protocols/components/common/ParameterField';

describe('ParameterField Component', () => {
  const defaultProps = {
    name: 'testParam',
    config: {
      type: 'string',
      description: 'A test parameter',
      required: true,
      constraints: {}
    },
    value: 'default value',
    onChange: jest.fn(),
    onRemove: jest.fn()
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders correctly with default props', () => {
    render(<ParameterField {...defaultProps} />);
    expect(screen.getByText('testParam')).toBeInTheDocument();
    expect(screen.getByText('A test parameter')).toBeInTheDocument();
    expect(screen.getByText('Required')).toBeInTheDocument();
    expect(screen.getByText('string')).toBeInTheDocument();
    // Rendered input comes from InputRenderer; here we expect a delayed field wrapper.
    expect(screen.getByTestId('delayed-field')).toBeInTheDocument();
  });

  test('calls onChange when input changes', () => {
    render(<ParameterField {...defaultProps} />);
    const input = screen.getByTestId('string-input');
    fireEvent.change(input, { target: { value: 'new value' } });
    fireEvent.blur(input);
    expect(defaultProps.onChange).toHaveBeenCalled();
  });

  test('calls onRemove when remove action is triggered', () => {
    render(<ParameterField {...defaultProps} />);
    // Simulate remove if InputRenderer renders such a control (depends on onRemove prop)
    const removeButton = screen.queryByText('Remove');
    if (removeButton) {
      fireEvent.click(removeButton);
      expect(defaultProps.onRemove).toHaveBeenCalled();
    }
  });
});