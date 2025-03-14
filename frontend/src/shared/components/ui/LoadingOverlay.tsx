import React from 'react';
import { Box, Spinner, Text, VStack } from '@chakra-ui/react';

interface LoadingOverlayProps {
  message?: string;
}

export const LoadingOverlay: React.FC<LoadingOverlayProps> = ({
  message = 'Loading...'
}) => {
  return (
    <Box
      position="fixed"
      top={0}
      left={0}
      right={0}
      bottom={0}
      bg="blackAlpha.300"
      backdropFilter="blur(2px)"
      display="flex"
      alignItems="center"
      justifyContent="center"
      zIndex={9999}
    >
      <VStack gap={4}>
        <Spinner
          size="xl"
          color="brand.500"
        />
        <Text
          color="gray.700"
          fontSize="lg"
          fontWeight="medium"
        >
          {message}
        </Text>
      </VStack>
    </Box>
  );
};
