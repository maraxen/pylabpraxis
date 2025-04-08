import { Asset } from "../types/asset";
import { ResourceTypeInfo, MachineTypeInfo, ResourceCategoriesResponse, ResourceFormData, MachineFormData } from "../types/plr-resources";

const API_BASE = `/api/assets`;

/**
 * Fetches metadata for all available PyLabRobot resource types
 */
export async function fetchResourceTypes(): Promise<Record<string, ResourceTypeInfo>> {
  const response = await fetch(`${API_BASE}/resources/types`);
  if (!response.ok) {
    throw new Error(`Failed to fetch resource types: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Fetches metadata for all available PyLabRobot machine types
 */
export async function fetchMachineTypes(): Promise<Record<string, MachineTypeInfo>> {
  const response = await fetch(`${API_BASE}/machines/types`);
  if (!response.ok) {
    throw new Error(`Failed to fetch machine types: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Fetches resource types categorized for easier browsing
 */
export async function fetchResourceCategories(): Promise<ResourceCategoriesResponse> {
  const response = await fetch(`${API_BASE}/resources/categories`);
  if (!response.ok) {
    throw new Error(`Failed to fetch resource categories: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Fetches assets by type
 */
export async function fetchAssetsByType(type: string): Promise<Asset[]> {
  const response = await fetch(`${API_BASE}/types/${encodeURIComponent(type)}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch assets: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Fetches available (unlocked) assets by type
 */
export async function fetchAvailableAssets(type: string): Promise<Asset[]> {
  const response = await fetch(`${API_BASE}/available/${encodeURIComponent(type)}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch available assets: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Gets details for a specific asset by name
 */
export async function fetchAssetDetails(name: string): Promise<Asset> {
  const response = await fetch(`${API_BASE}/${encodeURIComponent(name)}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch asset details: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Searches for assets by query
 */
export async function searchAssets(query: string): Promise<Asset[]> {
  const response = await fetch(`${API_BASE}/search/${encodeURIComponent(query)}`);
  if (!response.ok) {
    throw new Error(`Failed to search assets: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Creates a new resource in the database
 */
export async function createResource(data: ResourceFormData): Promise<Asset> {
  const response = await fetch(`${API_BASE}/resource`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    throw new Error(`Failed to create resource: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Creates a new machine in the database
 */
export async function createMachine(data: MachineFormData): Promise<Asset> {
  const response = await fetch(`${API_BASE}/machine`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    throw new Error(`Failed to create machine: ${response.statusText}`);
  }

  return response.json();
}