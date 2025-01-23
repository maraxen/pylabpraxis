import React from 'react';
import { Box, Heading, VStack, Button, Card } from '@chakra-ui/react';
import { LuPlay } from "react-icons/lu";

export const RunProtocols: React.FC = () => {
  return (
    <VStack align="stretch" gap={6}>
      <Heading size="lg">Run Protocols</Heading>
      <Card.Root>
        <Card.Body>
          <Button colorScheme="brand">
            <LuPlay />
            Start New Protocol
          </Button>
        </Card.Body>
      </Card.Root>
    </VStack>
  );
};
