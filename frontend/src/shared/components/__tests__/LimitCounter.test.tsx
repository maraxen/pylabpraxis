import { render, screen } from '@utils/test_utils';
import { LimitCounter } from '../ui/LimitCounter';

describe('LimitCounter Component', () => {
  describe('Rendering with default props', () => {
    test('does not render when max is Infinity and showAlways is false', () => {
      const { container } = render(<LimitCounter current={5} max={Infinity} />);
      expect(container.firstChild).toBeNull();
    });

    test('renders badge when max is Infinity and showAlways is true', () => {
      render(<LimitCounter current={3} max={Infinity} showAlways />);
      expect(screen.getByText('3/∞')).toBeInTheDocument();
      expect(screen.getByText('3 used out of ∞ maximum')).toBeInTheDocument();
    });

    test('renders badge with correct count and tooltip without custom label', () => {
      render(<LimitCounter current={2} max={10} />);
      expect(screen.getByText('2/10')).toBeInTheDocument();
      expect(screen.getByText('2 used out of 10 maximum')).toBeInTheDocument();
    });

    test('renders badge with custom label in tooltip', () => {
      render(<LimitCounter current={4} max={8} label="Items" />);
      expect(screen.getByText('4/8')).toBeInTheDocument();
      expect(screen.getByText('Items: 4 used out of 8 maximum')).toBeInTheDocument();
    });
  });

  describe('UI State based on usage', () => {
    test('uses blue when usage is less than 0.5', () => {
      render(<LimitCounter current={3} max={10} />);
      const badge = screen.getByText('3/10');
      expect(badge.parentElement).toHaveAttribute('data-colorscheme', 'blue');
    });

    test('uses yellow when usage is 0.5 or above but less than 0.8', () => {
      render(<LimitCounter current={6} max={10} />);
      const badge = screen.getByText('6/10');
      expect(badge.parentElement).toHaveAttribute('data-colorscheme', 'yellow');
    });

    test('uses orange when usage is 0.8 or above but less than 1', () => {
      render(<LimitCounter current={9} max={10} />);
      const badge = screen.getByText('9/10');
      expect(badge.parentElement).toHaveAttribute('data-colorscheme', 'orange');
    });

    test('uses red when usage is 1 or more', () => {
      render(<LimitCounter current={10} max={10} />);
      const badge = screen.getByText('10/10');
      expect(badge.parentElement).toHaveAttribute('data-colorscheme', 'red');
    });
  });

  describe('Conditional rendering and prop changes', () => {
    test('updates UI when props change', () => {
      const { rerender } = render(<LimitCounter current={3} max={10} />);
      expect(screen.getByText('3/10')).toBeInTheDocument();
      // Re-render with updated current value
      rerender(<LimitCounter current={7} max={10} />);
      expect(screen.getByText('7/10')).toBeInTheDocument();
      expect(screen.getByText('7 used out of 10 maximum')).toBeInTheDocument();
    });
  });
});
