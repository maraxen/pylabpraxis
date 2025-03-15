import { render, screen } from '@utils/test_utils';
import { ValueDisplayText } from '@protocols/nestedMapping/components/values/ValueDisplayText';

describe('ValueDisplayText Component', () => {
  test('renders string values correctly', () => {
    render(<ValueDisplayText value="Hello World" type="string" />);
    expect(screen.getByText('Hello World')).toBeInTheDocument();
  });

  test('renders number values correctly', () => {
    render(<ValueDisplayText value={123} type="number" />);
    expect(screen.getByText('123')).toBeInTheDocument();
  });

  test('renders boolean values correctly', () => {
    render(<ValueDisplayText value={true} type="boolean" />);
    expect(screen.getByText('True')).toBeInTheDocument();
  });

  test('renders placeholder for null/undefined values', () => {
    render(<ValueDisplayText value={null} type="string" />);
    expect(screen.getByText(/\(empty\)/i)).toBeInTheDocument();
  });

  test('renders object and array previews', () => {
    render(<ValueDisplayText value={{ a: 1, b: 2, c: 3 }} type="dict" />);
    expect(screen.getByText(/{/)).toBeInTheDocument();
    render(<ValueDisplayText value={['x', 'y', 'z']} type="array" />);
    expect(screen.getByText(/\[/)).toBeInTheDocument();
  });
});
