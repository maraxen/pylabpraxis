import React, { useState, useEffect } from 'react';
import {
  Box,
  Heading,
  VStack,
  Input,
  createListCollection,
  Group,
  Stack,
  Text,
} from '@chakra-ui/react';
import { useToast } from '@chakra-ui/toast';
import { Button } from '@/components/ui/button';
import { Card, CardBody } from '@/components/ui/card';
import {
  SelectRoot,
  SelectItem,
  SelectContent,
  SelectTrigger,
  SelectValueText
} from "@/components/ui/select";
import { Fieldset, FieldsetContent, FieldsetLegend } from '@/components/ui/fieldset';
import { Field } from '@/components/ui/field';
import { Checkbox } from '@/components/ui/checkbox';
import { LuPlay, LuRefreshCw, LuUpload, LuSettings, LuList } from "react-icons/lu";
import { api } from '@/services/api';
import { useOidc } from '@/oidc';
import { inputStyles, checkboxStyles } from '@/styles/form';
import {
  StepsCompletedContent,
  StepsContent,
  StepsItem,
  StepsList,
  StepsNextTrigger,
  StepsPrevTrigger,
  StepsRoot,
} from "@/components/ui/steps";
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

// Add new helper function
const filterProtocols = (protocols: ProtocolDetails[], searchTerm: string) => {
  const term = searchTerm.toLowerCase();
  return protocols.filter(p =>
    p.name.toLowerCase().includes(term) ||
    p.description.toLowerCase().includes(term)
  );
};

export const RunProtocols: React.FC = () => {
  const [protocols, setProtocols] = useState<Protocol[]>([]);
  const [runningProtocols, setRunningProtocols] = useState<RunningProtocol[]>([]);
  const [selectedProtocol, setSelectedProtocol] = useState<string>('');
  const [configFile, setConfigFile] = useState<File | null>(null);
  const [deckFiles, setDeckFiles] = useState<string[]>([]);
  const [selectedDeckFile, setSelectedDeckFile] = useState<string>('');
  const [liquidHandler, setLiquidHandler] = useState('');
  const [manualCheck, setManualCheck] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const toast = useToast();
  const { oidcTokens } = useOidc();
  const [availableProtocols, setAvailableProtocols] = useState<ProtocolDetails[]>([]);
  const [configPath, setConfigPath] = useState<ConfigurationPath | null>(null);
  const [currentStep, setCurrentStep] = useState<SetupStep>('select');
  const [protocolDetails, setProtocolDetails] = useState<any>(null);
  const [step, setStep] = useState(0);
  const [isConfigValid, setIsConfigValid] = useState(false);
  const [assets, setAssets] = useState<Asset[]>([]);
  const [assetConfig, setAssetConfig] = useState<AssetConfig>({});
  const [availableAssets, setAvailableAssets] = useState<{ [key: string]: AssetOption[] }>({});
  const [searchTerm, setSearchTerm] = useState('');
  const [isSelectOpen, setIsSelectOpen] = useState(false);
  const searchInputRef = React.useRef<HTMLInputElement>(null);
  const searchContainerRef = React.useRef<HTMLDivElement>(null);

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

  // Add this effect to maintain focus
  useEffect(() => {
    if (isSelectOpen && searchInputRef.current) {
      searchInputRef.current.focus();
    }
  }, [isSelectOpen]);

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
      if (!response?.data) {
        throw new Error('No data received from server');
      }
      setAvailableProtocols(response.data);
    } catch (error) {
      console.error('Error fetching protocols:', error);
      toast({
        title: 'Error fetching available protocols',
        description: error instanceof Error ? error.message : 'Failed to load protocols',
        status: 'error',
        duration: 3000,
      });
      setAvailableProtocols([]);
    }
  };

  const fetchAvailableAssets = async () => {
    try {
      const assetTypes = new Set(protocolDetails.assets.map((asset: Asset) => asset.type));
      const assetPromises = Array.from(assetTypes).map(async (type) => {
        const response = await api.get<AssetOption[]>(`/api/v1/assets/available/${type}`);
        return [type, response.data];
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

  const handleProtocolSelect = async (protocol: ProtocolDetails) => {
    setSelectedProtocol(protocol.name);
    try {
      const response = await api.get('/api/v1/protocols/details', {
        params: { protocol_path: protocol.path }
      });
      setProtocolDetails(response.data);
    } catch (error) {
      console.error('Error fetching protocol details:', error);
      toast({
        title: 'Error fetching protocol details',
        status: 'error',
        duration: 3000,
      });
    }
  };

  const handleConfigPathSelect = (path: ConfigurationPath) => {
    setConfigPath(path);
    setCurrentStep(path === 'upload' ? 'configure' : 'assets');
  };

  const handleConfigFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setConfigFile(file);
    try {
      const formData = new FormData();
      formData.append('file', file);
      const response = await api.post('/protocols/upload_config_file', formData);

      // If we have a valid config, we can skip asset and parameter configuration
      setIsConfigValid(true);
      setConfigPath('upload');
    } catch (error) {
      console.error('Error uploading config:', error);
      setIsConfigValid(false);
      toast({
        title: 'Error uploading configuration file',
        status: 'error',
        duration: 3000,
      });
    }
  };

  const handleAssetChange = (assetName: string, value: string) => {
    setAssetConfig(prev => ({
      ...prev,
      [assetName]: value
    }));
  };

  const canProceed = () => {
    if (step === 0) return selectedProtocol;
    if (step === 1) {
      if (isConfigValid) return true;
      if (!protocolDetails?.assets) return true;
      return protocolDetails.assets.every((asset: Asset) =>
        !asset.required || assetConfig[asset.name]
      );
    }
    if (step === 2) return isConfigValid || (configPath === 'specify' && protocolDetails?.parameters);
    return true;
  };

  // Create collections for select components
  const protocolsCollection = createListCollection({
    items: protocols.map(protocol => ({
      label: protocol.name,
      value: protocol.name
    }))
  });

  const deckFilesCollection = createListCollection({
    items: deckFiles.map(file => ({
      label: file,
      value: file
    }))
  });

  const handleSelectChange = (event: { value: string[] }) => {
    const protocol = availableProtocols.find(p => p.path === event.value[0]);
    if (protocol) {
      handleProtocolSelect(protocol);
      setIsSelectOpen(false);
    }
  };

  const handleSearchClick = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setSearchTerm(e.target.value);
  };

  const getStepProps = (index: number) => {
    if (index === 0) return {}; // First step always enabled

    return {
      disabled: !selectedProtocol,
      description: !selectedProtocol ? "Select a protocol first" : "Protocol selected"
    };
  };

  return (
    <VStack align="stretch" gap={6}>
      <Heading size="lg">Run Protocols</Heading>

      <StepsRoot
        step={step}
        onStepChange={(e) => {
          // Only allow step change if enabled
          if (!selectedProtocol && e.step > 0) return;
          setStep(e.step);
        }}
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
            title="Configure Assets"
            icon={<LuSettings />}
            {...getStepProps(1)}
          />
          <StepsItem
            index={2}
            title="Set Parameters"
            icon={<LuSettings />}
            {...getStepProps(2)}
          />
          <StepsItem
            index={3}
            title="Review & Start"
            icon={<LuPlay />}
            {...getStepProps(3)}
          />
        </StepsList>

        <StepsContent index={0}>
          <Card>
            <CardBody>
              <VStack gap={4}>
                <Field label="Select Protocol" required>
                  <AutoComplete
                    openOnFocus
                    onChange={(value) => {
                      const protocol = availableProtocols.find(p => p.path === value);
                      if (protocol) {
                        handleProtocolSelect(protocol);
                      }
                    }}
                  >
                    <AutoCompleteInput
                      variant="outline"
                      placeholder="Choose a protocol..."
                      disabled={isLoading}
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                    />
                    <AutoCompleteList>
                      {filterProtocols(availableProtocols, searchTerm).map((protocol) => (
                        <AutoCompleteItem
                          key={protocol.path}
                          value={protocol.path}
                          textTransform="capitalize"
                        >
                          <Stack gap={0}>
                            <Text>{protocol.name}</Text>
                            <Text fontSize="xs" color="gray.500">
                              {protocol.path}
                            </Text>
                          </Stack>
                        </AutoCompleteItem>
                      ))}
                    </AutoCompleteList>
                  </AutoComplete>
                </Field>

                <Field label="Configuration File (Optional)">
                  <Input
                    type="file"
                    onChange={handleConfigFileUpload}
                    accept=".json,.yaml,.yml"
                    {...inputStyles}
                  />
                  <Text fontSize="sm" color="gray.500">
                    Upload a configuration file to skip manual setup
                  </Text>
                </Field>
              </VStack>
            </CardBody>
          </Card>
        </StepsContent>

        <StepsContent index={1}>
          {isConfigValid ? (
            <Box p={4}>
              <Text>Assets configured from uploaded file</Text>
            </Box>
          ) : (
            <Card>
              <CardBody>
                <VStack gap={4}>
                  {protocolDetails?.assets?.map((asset: Asset) => (
                    <Field
                      key={asset.name}
                      label={asset.name}
                      required={asset.required}
                      helperText={asset.description}
                    >
                      <SelectRoot
                        collection={createListCollection({
                          items: (availableAssets[asset.type] || []).map(item => ({
                            label: `${item.name}${item.description ? ` - ${item.description}` : ''}`,
                            value: item.name,
                            disabled: !item.is_available
                          }))
                        })}
                        value={[assetConfig[asset.name] as string]}
                        onChange={(event) => handleAssetChange(asset.name, event.value[0])}
                      >
                        <SelectTrigger>
                          <SelectValueText placeholder={`Select ${asset.name}...`} />
                        </SelectTrigger>
                        <SelectContent>
                          {(availableAssets[asset.type] || []).map((item) => (
                            <SelectItem
                              key={item.name}
                              item={{
                                value: item.name,
                                label: `${item.name}${item.description ? ` - ${item.description}` : ''}`
                              }}
                            >
                              <Group gap={2}>
                                <Text>{item.name}</Text>
                                {!item.is_available && (
                                  <Text textStyle="sm" color="gray.500">(In use)</Text>
                                )}
                              </Group>
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </SelectRoot>
                    </Field>
                  ))}
                </VStack>
              </CardBody>
            </Card>
          )}
        </StepsContent>

        <StepsContent index={2}>
          {isConfigValid ? (
            <Box p={4}>
              <Text>Parameters configured from uploaded file</Text>
            </Box>
          ) : (
            <Card>
              <CardBody>
                {/* Parameter configuration form - to be implemented */}
                <Text>Parameter configuration coming soon</Text>
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
            <Button visual="outline" size="sm">Previous</Button>
          </StepsPrevTrigger>
          <StepsNextTrigger asChild>
            <Button
              visual="solid"
              size="sm"
              disabled={!canProceed() || (!selectedProtocol && step === 0)}
            >
              Next
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
