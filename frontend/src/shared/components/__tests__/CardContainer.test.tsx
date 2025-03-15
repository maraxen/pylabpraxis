import { render, screen } from '@utils/test_utils';
import { CardContainer } from '../ui/CardContainer';

// Mock the Box component from Chakra UI
jest.mock('@chakra-ui/react', () => {
  const originalModule = jest.requireActual('@chakra-ui/react');
  return {
    ...originalModule,
    Box: ({ children, ...props }: any) => (
      <div data-testid={props['data-testid'] || 'box'} {...props}>{children}</div>
    ),
  };
});

describe('CardContainer Component', () => {
  // Basic rendering tests
  describe('Rendering', () => {
    test('renders with children', () => {
      render(
        <CardContainer>
          <div data-testid="child-element">Child content</div>
        </CardContainer>
      );

      expect(screen.getByTestId('card-container')).toBeInTheDocument();
      expect(screen.getByTestId('child-element')).toBeInTheDocument();
      expect(screen.getByText('Child content')).toBeInTheDocument();
    });

    test('renders with custom test ID', () => {
      render(
        <CardContainer testId="custom-container">
          Test content
        </CardContainer>
      );

      expect(screen.getByTestId('custom-container')).toBeInTheDocument();
    });
  });

  // State styling tests
  describe('State-based styling', () => {
    test('applies default styling when no state props provided', () => {
      render(
        <CardContainer>Default state</CardContainer>
      );

      const cardContainer = screen.getByTestId('card-container');
      expect(cardContainer).toHaveStyle({
        'border-width': '1px',
        'border-radius': 'md',
        'padding': '3',
        'background': 'white',
        'position': 'relative',
        'border-color': 'gray.200',
        'box-shadow': 'none',
        'opacity': '1',
      });
    });

    test('applies highlighted styles', () => {
      render(
        <CardContainer isHighlighted>Highlighted card</CardContainer>
      );

      const cardContainer = screen.getByTestId('card-container');
      // Check for highlighted state styling
      expect(cardContainer).toHaveStyle({
        'box-shadow': 'md',
        'border-color': 'blue.300',
      });
    });

    test('applies dragging styles', () => {
      render(
        <CardContainer isDragging>Dragging card</CardContainer>
      );

      const cardContainer = screen.getByTestId('card-container');
      // Check for dragging state styling
      expect(cardContainer).toHaveStyle({
        'box-shadow': 'lg',
        'border-color': 'blue.400',
        'opacity': '0.7',
      });
    });

    test('applies active styles', () => {
      render(
        <CardContainer isActive>Active card</CardContainer>
      );

      const cardContainer = screen.getByTestId('card-container');
      // Check for active state styling
      expect(cardContainer).toHaveStyle({
        'box-shadow': 'sm',
        'border-color': 'gray.300',
      });
    });

    test('prioritizes state styling correctly with multiple states', () => {
      render(
        <CardContainer isHighlighted isDragging isActive>
          Multiple states card
        </CardContainer>
      );

      const cardContainer = screen.getByTestId('card-container');
      // Dragging should take precedence over highlighted and active
      expect(cardContainer).toHaveStyle({
        'box-shadow': 'lg',
        'border-color': 'blue.400',
        'opacity': '0.7',
      });
    });
  });

  // Additional props tests
  describe('Additional Props', () => {
    test('passes additional props to Box component', () => {
      render(
        <CardContainer
          width="300px"
          height="200px"
          margin="10px"
        >
          Card with custom props
        </CardContainer>
      );

      const cardContainer = screen.getByTestId('card-container');
      expect(cardContainer).toHaveStyle({
        'width': '300px',
        'height': '200px',
        'margin': '10px',
      });
    });
  });
});