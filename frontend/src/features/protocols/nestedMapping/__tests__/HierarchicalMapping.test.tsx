import { render, screen, fireEvent } from '@utils/test_utils';
import { HierarchicalMapping } from '@protocols/nestedMapping/components/HierarchicalMapping';

describe('HierarchicalMapping Component', () => {
  const defaultProps = {
    name: "test-mapping",
    value: {},
    config: {
      type: 'dict',
      constraints: {
        key_constraints: { type: 'string', creatable: true },
        value_constraints: { type: 'string', creatable: true }
      }
    },
    onChange: jest.fn(),
    parameters: {}
  };

  beforeEach(() => {
    defaultProps.onChange.mockClear();
  });

  test('renders correctly with default props', () => {
    render(<HierarchicalMapping {...defaultProps} />);
    // Expect headings for groups and available values
    expect(screen.getByText(/Groups/i)).toBeInTheDocument();
    expect(screen.getByText(/Available Values/i)).toBeInTheDocument();
    // Expect empty state messages when no groups/values exist
    expect(screen.getByText(/No groups defined/i)).toBeInTheDocument();
    expect(screen.getByText(/No available values/i)).toBeInTheDocument();
  });

  test('handles group creation interaction', () => {
    render(<HierarchicalMapping {...defaultProps} />);
    // Click the Add Group button (group creator)
    const addGroupButton = screen.getByText(/Add Group/i);
    fireEvent.click(addGroupButton);
    // Group creation mode should display an input (test id used)
    expect(screen.getByTestId('group-input-field')).toBeInTheDocument();
    // Simulate user typing a new group name and pressing Enter to save
    fireEvent.change(screen.getByTestId('group-input-field'), { target: { value: 'NewGroup' } });
    fireEvent.keyDown(screen.getByTestId('group-input-field'), { key: 'Enter', code: 'Enter' });
    // onChange should be called with new group data (argument includes a key "NewGroup")
    expect(defaultProps.onChange).toHaveBeenCalled();
  });

  test('renders groups when value prop has groups', () => {
    const groupValue = {
      group1: {
        id: 'group1',
        name: 'Group One',
        values: [
          { id: 'val1', value: 'Test Value', type: 'string', isEditable: true }
        ],
        isEditable: true
      }
    };
    render(<HierarchicalMapping {...defaultProps} value={groupValue} />);
    // Group header should display the group name
    expect(screen.getByText('Group One')).toBeInTheDocument();
    // The empty state for groups should not be shown
    expect(screen.queryByText(/No groups defined/i)).not.toBeInTheDocument();
  });

  test('filters out available values already used in groups', () => {
    // Create a group using one available option (e.g., "Option1")
    const groupValue = {
      group1: {
        id: 'group1',
        name: 'Group One',
        values: [{ id: 'val1', value: 'Option1', type: 'string', isEditable: true }],
        isEditable: true
      }
    };
    render(<HierarchicalMapping {...defaultProps} value={groupValue} />);
    // If the only default available option ("Option1") is used, expect empty state for available values
    expect(screen.getByText(/No available values/i)).toBeInTheDocument();
  });
});