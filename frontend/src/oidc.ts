
import { createReactOidc } from "oidc-spa/react";

export const { OidcProvider, useOidc, getOidc } = createReactOidc({
  // NOTE: If you don't have the params right away see note below.
  issuerUri: "http://localhost:8080/realms/praxis-realm", // TODO: change to use keycloak.json
  clientId: "praxis-client",
  homeUrl: import.meta.env.BASE_URL,
  autoLogin: true,
  postLoginRedirectUrl: "/home",
  debugLogs: true,
});



