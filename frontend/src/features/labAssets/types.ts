import { Asset } from '../../../types';

export interface AssetManagerProps {
  assets: Asset[];
  onAssetSelect?: (asset: Asset) => void;
  onAssetStatusChange?: (assetId: string, status: Asset['status']) => void;
  selectedAssetId?: string;
  isEditable?: boolean;
}

export interface AssetCardProps {
  asset: Asset;
  isSelected?: boolean;
  onSelect?: (asset: Asset) => void;
  onStatusChange?: (status: Asset['status']) => void;
  isEditable?: boolean;
}

export interface AssetListProps {
  assets: Asset[];
  selectedAssetId?: string;
  onAssetSelect?: (asset: Asset) => void;
  onAssetStatusChange?: (assetId: string, status: Asset['status']) => void;
  isEditable?: boolean;
  filter?: {
    type?: Asset['type'][];
    status?: Asset['status'][];
    search?: string;
  };
}