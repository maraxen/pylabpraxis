import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { DelayedField } from '../ui/delayedField';
import '@testing-library/jest-dom/extend-expect'; // Add this import for jest-dom matchers

describe('DelayedField Component', () => {
  // Basic rendering tests
  describe('Rendering', () => {
    test('renders children correctly', () => {
      const onBlur = jest.fn();

      render(
        <DelayedField value="test value" onBlur={onBlur}>
          {(value, onChange, onBlur) => (
            <div data-testid="test-component">
              <span data-testid="value-display">{value}</span>
              <button
                data-testid="change-button"
                onClick={() => onChange('new value')}
              >
                Change
              </button>
              <button
                data-testid="blur-button"
                onClick={onBlur}
              >
                Blur
              </button>
            </div>
          )}
        </DelayedField>
      );

      // Check that the value is correctly passed to children
      expect(screen.getByTestId('test-component')).toBeInTheDocument();
      expect(screen.getByTestId('value-display')).toHaveTextContent('test value');
    });
  });

  // Change handling tests
  describe('Change handling', () => {
    test('updates internal state when onChange is called', () => {
      const onBlur = jest.fn();

      render(
        <DelayedField value="test value" onBlur={onBlur}>
          {(value, onChange, onBlur) => (
            <div data-testid="test-component">
              <span data-testid="value-display">{value}</span>
              <button
                data-testid="change-button"
                onClick={() => onChange('new value')}
              >
                Change
              </button>
              <button
                data-testid="blur-button"
                onClick={onBlur}
              >
                Blur
              </button>
            </div>
          )}
        </DelayedField>
      );

      // Click the change button
      fireEvent.click(screen.getByTestId('change-button'));

      // Check that the displayed value has been updated locally
      expect(screen.getByTestId('value-display')).toHaveTextContent('new value');

      // But onBlur should not have been called yet
      expect(onBlur).not.toHaveBeenCalled();
    });

    test('commits changes when onBlur is called', () => {
      const onBlur = jest.fn();

      render(
        <DelayedField value="test value" onBlur={onBlur}>
          {(value, onChange, onBlur) => (
            <div data-testid="test-component">
              <span data-testid="value-display">{value}</span>
              <button
                data-testid="change-button"
                onClick={() => onChange('new value')}
              >
                Change
              </button>
              <button
                data-testid="blur-button"
                onClick={onBlur}
              >
                Blur
              </button>
            </div>
          )}
        </DelayedField>
      );

      // Change the value
      fireEvent.click(screen.getByTestId('change-button'));

      // Trigger a blur
      fireEvent.click(screen.getByTestId('blur-button'));

      // The onBlur prop should have been called with the new value
      expect(onBlur).toHaveBeenCalledWith('new value');
    });
  });

  // Effect tests
  describe('Effect behavior', () => {
    test('updates local value when prop value changes', async () => {
      const onBlur = jest.fn();
      const { rerender } = render(
        <DelayedField value="test value" onBlur={onBlur}>
          {(value, _onChange, _onBlur) => (
            <div data-testid="test-component">
              <span data-testid="value-display">{value}</span>
            </div>
          )}
        </DelayedField>
      );

      // Verify initial value
      expect(screen.getByTestId('value-display')).toHaveTextContent('test value');

      // Rerender with a new value prop
      rerender(
        <DelayedField value="updated value" onBlur={onBlur}>
          {(value, _onChange, _onBlur) => (
            <div data-testid="test-component">
              <span data-testid="value-display">{value}</span>
            </div>
          )}
        </DelayedField>
      );

      // Local value should be updated to match the new prop
      await waitFor(() => {
        expect(screen.getByTestId('value-display')).toHaveTextContent('updated value');
      });
    });
  });

  // Working with different input types
  describe('Different input types', () => {
    test('works with number values', () => {
      const onBlur = jest.fn();

      render(
        <DelayedField value={42} onBlur={onBlur}>
          {(value, onChange, onBlur) => (
            <div data-testid="test-component">
              <span data-testid="value-display">{value}</span>
              <button
                data-testid="change-button"
                onClick={() => onChange(100)}
              >
                Change
              </button>
              <button
                data-testid="blur-button"
                onClick={onBlur}
              >
                Blur
              </button>
            </div>
          )}
        </DelayedField>
      );

      // Change the value
      fireEvent.click(screen.getByTestId('change-button'));

      // Check local update
      expect(screen.getByTestId('value-display')).toHaveTextContent('100');

      // Trigger a blur
      fireEvent.click(screen.getByTestId('blur-button'));

      // The onBlur prop should have been called with the new value
      expect(onBlur).toHaveBeenCalledWith(100);
    });

    test('works with boolean values', () => {
      const onBlur = jest.fn();

      render(
        <DelayedField value={false} onBlur={onBlur}>
          {(value, onChange, onBlur) => (
            <div data-testid="test-component">
              <span data-testid="value-display">{value ? 'true' : 'false'}</span>
              <button
                data-testid="change-button"
                onClick={() => onChange(true)}
              >
                Change
              </button>
              <button
                data-testid="blur-button"
                onClick={onBlur}
              >
                Blur
              </button>
            </div>
          )}
        </DelayedField>
      );

      // Initially false
      expect(screen.getByTestId('value-display')).toHaveTextContent('false');

      // Change the value
      fireEvent.click(screen.getByTestId('change-button'));

      // Check local update
      expect(screen.getByTestId('value-display')).toHaveTextContent('true');

      // Trigger a blur
      fireEvent.click(screen.getByTestId('blur-button'));

      // The onBlur prop should have been called with the new value
      expect(onBlur).toHaveBeenCalledWith(true);
    });

    test('works with object values', () => {
      const initialValue = { name: 'John', age: 30 };
      const newValue = { name: 'Jane', age: 25 };
      const onBlur = jest.fn();

      render(
        <DelayedField value={initialValue} onBlur={onBlur}>
          {(value, onChange, onBlur) => (
            <div data-testid="test-component">
              <span data-testid="value-name">{value.name}</span>
              <span data-testid="value-age">{value.age}</span>
              <button
                data-testid="change-button"
                onClick={() => onChange(newValue)}
              >
                Change
              </button>
              <button
                data-testid="blur-button"
                onClick={onBlur}
              >
                Blur
              </button>
            </div>
          )}
        </DelayedField>
      );

      // Check initial values
      expect(screen.getByTestId('value-name')).toHaveTextContent('John');
      expect(screen.getByTestId('value-age')).toHaveTextContent('30');

      // Change the value
      fireEvent.click(screen.getByTestId('change-button'));

      // Check local update
      expect(screen.getByTestId('value-name')).toHaveTextContent('Jane');
      expect(screen.getByTestId('value-age')).toHaveTextContent('25');

      // Trigger a blur
      fireEvent.click(screen.getByTestId('blur-button'));

      // The onBlur prop should have been called with the new value
      expect(onBlur).toHaveBeenCalledWith(newValue);
    });
  });
});