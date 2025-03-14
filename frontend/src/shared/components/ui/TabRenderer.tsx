import React from 'react';
import { Box } from '@chakra-ui/react';
import { TabContent } from '@praxis-ui/tabs';

interface TabRendererProps {
  tabContent: Record<string, React.ReactNode>;
  selectedTab: string;
}

export const TabRenderer: React.FC<TabRendererProps> = ({ tabContent, selectedTab }) => (
  <Box position="relative" minH="400px" w="full" mt={4}>
    {Object.entries(tabContent).map(([key, content]) => (
      <TabContent key={key} value={key} hidden={key !== selectedTab}>
        <Box p={4}>{content}</Box>
      </TabContent>
    ))}
  </Box>
);