import React, { useEffect } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useDispatch } from 'react-redux';
import { setUser, setLoading } from './store/authSlice';
import ProtectedRoute from '@/components/ProtectedRoute';
import { Dashboard } from './pages/Dashboard';
import { Settings } from './pages/Settings';
import { RunProtocols } from './pages/protocols/RunProtocols';
import { authService } from './services/auth';
import { RootState } from './store';

export const App: React.FC = () => {
  const dispatch = useDispatch();
  // Fetch the current user on app load
  useEffect(() => {
    dispatch(setLoading(true));
    authService.getCurrentUser()
      .then(user => {
        dispatch(setUser(user));
      })
      .finally(() => {
        dispatch(setLoading(false));
      });
  }, [dispatch]);

  return (
    <Routes>
      <Route path="/" element={
        <ProtectedRoute>
          <Dashboard />
        </ProtectedRoute>
      } />
      <Route path="/settings" element={
        <ProtectedRoute>
          <Settings />
        </ProtectedRoute>
      } />
      <Route path="/protocols" element={
        <ProtectedRoute>
          <RunProtocols />
        </ProtectedRoute>
      } />
      {/* Add other routes as needed */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
};
