// Browser (Web) specific implementation of OidcAuthenticatorWrapper.

import 'package:openid_client/openid_client.dart' as oidc;
import 'package:openid_client/openid_client_browser.dart'
    as browser_authenticator;
import 'oidc_authenticator_wrapper.dart';
// import 'package:flutter/foundation.dart'; // For debugPrint if needed

class OidcAuthenticatorBrowser implements OidcAuthenticatorWrapper {
  final oidc.Client client;
  final List<String> scopes;
  // redirectUri for browser is often handled by the library using window.location
  // or by ensuring the client configuration in Keycloak is correct.
  // The browser Authenticator constructor doesn't always take it directly.

  OidcAuthenticatorBrowser({required this.client, required this.scopes});

  @override
  Future<oidc.Credential?> authorize() async {
    final authenticator = browser_authenticator.Authenticator(
      client,
      scopes: scopes,
      // For openid_client_browser, redirectUri is often implicitly taken from client's
      // registered redirect URIs or current window.location for callback.
      // The `authorize` method itself might not take a redirectUri.
    );
    // This initiates a browser redirect. The Future completes when navigation starts.
    authenticator.authorize();
    return null; // Credential is not obtained here, but after redirect.
  }

  @override
  Future<oidc.Credential?> processRedirect() async {
    final authenticator = browser_authenticator.Authenticator(
      client,
      scopes: scopes,
    );
    // This getter checks the current URL for OIDC response parameters.
    return await authenticator.credential;
  }
}
