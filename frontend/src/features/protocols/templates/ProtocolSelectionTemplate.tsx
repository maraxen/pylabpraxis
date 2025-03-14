import React from 'react';
import { VStack, Text, Input, Box } from '@chakra-ui/react';
import { Card, CardBody } from '@/components/ui/card';
import { Field } from '@/components/ui/field';
import { AutoComplete, AutoCompleteInput, AutoCompleteItem, AutoCompleteList } from "@choc-ui/chakra-autocomplete";
import { inputStyles } from '@/styles/form';

interface ProtocolDetails {
  name: string;
  path: string;
  description: string;
  has_assets: boolean;
  has_parameters: boolean;
}

interface ProtocolSelectionTemplateProps {
  selectedProtocol: string | null;
  availableProtocols: ProtocolDetails[];
  protocolDetails: ProtocolDetails | null;
  requiresConfig: boolean;
  configFile: File | null;
  onProtocolSelect: (protocol: ProtocolDetails) => void;
  onConfigFileUpload: (e: React.ChangeEvent<HTMLInputElement>) => void;
}

export const ProtocolSelectionTemplate: React.FC<ProtocolSelectionTemplateProps> = ({
  selectedProtocol,
  availableProtocols,
  protocolDetails,
  requiresConfig,
  configFile,
  onProtocolSelect,
  onConfigFileUpload,
}) => {
  return (
    <Card>
      <CardBody>
        <VStack gap={4}>
          <Field label="Select Protocol" required>
            <AutoComplete
              value={selectedProtocol}
              onChange={(value) => {
                const protocol = availableProtocols.find(p => p.name === value);
                if (protocol) onProtocolSelect(protocol);
              }}
            >
              <AutoCompleteInput placeholder="Choose a protocol..." />
              <AutoCompleteList>
                {availableProtocols.map((protocol) => (
                  <AutoCompleteItem
                    key={`${protocol.path}::${protocol.name}`}
                    value={protocol.name}
                    textTransform="capitalize"
                  >
                    {protocol.name}
                  </AutoCompleteItem>
                ))}
              </AutoCompleteList>
            </AutoComplete>
          </Field>

          {requiresConfig ? (
            <Field label="Configuration File" required>
              <Input
                type="file"
                onChange={onConfigFileUpload}
                accept=".json,.yaml,.yml"
                {...inputStyles}
              />
              <Text fontSize="sm" color="gray.500">
                This protocol requires a configuration file
              </Text>
            </Field>
          ) : (
            <Field label="Configuration File (Optional)">
              <Input
                type="file"
                onChange={onConfigFileUpload}
                accept=".json,.yaml,.yml"
                {...inputStyles}
              />
              <Text fontSize="sm" color="gray.500">
                Upload a configuration file or configure manually
              </Text>
            </Field>
          )}

          {protocolDetails && (
            <Box>
              <Text fontWeight="bold">Protocol Details:</Text>
              <Text>{protocolDetails.description}</Text>
              {protocolDetails.has_assets && (
                <Text color="green.500">✓ Configurable assets available</Text>
              )}
              {protocolDetails.has_parameters && (
                <Text color="green.500">✓ Configurable parameters available</Text>
              )}
            </Box>
          )}
        </VStack>
      </CardBody>
    </Card>
  );
};