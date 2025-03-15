import { render, screen, fireEvent } from '@utils/test_utils';
import GroupCreator from '@protocols/nestedMapping/components/groups/GroupCreator';

// Define a mutable mock context
const mockedContext = {
  localParentOptions: ['Group1', 'Group2'],
  creationMode: 'none',
  setCreationMode: jest.fn(),
  creatableKey: true,
  createGroup: jest.fn(),
  valueType: 'string',
  config: { constraints: { key_constraints: { type: 'string' }, creatable: true } },
  value: {}
};

jest.mock('@/features/protocols/contexts/nestedMappingContext', () => ({
  useNestedMapping: () => mockedContext,
}));

describe('GroupCreator Component', () => {
  beforeEach(() => {
    mockedContext.creationMode = 'none';
    mockedContext.setCreationMode.mockClear();
    mockedContext.createGroup.mockClear();
    mockedContext.value = {};
    mockedContext.valueType = 'string';
    mockedContext.config = { constraints: { key_constraints: { type: 'string' }, creatable: true } };
  });

  test('renders correctly with default props (button shown)', () => {
    render(<GroupCreator value={{}} />);
    expect(screen.getByText(/add group/i)).toBeInTheDocument();
  });

  test('enters creation mode when "Add Group" is clicked', () => {
    render(<GroupCreator value={{}} />);
    const addButton = screen.getByText(/add group/i);
    fireEvent.click(addButton);
    expect(mockedContext.setCreationMode).toHaveBeenCalledWith('group');
  });

  test('renders creation form when in group creation mode and handles create & cancel actions', () => {
    mockedContext.creationMode = 'group';
    render(<GroupCreator value={{}} />);
    // Input field should be rendered
    const input = screen.getByRole('textbox');
    fireEvent.change(input, { target: { value: 'NewGroup' } });
    // Simulate Enter key press to create group
    fireEvent.keyDown(input, { key: 'Enter', code: 'Enter' });
    expect(mockedContext.createGroup).toHaveBeenCalledWith('NewGroup');
    // Cancel action
    const cancelButton = screen.getByText(/cancel/i);
    fireEvent.click(cancelButton);
    expect(mockedContext.setCreationMode).toHaveBeenCalledWith(null);
  });

  test('renders unsupported type error for boolean group keys', () => {
    mockedContext.creationMode = 'group';
    mockedContext.valueType = 'boolean';
    mockedContext.config = { constraints: { key_constraints: { type: 'boolean' }, creatable: true } };
    render(<GroupCreator value={{}} />);
    expect(screen.getByText(/unsupported group type/i)).toBeInTheDocument();
  });
});
