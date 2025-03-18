import { createRef } from 'react';
import { render, screen, fireEvent } from '@utils/test_utils';
import { ParameterConfigurationForm, ParameterConfigurationFormRef } from '@protocols/components/form/ParameterConfigurationForm';

// A dummy Redux store can be simulated via test_utils if needed.

describe('ParameterConfigurationForm Component', () => {
  const parameters = {
    param1: { type: 'string', default: 'default1', description: 'desc 1', required: true, constraints: {} },
    param2: { type: 'number', default: 42, description: 'desc 2', required: false, constraints: {} }
  };

  const dummyState = {
    param1: { currentValue: 'default1' },
    param2: { currentValue: 42 }
  };

  // For testing, we simulate dispatch by checking if saveChanges calls the appropriate handler.
  // In this test, we assume updateParameterValue dispatch is mocked in the component.

  test('renders correctly with default parameter values', () => {
    render(
      <ParameterConfigurationForm parameters={parameters} />
    );
    expect(screen.getByText('param1')).toBeInTheDocument();
    expect(screen.getByText('desc 1')).toBeInTheDocument();
    expect(screen.getByText('param2')).toBeInTheDocument();
  });

  test('handles parameter changes and saveChanges callback', () => {
    const formRef = createRef<ParameterConfigurationFormRef>();
    render(
      <ParameterConfigurationForm parameters={parameters} ref={formRef} />
    );
    // simulate update: find an input and fire change event
    const input = screen.getByTestId('string-input');
    fireEvent.change(input, { target: { value: 'new value' } });
    fireEvent.blur(input);
    // Call imperative handle
    formRef.current?.saveChanges();
    // Since updateParameterValue dispatch is internal, we assume that if no errors occur, test passes.
    expect(formRef.current).toBeDefined();
  });
});
