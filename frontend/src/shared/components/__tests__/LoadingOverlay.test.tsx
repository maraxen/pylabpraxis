import { render, screen } from '@utils/test_utils';
import { LoadingOverlay } from '../ui/LoadingOverlay';

// Mock Chakra UI components used in LoadingOverlay
jest.mock('@chakra-ui/react', () => {
  const originalModule = jest.requireActual('@chakra-ui/react');
  return {
    ...originalModule,
    Box: ({ children, ...props }: any) => (
      <div data-testid="overlay-container" {...props}>{children}</div>
    ),
    VStack: ({ children, ...props }: any) => (
      <div data-testid="overlay-content-stack" {...props}>{children}</div>
    ),
    Spinner: (props: any) => (
      <div data-testid="spinner" data-size={props.size} data-color={props.color}>Loading spinner</div>
    ),
    Text: ({ children, ...props }: any) => (
      <span data-testid="loading-text" {...props}>{children}</span>
    )
  };
});

describe('LoadingOverlay Component', () => {
  // Basic rendering tests
  describe('Rendering', () => {
    test('renders with default props', () => {
      render(<LoadingOverlay />);

      expect(screen.getByTestId('overlay-container')).toBeInTheDocument();
      expect(screen.getByTestId('spinner')).toBeInTheDocument();
      expect(screen.getByTestId('loading-text')).toHaveTextContent('Loading...');
    });

    test('renders with custom message', () => {
      render(<LoadingOverlay message="Please wait..." />);

      expect(screen.getByTestId('loading-text')).toHaveTextContent('Please wait...');
    });
  });

  // Styling tests
  describe('Styling', () => {
    test('has correct overlay styling', () => {
      render(<LoadingOverlay />);

      const overlay = screen.getByTestId('overlay-container');
      expect(overlay).toHaveStyle('position: fixed');
      expect(overlay).toHaveStyle('top: 0');
      expect(overlay).toHaveStyle('left: 0');
      expect(overlay).toHaveStyle('right: 0');
      expect(overlay).toHaveStyle('bottom: 0');
      expect(overlay).toHaveStyle('z-index: 9999');
      expect(overlay).toHaveStyle('display: flex');
      expect(overlay).toHaveStyle('align-items: center');
      expect(overlay).toHaveStyle('justify-content: center');
    });

    test('uses correct spinner styling', () => {
      render(<LoadingOverlay />);

      const spinner = screen.getByTestId('spinner');
      expect(spinner).toHaveAttribute('data-size', 'xl');
      expect(spinner).toHaveAttribute('data-color', 'brand.500');
    });

    test('uses correct text styling', () => {
      render(<LoadingOverlay />);

      const text = screen.getByTestId('loading-text');
      expect(text).toHaveStyle('color: gray.700');
      expect(text).toHaveStyle('font-size: lg');
      expect(text).toHaveStyle('font-weight: medium');
    });
  });

  // Accessibility tests
  describe('Accessibility', () => {
    test('uses semantic markup that conveys loading state', () => {
      render(<LoadingOverlay />);

      // The loading text is visible to screen readers
      expect(screen.getByText('Loading...')).toBeInTheDocument();

      // The spinner should be perceivable visually
      expect(screen.getByTestId('spinner')).toBeInTheDocument();
    });
  });
});