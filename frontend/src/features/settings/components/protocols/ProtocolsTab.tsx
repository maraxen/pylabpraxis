import React from 'react';
import { VStack, HStack, Text } from '@chakra-ui/react';
import { Button, Card, CardBody, Fieldset, FieldsetContent, FieldsetLegend } from "@atoms";

interface ProtocolsTabProps {
  directories: string[];
  onRemove: (dir: string) => void;
  onAdd: () => void;
}

const ProtocolsTab: React.FC<ProtocolsTabProps> = ({ directories, onRemove, onAdd }) => (
  <Card>
    <CardBody>
      <Fieldset>
        <FieldsetLegend>Protocol Directories</FieldsetLegend>
        <FieldsetContent>
          <VStack align="stretch" gap={4}>
            {directories.map((dir) => (
              <HStack key={dir} justify="space-between">
                <Text>{dir}</Text>
                <Button
                  size="sm"
                  visual="ghost"
                  color={{ base: 'brand.300', _dark: 'brand.100' }}
                  _hover={{
                    color: { base: 'white', _dark: 'brand.50' },
                    bg: { base: 'brand.300', _dark: 'brand.800' },
                  }}
                  onClick={() => onRemove(dir)}
                >
                  Remove
                </Button>
              </HStack>
            ))}
            <Button
              visual="outline"
              color={{ base: 'brand.300', _dark: 'brand.100' }}
              borderColor={{ base: 'brand.300', _dark: 'brand.100' }}
              _hover={{
                color: { base: 'white', _dark: 'brand.50' },
                bg: { base: 'brand.300', _dark: 'brand.800' },
              }}
              onClick={onAdd}
            >
              Add Directory
            </Button>
          </VStack>
        </FieldsetContent>
      </Fieldset>
    </CardBody>
  </Card>
);

export default ProtocolsTab;