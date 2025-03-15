import { render, screen, fireEvent } from '@utils/test_utils';
import { BooleanInput } from '../ui/BooleanInput';

// Mock the Switch component from Chakra UI
jest.mock('@chakra-ui/react', () => ({
  Switch: {
    Root: ({ children, checked, onCheckedChange, onFocus, onBlur }: any) => (
      <div
        data-testid="switch-root"
        data-checked={checked}
        onClick={() => onCheckedChange({ checked: !checked })}
        onFocus={onFocus}
        onBlur={onBlur}
      >
        {children}
      </div>
    ),
    HiddenInput: () => <input data-testid="switch-hidden-input" />,
    Control: ({ children }: any) => <div data-testid="switch-control">{children}</div>,
    Thumb: () => <div data-testid="switch-thumb" />,
    Label: ({ children }: any) => <div data-testid="switch-label">{children}</div>,
  }
}));

describe('BooleanInput Component', () => {
  const defaultProps = {
    name: 'testBoolean',
    value: false,
    onChange: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Rendering', () => {
    it('renders with the correct checked state when false', () => {
      render(<BooleanInput {...defaultProps} />);

      const switchRoot = screen.getByTestId('switch-root');
      expect(switchRoot).toHaveAttribute('data-checked', 'false');
      expect(screen.getByTestId('switch-label')).toHaveTextContent('testBoolean');
    });

    it('renders with the correct checked state when true', () => {
      render(<BooleanInput {...defaultProps} value={true} />);

      const switchRoot = screen.getByTestId('switch-root');
      expect(switchRoot).toHaveAttribute('data-checked', 'true');
    });

    it('renders all required Switch components', () => {
      render(<BooleanInput {...defaultProps} />);

      expect(screen.getByTestId('switch-root')).toBeInTheDocument();
      expect(screen.getByTestId('switch-hidden-input')).toBeInTheDocument();
      expect(screen.getByTestId('switch-control')).toBeInTheDocument();
      expect(screen.getByTestId('switch-thumb')).toBeInTheDocument();
      expect(screen.getByTestId('switch-label')).toBeInTheDocument();
    });
  });

  describe('Interactions', () => {
    it('calls onChange with true when clicked while false', () => {
      render(<BooleanInput {...defaultProps} />);

      fireEvent.click(screen.getByTestId('switch-root'));

      expect(defaultProps.onChange).toHaveBeenCalledWith('testBoolean', true);
    });

    it('calls onChange with false when clicked while true', () => {
      render(<BooleanInput {...defaultProps} value={true} />);

      fireEvent.click(screen.getByTestId('switch-root'));

      expect(defaultProps.onChange).toHaveBeenCalledWith('testBoolean', false);
    });

    it('calls onFocus when focused', () => {
      const onFocus = jest.fn();
      render(<BooleanInput {...defaultProps} onFocus={onFocus} />);

      fireEvent.focus(screen.getByTestId('switch-root'));

      expect(onFocus).toHaveBeenCalled();
    });

    it('calls onBlur when blurred', () => {
      const onBlur = jest.fn();
      render(<BooleanInput {...defaultProps} onBlur={onBlur} />);

      fireEvent.blur(screen.getByTestId('switch-root'));

      expect(onBlur).toHaveBeenCalled();
    });
  });

  describe('Edge cases', () => {
    it('handles undefined value as falsy', () => {
      render(<BooleanInput {...defaultProps} value={undefined} />);

      const switchRoot = screen.getByTestId('switch-root');
      expect(switchRoot).toHaveAttribute('data-checked', 'false');
    });

    it('handles null value as falsy', () => {
      render(<BooleanInput {...defaultProps} value={null} />);

      const switchRoot = screen.getByTestId('switch-root');
      expect(switchRoot).toHaveAttribute('data-checked', 'false');
    });

    it('handles string "true" value as truthy', () => {
      render(<BooleanInput {...defaultProps} value="true" />);

      const switchRoot = screen.getByTestId('switch-root');
      expect(switchRoot).toHaveAttribute('data-checked', 'true');
    });

    it('handles number 1 value as truthy', () => {
      render(<BooleanInput {...defaultProps} value={1} />);

      const switchRoot = screen.getByTestId('switch-root');
      expect(switchRoot).toHaveAttribute('data-checked', 'true');
    });
  });
});