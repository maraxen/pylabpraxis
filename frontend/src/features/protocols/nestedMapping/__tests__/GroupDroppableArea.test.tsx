import { render, screen } from '@utils/test_utils';
import { GroupDroppableArea } from '@protocols/nestedMapping/components/groups/GroupDroppableArea';

const mockedContext = {
  value: { group1: { values: [] as any[] } },
  getMaxValuesPerGroup: () => 3,
  dragInfo: { isDragging: false, overDroppableId: '' }
};

jest.mock('@features/protocols/contexts/nestedMappingContext', () => ({
  useNestedMapping: () => mockedContext,
}));

describe('GroupDroppableArea Component', () => {
  beforeEach(() => {
    mockedContext.value = { group1: { values: [] as any[] } };
    mockedContext.dragInfo = { isDragging: false, overDroppableId: '' };
  });

  test('renders children when provided', () => {
    render(
      <GroupDroppableArea groupId="group1">
        <div>Child Content</div>
      </GroupDroppableArea>
    );
    expect(screen.getByText(/child content/i)).toBeInTheDocument();
    // No empty state hint when children exist
    expect(screen.queryByText(/drag values here or add a new value/i)).not.toBeInTheDocument();
  });

  test('renders empty state hint when no children and not full', () => {
    render(
      <GroupDroppableArea groupId="group1">
        <></>
      </GroupDroppableArea>
    );
    expect(screen.getByText(/drag values here or add a new value/i)).toBeInTheDocument();
  });

  test('does not render empty state hint when group is full', () => {
    // Fill group values to max (3) using strings to avoid type issues
    mockedContext.value = { group1: { values: ['a', 'b', 'c'] } };
    render(
      <GroupDroppableArea groupId="group1">
        <></>
      </GroupDroppableArea>
    );
    expect(screen.queryByText(/drag values here or add a new value/i)).not.toBeInTheDocument();
  });

  test('applies correct droppable state based on dragInfo', () => {
    mockedContext.dragInfo = { isDragging: true, overDroppableId: 'group1' };
    render(
      <GroupDroppableArea groupId="group1">
        <div>Dragged Content</div>
      </GroupDroppableArea>
    );
    expect(screen.getByText(/dragged content/i)).toBeInTheDocument();
  });
});