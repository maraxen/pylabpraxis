
import { createReactOidc } from "oidc-spa/react";

export const { OidcProvider, useOidc, getOidc } = createReactOidc({
  // NOTE: If you don't have the params right away see note below.
  issuerUri: "http://localhost:8080/realms/praxis", // TODO: change to use keycloak.json
  clientId: "praxis-client",
  publicUrl: import.meta.env.BASE_URL,
  isAuthGloballyRequired: true,
});
