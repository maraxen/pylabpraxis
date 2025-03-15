import { render, screen } from '@utils/test_utils';
import { DroppableArea } from '../ui/DroppableArea';

// Updated Box mock to convert relevant props to inline styles
jest.mock('@chakra-ui/react', () => {
  const originalModule = jest.requireActual('@chakra-ui/react');
  return {
    ...originalModule,
    Box: ({ children, ...props }: any) => {
      const styleProps: React.CSSProperties = {};
      if (props.borderWidth !== undefined) {
        styleProps.borderWidth = typeof props.borderWidth === 'number' ? props.borderWidth + 'px' : props.borderWidth;
      }
      if (props.borderRadius !== undefined) {
        styleProps.borderRadius = props.borderRadius;
      }
      if (props.p !== undefined) {
        styleProps.padding = typeof props.p === 'number' ? props.p + 'px' : props.p;
      }
      if (props.bg !== undefined) {
        styleProps.background = props.bg;
      }
      if (props.borderStyle !== undefined) {
        styleProps.borderStyle = props.borderStyle;
      }
      if (props.borderColor !== undefined) {
        styleProps.borderColor = props.borderColor;
      }
      return (
        <div data-testid={props['data-testid'] || 'box'} style={styleProps} {...props}>
          {children}
        </div>
      );
    },
  };
});

describe('DroppableArea Component', () => {
  describe('Rendering', () => {
    it('renders with children', () => {
      render(
        <DroppableArea id="test-droppable" defaultFull={false}>
          <div data-testid="child-element">Child content</div>
        </DroppableArea>
      );

      expect(screen.getByTestId('box')).toBeInTheDocument();
      expect(screen.getByTestId('child-element')).toBeInTheDocument();
      expect(screen.getByText('Child content')).toBeInTheDocument();
    });

    it('renders with default styles', () => {
      render(<DroppableArea id="test-droppable" defaultFull={false} />);

      const box = screen.getByTestId('box');
      expect(box).toHaveStyle({
        'border-width': '1px',
        'border-radius': 'md',
        'padding': '2px',
        'background': 'transparent',
        'border-style': 'dashed',
      });
    });

    it('renders "Drop here" text when there are no children', () => {
      render(<DroppableArea id="test-droppable" defaultFull={false} />);

      expect(screen.getByText('Drop here')).toBeInTheDocument();
    });

    it('renders "Full" text when isFull is true and there are no children', () => {
      render(<DroppableArea id="test-droppable" defaultFull={true} />);

      expect(screen.getByText('Full')).toBeInTheDocument();
    });

    it('applies brand.100 background when isOver and canReceiveDrops', () => {
      render(<DroppableArea id="test-droppable" isOver defaultFull={false} />);
      const box = screen.getByTestId('box');
      expect(box).toHaveStyle({ background: 'brand.100' });
    });

    it('applies correct border color when isOver and canReceiveDrops', () => {
      render(<DroppableArea id="test-droppable" isOver defaultFull={false} />);
      const box = screen.getByTestId('box');
      expect(box).toHaveStyle({ 'border-color': 'brand.500' });
    });

    it('applies correct border color when isDragging and canReceiveDrops', () => {
      render(<DroppableArea id="test-droppable" isDragging defaultFull={false} />);
      const box = screen.getByTestId('box');
      expect(box).toHaveStyle({ 'border-color': 'brand.400' });
    });

    it('applies correct border color when isFull', () => {
      render(<DroppableArea id="test-droppable" defaultFull={true} />);
      const box = screen.getByTestId('box');
      expect(box).toHaveStyle({ 'border-color': 'red.200' });
    });

    it('applies custom data-droppable-id attribute', () => {
      render(<DroppableArea id="custom-id" defaultFull={false} />);
      const box = screen.getByTestId('box');
      expect(box).toHaveAttribute('data-droppable-id', 'custom-id');
    });

    it('applies custom data-full attribute', () => {
      render(<DroppableArea id="test-droppable" defaultFull={true} />);
      const box = screen.getByTestId('box');
      expect(box).toHaveAttribute('data-full', 'true');
    });
  });
});
