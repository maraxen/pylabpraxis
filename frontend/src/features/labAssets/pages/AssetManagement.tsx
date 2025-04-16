import React, { useState, useEffect } from 'react';
import {
  Box,
  Heading,
  Flex,
  Text,
  Spinner,
  Grid,
  GridItem,
  Input,
} from '@chakra-ui/react';
import { Container } from '@shared/components/ui/container';
import {
  Tabs,
  TabList,
  TabTrigger,
  TabContent,
  Button as CustomButton,
} from '@shared/components/ui';
import { Alert as ChakraAlert } from '@chakra-ui/react';
import { InputGroup } from '@shared/components/ui/input-group';
import { FiSearch, FiPlus } from 'react-icons/fi';
import { ResourceForm } from '../components/ResourceForm';
import { MachineForm } from '../components/MachineForm';
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
  SEARCH = 'search',
  ADD_RESOURCE = 'add_resource',
  ADD_MACHINE = 'add_machine',
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
  const [activeTab, setActiveTab] = useState<AssetTabType>(AssetTabType.SEARCH);

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

  useEffect(() => {
    async function fetchDetails() {
      if (selectedAsset) {
        setIsLoadingDetails(true);
        try {
          const details = await fetchAssetDetails(selectedAsset.name);
          setSelectedAssetDetails(details);
        } catch (err) {
          setError(`Failed to fetch asset details: ${err instanceof Error ? err.message : String(err)}`);
          setSelectedAssetDetails(selectedAsset);
        } finally {
          setIsLoadingDetails(false);
        }
      } else {
        setSelectedAssetDetails(null);
      }
    }

    fetchDetails();
  }, [selectedAsset]);

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

  const handleSearchKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  const handleAssetCreated = async (name: string) => {
    setSearchQuery('');
    try {
      const allAssets = await fetchAssetsByType('');
      setSearchResults(allAssets);
      setActiveTab(AssetTabType.SEARCH);

      const newAsset = allAssets.find(asset => asset.name === name);
      if (newAsset) {
        setSelectedAsset(newAsset);
      }
    } catch (err) {
      setError(`Failed to refresh assets: ${err instanceof Error ? err.message : String(err)}`);
    }
  };

  const handleAssetDelete = async (asset: Asset) => {
    alert(`Delete functionality for asset ${asset.name} will be implemented in a future update.`);
  };

  return (
    <Container maxWidth="container.xl">
      <Heading size="lg" mb={6}>Asset Management</Heading>

      <Tabs value={activeTab} onChange={({ value }) => setActiveTab(value as AssetTabType)}>
        <TabList>
          <TabTrigger value={AssetTabType.SEARCH}>Search Assets</TabTrigger>
          <TabTrigger value={AssetTabType.ADD_RESOURCE}>Add Resource</TabTrigger>
          <TabTrigger value={AssetTabType.ADD_MACHINE}>Add Machine</TabTrigger>
        </TabList>

        <TabContent value={AssetTabType.SEARCH}>
          {error && (
            <ChakraAlert.Root status="error" style={{ marginBottom: '1rem' }}>
              <ChakraAlert.Indicator />
              <ChakraAlert.Content>
                <ChakraAlert.Title>Error</ChakraAlert.Title>
                <ChakraAlert.Description>{error}</ChakraAlert.Description>
              </ChakraAlert.Content>
            </ChakraAlert.Root>
          )}

          {isLoading ? (
            <Flex justify="center" align="center" my={8}>
              <Spinner size="lg" />
            </Flex>
          ) : (
            <Grid templateColumns={{ base: '1fr', lg: '1fr 1fr' }} gap={6}>
              <GridItem>
                <Box mb={6} display="flex" alignItems="center">
                  <InputGroup
                    flex="1"
                    startElement={<FiSearch color="gray.300" />}
                  >
                    <Input
                      placeholder="Search assets..."
                      value={searchQuery}
                      onChange={(e: React.ChangeEvent<HTMLInputElement>) => setSearchQuery(e.target.value)}
                      onKeyUp={handleSearchKeyPress}
                    />
                  </InputGroup>
                  <CustomButton ml={2} onClick={handleSearch}>
                    Search
                  </CustomButton>
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
                    <CustomButton mt={4} onClick={() => setActiveTab(AssetTabType.ADD_RESOURCE)}>
                      <FiPlus style={{ marginRight: '0.5rem' }} />
                      Add New Asset
                    </CustomButton>
                  </Box>
                )}
              </GridItem>

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
                        <CustomButton mt={4} onClick={() => setActiveTab(AssetTabType.ADD_RESOURCE)}>
                          <FiPlus style={{ marginRight: '0.5rem' }} />
                          Add New Asset
                        </CustomButton>
                      </>
                    )}
                  </Box>
                )}
              </GridItem>
            </Grid>
          )}
        </TabContent>

        <TabContent value={AssetTabType.ADD_RESOURCE}>
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
        </TabContent>

        <TabContent value={AssetTabType.ADD_MACHINE}>
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
        </TabContent>
      </Tabs>
    </Container>
  );
};