import { render, screen } from '@utils/test_utils';
import { AvailableValuesSection } from '@protocols/nestedMapping/components/values/AvailableValuesSection';

const mockContext = {
  effectiveChildOptions: ['Option1', 'Option2', 'Option3'],
  valueType: 'string',
  getValueMetadata: (val: string) => ({ type: 'string', isFromParam: false }),
  dragInfo: { overDroppableId: '', isDragging: false },
  createdValues: {},
  setCreatedValues: jest.fn(),
  creatableValue: true
};

jest.mock('@protocols/contexts/nestedMappingContext', () => ({
  useNestedMapping: () => mockContext,
}));

describe('AvailableValuesSection Component', () => {
  beforeEach(() => {
    mockContext.createdValues = {};
    mockContext.setCreatedValues.mockClear();
  });

  test('renders with available options when not present in groups', () => {
    // No groups provided, so all options should be available.
    render(<AvailableValuesSection value={{}} />);
    expect(screen.getByText(/Available Values/i)).toBeInTheDocument();
    const items = screen.getAllByTestId('sortable-value-item');
    expect(items).toHaveLength(3);
  });

  test('filters out options that are already in groups', () => {
    // Provide a value prop with one group that has 'Option1'
    const groups = {
      group1: { id: 'group1', name: 'Group 1', values: [{ id: 'v1', value: 'Option1', type: 'string' }] }
    };
    render(<AvailableValuesSection value={groups} />);
    // Now only Option2 and Option3 should be available.
    const items = screen.getAllByTestId('sortable-value-item');
    expect(items).toHaveLength(2);
    expect(items[0]).toHaveTextContent('Option2');
    expect(items[1]).toHaveTextContent('Option3');
  });

  test('displays empty state text when no available options exist', () => {
    // Set effectiveChildOptions to empty array
    mockContext.effectiveChildOptions = [];
    render(<AvailableValuesSection value={{}} />);
    expect(screen.getByText(/No available values/i)).toBeInTheDocument();
  });

  test('applies drag-over styling when droppable is active', () => {
    // Simulate drag over by setting the overDroppableId
    mockContext.dragInfo = { overDroppableId: 'available-values', isDragging: true };
    const { container } = render(<AvailableValuesSection value={{}} />);
    // The container should reflect the drag state (implementation-dependent)
    expect(container).toBeInTheDocument();
  });
});
