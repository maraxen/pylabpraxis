import { createSlice, PayloadAction } from '@reduxjs/toolkit';

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
  configPath: null
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
    }
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
  resetForm
} = protocolFormSlice.actions;

export default protocolFormSlice.reducer;
