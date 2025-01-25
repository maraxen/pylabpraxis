import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useSelector } from 'react-redux';
import { Box, Spinner, Center } from '@chakra-ui/react';
import { Navbar } from './Navbar';
import { StatusBar } from './StatusBar';
import { RootState } from '../store';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requireAdmin?: boolean;
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  requireAdmin = false
}) => {
  const location = useLocation();
  const { user, isAuthenticated, isLoading } = useSelector((state: RootState) => state.auth);

  if (isLoading) {
    return (
      <Center h="100vh">
        <Spinner size="xl" color="brand.500" />
      </Center>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (requireAdmin && !user?.is_admin) {
    return <Navigate to="/" replace />;
  }

  return (
    <>
      <Navbar />
      <Box
        as="main"
        p="6"
        pb="12" // Add padding at bottom for StatusBar
        minH="calc(100vh - 8rem)"
        bg={{ base: 'gray.50', _dark: 'gray.900' }}
      >
        {children}
      </Box>
      <StatusBar />
    </>
  );
};

export default ProtectedRoute;