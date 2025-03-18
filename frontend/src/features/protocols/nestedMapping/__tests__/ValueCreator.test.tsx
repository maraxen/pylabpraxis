import { render, screen, fireEvent } from '@utils/test_utils';
import { ValueCreator } from '@protocols/nestedMapping/components/values/ValueCreator';
import { ValueData } from '@shared/types/protocol';

// Update the type for creationMode and setCreationMode
const mockContext = {
  localChildOptions: ['opt1', 'opt2'],
  creationMode: null as 'value' | null,
  setCreationMode: jest.fn() as jest.Mock<(mode: 'value' | null) => void>,
  creatableValue: true,
  createValue: jest.fn().mockReturnValue('new-id'),
  valueType: 'string',
  config: { constraints: { creatable: true } }
};

jest.mock('@protocols/contexts/nestedMappingContext', () => ({
  useNestedMapping: () => mockContext,
}));

describe('ValueCreator Component', () => {
  beforeEach(() => {
    mockContext.creationMode = null;
    mockContext.setCreationMode.mockClear();
    mockContext.createValue.mockClear();
  });

  // Create sample values for testing
  const sampleValues: ValueData[] = [];

  test('renders correctly with default props', () => {
    render(<ValueCreator value={sampleValues} />);
    expect(screen.getByText(/Add Value/i)).toBeInTheDocument();
  });

  test('enters creation mode on button click', () => {
    render(<ValueCreator value={sampleValues} />);
    fireEvent.click(screen.getByText(/Add Value/i));
    expect(mockContext.setCreationMode).toHaveBeenCalledWith('value');
  });

  test('renders creation UI when in creation mode', () => {
    mockContext.creationMode = 'value';
    render(<ValueCreator value={sampleValues} />);
    // Check for input rendered by InputRenderer (using testId if provided)
    expect(screen.getByRole('textbox')).toBeInTheDocument();
    expect(screen.getByText(/Create/i)).toBeInTheDocument();
    expect(screen.getByText(/Cancel/i)).toBeInTheDocument();
  });

  test('calls createValue and resets creation mode on value submission', () => {
    mockContext.creationMode = 'value';
    render(<ValueCreator value={sampleValues} />);
    const input = screen.getByRole('textbox');
    fireEvent.change(input, { target: { value: 'new-value' } });
    fireEvent.click(screen.getByText(/Create/i));
    expect(mockContext.createValue).toHaveBeenCalledWith('new-value');
    expect(mockContext.setCreationMode).toHaveBeenCalledWith(null);
  });
});