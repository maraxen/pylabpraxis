import { configureStore } from '@reduxjs/toolkit';
import settingsReducer from '@settings/store/settingsSlice';
import userReducer from '@users/store/userSlice';
import protocolFormReducer from '@protocols/store/slice';

export const store = configureStore({
  reducer: {
    settings: settingsReducer,
    protocolForm: protocolFormReducer,
    user: userReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
