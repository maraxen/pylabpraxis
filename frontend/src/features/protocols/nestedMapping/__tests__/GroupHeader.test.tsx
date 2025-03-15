import { render, screen, fireEvent } from '@utils/test_utils';
import { GroupHeader } from '@protocols/nestedMapping/components/groups/GroupHeader';

describe('GroupHeader Component', () => {
  const defaultProps = {
    groupId: 'group1',
    groupName: 'Group One',
    isEditingName: false,
    startEditingName: jest.fn(),
    saveGroupName: jest.fn(),
    cancelEditName: jest.fn(),
    groupEditable: true,
    hasParameterValues: false,
    allowDelete: true,
    onDelete: jest.fn(),
    keyConstraints: {},
    constraints: {}
  };

  afterEach(() => {
    jest.clearAllMocks();
  });

  test('renders correctly with default props', () => {
    render(<GroupHeader {...defaultProps} />);
    expect(screen.getByText('Group One')).toBeInTheDocument();
    // Group value limit badge should be rendered (if provided in GroupHeader)
    expect(screen.getByText(/values/i)).toBeInTheDocument();
    // Check that edit and delete buttons are rendered via GroupActions
    expect(screen.getByTestId('edit-group-button')).toBeInTheDocument();
    expect(screen.getByTestId('delete-group-button')).toBeInTheDocument();
  });

  test('triggers startEditingName when group name is clicked', () => {
    render(<GroupHeader {...defaultProps} />);
    fireEvent.click(screen.getByText('Group One'));
    expect(defaultProps.startEditingName).toHaveBeenCalled();
  });

  test('renders editing mode and shows GroupInputField', () => {
    render(<GroupHeader {...defaultProps} isEditingName={true} />);
    // GroupInputField renders an EditableLabel with testId "group-input-field"
    expect(screen.getByTestId('group-input-field')).toBeInTheDocument();
  });

  test('calls onDelete when delete button is clicked', () => {
    render(<GroupHeader {...defaultProps} />);
    fireEvent.click(screen.getByTestId('delete-group-button'));
    expect(defaultProps.onDelete).toHaveBeenCalled();
  });
});
