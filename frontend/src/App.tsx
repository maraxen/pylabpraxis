import React from 'react';
import { useOidc } from './oidc';
import { selectUserProfile } from '@/store/userSlice';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Dashboard } from './pages/Dashboard';
import { Settings } from './pages/Settings';
import { RunProtocols } from './pages/protocols/RunProtocols';
import ProtectedRoute from '@/components/ProtectedRoute';


export const App = () => {

  return (
    <Routes>
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
      // <Route path="/" element={<Navigate to="/home" replace />} />
    </Routes>
  );
};
