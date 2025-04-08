export type AssetType = 'machine' | 'liquid_handler' | 'resource';

export type ResourceType = 'plate' | 'tip_rack' | 'tip_spot' | 'well' | 'lid';

export interface ResourceDimensions {
  width: number;
  length: number;
  height: number;
}

export interface ResourcePosition {
  x: number;
  y: number;
  z: number;
}

export interface Resource {
  name: string;
  type: ResourceType;
  dimensions?: ResourceDimensions;
  position?: ResourcePosition;
  max_volume?: number;  // For wells
  capacity?: number;    // For tip racks
  children?: Resource[];
}

/**
 * Represents an asset in the system, such as a lab resource or machine
 */
export interface Asset {
  id?: string;
  name: string;
  type: string;
  is_available: boolean;
  description?: string;
  metadata: Record<string, any>;
}

/**
 * Asset with additional information such as detailed configuration
 */
export interface DetailedAsset extends Asset {
  configuration?: Record<string, any>;
  lock_expires_at?: string;
  created_at?: string;
  updated_at?: string;
  plr_serialized?: Record<string, any>;
}