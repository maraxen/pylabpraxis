import { render, screen } from '@utils/test_utils';
import { GroupValueLimit } from '@protocols/nestedMapping/components/groups/GroupValueLimit';

const mockedContext = {
  value: { group1: { values: ['a', 'b'] } },
  getMaxValuesPerGroup: () => 4
};

jest.mock('@features/protocols/contexts/nestedMappingContext', () => ({
  useNestedMapping: () => mockedContext,
}));

describe('GroupValueLimit Component', () => {
  test('renders correctly with existing group', () => {
    render(<GroupValueLimit groupId="group1" />);
    // Expect LimitCounter label "Values in Group" to appear
    expect(screen.getByText(/values in group/i)).toBeInTheDocument();
  });

  test('renders nothing when group does not exist', () => {
    render(<GroupValueLimit groupId="nonexistent" />);
    // Should return null so nothing is rendered
    expect(screen.queryByText(/values in group/i)).not.toBeInTheDocument();
  });
});
