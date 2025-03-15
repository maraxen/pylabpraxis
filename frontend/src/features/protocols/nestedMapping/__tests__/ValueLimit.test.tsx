import { render, screen } from '@utils/test_utils';
import { ValueLimit } from '@protocols/nestedMapping/components/values/ValueLimit';

const mockContext = {
  value: {
    group1: { values: [{ id: 'v1', value: 'A', type: 'string' }] },
    group2: { values: [{ id: 'v2', value: 'B', type: 'string' }, { id: 'v3', value: 'C', type: 'string' }] }
  },
  getMaxTotalValues: () => 10,
};

jest.mock('@protocols/contexts/nestedMappingContext', () => ({
  useNestedMapping: () => mockContext,
}));

describe('ValueLimit Component', () => {
  test('renders correctly with total values count', () => {
    render(<ValueLimit />);
    // Total values are 3; check that LimitCounter displays "3" and "10"
    expect(screen.getByText(/3/)).toBeInTheDocument();
    expect(screen.getByText(/10/)).toBeInTheDocument();
    expect(screen.getByText(/Total Values/i)).toBeInTheDocument();
  });
});
