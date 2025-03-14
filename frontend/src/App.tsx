import { Routes, Route, Navigate } from 'react-router-dom';
import { Dashboard } from '@homeDashboard/index';
import { Settings } from './features/settings/pages/Settings';
import { RunProtocols } from '@protocols/index';
import { Vixn } from '@/pages/Vixn';
import { Documentation } from '@/pages/Documentation';
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
      <Route path="/vixn" element={
        <ProtectedRoute>
          <Vixn />
        </ProtectedRoute>
      } />
      <Route path="/docs" element={
        <ProtectedRoute>
          <Documentation />
        </ProtectedRoute>
      } />
      <Route path="/" element={<Navigate to="/home" />} />
    </Routes>
  );
};
