import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Login } from './pages/Login';
import { Home } from './pages/Home';
import { ManageUsers } from './pages/ManageUsers';
import { Settings } from './pages/Settings';
import { authService } from './services/auth';
import { Layout } from './components/Layout';
import { RunProtocols } from './pages/protocols/RunProtocols';
import { ErrorBoundary } from './components/ErrorBoundary';
import { useAppDispatch } from './hooks/redux';
import { refreshUserSession } from './store/userSlice';

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
  const dispatch = useAppDispatch();

  useEffect(() => {
    authService.setupAxiosInterceptors(dispatch);

    // Check and refresh user session
    if (authService.isAuthenticated()) {
      dispatch(refreshUserSession());
    }
  }, [dispatch]);

  return (
    <ErrorBoundary>
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
          <Route
            path="/protocols"
            element={
              <ProtectedRoute>
                <Layout>
                  <RunProtocols />
                </Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/databases"
            element={
              <ProtectedRoute>
                <Layout>
                  <div>Database Management Coming Soon</div>
                </Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/vixn"
            element={
              <ProtectedRoute>
                <Layout>
                  <div>Vixn Coming Soon</div>
                </Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/docs"
            element={
              <ProtectedRoute>
                <Layout>
                  <div>Documentation Coming Soon</div>
                </Layout>
              </ProtectedRoute>
            }
          />
          {/* Add more routes here */}
        </Routes>
      </Router>
    </ErrorBoundary>
  );
}

export default App;
