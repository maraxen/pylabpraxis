import React from 'react';
import { Box, Text } from '@chakra-ui/react';
import { Card, CardBody } from '@praxis-ui';
import { AssetConfigurationForm } from '../components/assets/AssetConfigurationForm';

interface ProtocolAssetTemplateProps {
  assets: Array<{
    name: string;
    type: string;
    required: boolean;
    description?: string;
  }>;
  availableAssets: {
    [key: string]: Array<{
      name: string;
      type: string;
      is_available: boolean;
      description?: string;
    }>
  };
  deckFiles: string[];
  selectedDeckFile: string;
  onDeckFileChange: (file: string) => void;
  isConfigValid?: boolean;
}

export const ProtocolAssetTemplate: React.FC<ProtocolAssetTemplateProps> = ({
  assets,
  availableAssets,
  deckFiles,
  selectedDeckFile,
  onDeckFileChange,
  isConfigValid
}) => {
  if (isConfigValid) {
    return (
      <Box p={4}>
        <Text>Assets configured from uploaded file</Text>
      </Box>
    );
  }

  return (
    <Card>
      <CardBody>
        <AssetConfigurationForm
          assets={assets}
          availableAssets={availableAssets}
          deckFiles={deckFiles}
          selectedDeckFile={selectedDeckFile}
          onDeckFileChange={onDeckFileChange}
        />
      </CardBody>
    </Card>
  );
}