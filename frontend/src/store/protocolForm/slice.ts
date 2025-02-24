import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface ParameterState {
  definition: {
    type: string;
    required?: boolean;
    default?: any;
    description?: string;
    constraints?: Record<string, any>;
  };
  currentValue: any;
}

interface AssetState {
  definition: {
    name: string;
    type: string;
    required: boolean;
    description?: string;
  };
  currentValue: string;
  availableOptions: Array<{
    name: string;
    type: string;
    is_available: boolean;
    description?: string;
    metadata?: Record<string, any>;
    last_used?: string;
  }>;
}

interface ProtocolFormState {
  selectedProtocol: string;
  protocolDetails: any;
  assetConfig: Record<string, any>;
  parameterValues: Record<string, any>;
  configFile: string | null;
  isConfigValid: boolean;
  step: number;
  currentStep: 'select' | 'configure' | 'assets' | 'parameters';
  configPath: 'upload' | 'specify' | null;
  parameters: Record<string, ParameterState>;
  assets: Record<string, AssetState>;
}

const initialState: ProtocolFormState = {
  selectedProtocol: '',
  protocolDetails: null,
  assetConfig: {},
  parameterValues: {},
  configFile: null,
  isConfigValid: false,
  step: 0,
  currentStep: 'select',
  configPath: null,
  parameters: {},
  assets: {},
};

export const protocolFormSlice = createSlice({
  name: 'protocolForm',
  initialState,
  reducers: {
    setSelectedProtocol: (state, action: PayloadAction<string>) => {
      state.selectedProtocol = action.payload;
    },
    setProtocolDetails: (state, action: PayloadAction<any>) => {
      state.protocolDetails = action.payload;
    },
    setAssetConfig: (state, action: PayloadAction<Record<string, any>>) => {
      state.assetConfig = action.payload;
    },
    updateAssetConfig: (state, action: PayloadAction<{ name: string, value: any }>) => {
      state.assetConfig[action.payload.name] = action.payload.value;
    },
    setParameterValues: (state, action: PayloadAction<Record<string, any>>) => {
      state.parameterValues = action.payload;
    },
    updateParameterValue: (state, action: PayloadAction<{ name: string, value: any }>) => {
      state.parameterValues[action.payload.name] = action.payload.value;
    },
    setConfigFile: (state, action: PayloadAction<string | null>) => {
      state.configFile = action.payload;
    },
    setIsConfigValid: (state, action: PayloadAction<boolean>) => {
      state.isConfigValid = action.payload;
    },
    setStep: (state, action: PayloadAction<number>) => {
      state.step = action.payload;
    },
    setCurrentStep: (state, action: PayloadAction<'select' | 'configure' | 'assets' | 'parameters'>) => {
      state.currentStep = action.payload;
    },
    setConfigPath: (state, action: PayloadAction<'upload' | 'specify' | null>) => {
      state.configPath = action.payload;
    },
    resetForm: (state) => {
      return initialState;
    },
    resetParameters: (state) => {
      state.parameters = {};
      state.parameterValues = {};
    },
    initializeParameters: (state, action: PayloadAction<Record<string, any>>) => {
      // First reset any existing parameters
      state.parameters = {};
      state.parameterValues = {};

      // Then initialize new ones
      state.parameters = Object.entries(action.payload).reduce((acc, [name, def]) => {
        acc[name] = {
          definition: def,
          currentValue: def.default || (def.type === 'array' ? [] : null)
        };
        return acc;
      }, {} as Record<string, ParameterState>);
    },
    removeParameterValue: (state, action: PayloadAction<{ name: string, index: number }>) => {
      const { name, index } = action.payload;
      if (state.parameters[name] && Array.isArray(state.parameters[name].currentValue)) {
        state.parameters[name].currentValue = state.parameters[name].currentValue.filter((_, i) => i !== index);
      }
    },
    initializeAssets: (state, action: PayloadAction<Array<{
      name: string;
      type: string;
      required: boolean;
      description?: string;
    }>>) => {
      state.assets = {};
      state.assetConfig = {};

      state.assets = action.payload.reduce((acc, asset) => {
        acc[asset.name] = {
          definition: asset,
          currentValue: '',
          availableOptions: []
        };
        return acc;
      }, {} as Record<string, AssetState>);
    },

    updateAssetOptions: (state, action: PayloadAction<{
      type: string;
      options: Array<any>;
    }>) => {
      Object.values(state.assets).forEach(asset => {
        if (asset.definition.type === action.payload.type) {
          asset.availableOptions = action.payload.options;
        }
      });
    },

    resetAssets: (state) => {
      state.assets = {};
      state.assetConfig = {};
    },
  }
});

export const {
  setSelectedProtocol,
  setProtocolDetails,
  setAssetConfig,
  updateAssetConfig,
  setParameterValues,
  updateParameterValue,
  setConfigFile,
  setIsConfigValid,
  setStep,
  setCurrentStep,
  setConfigPath,
  resetForm,
  initializeParameters,
  removeParameterValue,
  resetParameters,
  initializeAssets,
  updateAssetOptions,
  resetAssets,
} = protocolFormSlice.actions;

export default protocolFormSlice.reducer;
