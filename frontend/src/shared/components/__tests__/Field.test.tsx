import { render, screen } from '@utils/test_utils';
import { Field } from '../ui/field';

// Mock the ChakraField component and its subcomponents
jest.mock('@chakra-ui/react', () => {
  const originalModule = jest.requireActual('@chakra-ui/react');
  return {
    ...originalModule,
    Field: {
      Root: ({ children, ...props }: any) => (
        <div data-testid="field-root" {...props}>{children}</div>
      ),
      Label: ({ children }: any) => (
        <label data-testid="field-label">{children}</label>
      ),
      RequiredIndicator: ({ fallback }: any) => (
        <span data-testid="field-required-indicator" data-fallback={fallback}>*</span>
      ),
      HelperText: ({ children }: any) => (
        <span data-testid="field-helper-text">{children}</span>
      ),
      ErrorText: ({ children }: any) => (
        <span data-testid="field-error-text">{children}</span>
      )
    }
  };
});

describe('Field Component', () => {
  // Basic rendering tests
  describe('Rendering', () => {
    test('renders without errors', () => {
      render(<Field />);

      expect(screen.getByTestId('field-root')).toBeInTheDocument();
    });

    test('renders with label', () => {
      render(<Field label="Test Field" />);

      expect(screen.getByTestId('field-label')).toBeInTheDocument();
      expect(screen.getByText('Test Field')).toBeInTheDocument();
      expect(screen.getByTestId('field-required-indicator')).toBeInTheDocument();
    });

    test('renders with children', () => {
      render(
        <Field>
          <input data-testid="test-input" />
        </Field>
      );

      expect(screen.getByTestId('field-root')).toBeInTheDocument();
      expect(screen.getByTestId('test-input')).toBeInTheDocument();
    });
  });

  // Conditional rendering tests
  describe('Conditional Rendering', () => {
    test('renders helper text when provided', () => {
      render(<Field helperText="This is a helpful hint" />);

      expect(screen.getByTestId('field-helper-text')).toBeInTheDocument();
      expect(screen.getByText('This is a helpful hint')).toBeInTheDocument();
    });

    test('renders error text when provided', () => {
      render(<Field errorText="This field has an error" />);

      expect(screen.getByTestId('field-error-text')).toBeInTheDocument();
      expect(screen.getByText('This field has an error')).toBeInTheDocument();
    });

    test('does not render label when not provided', () => {
      render(<Field />);

      expect(screen.queryByTestId('field-label')).not.toBeInTheDocument();
    });

    test('does not render helper text when not provided', () => {
      render(<Field />);

      expect(screen.queryByTestId('field-helper-text')).not.toBeInTheDocument();
    });

    test('does not render error text when not provided', () => {
      render(<Field />);

      expect(screen.queryByTestId('field-error-text')).not.toBeInTheDocument();
    });
  });

  // Optional text tests
  describe('Optional Text', () => {
    test('passes optionalText to RequiredIndicator', () => {
      render(<Field label="Optional Field" optionalText="(optional)" />);

      expect(screen.getByTestId('field-required-indicator')).toHaveAttribute('data-fallback', '(optional)');
    });
  });

  // Props passing tests
  describe('Props Passing', () => {
    test('passes additional props to Field.Root', () => {
      render(<Field required disabled invalid />);

      const fieldRoot = screen.getByTestId('field-root');
      expect(fieldRoot).toHaveAttribute('required', 'true');
      expect(fieldRoot).toHaveAttribute('disabled', 'true');
      expect(fieldRoot).toHaveAttribute('invalid', 'true');
    });
  });

  // Complex cases tests
  describe('Complex Cases', () => {
    test('renders all elements when fully configured', () => {
      render(
        <Field
          label="Complete Field"
          helperText="Helper information"
          errorText="Error information"
          required
        >
          <input data-testid="test-input" />
        </Field>
      );

      expect(screen.getByTestId('field-label')).toBeInTheDocument();
      expect(screen.getByTestId('field-required-indicator')).toBeInTheDocument();
      expect(screen.getByTestId('test-input')).toBeInTheDocument();
      expect(screen.getByTestId('field-helper-text')).toBeInTheDocument();
      expect(screen.getByTestId('field-error-text')).toBeInTheDocument();

      expect(screen.getByText('Complete Field')).toBeInTheDocument();
      expect(screen.getByText('Helper information')).toBeInTheDocument();
      expect(screen.getByText('Error information')).toBeInTheDocument();
    });
  });
});