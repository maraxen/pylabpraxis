import React from 'react';
import { render, screen, fireEvent } from '@utils/test_utils';
import { Tabs, TabList, TabTrigger, TabContent } from '../ui/tabs';

// Mock createSlotRecipeContext and other Chakra UI dependencies
jest.mock('@chakra-ui/react', () => {
  const originalModule = jest.requireActual('@chakra-ui/react');
  return {
    ...originalModule,
    createSlotRecipeContext: () => ({
      withProvider: (_: string, slot: string) =>
        React.forwardRef(({ children, ...props }: any, ref: any) => (
          <div data-testid={`tabs-${slot}`} ref={ref} {...props}>{children}</div>
        )),
      withContext: (_: string, slot: string) =>
        React.forwardRef(({ children, ...props }: any, ref: any) => (
          <div data-testid={`tabs-${slot}`} ref={ref} {...props}>{children}</div>
        ))
    })
  };
});

// Mock recipe import
jest.mock('@recipes/tabs.recipe', () => ({
  tabsRecipe: {}
}));

describe('Tabs Component', () => {
  describe('Basic Rendering', () => {
    it('should render basic tabs structure', () => {
      render(
        <Tabs defaultValue="tab1">
          <TabList>
            <TabTrigger value="tab1">Tab 1</TabTrigger>
            <TabTrigger value="tab2">Tab 2</TabTrigger>
          </TabList>
          <TabContent value="tab1">Content 1</TabContent>
          <TabContent value="tab2">Content 2</TabContent>
        </Tabs>
      );

      expect(screen.getByTestId('tabs-root')).toBeInTheDocument();
      expect(screen.getByTestId('tabs-list')).toBeInTheDocument();
      expect(screen.getAllByTestId('tabs-trigger').length).toBe(2);
      expect(screen.getAllByTestId('tabs-content').length).toBe(2);

      expect(screen.getByText('Tab 1')).toBeInTheDocument();
      expect(screen.getByText('Tab 2')).toBeInTheDocument();
      expect(screen.getByText('Content 1')).toBeInTheDocument();
      expect(screen.queryByText('Content 2')).toBeInTheDocument();
    });
  });

  describe('Tab Selection', () => {
    it('should select default tab correctly', () => {
      render(
        <Tabs defaultValue="tab2">
          <TabList>
            <TabTrigger value="tab1">Tab 1</TabTrigger>
            <TabTrigger value="tab2">Tab 2</TabTrigger>
          </TabList>
          <TabContent value="tab1">Content 1</TabContent>
          <TabContent value="tab2">Content 2</TabContent>
        </Tabs>
      );

      const tabTriggers = screen.getAllByTestId('tabs-trigger');
      expect(tabTriggers[1]).toHaveAttribute('aria-selected', 'true');
      expect(tabTriggers[0]).toHaveAttribute('aria-selected', 'false');
    });

    it('should use controlled value when provided', () => {
      render(
        <Tabs value="tab2">
          <TabList>
            <TabTrigger value="tab1">Tab 1</TabTrigger>
            <TabTrigger value="tab2">Tab 2</TabTrigger>
          </TabList>
          <TabContent value="tab1">Content 1</TabContent>
          <TabContent value="tab2">Content 2</TabContent>
        </Tabs>
      );

      const tabTriggers = screen.getAllByTestId('tabs-trigger');
      expect(tabTriggers[1]).toHaveAttribute('aria-selected', 'true');
    });
  });

  describe('Tab Interaction', () => {
    it('should call onChange when tab is clicked', () => {
      const handleChange = jest.fn();

      render(
        <Tabs defaultValue="tab1" onChange={handleChange}>
          <TabList>
            <TabTrigger value="tab1">Tab 1</TabTrigger>
            <TabTrigger value="tab2">Tab 2</TabTrigger>
          </TabList>
          <TabContent value="tab1">Content 1</TabContent>
          <TabContent value="tab2">Content 2</TabContent>
        </Tabs>
      );

      fireEvent.click(screen.getByText('Tab 2'));
      expect(handleChange).toHaveBeenCalledWith({ value: 'tab2' });
    });

    it('should update local state when uncontrolled', () => {
      const handleChange = jest.fn();

      render(
        <Tabs defaultValue="tab1" onChange={handleChange}>
          <TabList>
            <TabTrigger value="tab1">Tab 1</TabTrigger>
            <TabTrigger value="tab2">Tab 2</TabTrigger>
          </TabList>
          <TabContent value="tab1">Content 1</TabContent>
          <TabContent value="tab2">Content 2</TabContent>
        </Tabs>
      );

      fireEvent.click(screen.getByText('Tab 2'));
      expect(handleChange).toHaveBeenCalledWith({ value: 'tab2' });

      const tabTriggers = screen.getAllByTestId('tabs-trigger');
      expect(tabTriggers[1]).toHaveAttribute('aria-selected', 'true');
    });
  });

  describe('TabContent Behavior', () => {
    it('should show content based on selected tab', () => {
      render(
        <Tabs defaultValue="tab1">
          <TabList>
            <TabTrigger value="tab1">Tab 1</TabTrigger>
            <TabTrigger value="tab2">Tab 2</TabTrigger>
          </TabList>
          <TabContent value="tab1" data-testid="content-1">Content 1</TabContent>
          <TabContent value="tab2" data-testid="content-2">Content 2</TabContent>
        </Tabs>
      );

      const tabContents = screen.getAllByTestId('tabs-content');
      expect(tabContents[0]).toBeVisible();
      expect(tabContents[1]).toBeInTheDocument();
    });
  });

  describe('Props Handling', () => {
    it('should pass additional props to tab components', () => {
      render(
        <Tabs defaultValue="tab1" className="custom-tabs">
          <TabList className="custom-tab-list">
            <TabTrigger value="tab1" className="custom-trigger">Tab 1</TabTrigger>
          </TabList>
          <TabContent value="tab1" className="custom-content">Content 1</TabContent>
        </Tabs>
      );

      expect(screen.getByTestId('tabs-root')).toHaveAttribute('className', 'custom-tabs');
      expect(screen.getByTestId('tabs-list')).toHaveAttribute('className', 'custom-tab-list');
      expect(screen.getByTestId('tabs-trigger')).toHaveAttribute('className', 'custom-trigger');
      expect(screen.getByTestId('tabs-content')).toHaveAttribute('className', 'custom-content');
    });
  });
});