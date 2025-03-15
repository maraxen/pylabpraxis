import { render, screen } from '@utils/test_utils';
import { TabRenderer } from '../ui/TabRenderer';

// Mock the TabContent component
jest.mock('@praxis-ui/tabs', () => ({
  TabContent: ({ children, value, hidden }: any) => (
    <div data-testid="tab-content" data-value={value} hidden={hidden}>{children}</div>
  )
}));

// Mock Box component
jest.mock('@chakra-ui/react', () => {
  const originalModule = jest.requireActual('@chakra-ui/react');
  return {
    ...originalModule,
    Box: ({ children, ...props }: any) => (
      <div data-testid="chakra-box" {...props}>{children}</div>
    )
  };
});

describe('TabRenderer Component', () => {
  // Define test data
  const testTabContent = {
    'tab1': <div data-testid="tab1-content">Tab 1 Content</div>,
    'tab2': <div data-testid="tab2-content">Tab 2 Content</div>,
    'tab3': <div data-testid="tab3-content">Tab 3 Content</div>
  };

  // Basic rendering tests
  describe('Rendering', () => {
    test('renders without errors', () => {
      render(<TabRenderer tabContent={testTabContent} selectedTab="tab1" />);

      expect(screen.getByTestId('chakra-box')).toBeInTheDocument();
      expect(screen.getAllByTestId('tab-content').length).toBe(3);
    });

    test('renders with correct styling', () => {
      render(<TabRenderer tabContent={testTabContent} selectedTab="tab1" />);

      const container = screen.getByTestId('chakra-box');
      expect(container).toHaveStyle({
        position: 'relative',
        width: 'full',
        marginTop: '4'
      });
    });
  });

  // Tab content visibility tests
  describe('Tab Content Visibility', () => {
    test('displays the selected tab content', () => {
      render(<TabRenderer tabContent={testTabContent} selectedTab="tab1" />);

      const tabContents = screen.getAllByTestId('tab-content');

      // tab1 should not be hidden
      expect(tabContents.find(tab => tab.dataset.value === 'tab1')).not.toHaveAttribute('hidden');

      // tab2 and tab3 should be hidden
      expect(tabContents.find(tab => tab.dataset.value === 'tab2')).toHaveAttribute('hidden');
      expect(tabContents.find(tab => tab.dataset.value === 'tab3')).toHaveAttribute('hidden');
    });

    test('changes visible tab when selectedTab prop changes', () => {
      const { rerender } = render(<TabRenderer tabContent={testTabContent} selectedTab="tab1" />);

      // Initial render - tab1 should be visible
      let tabContents = screen.getAllByTestId('tab-content');
      expect(tabContents.find(tab => tab.dataset.value === 'tab1')).not.toHaveAttribute('hidden');

      // Rerender with a different selected tab
      rerender(<TabRenderer tabContent={testTabContent} selectedTab="tab2" />);

      // After rerender - tab2 should be visible, tab1 hidden
      tabContents = screen.getAllByTestId('tab-content');
      expect(tabContents.find(tab => tab.dataset.value === 'tab1')).toHaveAttribute('hidden');
      expect(tabContents.find(tab => tab.dataset.value === 'tab2')).not.toHaveAttribute('hidden');
    });
  });

  // Content rendering tests
  describe('Content Rendering', () => {
    test('renders all tab content correctly', () => {
      render(<TabRenderer tabContent={testTabContent} selectedTab="tab1" />);

      // All content should be rendered, even if some are hidden
      expect(screen.getByTestId('tab1-content')).toBeInTheDocument();
      expect(screen.getByTestId('tab2-content')).toBeInTheDocument();
      expect(screen.getByTestId('tab3-content')).toBeInTheDocument();
    });

    test('correctly wraps content in Box components', () => {
      render(<TabRenderer tabContent={testTabContent} selectedTab="tab1" />);

      // Each tab content should be wrapped in a Box with padding
      const innerBoxes = screen.getAllByTestId('chakra-box').filter(
        box => box.getAttribute('p') === '4'
      );

      expect(innerBoxes.length).toBe(3); // One for each tab content
    });
  });

  // Edge cases tests
  describe('Edge Cases', () => {
    test('handles empty tabContent object', () => {
      render(<TabRenderer tabContent={{}} selectedTab="tab1" />);

      // Should render container but no tab content
      expect(screen.getByTestId('chakra-box')).toBeInTheDocument();
      expect(screen.queryByTestId('tab-content')).not.toBeInTheDocument();
    });

    test('handles selected tab not in tabContent', () => {
      render(<TabRenderer tabContent={testTabContent} selectedTab="nonexistent-tab" />);

      // Should render all tabs but all should be hidden
      const tabContents = screen.getAllByTestId('tab-content');
      expect(tabContents.length).toBe(3);

      tabContents.forEach(tab => {
        expect(tab).toHaveAttribute('hidden');
      });
    });
  });
});