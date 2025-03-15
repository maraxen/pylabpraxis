import { render, screen } from '@utils/test_utils';
import { StatusBadge } from '../ui/StatusBadge';

// Mock the Badge component from Chakra UI
jest.mock('@chakra-ui/react', () => {
  const originalModule = jest.requireActual('@chakra-ui/react');
  return {
    ...originalModule,
    Badge: ({ children, colorScheme, title, variant, ...props }: any) => (
      <span
        data-testid="badge"
        data-colorscheme={colorScheme}
        data-variant={variant}
        title={title}
        {...props}
      >
        {children}
      </span>
    )
  };
});

describe('StatusBadge Component', () => {
  describe('Basic Rendering', () => {
    it('should render badge with correct status text', () => {
      render(<StatusBadge status="editable" />);

      const badge = screen.getByTestId('badge');
      expect(badge).toBeInTheDocument();
      expect(badge).toHaveTextContent('editable');
      expect(badge).toHaveAttribute('data-colorscheme', 'green');
      expect(badge).toHaveAttribute('data-variant', 'outline');
    });

    it('should render with custom label', () => {
      render(<StatusBadge status="readonly" label="Custom Label" />);

      const badge = screen.getByTestId('badge');
      expect(badge).toHaveTextContent('Custom Label');
      expect(badge).toHaveAttribute('data-colorscheme', 'gray');
    });

    it('should apply correct test ID', () => {
      render(<StatusBadge status="required" data-testid="custom-test-id" />);

      const badge = screen.getByTestId('badge');
      expect(badge).toHaveAttribute('data-testid', 'status-badge-required');
    });
  });

  describe('Status Configurations', () => {
    const statusConfigs = [
      { status: 'editable', expectedColor: 'green', expectedLabel: 'editable' },
      { status: 'readonly', expectedColor: 'gray', expectedLabel: 'read-only' },
      { status: 'parameter', expectedColor: 'blue', expectedLabel: 'parameter' },
      { status: 'required', expectedColor: 'red', expectedLabel: 'required' },
      { status: 'optional', expectedColor: 'gray', expectedLabel: 'optional' },
      { status: 'type', expectedColor: 'purple', expectedLabel: 'type' }
    ];

    it.each(statusConfigs)(
      'should apply correct styling for $status status',
      ({ status, expectedColor, expectedLabel }) => {
        render(<StatusBadge status={status as any} />);

        const badge = screen.getByTestId('badge');
        expect(badge).toHaveTextContent(expectedLabel);
        expect(badge).toHaveAttribute('data-colorscheme', expectedColor);
      }
    );
  });

  describe('Tooltip Configuration', () => {
    it('should set default tooltip based on status', () => {
      render(<StatusBadge status="required" />);

      const badge = screen.getByTestId('badge');
      expect(badge).toHaveAttribute('title', 'This field is required');
    });

    it('should use custom tooltip when provided', () => {
      render(<StatusBadge status="editable" tooltip="Custom tooltip text" />);

      const badge = screen.getByTestId('badge');
      expect(badge).toHaveAttribute('title', 'Custom tooltip text');
    });
  });

  describe('Variant Configuration', () => {
    it('should use outline variant by default', () => {
      render(<StatusBadge status="parameter" />);

      const badge = screen.getByTestId('badge');
      expect(badge).toHaveAttribute('data-variant', 'outline');
    });

    it('should apply custom variant when provided', () => {
      render(<StatusBadge status="parameter" variant="solid" />);

      const badge = screen.getByTestId('badge');
      expect(badge).toHaveAttribute('data-variant', 'solid');
    });
  });

  describe('Additional Props', () => {
    it('should pass additional props to Badge component', () => {
      render(
        <StatusBadge
          status="editable"
          fontSize="xs"
          marginLeft="2"
        />
      );

      const badge = screen.getByTestId('badge');
      expect(badge).toHaveAttribute('fontSize', 'xs');
      expect(badge).toHaveAttribute('marginLeft', '2');
    });
  });
});