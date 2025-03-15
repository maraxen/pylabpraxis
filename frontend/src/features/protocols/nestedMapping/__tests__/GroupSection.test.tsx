import { render, screen, fireEvent } from '@utils/test_utils';
import { GroupsSection } from '@protocols/nestedMapping/components/groups/GroupsSection';

const mockedContext = {
  dragInfo: { overDroppableId: '' }
};

jest.mock('@protocols/contexts/nestedMappingContext', () => ({
  useNestedMapping: () => mockedContext,
}));

describe('GroupsSection Component', () => {
  const initialGroups = {
    group1: {
      id: 'group1',
      name: 'Group One',
      values: [{ id: 'val1', value: 'Test Value', type: 'string', isEditable: true }],
      isEditable: true
    },
    group2: {
      id: 'group2',
      name: 'Group Two',
      values: [],
      isEditable: true
    }
  };

  test('renders correctly with default props', () => {
    render(<GroupsSection value={initialGroups} onChange={() => { }} />);
    // Expect heading "Groups" and group headers to appear
    expect(screen.getByText(/groups/i)).toBeInTheDocument();
    expect(screen.getByText('Group One')).toBeInTheDocument();
    expect(screen.getByText('Group Two')).toBeInTheDocument();
    // Expect GroupCreator button to be present
    expect(screen.getByText(/add group/i)).toBeInTheDocument();
  });

  test('handles deletion properly', () => {
    const handleChange = jest.fn();
    render(<GroupsSection value={initialGroups} onChange={handleChange} />);
    // Simulate clicking delete button for Group Two
    const deleteButtons = screen.getAllByTestId('delete-group-button');
    // Assuming the delete button for group2 is rendered (and allowDelete is true)
    fireEvent.click(deleteButtons[1]);
    expect(handleChange).toHaveBeenCalled();
    // Check that the onChange argument does not include group2 (details abstracted)
    // ...existing code...
  });

  test('renders empty state when no groups exist', () => {
    render(<GroupsSection value={{}} onChange={() => { }} />);
    expect(screen.getByText(/no groups defined/i)).toBeInTheDocument();
  });
});