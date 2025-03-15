import { render, screen } from '@utils/test_utils';
import { GroupLimit } from '@protocols/nestedMapping/components/groups/GroupLimit';

const mockedContext = {
  value: { group1: {}, group2: {} },
  getMaxTotalValues: () => 5
};

jest.mock('@features/protocols/contexts/nestedMappingContext', () => ({
  useNestedMapping: () => mockedContext,
}));

describe('GroupLimit Component', () => {
  test('renders correctly with default props', () => {
    render(<GroupLimit />);
    // Expect LimitCounter label "Groups" to appear
    expect(screen.getByText(/groups/i)).toBeInTheDocument();
    // Expect current count to be 2 and max to be 5
    expect(screen.getByText('2 / 5')).toBeInTheDocument();
  });

  test('updates current value based on context', () => {
    // Overwrite value for testing current count
    mockedContext.value = { group1: {}, group2: {}, group3: {} } as any;
    render(<GroupLimit />);
    // Since current count is 3 and max is 5, LimitCounter should reflect that.
    expect(screen.getByText(/groups/i)).toBeInTheDocument();
    expect(screen.getByText('3 / 5')).toBeInTheDocument();
  });
});