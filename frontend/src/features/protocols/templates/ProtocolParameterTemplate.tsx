import React from 'react';
import { Box, Text } from '@chakra-ui/react';
import { Card, CardBody } from '@praxis-ui';
import { ParameterConfigurationForm } from '../components/form/ParameterConfigurationForm';
import type { ParameterConfigurationFormRef } from '../components/form/ParameterConfigurationForm';

interface ProtocolParameterTemplateProps {
  formRef: React.RefObject<ParameterConfigurationFormRef>;
  parameters: Record<string, {
    type: 'string' | 'number' | 'boolean' | 'array' | 'integer' | 'float';
    required?: boolean;
    default?: any;
    description?: string;
    constraints?: {
      min?: number;
      max?: number;
      step?: number;
      options?: string[];
    };
  }>;
  isConfigValid?: boolean;
}

export const ProtocolParameterTemplate: React.FC<ProtocolParameterTemplateProps> = ({
  formRef,
  parameters,
  isConfigValid
}) => {
  if (isConfigValid) {
    return (
      <Box p={4}>
        <Text>Parameters configured from uploaded file</Text>
      </Box>
    );
  }

  return (
    <Card>
      <CardBody>
        <ParameterConfigurationForm
          ref={formRef}
          parameters={parameters}
        />
      </CardBody>
    </Card>
  );
};