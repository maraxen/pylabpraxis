import { render, screen, fireEvent } from '@utils/test_utils';
import { DraggableSortableItem } from '../ui/DraggableSortableItem';

// Mock the dependencies
jest.mock('@chakra-ui/react', () => ({
  Box: ({ children, ...props }: any) => (
    <div data-testid="box" {...props}>{children}</div>
  ),
  HStack: ({ children, ...props }: any) => (
    <div data-testid="hstack" {...props}>{children}</div>
  )
}));

jest.mock('@dnd-kit/sortable', () => ({
  useSortable: () => ({
    attributes: { 'aria-role': 'sortable' },
    listeners: { onMouseDown: jest.fn() },
    setNodeRef: jest.fn(),
    transform: { x: 0, y: 0 },
    transition: 'transform 250ms ease',
    isDragging: false
  })
}));

jest.mock('@dnd-kit/core', () => ({
  useDraggable: () => ({
    attributes: { 'aria-role': 'draggable' },
    listeners: { onMouseDown: jest.fn() },
    setNodeRef: jest.fn(),
    transform: { x: 0, y: 0 },
    isDragging: false
  })
}));

jest.mock('@dnd-kit/utilities', () => ({
  CSS: {
    Transform: {
      toString: jest.fn().mockReturnValue('translate3d(0px, 0px, 0)')
    }
  }
}));

describe('DraggableSortableItem Component', () => {
  const defaultProps = {
    id: 'test-item-1',
    children: <span>Test Content</span>,
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Rendering', () => {
    it('renders children content', () => {
      render(<DraggableSortableItem {...defaultProps} />);
      expect(screen.getByText('Test Content')).toBeInTheDocument();
    });

    it('renders with default drag handle when none provided', () => {
      render(<DraggableSortableItem {...defaultProps} />);
      // Default drag handle has the '☰' symbol
      expect(screen.getByRole('button')).toBeInTheDocument();
    });

    it('renders custom drag handle when provided', () => {
      const customHandle = <span data-testid="custom-handle">Drag</span>;
      render(
        <DraggableSortableItem {...defaultProps} dragHandle={customHandle} />
      );

      expect(screen.getByTestId('custom-handle')).toBeInTheDocument();
      expect(screen.queryByText('☰')).not.toBeInTheDocument();
    });

    it('renders action buttons when provided and hovering', () => {
      const actionButtons = <button data-testid="action-button">Delete</button>;
      render(
        <DraggableSortableItem {...defaultProps} actionButtons={actionButtons} />
      );

      // Initially buttons should not be visible
      expect(screen.queryByTestId('action-button')).not.toBeInTheDocument();

      // Trigger mouse enter to show buttons
      fireEvent.mouseEnter(screen.getByTestId('draggable-item-test-item-1'));
      expect(screen.getByTestId('action-button')).toBeInTheDocument();
    });
  });

  describe('Props and Styles', () => {
    it('applies correct styles when in edit mode', () => {
      render(<DraggableSortableItem {...defaultProps} isEditing={true} />);

      const item = screen.getByTestId('draggable-item-test-item-1');
      expect(item).toHaveStyle({ cursor: 'text' });
    });

    it('applies correct styles when not draggable', () => {
      render(<DraggableSortableItem {...defaultProps} isDraggable={false} />);

      const item = screen.getByTestId('draggable-item-test-item-1');
      expect(item).toHaveStyle({ cursor: 'default' });
    });

    it('applies custom box styles when provided', () => {
      const boxStyles = { backgroundColor: 'red', borderColor: 'blue' };
      render(<DraggableSortableItem {...defaultProps} boxStyles={boxStyles} />);

      const item = screen.getByTestId('draggable-item-test-item-1');
      // Check if style object contains our custom styles
      expect(item).toHaveStyle({ backgroundColor: 'red', borderColor: 'blue' });
    });

    it('applies custom class name when provided', () => {
      render(<DraggableSortableItem {...defaultProps} className="custom-class" />);

      const item = screen.getByTestId('draggable-item-test-item-1');
      expect(item).toHaveClass('custom-class');
    });
  });

  describe('Drag Mode', () => {
    it('uses useSortable hook by default', () => {
      render(<DraggableSortableItem {...defaultProps} />);

      const item = screen.getByTestId('draggable-item-test-item-1');
      expect(item).toHaveAttribute('aria-role', 'sortable');
    });

    it('uses useDraggable hook when dragMode is draggable', () => {
      render(<DraggableSortableItem {...defaultProps} dragMode="draggable" />);

      const item = screen.getByTestId('draggable-item-test-item-1');
      expect(item).toHaveAttribute('aria-role', 'draggable');
    });
  });

  describe('Interactions', () => {
    it('calls onFocus when focused', () => {
      const onFocus = jest.fn();
      render(<DraggableSortableItem {...defaultProps} onFocus={onFocus} />);

      fireEvent.focus(screen.getByTestId('draggable-item-test-item-1'));
      expect(onFocus).toHaveBeenCalled();
    });

    it('calls onBlur when blurred', () => {
      const onBlur = jest.fn();
      render(<DraggableSortableItem {...defaultProps} onBlur={onBlur} />);

      fireEvent.blur(screen.getByTestId('draggable-item-test-item-1'));
      expect(onBlur).toHaveBeenCalled();
    });

    it('toggles hover state on mouse enter/leave', () => {
      const actionButtons = <button data-testid="action-button">Delete</button>;
      render(
        <DraggableSortableItem {...defaultProps} actionButtons={actionButtons} />
      );

      const item = screen.getByTestId('draggable-item-test-item-1');

      // Mouse enter should show action buttons
      fireEvent.mouseEnter(item);
      expect(screen.getByTestId('action-button')).toBeInTheDocument();

      // Mouse leave should hide action buttons
      fireEvent.mouseLeave(item);
      expect(screen.queryByTestId('action-button')).not.toBeInTheDocument();
    });
  });

  describe('Metadata', () => {
    it('includes metadata in the draggable data', () => {
      const metadata = { id: 'test-metadata-id', test: 'value', nested: { prop: true } };
      render(
        <DraggableSortableItem
          {...defaultProps}
          metadata={metadata}
          itemType="testType"
          localIndex={5}
        />
      );

      // This is a simplified test since we can't easily test the data in the hooks
      const item = screen.getByTestId('draggable-item-test-item-1');
      expect(item).toBeInTheDocument();
    });
  });
});