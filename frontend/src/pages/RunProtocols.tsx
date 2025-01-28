import React, { useState, useEffect } from 'react';
import {
  Box,
  Heading,
  VStack,
  Input,
  Checkbox,
  For,
  createListCollection
} from '@chakra-ui/react';
import { useToast } from '@chakra-ui/toast';
import { Button } from '@/components/ui/button';
import { Card, CardBody } from '@/components/ui/card';
import { SelectRoot, SelectItem, SelectContent, SelectTrigger, SelectValueText } from "@/components/ui/select";
import { Fieldset, FieldsetContent, FieldsetLegend } from '@/components/ui/fieldset';
import { Field } from '@/components/ui/field';
import { LuPlay, LuRefreshCw } from "react-icons/lu";
import { api } from '@/services/api';
import { useOidc } from '@/oidc';
import { inputStyles, selectStyles, checkboxStyles, formControlStyles } from '@/styles/form';

interface Protocol {
  name: string;
  // Add other protocol properties as needed
}

interface RunningProtocol {
  name: string;
  status: string;
}

export const RunProtocols: React.FC = () => {
  const [protocols, setProtocols] = useState<Protocol[]>([]);
  const [runningProtocols, setRunningProtocols] = useState<RunningProtocol[]>([]);
  const [selectedProtocol, setSelectedProtocol] = useState<string[]>([]);
  const [configFile, setConfigFile] = useState<File | null>(null);
  const [deckFiles, setDeckFiles] = useState<string[]>([]);
  const [selectedDeckFile, setSelectedDeckFile] = useState('');
  const [liquidHandler, setLiquidHandler] = useState('');
  const [manualCheck, setManualCheck] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const toast = useToast();
  const { oidcTokens } = useOidc();

  useEffect(() => {
    fetchProtocols();
    fetchRunningProtocols();
    fetchDeckFiles();
  }, []);



  const fetchProtocols = async () => {
    try {
      const response = await api.get<Protocol[]>('/protocols/');
      setProtocols(response.data);
    } catch (error) {
      console.error('Error fetching protocols:', error);
      toast({
        title: 'Error fetching protocols',
        status: 'error',
        duration: 3000,
      });
    }
  };

  const fetchRunningProtocols = async () => {
    try {
      const response = await api.get<RunningProtocol[]>('/protocols/running');
      setRunningProtocols(response.data);
    } catch (error) {
      console.error('Error fetching running protocols:', error);
    }
  };

  const fetchDeckFiles = async () => {
    try {
      const response = await api.get<string[]>('/protocols/deck_layouts');
      setDeckFiles(response.data);
    } catch (error) {
      console.error('Error fetching deck files:', error);
    }
  };

  const handleStartProtocol = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedProtocol || !configFile || !selectedDeckFile) {
      toast({
        title: 'Missing required fields',
        status: 'error',
        duration: 3000,
      });
      return;
    }

    setIsLoading(true);
    try {
      const formData = new FormData();
      formData.append('file', configFile);

      // Upload config file
      const configResponse = await api.post('/protocols/upload_config_file', formData);
      const configFilePath = configResponse.data;

      // Start protocol
      await api.post('/protocols/start', {
        protocol_name: selectedProtocol[0],
        config_file: configFilePath,
        deck_file: `./protocol/deck_layouts/${selectedDeckFile}`,
        liquid_handler_name: liquidHandler,
        manual_check_list: manualCheck ? ['Manual check required'] : []
      });

      toast({
        title: 'Protocol started successfully',
        status: 'success',
        duration: 3000,
      });

      // Refresh running protocols
      fetchRunningProtocols();
    } catch (error) {
      toast({
        title: 'Failed to start protocol',
        description: error instanceof Error ? error.message : 'Unknown error',
        status: 'error',
        duration: 5000,
      });
    } finally {
      setIsLoading(false);
    }
  };

  const protocolsCollection = createListCollection({
    items: protocols.map(protocol => ({
      label: protocol.name,
      value: protocol.name
    }))
  });

  return (
    <VStack align="stretch" gap={6}>
      <Heading size="lg">Run Protocols</Heading>
      <Card>
        <CardBody>
          <form onSubmit={handleStartProtocol}>
            <Fieldset>
              <FieldsetLegend>Protocol Configuration</FieldsetLegend>
              <FieldsetContent>
                <VStack gap={4}>
                  <Field label="Select Protocol" required>
                    <SelectRoot collection={protocolsCollection} onChange={(value) => setSelectedProtocol(value)}>
                      <SelectTrigger>
                        <SelectValueText placeholder="Choose a protocol..." />
                      </SelectTrigger>
                      <SelectContent>
                        {protocols.map((protocol) => (
                          <SelectItem key={protocol.name} value={protocol.name}>
                            {protocol.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </SelectRoot>
                  </Field>

                  <Field label="Configuration File" required>
                    <Input
                      type="file"
                      onChange={(e) => setConfigFile(e.target.files?.[0] || null)}
                      accept=".json,.yaml,.yml"
                      {...inputStyles}
                    />
                  </Field>

                  <Field label="Deck Layout" required>
                    <SelectRoot value={selectedDeckFile} onValueChange={setSelectedDeckFile}>
                      <SelectTrigger>
                        <SelectValueText placeholder="Select deck layout..." />
                      </SelectTrigger>
                      <SelectContent>
                        {deckFiles.map((file) => (
                          <SelectItem key={file} value={file}>
                            {file}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </SelectRoot>
                  </Field>

                  <Field label="Liquid Handler" required>
                    <Input
                      value={liquidHandler}
                      onChange={(e) => setLiquidHandler(e.target.value)}
                      placeholder="Enter liquid handler name"
                      {...inputStyles}
                    />
                  </Field>

                  <Box pt={2}>
                    <Checkbox
                      isChecked={manualCheck}
                      onChange={(e) => setManualCheck(e.target.checked)}
                      {...checkboxStyles}
                    >
                      Require Manual Check
                    </Checkbox>
                  </Box>

                  <Button
                    type="submit"
                    visual="solid"
                    loading={isLoading}
                    width="full"
                  >
                    <LuPlay />Start Protocol
                  </Button>
                </VStack>
              </FieldsetContent>
            </Fieldset>
          </form>
        </CardBody>
      </Card>

      <Card>
        <CardBody>
          <Heading size="md" mb={4}>
            Running Protocols
            <Button
              size="sm"
              ml={4}
              onClick={fetchRunningProtocols}
              visual="ghost"
            >
              <LuRefreshCw />Refresh
            </Button>
          </Heading>
          <VStack align="stretch">
            {runningProtocols.map((protocol) => (
              <Box
                key={protocol.name}
                p={4}
                borderWidth={1}
                borderRadius="md"
                display="flex"
                justifyContent="space-between"
                alignItems="center"
              >
                <Box>
                  {protocol.name}
                  <Box as="span" ml={2} color="gray.500"></Box>
                  (Status: {protocol.status})
                </Box>
              </Box>
            ))}
          </VStack>
        </CardBody>
      </Card>
    </VStack >
  );
};
