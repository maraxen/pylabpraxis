import { createSlice } from '@reduxjs/toolkit';

interface UserState {
  loadingStates: {
    updateAvatar: boolean;
    updatePassword: boolean;
  };
  errors: {
    updateAvatar: string | null;
    updatePassword: string | null;
  };
}

const initialState: UserState = {
  loadingStates: {
    updateAvatar: false,
    updatePassword: false,
  },
  errors: {
    updateAvatar: null,
    updatePassword: null,
  },
};

const userSlice = createSlice({
  name: 'user',
  initialState,
  reducers: {
    clearErrors: (state) => {
      state.errors = initialState.errors;
    },
    clearLoadingStates: (state) => {
      state.loadingStates = initialState.loadingStates;
    },
  }
});

export const { clearErrors, clearLoadingStates } = userSlice.actions;

// Type-safe selectors using OIDC token
export const selectUsername = (decodedIdToken: any): string =>
  decodedIdToken?.preferred_username ?? '';

export const selectIsAdmin = (decodedIdToken: any): boolean =>
  decodedIdToken?.realm_access?.roles?.includes('admin') ?? false;

export const selectUserProfile = (decodedIdToken: any) => ({
  username: decodedIdToken?.preferred_username ?? '',
  email: decodedIdToken?.email ?? '',
  isAdmin: decodedIdToken?.realm_access?.roles?.includes('admin') ?? false,
  picture: decodedIdToken?.picture ?? null,
  roles: decodedIdToken?.realm_access?.roles ?? []
});

export const createPermissionSelector = (permission: string) =>
  (decodedIdToken: any): boolean => {
    if (!decodedIdToken) return false;
    if (decodedIdToken.realm_access?.roles?.includes('admin')) return true;
    return decodedIdToken.realm_access?.roles?.includes(permission) ?? false;
  };

export default userSlice.reducer;
