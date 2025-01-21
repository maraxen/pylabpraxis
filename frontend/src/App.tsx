import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ChakraProvider } from '@chakra-ui/react';
import { Login } from './pages/Login';
import { authService } from './services/auth';

// Protected route wrapper
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const isAuthenticated = authService.isAuthenticated();
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" />;
};

function App() {
  useEffect(() => {
    // Setup axios interceptors for authentication
    authService.setupAxiosInterceptors();
  }, []);

  return (
    <ChakraProvider>
      <Router>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <div>Home Page (Protected)</div>
              </ProtectedRoute>
            }
          />
          {/* Add more routes here */}
        </Routes>
      </Router>
    </ChakraProvider>
  );
}

export default App;
