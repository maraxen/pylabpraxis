import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ChakraProvider } from '@chakra-ui/react';
import { EditableLabel } from '../ui/EditableLabel';
import { system } from '../../../styles/theme';

// Mock the DelayedField component
jest.mock('../../../../shared/components/ui/delayedField', () => ({
  DelayedField: ({ children, value, onBlur }: any) => {
    // Call the children render prop with helpers
    const renderedChildren = children(
      value,
      (newValue: any) => { /* This would update the internal value */ },
      () => onBlur(value)
    );
    return (
      <div data-testid="delayed-field">
        {renderedChildren}
      </div>
    );
  }
}));

// Mock StringInput
jest.mock('../../../../shared/components/ui/StringInput', () => ({
  StringInput: React.forwardRef(
    ({ name, value, onChange, onBlur, onKeyDown }: any, ref: any) => (
      <input
        data-testid="string-input"
        name={name}
        value={value}
        ref={ref}
        onChange={(e) => onChange(name, e.target.value)}
        onBlur={onBlur}
        onKeyDown={onKeyDown}
      />
    )
  )
}));

// Helper to render with providers
const renderWithChakra = (ui: React.ReactElement) => {
  return render(
    <ChakraProvider theme={system}>{ui}</ChakraProvider>
  );
};

describe('EditableLabel Component', () => {
  const defaultProps = {
    value: 'Test Value',
    isEditable: true,
    isEditing: false,
    onEdit: jest.fn(),
    onSave: jest.fn(),
    onCancel: jest.fn()
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  // Basic rendering tests
  describe('Rendering', () => {
    test('renders text in display mode', () => {
      renderWithChakra(
        <EditableLabel {...defaultProps} />
      );

      expect(screen.getByTestId('editable-label-text')).toBeInTheDocument();
      expect(screen.getByText('Test Value')).toBeInTheDocument();
    });

    test('renders input in edit mode', () => {
      renderWithChakra(
        <EditableLabel {...defaultProps} isEditing={true} />
      );

      expect(screen.getByTestId('delayed-field')).toBeInTheDocument();
      expect(screen.getByTestId('string-input')).toBeInTheDocument();
    });

    test('uses placeholder when value is empty', () => {
      renderWithChakra(
        <EditableLabel {...defaultProps} value="" placeholder="Enter value" />
      );

      expect(screen.getByText('Enter value')).toBeInTheDocument();
    });
  });

  // Interaction tests
  describe('Interactions', () => {
    test('calls onEdit when clicked in editable mode', () => {
      renderWithChakra(
        <EditableLabel {...defaultProps} />
      );

      fireEvent.click(screen.getByTestId('editable-label-text'));
      expect(defaultProps.onEdit).toHaveBeenCalled();
    });

    test('does not call onEdit when clicked in non-editable mode', () => {
      renderWithChakra(
        <EditableLabel {...defaultProps} isEditable={false} />
      );

      fireEvent.click(screen.getByTestId('editable-label-text'));
      expect(defaultProps.onEdit).not.toHaveBeenCalled();
    });

    test('calls onBlur when input is blurred', async () => {
      renderWithChakra(
        <EditableLabel {...defaultProps} isEditing={true} />
      );

      const input = screen.getByTestId('string-input');
      fireEvent.blur(input);

      // DelayedField's onBlur should eventually call our onCancel since value hasn't changed
      await waitFor(() => {
        expect(defaultProps.onCancel).toHaveBeenCalled();
      });
    });

    test('handles empty value edge case correctly', async () => {
      renderWithChakra(
        <EditableLabel {...defaultProps} value="" isEditing={true} />
      );

      const input = screen.getByTestId('string-input');
      fireEvent.blur(input);

      // Should call onCancel for empty string
      await waitFor(() => {
        expect(defaultProps.onCancel).toHaveBeenCalled();
      });
    });
  });

  // Appearance tests
  describe('Appearance', () => {
    test('applies correct cursor when editable', () => {
      const { container } = renderWithChakra(
        <EditableLabel {...defaultProps} />
      );

      const textElement = screen.getByTestId('editable-label-text');
      const styles = window.getComputedStyle(textElement);
      expect(textElement).toHaveStyle('cursor: pointer');
    });

    test('applies correct cursor when not editable', () => {
      const { container } = renderWithChakra(
        <EditableLabel {...defaultProps} isEditable={false} />
      );

      const textElement = screen.getByTestId('editable-label-text');
      expect(textElement).toHaveStyle('cursor: default');
    });
  });
});