import { render, screen } from '@utils/test_utils';
import { Slider } from '../ui/slider';

// Mock Chakra UI Slider components
jest.mock('@chakra-ui/react', () => {
  const originalModule = jest.requireActual('@chakra-ui/react');
  return {
    ...originalModule,
    Slider: {
      Root: ({ children, ...props }: any) => (
        <div data-testid="slider-root" {...props}>{children}</div>
      ),
      Label: ({ children }: any) => (
        <div data-testid="slider-label">{children}</div>
      ),
      ValueText: () => (
        <div data-testid="slider-value-text">Value Text</div>
      ),
      Control: ({ children, ...props }: any) => (
        <div data-testid="slider-control" {...props}>{children}</div>
      ),
      Track: ({ children }: any) => (
        <div data-testid="slider-track">{children}</div>
      ),
      Range: () => <div data-testid="slider-range" />,
      Thumb: ({ index, children }: any) => (
        <div data-testid={`slider-thumb-${index}`}>{children}</div>
      ),
      HiddenInput: () => <div data-testid="slider-hidden-input" />,
      MarkerGroup: ({ children }: any) => (
        <div data-testid="slider-marker-group">{children}</div>
      ),
      Marker: ({ value, children }: any) => (
        <div data-testid={`slider-marker-${value}`}>{children}</div>
      ),
      MarkerIndicator: () => <div data-testid="slider-marker-indicator" />
    },
    For: ({ each, children }: any) => (
      <>{each?.map((_: any, i: any) => children(_, i))}</>
    ),
    HStack: ({ children, ...props }: any) => (
      <div data-testid="hstack" {...props}>{children}</div>
    ),
  };
});

describe('Slider Component', () => {
  describe('Basic Rendering', () => {
    it('should render basic slider without errors', () => {
      render(<Slider />);

      expect(screen.getByTestId('slider-root')).toBeInTheDocument();
      expect(screen.getByTestId('slider-control')).toBeInTheDocument();
      expect(screen.getByTestId('slider-track')).toBeInTheDocument();
      expect(screen.getByTestId('slider-range')).toBeInTheDocument();
    });

    it('should render label when provided', () => {
      render(<Slider label="Test Label" />);

      const label = screen.getByTestId('slider-label');
      expect(label).toBeInTheDocument();
      expect(label).toHaveTextContent('Test Label');
    });

    it('should render label and value when showValue is true', () => {
      render(<Slider label="Test Label" showValue />);

      expect(screen.getByTestId('slider-label')).toBeInTheDocument();
      expect(screen.getByTestId('slider-value-text')).toBeInTheDocument();
      expect(screen.getByTestId('hstack')).toBeInTheDocument();
    });
  });

  describe('Thumb Behavior', () => {
    it('should render single thumb by default', () => {
      render(<Slider value={[50]} />);

      expect(screen.getByTestId('slider-thumb-0')).toBeInTheDocument();
      expect(screen.getByTestId('slider-hidden-input')).toBeInTheDocument();
    });

    it('should render multiple thumbs for multiple values', () => {
      render(<Slider value={[25, 75]} />);

      expect(screen.getByTestId('slider-thumb-0')).toBeInTheDocument();
      expect(screen.getByTestId('slider-thumb-1')).toBeInTheDocument();
      expect(screen.getAllByTestId('slider-hidden-input').length).toBe(2);
    });
  });

  describe('Marks Rendering', () => {
    it('should render numeric marks correctly', () => {
      render(<Slider marks={[0, 25, 50, 75, 100]} />);

      expect(screen.getByTestId('slider-marker-group')).toBeInTheDocument();
      expect(screen.getByTestId('slider-marker-0')).toBeInTheDocument();
      expect(screen.getByTestId('slider-marker-25')).toBeInTheDocument();
      expect(screen.getByTestId('slider-marker-50')).toBeInTheDocument();
      expect(screen.getByTestId('slider-marker-75')).toBeInTheDocument();
      expect(screen.getByTestId('slider-marker-100')).toBeInTheDocument();
    });

    it('should render marks with labels correctly', () => {
      render(
        <Slider
          marks={[
            { value: 0, label: 'Min' },
            { value: 50, label: 'Mid' },
            { value: 100, label: 'Max' }
          ]}
        />
      );

      expect(screen.getByTestId('slider-marker-group')).toBeInTheDocument();
      expect(screen.getByText('Min')).toBeInTheDocument();
      expect(screen.getByText('Mid')).toBeInTheDocument();
      expect(screen.getByText('Max')).toBeInTheDocument();
    });

    it('should not render marker group when no marks provided', () => {
      render(<Slider />);
      expect(screen.queryByTestId('slider-marker-group')).not.toBeInTheDocument();
    });

    it('should set hasMarkLabel data attribute when marks have labels', () => {
      render(
        <Slider
          marks={[
            { value: 0, label: 'Min' },
            { value: 100, label: 'Max' }
          ]}
        />
      );

      const control = screen.getByTestId('slider-control');
      expect(control).toHaveAttribute('data-has-mark-label', 'true');
    });

    it('should not set hasMarkLabel when marks have no labels', () => {
      render(<Slider marks={[0, 50, 100]} />);

      const control = screen.getByTestId('slider-control');
      expect(control).not.toHaveAttribute('data-has-mark-label');
    });
  });

  describe('Props Handling', () => {
    it('should pass props to ChakraSlider.Root', () => {
      render(
        <Slider min={0} max={100} step={5} orientation="horizontal" />
      );

      const root = screen.getByTestId('slider-root');
      expect(root).toHaveAttribute('min', '0');
      expect(root).toHaveAttribute('max', '100');
      expect(root).toHaveAttribute('step', '5');
      expect(root).toHaveAttribute('orientation', 'horizontal');
    });

    it('should set thumbAlignment prop to center', () => {
      render(<Slider />);

      const root = screen.getByTestId('slider-root');
      expect(root).toHaveAttribute('thumbAlignment', 'center');
    });
  });
});