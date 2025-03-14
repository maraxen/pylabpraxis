import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import type { RootState } from './index';

interface SettingsState {
  theme: string;
  accentColor: string;
  protocolDirectories: string[];
  uiPreferences: {
    sidebarExpanded: boolean;
    denseMode: boolean;
  };
}

const initialState: SettingsState = {
  theme: localStorage.getItem('theme') || 'system',
  accentColor: localStorage.getItem('accentColor') || 'blue',
  protocolDirectories: [],
  uiPreferences: {
    sidebarExpanded: true,
    denseMode: false,
  },
};

const settingsSlice = createSlice({
  name: 'settings',
  initialState,
  reducers: {
    setTheme: (state, action: PayloadAction<string>) => {
      state.theme = action.payload;
      localStorage.setItem('theme', action.payload);
      document.documentElement.setAttribute('data-theme', action.payload);
    },
    setAccentColor: (state, action: PayloadAction<string>) => {
      state.accentColor = action.payload;
      localStorage.setItem('accentColor', action.payload);
      document.documentElement.setAttribute('data-accent-color', action.payload);
    },
    addProtocolDirectory: (state, action: PayloadAction<string>) => {
      if (!state.protocolDirectories.includes(action.payload)) {
        state.protocolDirectories.push(action.payload);
      }
    },
    removeProtocolDirectory: (state, action: PayloadAction<string>) => {
      state.protocolDirectories = state.protocolDirectories.filter(
        dir => dir !== action.payload
      );
    },
    setUiPreference: (state, action: PayloadAction<{ key: keyof SettingsState['uiPreferences']; value: boolean }>) => {
      state.uiPreferences[action.payload.key] = action.payload.value;
    },
  },
});

// Actions
export const {
  setTheme,
  setAccentColor,
  addProtocolDirectory,
  removeProtocolDirectory,
  setUiPreference,
} = settingsSlice.actions;

// Selectors
export const selectTheme = (state: RootState): string => state.settings.theme;
export const selectAccentColor = (state: RootState): string => state.settings.accentColor;
export const selectProtocolDirectories = (state: RootState): string[] => state.settings.protocolDirectories;
export const selectUiPreferences = (state: RootState) => state.settings.uiPreferences;

export default settingsSlice.reducer;
