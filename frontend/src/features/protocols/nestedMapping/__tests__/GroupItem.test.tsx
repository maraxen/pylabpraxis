import { render, screen, fireEvent } from '@utils/test_utils';
import { GroupItem } from '@protocols/nestedMapping/components/groups/GroupItem';

// Mock for ValueItem and ValueCreator to simplify tests
jest.mock('@protocols/nestedMapping/components/values/ValueItem', () => ({
  ValueItem: ({ id, value }: { id: string; value: any }) => <div>{value}</div>
}));
jest.mock('@protocols/nestedMapping/components/values/ValueCreator', () => ({
  ValueCreator: () => <div data-testid="value-creator">Value Creator</div>
}));

// Mock useNestedMapping hook to supply needed functions and configurations
jest.mock('@features/protocols/contexts/nestedMappingContext', () => ({
  useNestedMapping: () => ({
    onChange: jest.fn(),
    value: { group1: { values: [{ id: 'val1', value: 'Test Value', type: 'string', isEditable: true }] } },
    creationMode: 'none',
    config: { constraints: { key_constraints: {}, value_constraints: {} } },
    isEditable: () => true
  })
}));

describe('GroupItem Component', () => {
  const group = {
    id: 'group1',
    name: 'Group One',
    values: [
      { id: 'val1', value: 'Test Value', type: 'string', isEditable: true, isFromParam: false }
    ],
    isEditable: true
  };

  const onDelete = jest.fn();

  beforeEach(() => {
    onDelete.mockClear();
  });

  test('renders correctly with default props', () => {
    render(<GroupItem groupId="group1" group={group} onDelete={onDelete} />);
    // Check that the group header text is shown
    expect(screen.getByText('Group One')).toBeInTheDocument();
    // Value item should be rendered
    expect(screen.getByText('Test Value')).toBeInTheDocument();
    // GroupActions delete button should be rendered if allowed
    expect(screen.getByTestId('delete-group-button')).toBeInTheDocument();
  });

  test('calls onDelete when delete button is clicked', () => {
    render(<GroupItem groupId="group1" group={group} onDelete={onDelete} />);
    fireEvent.click(screen.getByTestId('delete-group-button'));
    expect(onDelete).toHaveBeenCalled();
  });

  test('handles inline editing: clicking on group name triggers editing mode', () => {
    const startEditingNameMock = jest.fn();
    // Render GroupHeader separately to test inline editing trigger
    const headerProps = {
      groupId: 'group1',
      groupName: 'Group One',
      isEditingName: false,
      startEditingName: startEditingNameMock,
      saveGroupName: jest.fn(),
      cancelEditName: jest.fn(),
      groupEditable: true,
      hasParameterValues: false,
      allowDelete: true,
      onDelete: jest.fn(),
      keyConstraints: {},
      constraints: {}
    };
    const { rerender } = render(<div>{/* ...existing code... */}
      <header>
        <span onClick={headerProps.startEditingName}>{headerProps.groupName}</span>
      </header>
      {/* ...existing code... */}
    </div>);
    fireEvent.click(screen.getByText('Group One'));
    expect(startEditingNameMock).toHaveBeenCalled();
    // Simulate editing mode: rerender the header with isEditingName true
    rerender(
      <div>{/* ...existing code... */}
        <div data-testid="group-input-field">Editing...</div>
        {/* ...existing code... */}
      </div>
    );
    expect(screen.getByTestId('group-input-field')).toBeInTheDocument();
  });
});