import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Dashboard } from './pages/Dashboard';
import { Settings } from './pages/Settings';
import { RunProtocols } from './pages/protocols/RunProtocols';
import ProtectedRoute from '@/components/ProtectedRoute';
import { useOidc } from './oidc';


export const App = () => {
  const { isUserLoggedIn, login } = useOidc();

  return (
    <Routes>
      <Route path="/" element={
        isUserLoggedIn ? <Navigate to="/home" /> : <Navigate to="/login" />
      } />
      <Route path="/login" />
      <Route path="/home" element={
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
      <Route path="*" element={<Navigate to="/home" replace />} />
    </Routes>
  );
};
