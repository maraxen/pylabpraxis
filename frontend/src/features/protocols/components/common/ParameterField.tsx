import React from 'react';
import { Text, Badge, Box } from '@chakra-ui/react';
import { Container } from '@praxis-ui';
import { InputRenderer } from './InputRenderer';
import { ParameterConfig } from '@protocols/types/protocol';

interface ParameterFieldProps {
  name: string;
  config: ParameterConfig;
  value: any;
  onChange: (name: string, value: any) => void;
  onRemove: (name: string, index: number) => void;
}

const ParameterFieldComponent: React.FC<ParameterFieldProps> = ({ name, config, value, onChange, onRemove }) => {
  return (
    <Container solid maxW="container.md" p={4}>
      <Box mb={2}>
        <Text fontSize="lg" fontWeight="semibold">
          {name}
          {config.required && <Badge ml={2} colorScheme="brand" variant="outline">Required</Badge>}
          <Badge ml={2} colorScheme="brand" variant="outline">
            {String(config.type)}
          </Badge>
        </Text>
        {config.description && (
          <Text fontSize="sm" mb={3}>
            {config.description}
          </Text>
        )}
      </Box>
      <Box>
        <InputRenderer
          name={name}
          value={value}
          config={config}
          onChange={onChange}
          useDelayed={true}
          onRemove={onRemove}
        />
      </Box>
    </Container>
  );
};

export const ParameterField = React.memo(ParameterFieldComponent);