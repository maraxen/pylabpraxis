import React, { useState, useEffect, useMemo } from 'react';
import {
  Box,
  Heading,
  Tabs,
  Tab,
  TabList,
  TabPanel,
  TabPanels,
  Divider,
  Input,
  InputGroup,
  InputLeftElement,
  Flex,
  Text,
  Button,
  useDisclosure,
  SimpleGrid,
  Spinner,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  Grid,
  GridItem,
} from '@chakra-ui/react';
import { Container } from '@shared/components/ui/container';
import { FiSearch, FiPlus } from 'react-icons/fi';
import { ResourceForm } from '../components/ResourceForm';
import { MachineForm } from '../components/MachineForm';
import { AssetCard } from '../AssetCard';
import { AssetList } from '../AssetList';
import { AssetDetails } from '../components/AssetDetails';
import { Asset } from '../types/asset';
import { ResourceTypeInfo, MachineTypeInfo, ResourceCategoriesResponse } from '../types/plr-resources';
import {
  fetchResourceTypes,
  fetchMachineTypes,
  fetchResourceCategories,
  searchAssets,
  fetchAssetsByType,
  fetchAssetDetails,
} from '../api/assets-api';

enum AssetTabType {
  SEARCH = 0,
  ADD_RESOURCE = 1,
  ADD_MACHINE = 2,
}

export const AssetManagement: React.FC = () => {
  const [resourceTypes, setResourceTypes] = useState<Record<string, ResourceTypeInfo>>({});
  const [machineTypes, setMachineTypes] = useState<Record<string, MachineTypeInfo>>({});
  const [resourceCategories, setResourceCategories] = useState<ResourceCategoriesResponse>({
    categories: {
      Containers: [], Carriers: [], Tips: [], Plates: [], Other: []
    }
  });

  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<Asset[]>([]);
  const [selectedAsset, setSelectedAsset] = useState<Asset | null>(null);
  const [selectedAssetDetails, setSelectedAssetDetails] = useState<Asset | null>(null);

  const [isLoading, setIsLoading] = useState(true);
  const [isLoadingDetails, setIsLoadingDetails] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState(AssetTabType.SEARCH);

  // Load initial data
  useEffect(() => {
    async function loadData() {
      setIsLoading(true);
      setError(null);
      try {
        const [resourceTypesData, machineTypesData, categoriesData] = await Promise.all([
          fetchResourceTypes(),
          fetchMachineTypes(),
          fetchResourceCategories(),
        ]);

        setResourceTypes(resourceTypesData);
        setMachineTypes(machineTypesData);
        setResourceCategories(categoriesData);

        // Load initial assets
        const initialAssets = await fetchAssetsByType('');
        setSearchResults(initialAssets);
      } catch (err) {
        setError(`Failed to load asset data: ${err instanceof Error ? err.message : String(err)}`);
      } finally {
        setIsLoading(false);
      }
    }

    loadData();
  }, []);

  // Fetch asset details when selection changes
  useEffect(() => {
    async function fetchDetails() {
      if (selectedAsset) {
        setIsLoadingDetails(true);
        try {
          const details = await fetchAssetDetails(selectedAsset.name);
          setSelectedAssetDetails(details);
        } catch (err) {
          setError(`Failed to fetch asset details: ${err instanceof Error ? err.message : String(err)}`);
          setSelectedAssetDetails(selectedAsset); // Fall back to basic info
        } finally {
          setIsLoadingDetails(false);
        }
      } else {
        setSelectedAssetDetails(null);
      }
    }

    fetchDetails();
  }, [selectedAsset]);

  // Handle search
  const handleSearch = async () => {
    setIsLoading(true);
    setError(null);

    try {
      let results: Asset[];
      if (searchQuery.trim()) {
        results = await searchAssets(searchQuery.trim());
      } else {
        results = await fetchAssetsByType('');
      }
      setSearchResults(results);
    } catch (err) {
      setError(`Search failed: ${err instanceof Error ? err.message : String(err)}`);
    } finally {
      setIsLoading(false);
    }
  };

  // Handle enter key in search input
  const handleSearchKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  // Handle asset creation success
  const handleAssetCreated = async (name: string) => {
    // Reset search and update results
    setSearchQuery('');
    try {
      const allAssets = await fetchAssetsByType('');
      setSearchResults(allAssets);
      setActiveTab(AssetTabType.SEARCH); // Switch back to search tab

      // Find and select the newly created asset
      const newAsset = allAssets.find(asset => asset.name === name);
      if (newAsset) {
        setSelectedAsset(newAsset);
      }
    } catch (err) {
      setError(`Failed to refresh assets: ${err instanceof Error ? err.message : String(err)}`);
    }
  };

  // Handle asset deletion
  const handleAssetDelete = async (asset: Asset) => {
    // TODO: Implement asset deletion functionality
    alert(`Delete functionality for asset ${asset.name} will be implemented in a future update.`);
  };

  return (
    <Container maxWidth="container.xl">
      <Heading size="lg" mb={6}>Asset Management</Heading>

      <Tabs index={activeTab} onChange={(index) => setActiveTab(index)}>
        <TabList>
          <Tab>Search Assets</Tab>
          <Tab>Add Resource</Tab>
          <Tab>Add Machine</Tab>
        </TabList>

        <TabPanels>
          {/* Search Assets Tab */}
          <TabPanel>
            {error && (
              <Alert status="error" mb={4}>
                <AlertIcon />
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            {isLoading ? (
              <Flex justify="center" align="center" my={8}>
                <Spinner size="lg" />
              </Flex>
            ) : (
              <Grid templateColumns={{ base: '1fr', lg: '1fr 1fr' }} gap={6}>
                {/* Asset List */}
                <GridItem>
                  <Box mb={6}>
                    <InputGroup>
                      <InputLeftElement pointerEvents='none'>
                        <FiSearch color='gray.300' />
                      </InputLeftElement>
                      <Input
                        placeholder='Search assets...'
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        onKeyUp={handleSearchKeyPress}
                      />
                      <Button ml={2} onClick={handleSearch}>Search</Button>
                  </Box>
                </Box>

                {searchResults.length > 0 ? (
                  <AssetList
                    assets={searchResults}
                    selectedAssetId={selectedAsset?.name}
                    onAssetSelect={setSelectedAsset}
                  />
                ) : (
                  <Box textAlign="center" py={10}>
                    <Text fontSize="lg" color="gray.500">No assets found</Text>
                    <Button
                      mt={4}
                      leftIcon={<FiPlus />}
                      onClick={() => setActiveTab(AssetTabType.ADD_RESOURCE)}
                    >
                      Add New Asset
                    </Button>
                  </Box>
                )}
              </GridItem>

                {/* Asset Details */}
            <GridItem display={{ base: selectedAsset ? 'block' : 'none', lg: 'block' }}>
              {selectedAssetDetails ? (
                <AssetDetails
                  asset={selectedAssetDetails}
                  onDelete={handleAssetDelete}
                />
              ) : (
                <Box
                  borderWidth="1px"
                  borderRadius="lg"
                  p={6}
                  bg="gray.50"
                  height="100%"
                  display="flex"
                  flexDirection="column"
                  justifyContent="center"
                  alignItems="center"
                >
                  {isLoadingDetails ? (
                    <Spinner size="lg" />
                  ) : (
                    <>
                      <Text fontSize="lg" color="gray.500" textAlign="center">
                        Select an asset to view its details
                      </Text>
                      <Button
                        mt={4}
                        leftIcon={<FiPlus />}
                        onClick={() => setActiveTab(AssetTabType.ADD_RESOURCE)}
                      >
                        Add New Asset
                      </Button>
                    </>
                  )}
                </Box>
              )}
            </GridItem>
          </Grid>
            )}
        </TabPanel>

        {/* Add Resource Tab */}
        <TabPanel>
          {isLoading ? (
            <Flex justify="center" align="center" my={8}>
              <Spinner size="lg" />
            </Flex>
          ) : (
            <ResourceForm
              resourceTypes={resourceTypes}
              categories={resourceCategories.categories}
              onSuccess={handleAssetCreated}
            />
          )}
        </TabPanel>

        {/* Add Machine Tab */}
        <TabPanel>
          {isLoading ? (
            <Flex justify="center" align="center" my={8}>
              <Spinner size="lg" />
            </Flex>
          ) : (
            <MachineForm
              machineTypes={machineTypes}
              onSuccess={handleAssetCreated}
            />
          )}
        </TabPanel>
      </TabPanels>
    </Tabs>
    </Container >
  );
};