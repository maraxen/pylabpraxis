import { Box } from '@chakra-ui/react';
import { Navbar } from '../components/layout/Navbar';
import { StatusBar } from '../components/layout/StatusBar';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requireAdmin?: boolean;
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
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