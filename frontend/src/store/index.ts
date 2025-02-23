import { configureStore } from '@reduxjs/toolkit';
import settingsReducer from '@/store/settingsSlice';
import userReducer from '@/store/userSlice';
import protocolFormReducer from './protocolForm/slice';

export const store = configureStore({
  reducer: {
    settings: settingsReducer,
    protocolForm: protocolFormReducer,
    user: userReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
