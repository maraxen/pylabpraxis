import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  setSelectedProtocol,
  setProtocolDetails,
  setAssetConfig,
  updateAssetConfig,
  updateParameterValue,
  setConfigFile,
  setIsConfigValid,
  setStep,
  setCurrentStep,
  setConfigPath,
  initializeParameters,
  resetParameters,
  resetAssets,
  initializeAssets,
  updateAssetOptions,
} from '@/store/protocolForm/slice';
import { RootState } from '@/store';
import {
  Box,
  Heading,
  VStack,
  Input,
  createListCollection,
  Group,
  Text,
} from '@chakra-ui/react';
import { useToast } from '@chakra-ui/toast';
import { Button } from '@/components/ui/button';
import { Card, CardBody } from '@/components/ui/card';
import { Field } from '@/components/ui/field';
import { LuPlay, LuRefreshCw, LuList, LuSettings } from "react-icons/lu";
import { api } from '@/services/api';  // Add this import
import { inputStyles } from '@/styles/form';
import {
  StepsContent,
  StepsItem,
  StepsList,
  StepsNextTrigger,
  StepsPrevTrigger,
  StepsRoot,
} from "@/components/ui/steps";
import { AssetConfigurationForm } from '@/components/AssetConfigurationForm';
import { ParameterConfigurationForm } from '@/components/ParameterConfigurationForm';
import {
  AutoComplete,
  AutoCompleteInput,
  AutoCompleteItem,
  AutoCompleteList,
} from "@choc-ui/chakra-autocomplete";

interface Protocol {
  name: string;
  path: string;
}

interface RunningProtocol {
  name: string;
  status: string;
}

interface ProtocolDetails {
  name: string;
  path: string;
  description: string;
  requires_config: boolean;
  parameters: Record<string, {
    type: 'string' | 'number' | 'boolean' | 'enum';
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
  assets: Array<{
    name: string;
    type: string;
    required: boolean;
    description?: string;
  }>;
  has_assets: boolean;
  has_parameters: boolean;
}

interface Asset {
  name: string;
  type: string;
  required: boolean;
  description?: string;
  is_available?: boolean;
  options?: string[];
}

interface AssetOption {
  name: string;
  type: string;
  is_available: boolean;
  description?: string;
}

interface AssetConfig {
  [key: string]: string | number;
}

type ConfigurationPath = 'upload' | 'specify';
type SetupStep = 'select' | 'configure' | 'assets' | 'parameters';

interface ProtocolListItem extends Protocol {
  label: string;
  value: string;
}

interface DeckFileItem {
  label: string;
  value: string;
}

interface ParameterConfig {
  type: 'string' | 'number' | 'boolean' | 'enum';
  required?: boolean;
  default?: any;
  description?: string;
  constraints?: {
    min?: number;
    max?: number;
    step?: number;
    options?: string[];
  };
}

export const RunProtocols: React.FC = () => {
  const dispatch = useDispatch();
  const {
    selectedProtocol,
    protocolDetails,
    assetConfig,
    parameterValues,
    configFile,
    isConfigValid,
    step,
  } = useSelector((state: RootState) => state.protocolForm);

  const toast = useToast();

  const [protocols, setProtocols] = useState<Protocol[]>([]);
  const [runningProtocols, setRunningProtocols] = useState<RunningProtocol[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [availableProtocols, setAvailableProtocols] = useState<ProtocolDetails[]>([]);
  const [availableAssets, setAvailableAssets] = useState<{ [key: string]: AssetOption[] }>({});
  const [deckFiles, setDeckFiles] = useState<string[]>([]);
  const [selectedDeckFile, setSelectedDeckFile] = useState<string>('');

  useEffect(() => {
    fetchProtocols();
    fetchRunningProtocols();
    fetchDeckFiles();
    fetchAvailableProtocols();
  }, []);

  useEffect(() => {
    if (selectedProtocol && protocolDetails?.assets) {
      fetchAvailableAssets();
    }
  }, [selectedProtocol, protocolDetails]);

  const fetchProtocols = async () => {
    try {
      const response = await api.get<Protocol[]>('/api/v1/protocols/');
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
      const response = await api.get<RunningProtocol[]>('/api/v1/protocols/running');
      setRunningProtocols(response.data);
    } catch (error) {
      console.error('Error fetching running protocols:', error);
    }
  };

  const fetchDeckFiles = async () => {
    try {
      const response = await api.get<string[]>('/api/v1/protocols/deck_layouts');
      setDeckFiles(response.data);
    } catch (error) {
      console.error('Error fetching deck files:', error);
    }
  };

  const fetchAvailableProtocols = async () => {
    try {
      const response = await api.get<ProtocolDetails[]>('/api/v1/protocols/discover');
      setAvailableProtocols(response.data);
    } catch (error) {
      console.error('Error fetching protocols:', error);
      toast({
        title: 'Error fetching available protocols',
        status: 'error',
        duration: 3000,
      });
    }
  };

  const fetchAvailableAssets = async () => {
    try {
      const assetTypes = new Set(protocolDetails.assets.map((asset: Asset) => asset.type));
      // Fix the map typing by explicitly typing the array
      const assetPromises = Array.from(assetTypes).map((type) => {
        return api.get<AssetOption[]>(`/api/v1/assets/available/${type}`)
          .then(response => [type, response.data] as [string, AssetOption[]]);
      });

      const results = await Promise.all(assetPromises);
      const assetsMap = Object.fromEntries(results);
      setAvailableAssets(assetsMap);
    } catch (error) {
      console.error('Error fetching available assets:', error);
      toast({
        title: 'Error fetching available assets',
        status: 'error',
        duration: 3000,
      });
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
      const configResponse = await api.post('/api/v1/protocols/upload_config_file', formData);
      const configFilePath = configResponse.data;

      // Start protocol
      await api.post('/api/v1/protocols/start', {
        protocol_name: selectedProtocol,
        config_file: configFilePath
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

  const handleProtocolSelect = async (protocol: ProtocolDetails) => {
    // Reset all state
    dispatch(resetParameters());
    dispatch(resetAssets());
    dispatch(setConfigFile(null));
    dispatch(setIsConfigValid(false));
    dispatch(setStep(0));

    dispatch(setSelectedProtocol(protocol.name));

    try {
      const response = await api.get<ProtocolDetails>('/api/v1/protocols/details', {
        params: { protocol_path: protocol.path }
      });

      if (response.data) {
        dispatch(setProtocolDetails(response.data));
        if (response.data.parameters) {
          dispatch(initializeParameters(response.data.parameters));
        }
        if (response.data.assets) {
          dispatch(initializeAssets(response.data.assets));
        }
      }
    } catch (error) {
      console.error('Error fetching protocol details:', error);
      toast({
        title: 'Error fetching protocol details',
        status: 'error',
        duration: 3000,
      });
    }
  };

  const handleConfigFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    dispatch(setConfigFile(file.name));
    try {
      const formData = new FormData();
      formData.append('file', file);
      const response = await api.post('/protocols/upload_config_file', formData);

      // If we have a valid config, we can skip asset and parameter configuration
      dispatch(setIsConfigValid(true));
      dispatch(setConfigPath('upload'));
    } catch (error) {
      console.error('Error uploading config:', error);
      dispatch(setIsConfigValid(false));
      toast({
        title: 'Error uploading configuration file',
        status: 'error',
        duration: 3000,
      });
    }
  };

  const handleAssetChange = (assetName: string, value: string) => {
    dispatch(updateAssetConfig({ name: assetName, value }));
  };

  const handleParameterChange = (name: string, value: any) => {
    dispatch(updateParameterValue({ name, value }));
  };

  const isStepValid = (stepIndex: number): boolean => {
    switch (stepIndex) {
      case 0: // Protocol Selection
        if (!selectedProtocol) return false;
        if (protocolDetails?.requires_config) return !!configFile;
        return true;

      case 1: // Parameter Configuration
        if (isConfigValid) return true;
        if (!protocolDetails?.parameters) return true;
        return Object.entries<ParameterConfig>(protocolDetails.parameters)
          .filter(([_, config]) => config.required)
          .every(([name]) => parameterValues[name] !== undefined);

      case 2: // Asset Configuration
        if (isConfigValid) return true;
        if (!protocolDetails?.assets) return true;
        const hasRequiredAssets = protocolDetails.assets
          .filter((asset: Asset) => asset.required)
          .every((asset: Asset) => assetConfig[asset.name]);
        return hasRequiredAssets && !!selectedDeckFile;

      case 3: // Review
        return isStepValid(0) && isStepValid(1) && isStepValid(2);

      default:
        return false;
    }
  };

  const handleStepChange = (details: { step: number }) => {
    // Only allow moving to next step if current step is valid
    if (details.step > step && !isStepValid(step)) {
      toast({
        title: 'Invalid Step',
        description: 'Please complete all required fields before proceeding',
        status: 'error',
        duration: 3000,
      });
      return;
    }
    dispatch(setStep(details.step));
  };

  return (
    <VStack align="stretch" gap={6}>
      <Heading size="lg">Run Protocols</Heading>

      <StepsRoot
        step={step}
        onStepChange={handleStepChange}
        count={4}
        colorPalette="brand"
        size="lg"
      >
        <StepsList>
          <StepsItem
            index={0}
            title="Select Protocol"
            icon={<LuList />}
            description="Choose a protocol to run"
          />
          <StepsItem
            index={1}
            title="Set Parameters"
            icon={<LuSettings />}
            description="Configure protocol parameters"
          />
          <StepsItem
            index={2}
            title="Configure Assets"
            icon={<LuSettings />}
            description="Set up required resources"
          />
          <StepsItem
            index={3}
            title="Review & Start"
            icon={<LuPlay />}
            description="Review and start protocol"
          />
        </StepsList>

        <StepsContent index={0}>
          <Card>
            <CardBody>
              <VStack gap={4}>
                <Field label="Select Protocol" required>
                  <AutoComplete
                    value={selectedProtocol}
                    onChange={(value) => {
                      const protocol = availableProtocols.find(p => p.name === value);
                      if (protocol) handleProtocolSelect(protocol);
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

                {protocolDetails?.requires_config ? (
                  <Field label="Configuration File" required>
                    <Input
                      type="file"
                      onChange={handleConfigFileUpload}
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
                      onChange={handleConfigFileUpload}
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
        </StepsContent>

        <StepsContent index={1}>
          {isConfigValid ? (
            <Box p={4}>
              <Text>Parameters configured from uploaded file</Text>
            </Box>
          ) : (
            <Card>
              <CardBody>
                <ParameterConfigurationForm
                  parameters={protocolDetails?.parameters || {}}
                />
              </CardBody>
            </Card>
          )}
        </StepsContent>

        <StepsContent index={2}>
          {isConfigValid ? (
            <Box p={4}>
              <Text>Assets configured from uploaded file</Text>
            </Box>
          ) : (
            <Card>
              <CardBody>
                <AssetConfigurationForm
                  assets={protocolDetails?.assets || []}
                  deckFiles={deckFiles}
                  selectedDeckFile={selectedDeckFile}
                  onDeckFileChange={setSelectedDeckFile}
                />
              </CardBody>
            </Card>
          )}
        </StepsContent>

        <StepsContent index={3}>
          <Card>
            <CardBody>
              <VStack gap={4}>
                {/* Review summary */}
                <Button
                  type="submit"
                  visual="solid"
                  loading={isLoading}
                  width="full"
                  onClick={handleStartProtocol}
                >
                  <LuPlay />Start Protocol
                </Button>
              </VStack>
            </CardBody>
          </Card>
        </StepsContent>

        <Group justify="space-between" mt={4}>
          <StepsPrevTrigger asChild>
            <Button
              visual="outline"
              size="sm"
              disabled={step === 0}
            >
              Previous
            </Button>
          </StepsPrevTrigger>
          <StepsNextTrigger asChild>
            <Button
              visual="solid"
              size="sm"
              disabled={!isStepValid(step)}
            >
              {step === 3 ? 'Start' : 'Next'}
            </Button>
          </StepsNextTrigger>
        </Group>
      </StepsRoot>

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
