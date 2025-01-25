import React, { useEffect } from 'react';
import { Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { useDispatch } from 'react-redux';
import { setUser, setLoading } from './store/authSlice';
import ProtectedRoute from '@/components/ProtectedRoute';
import { Login } from './pages/Login';
import { Dashboard } from './pages/Dashboard';
import { Settings } from './pages/Settings';
import { RunProtocols } from './pages/protocols/RunProtocols';
import { authService } from './services/auth';

export const App = () => {
  const dispatch = useDispatch();
  const location = useLocation();

  useEffect(() => {
    const initAuth = async () => {
      // Skip auth initialization on login page
      if (location.pathname === '/login') {
        dispatch(setLoading(false));
        return;
      }

      dispatch(setLoading(true));

      if (!authService.getStoredToken()) {
        dispatch(setUser(null));
        dispatch(setLoading(false));
        return;
      }

      try {
        const user = await authService.getCurrentUser();
        dispatch(setUser(user));
      } catch (error) {
        console.error('Auth initialization failed:', error);
        dispatch(setUser(null));
      } finally {
        dispatch(setLoading(false));
      }
    };

    initAuth();
  }, [dispatch, location.pathname]);

  return (
    <Routes>
      <Route path="/login" element={<Login />} />
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

