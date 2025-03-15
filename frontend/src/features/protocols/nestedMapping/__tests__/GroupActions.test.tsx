import { render, screen, fireEvent } from '@utils/test_utils';
import { GroupActions } from '@protocols/nestedMapping/components/groups/GroupActions';

describe('GroupActions Component', () => {
  // Test default rendering with default props
  test('renders correctly with default props', () => {
    const onDelete = jest.fn();
    const startEditingName = jest.fn();

    render(
      <GroupActions
        groupEditable={true}
        isEditingName={false}
        allowDelete={true}
        onDelete={onDelete}
        startEditingName={startEditingName}
      />
    );

    // Expect edit button to render (action "edit")
    const editButton = screen.getByTestId('icon-button');
    expect(editButton).toBeInTheDocument();

    // Render should show delete button as well (action "remove")
    // Since we use two buttons, check for both icons.
    expect(screen.getByTestId('icon-pencil')).toBeInTheDocument();
    expect(screen.getByTestId('icon-trash')).toBeInTheDocument();
  });

  // Test conditional rendering: When isEditingName is true, buttons should not be rendered.
  test('does not render action buttons when isEditingName is true', () => {
    const onDelete = jest.fn();
    const startEditingName = jest.fn();

    render(
      <GroupActions
        groupEditable={true}
        isEditingName={true}
        allowDelete={true}
        onDelete={onDelete}
        startEditingName={startEditingName}
      />
    );

    // Expect no edit or delete button to be in the document.
    expect(screen.queryByTestId('icon-pencil')).not.toBeInTheDocument();
    expect(screen.queryByTestId('icon-trash')).not.toBeInTheDocument();
  });

  // Test conditional rendering: When groupEditable is false, edit button should not render.
  test('does not render edit button when groupEditable is false', () => {
    const onDelete = jest.fn();
    const startEditingName = jest.fn();

    render(
      <GroupActions
        groupEditable={false}
        isEditingName={false}
        allowDelete={true}
        onDelete={onDelete}
        startEditingName={startEditingName}
      />
    );

    // Expect no edit button, but delete may still render.
    expect(screen.queryByTestId('icon-pencil')).not.toBeInTheDocument();
    // Delete button should be visible if allowDelete is true.
    expect(screen.getByTestId('icon-trash')).toBeInTheDocument();
  });

  // Test event handling: callbacks are called on click events.
  test('calls the correct callbacks on button clicks', () => {
    const onDelete = jest.fn();
    const startEditingName = jest.fn();

    render(
      <GroupActions
        groupEditable={true}
        isEditingName={false}
        allowDelete={true}
        onDelete={onDelete}
        startEditingName={startEditingName}
      />
    );

    // Click on edit button
    const editButton = screen.getByTestId('icon-button');
    // In our test, the first rendered IconButton is for edit action.
    fireEvent.click(editButton);
    expect(startEditingName).toHaveBeenCalledTimes(1);

    // Get delete button by finding a sibling by removing first one.
    // Since both buttons are rendered via separate IconButtons let us query for the specific icons.
    const deleteButton = screen.getByTestId('icon-trash').closest('button');
    fireEvent.click(deleteButton!);
    expect(onDelete).toHaveBeenCalledTimes(1);
  });

  // Test UI state: when allowDelete is false, delete button is not rendered.
  test('does not render delete button when allowDelete is false', () => {
    const onDelete = jest.fn();
    const startEditingName = jest.fn();

    render(
      <GroupActions
        groupEditable={true}
        isEditingName={false}
        allowDelete={false}
        onDelete={onDelete}
        startEditingName={startEditingName}
      />
    );

    // Delete button should not be rendered.
    expect(screen.queryByTestId('icon-trash')).not.toBeInTheDocument();
  });
});
