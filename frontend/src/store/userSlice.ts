import { createSlice, createAsyncThunk, SerializedError } from '@reduxjs/toolkit';
import type { RootState } from './index';
import { authService } from '../services/auth';
import type { User, LoginCredentials } from '../services/auth';

interface LoadingState {
  login: boolean;
  fetchUser: boolean;
  updateAvatar: boolean;
  updatePassword: boolean;
}

interface ErrorState {
  login: string | null;
  fetchUser: string | null;
  updateAvatar: string | null;
  updatePassword: string | null;
}

interface UserState {
  currentUser: User | null;
  loadingStates: LoadingState;
  errors: ErrorState;
  isAuthenticated: boolean;
}

const initialState: UserState = {
  currentUser: null,
  loadingStates: {
    login: false,
    fetchUser: false,
    updateAvatar: false,
    updatePassword: false,
  },
  errors: {
    login: null,
    fetchUser: null,
    updateAvatar: null,
    updatePassword: null,
  },
  isAuthenticated: authService.isAuthenticated(),
};

export const loginUser = createAsyncThunk<User, LoginCredentials>(
  'user/login',
  async (credentials, { rejectWithValue }) => {
    try {
      const response = await authService.login(credentials);
      return response.user;
    } catch (error) {
      return rejectWithValue((error as Error).message || 'Login failed');
    }
  }
);

export const fetchCurrentUser = createAsyncThunk<User, void>(
  'user/fetchCurrent',
  async (_, { rejectWithValue }) => {
    try {
      const user = await authService.getCurrentUser();
      if (!user) throw new Error('No user found');
      return user;
    } catch (error) {
      return rejectWithValue((error as Error).message || 'Failed to fetch user data');
    }
  }
);

export const updateUserAvatar = createAsyncThunk<string, File>(
  'user/updateAvatar',
  async (file, { rejectWithValue }) => {
    try {
      const formData = new FormData();
      formData.append('avatar', file);
      const response = await authService.updateAvatar(formData);
      return response.avatarUrl;
    } catch (error) {
      return rejectWithValue((error as Error).message || 'Failed to update avatar');
    }
  }
);

export const updateUserPassword = createAsyncThunk(
  'user/updatePassword',
  async (passwords: { current: string; new: string }, { rejectWithValue }) => {
    try {
      await authService.updatePassword(passwords.current, passwords.new);
      return true;
    } catch (error) {
      return rejectWithValue('Failed to update password');
    }
  }
);

export const refreshUserSession = createAsyncThunk(
  'user/refreshSession',
  async (_, { rejectWithValue }) => {
    try {
      const token = authService.getStoredToken();
      if (!token) throw new Error('No token found');
      const user = await authService.getCurrentUser();
      return user;
    } catch (error) {
      return rejectWithValue('Session expired');
    }
  }
);

// Update selector types
export const selectUser = (state: RootState) => state.user;
export const selectCurrentUser = (state: RootState) => state.user.currentUser;
export const selectLoadingStates = (state: RootState) => state.user.loadingStates;
export const selectErrors = (state: RootState) => state.user.errors;
export const selectError = (state: RootState): string | null => {
  const errors = state.user.errors;
  return Object.values(errors).find(error => error !== null) ?? null;
};

// Remove sessionExpired and use logout instead
const userSlice = createSlice({
  name: 'user',
  initialState,
  reducers: {
    logout: (state) => {
      state.currentUser = null;
      state.isAuthenticated = false;
      state.errors = initialState.errors;
      state.loadingStates = initialState.loadingStates;
      authService.logout();
    },
    clearErrors: (state) => {
      state.errors = initialState.errors;
    },
    clearLoadingStates: (state) => {
      state.loadingStates = initialState.loadingStates;
    },
  },
  extraReducers: (builder) => {
    builder
      // Login
      .addCase(loginUser.pending, (state) => {
        state.loadingStates.login = true;
        state.errors.login = null;
      })
      .addCase(loginUser.fulfilled, (state, action) => {
        state.loadingStates.login = false;
        state.currentUser = action.payload;
        state.isAuthenticated = true;
        state.errors.login = null;
      })
      .addCase(loginUser.rejected, (state, action) => {
        state.loadingStates.login = false;
        state.errors.login = action.payload as string;
        state.isAuthenticated = false;
        state.currentUser = null;
      })
      // Fetch current user
      .addCase(fetchCurrentUser.pending, (state) => {
        state.loadingStates.fetchUser = true;
        state.errors.fetchUser = null;
      })
      .addCase(fetchCurrentUser.fulfilled, (state, action) => {
        state.loadingStates.fetchUser = false;
        state.currentUser = action.payload;
        state.isAuthenticated = true;
        state.errors.fetchUser = null;
      })
      .addCase(fetchCurrentUser.rejected, (state, action) => {
        state.loadingStates.fetchUser = false;
        state.errors.fetchUser = action.payload as string;
        state.isAuthenticated = false;
      })
      .addCase(updateUserAvatar.pending, (state) => {
        state.loadingStates.updateAvatar = true;
        state.errors.updateAvatar = null;
      })
      .addCase(updateUserAvatar.fulfilled, (state, action) => {
        state.loadingStates.updateAvatar = false;
        if (state.currentUser) {
          state.currentUser.picture = action.payload;
        }
        state.errors.updateAvatar = null;
      })
      .addCase(updateUserAvatar.rejected, (state, action) => {
        state.loadingStates.updateAvatar = false;
        state.errors.updateAvatar = action.payload as string;
      })
      .addCase(updateUserPassword.pending, (state) => {
        state.loadingStates.updatePassword = true;
        state.errors.updatePassword = null;
      })
      .addCase(updateUserPassword.fulfilled, (state) => {
        state.loadingStates.updatePassword = false;
      })
      .addCase(updateUserPassword.rejected, (state, action) => {
        state.loadingStates.updatePassword = false;
        state.errors.updatePassword = action.payload as string;
      })
      .addCase(refreshUserSession.fulfilled, (state, action) => {
        state.currentUser = action.payload;
        state.isAuthenticated = true;
      })
      .addCase(refreshUserSession.rejected, (state) => {
        userSlice.caseReducers.logout(state);
      });
  },
});

export const { logout, clearErrors, clearLoadingStates } = userSlice.actions;

// Type-safe selectors
export const selectIsAuthenticated = (state: RootState): boolean => state.user.isAuthenticated;
export const selectIsLoading = (state: RootState): boolean =>
  Object.values(state.user.loadingStates).some(Boolean);
export const selectIsAdmin = (state: RootState): boolean => state.user.currentUser?.is_admin ?? false;

// Helper selector to get username safely
export const selectUsername = (state: RootState): string => state.user.currentUser?.username ?? '';

// Composite selectors
export const selectUserProfile = (state: RootState): {
  username: string;
  isAdmin: boolean;
  avatarUrl: string | null;
} => ({
  username: state.user.currentUser?.username ?? '',
  isAdmin: state.user.currentUser?.is_admin ?? false,
  avatarUrl: state.user.currentUser?.picture ?? null,
});

// Memoized selector for checking specific permissions
export const createPermissionSelector = (permission: string) =>
  (state: RootState): boolean => {
    const user = state.user.currentUser;
    if (!user) return false;
    if (user.is_admin) return true;
    return false; // Add more permission logic as needed
  };

export default userSlice.reducer;
