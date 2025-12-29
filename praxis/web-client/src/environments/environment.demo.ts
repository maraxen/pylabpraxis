// Demo environment configuration for GitHub Pages deployment
// This environment runs entirely client-side without backend dependencies
export const environment = {
    production: false,
    demo: true,  // Enable demo mode - uses mock data and bypasses auth
    apiUrl: '/api/v1',  // Will be intercepted by DemoInterceptor
    wsUrl: '',  // WebSockets disabled in demo mode
    keycloak: {
        // Keycloak is disabled in demo mode
        enabled: false,
        url: '',
        realm: '',
        clientId: ''
    }
};
