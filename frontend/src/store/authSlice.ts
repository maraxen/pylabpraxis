import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { RootState } from './index';

interface AuthState {
  isLoading: boolean;
  error: string | null;
}

const initialState: AuthState = {
  isLoading: false,
  error: null
};

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.isLoading = action.payload;
    },
    setError: (state, action: PayloadAction<string | null>) => {
      state.error = action.payload;
    },
    clearError: (state) => {
      state.error = null;
    }
  }
});

export const { setLoading, setError, clearError } = authSlice.actions;
export default authSlice.reducer;
