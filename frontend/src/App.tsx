import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Login } from './pages/Login';
import { Home } from './pages/Home';
import { ManageUsers } from './pages/ManageUsers';
import { Settings } from './pages/Settings';
import { authService } from './services/auth';
import { Layout } from './components/Layout';

// Protected route wrapper
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const isAuthenticated = authService.isAuthenticated();
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" />;
};

// Protected route wrapper that checks for admin status
const AdminRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [isAdmin, setIsAdmin] = React.useState<boolean | null>(null);

  React.useEffect(() => {
    const checkAdmin = async () => {
      const user = await authService.getCurrentUser();
      setIsAdmin(user?.is_admin ?? false);
    };
    checkAdmin();
  }, []);

  if (isAdmin === null) return null; // Loading state
  return isAdmin ? <>{children}</> : <Navigate to="/" />;
};

function App() {
  useEffect(() => {
    // Setup axios interceptors for authentication
    authService.setupAxiosInterceptors();
  }, []);

  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <Layout>
                <Home />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/manage-users"
          element={
            <ProtectedRoute>
              <AdminRoute>
                <Layout>
                  <ManageUsers />
                </Layout>
              </AdminRoute>
            </ProtectedRoute>
          }
        />
        <Route
          path="/settings"
          element={
            <ProtectedRoute>
              <Layout>
                <Settings />
              </Layout>
            </ProtectedRoute>
          }
        />
        {/* Add more routes here */}
      </Routes>
    </Router>
  );
}

export default App;
