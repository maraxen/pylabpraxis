import { render, screen } from '@utils/test_utils';
import { GroupBadges } from '@protocols/nestedMapping/components/groups/GroupBadges';

describe('GroupBadges Component', () => {
  test('renders correctly with default props (editable, no parameter, string type, no constraints)', () => {
    render(
      <GroupBadges
        groupEditable={true}
        hasParameterValues={false}
        keyConstraints={{ type: 'string' }}
        constraints={{}}
      />
    );
    // Should show "editable" badge
    expect(screen.getByText(/editable/i)).toBeInTheDocument();
    // Should not render parameter, type or constraint badges
    expect(screen.queryByText(/parameter/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/constrained/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/number/i)).not.toBeInTheDocument();
  });

  test('renders parameter badge, type badge and constraint badge when provided', () => {
    render(
      <GroupBadges
        groupEditable={false}
        hasParameterValues={true}
        keyConstraints={{ type: 'number' }}
        constraints={{ min: 1 }}
      />
    );
    // Should show "readonly" badge for non-editable groups
    expect(screen.getByText(/readonly/i)).toBeInTheDocument();
    // Parameter badge appears
    expect(screen.getByText(/parameter/i)).toBeInTheDocument();
    // Type badge with label "number"
    expect(screen.getByText('number')).toBeInTheDocument();
    // Constraint badge appears with label "constrained"
    expect(screen.getByText(/constrained/i)).toBeInTheDocument();
  });
});
