import { render, screen, fireEvent } from '@utils/test_utils';
import { ActionButton } from '../ui/ActionButton';

// Mock the icon components
jest.mock('react-icons/lu', () => ({
  LuX: () => <span data-testid="icon-x">X</span>,
  LuPencil: () => <span data-testid="icon-pencil">Pencil</span>,
  LuPlus: () => <span data-testid="icon-plus">Plus</span>,
  LuTrash: () => <span data-testid="icon-trash">Trash</span>,
  LuCopy: () => <span data-testid="icon-copy">Copy</span>,
  LuInfo: () => <span data-testid="icon-info">Info</span>,
}));

// Mock the IconButton component
jest.mock('@chakra-ui/react', () => {
  const originalModule = jest.requireActual('@chakra-ui/react');
  return {
    ...originalModule,
    IconButton: ({ children, 'aria-label': ariaLabel, colorScheme, size, variant, onClick, ...props }: any) => (
      <button
        data-testid="icon-button"
        data-aria-label={ariaLabel}
        data-colorscheme={colorScheme}
        data-size={size}
        data-variant={variant}
        onClick={onClick}
        {...props}
      >
        {children}
      </button>
    )
  };
});

describe('ActionButton Component', () => {
  // Basic rendering tests
  describe('Rendering', () => {
    test('renders edit button correctly', () => {
      render(<ActionButton action="edit" />);

      expect(screen.getByTestId('icon-button')).toBeInTheDocument();
      expect(screen.getByTestId('icon-pencil')).toBeInTheDocument();
      expect(screen.getByTestId('icon-button')).toHaveAttribute('data-aria-label', 'Edit item');
      expect(screen.getByTestId('icon-button')).toHaveAttribute('data-colorscheme', 'blue');
    });

    test('renders delete button correctly', () => {
      render(<ActionButton action="delete" />);

      expect(screen.getByTestId('icon-button')).toBeInTheDocument();
      expect(screen.getByTestId('icon-x')).toBeInTheDocument();
      expect(screen.getByTestId('icon-button')).toHaveAttribute('data-aria-label', 'Delete item');
      expect(screen.getByTestId('icon-button')).toHaveAttribute('data-colorscheme', 'red');
    });

    test('renders add button correctly', () => {
      render(<ActionButton action="add" />);

      expect(screen.getByTestId('icon-button')).toBeInTheDocument();
      expect(screen.getByTestId('icon-plus')).toBeInTheDocument();
      expect(screen.getByTestId('icon-button')).toHaveAttribute('data-aria-label', 'Add item');
      expect(screen.getByTestId('icon-button')).toHaveAttribute('data-colorscheme', 'green');
    });

    test('renders remove button correctly', () => {
      render(<ActionButton action="remove" />);

      expect(screen.getByTestId('icon-button')).toBeInTheDocument();
      expect(screen.getByTestId('icon-trash')).toBeInTheDocument();
      expect(screen.getByTestId('icon-button')).toHaveAttribute('data-aria-label', 'Remove item');
      expect(screen.getByTestId('icon-button')).toHaveAttribute('data-colorscheme', 'red');
    });

    test('renders copy button correctly', () => {
      render(<ActionButton action="copy" />);

      expect(screen.getByTestId('icon-button')).toBeInTheDocument();
      expect(screen.getByTestId('icon-copy')).toBeInTheDocument();
      expect(screen.getByTestId('icon-button')).toHaveAttribute('data-aria-label', 'Copy item');
      expect(screen.getByTestId('icon-button')).toHaveAttribute('data-colorscheme', 'blue');
    });

    test('renders info button correctly', () => {
      render(<ActionButton action="info" />);

      expect(screen.getByTestId('icon-button')).toBeInTheDocument();
      expect(screen.getByTestId('icon-info')).toBeInTheDocument();
      expect(screen.getByTestId('icon-button')).toHaveAttribute('data-aria-label', 'Show information');
      expect(screen.getByTestId('icon-button')).toHaveAttribute('data-colorscheme', 'gray');
    });
  });

  // Custom props tests
  describe('Custom Properties', () => {
    test('applies custom label', () => {
      render(<ActionButton action="edit" label="Custom edit label" />);

      expect(screen.getByTestId('icon-button')).toHaveAttribute('data-aria-label', 'Custom edit label');
    });

    test('applies custom size', () => {
      render(<ActionButton action="edit" size="lg" />);

      expect(screen.getByTestId('icon-button')).toHaveAttribute('data-size', 'lg');
    });

    test('applies custom variant', () => {
      render(<ActionButton action="edit" variant="solid" />);

      expect(screen.getByTestId('icon-button')).toHaveAttribute('data-variant', 'solid');
    });

    test('applies default size and variant when not specified', () => {
      render(<ActionButton action="edit" />);

      expect(screen.getByTestId('icon-button')).toHaveAttribute('data-size', 'sm');
      expect(screen.getByTestId('icon-button')).toHaveAttribute('data-variant', 'ghost');
    });

    test('applies custom test id', () => {
      render(<ActionButton action="edit" testId="custom-test-id" />);

      expect(screen.getByTestId('icon-button')).toHaveAttribute('data-testid', 'custom-test-id');
    });
  });

  // Event handling tests
  describe('Event Handling', () => {
    test('handles click events', () => {
      const handleClick = jest.fn();

      render(<ActionButton action="edit" onClick={handleClick} />);

      fireEvent.click(screen.getByTestId('icon-button'));
      expect(handleClick).toHaveBeenCalledTimes(1);
    });
  });

  // Additional props tests
  describe('Additional Props', () => {
    test('passes additional props to IconButton', () => {
      render(<ActionButton action="edit" disabled={true} title="Edit tooltip" />);

      expect(screen.getByTestId('icon-button')).toHaveAttribute('isDisabled', 'true');
      expect(screen.getByTestId('icon-button')).toHaveAttribute('title', 'Edit tooltip');
    });
  });
});