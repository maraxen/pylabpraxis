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

export interface Asset {
  id: string;
  name: string;
  type: AssetType;
  description: string;
  resource?: Resource;  // For deck resources
  status?: 'available' | 'in_use' | 'offline';
  metadata?: Record<string, any>;
}