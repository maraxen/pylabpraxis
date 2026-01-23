// Development environment configuration
export const environment = {
  production: false,
  apiUrl: '/api/v1',
  wsUrl: 'ws://localhost:8000/api/v1/ws',
  keycloak: {
    url: 'http://localhost:8080',
    realm: 'praxis',
    clientId: 'praxis'
  },
  sqliteOpfsEnabled: false // Opt-in to experimental OPFS storage
};
