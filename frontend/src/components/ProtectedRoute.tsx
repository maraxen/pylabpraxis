import React, { useEffect } from 'react';
import { Navigate } from 'react-router-dom';
import { Box, Spinner, Center } from '@chakra-ui/react';
import { Navbar } from './Navbar';
import { StatusBar } from './StatusBar';
import { selectIsAdmin } from '@/store/userSlice';
import { useOidc } from '../oidc';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requireAdmin?: boolean;
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  requireAdmin = false
}) => {
  // const { oidcTokens } = useOidc();

  // const isAdmin = selectIsAdmin(oidcTokens.decodedIdToken);
  // if (requireAdmin && !isAdmin) {
  //  return <Navigate to="/home" replace />;
  // }

  return (
    <>
      <Navbar />
      <Box as="main" p="6" pb="12" minH="calc(100vh - 8rem)" bg={{ base: 'gray.50', _dark: 'gray.900' }}>
        {children}
      </Box>
      <StatusBar />
    </>
  );
};

export default ProtectedRoute;