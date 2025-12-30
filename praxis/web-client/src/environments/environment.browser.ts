// Browser Mode environment configuration
// Runs entirely in-browser with no backend dependencies
// Uses LocalStorage for persistence and bypasses authentication
export const environment = {
    production: false,
    browserMode: true,  // Pure browser mode - no server required
    demo: false,        // Not demo mode (no pre-loaded fake content)
    apiUrl: '/api/v1',  // Will be intercepted by DemoInterceptor
    wsUrl: '',          // WebSockets disabled in browser mode
    keycloak: {
        enabled: false,
        url: '',
        realm: '',
        clientId: ''
    }
};
