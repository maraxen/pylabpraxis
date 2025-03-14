import React from 'react';
import { Box, BoxProps } from '@chakra-ui/react';

interface CardContainerProps extends BoxProps {
  isHighlighted?: boolean;
  isDragging?: boolean;
  isActive?: boolean;
  testId?: string;
}

/**
 * A consistent container component for cards/items with state-dependent styling
 */
export const CardContainer: React.FC<CardContainerProps> = ({
  children,
  isHighlighted = false,
  isDragging = false,
  isActive = false,
  testId = "card-container",
  ...props
}) => {
  return (
    <Box
      borderWidth={1}
      borderRadius="md"
      p={3}
      bg="white"
      _dark={{ bg: "gray.700" }}
      position="relative"
      boxShadow={getBoxShadow(isHighlighted, isDragging, isActive)}
      borderColor={getBorderColor(isHighlighted, isDragging, isActive)}
      opacity={isDragging ? 0.7 : 1}
      transition="all 0.2s"
      data-testid={testId}
      {...props}
    >
      {children}
    </Box>
  );
};

// Helper function to get appropriate box shadow based on state
function getBoxShadow(isHighlighted: boolean, isDragging: boolean, isActive: boolean) {
  if (isDragging) return "lg";
  if (isHighlighted) return "md";
  if (isActive) return "sm";
  return "none";
}

// Helper function to get appropriate border color based on state
function getBorderColor(isHighlighted: boolean, isDragging: boolean, isActive: boolean) {
  if (isDragging) return "blue.400";
  if (isHighlighted) return "blue.300";
  if (isActive) return "gray.300";
  return "gray.200";
}