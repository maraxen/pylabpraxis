// Defines an abstract wrapper for OIDC authentication operations,
// allowing for platform-specific implementations (IO vs. Browser).

import 'package:openid_client/openid_client.dart' as oidc;
// Import the stub file to get access to the createOidcAuthenticatorWrapper factory function
import 'oidc_authenticator.dart';

/// Abstract interface for an OIDC authenticator.
/// This allows for different implementations for mobile (IO) and web (browser).
abstract class OidcAuthenticatorWrapper {
  /// Factory constructor to create the appropriate platform-specific authenticator.
  ///
  /// This constructor calls the top-level `createOidcAuthenticatorWrapper` function
  /// (defined in `oidc_authenticator.dart`) which handles the platform-specific instantiation.
  factory OidcAuthenticatorWrapper({
    required oidc.Client client,
    required List<String> scopes,
    required Uri redirectUri,
    int? port, // Conditionally used by the IO implementation
  }) {
    // Call the top-level factory function defined in the stub file.
    return createOidcAuthenticatorWrapper(
      client: client,
      scopes: scopes,
      redirectUri: redirectUri,
      port: port,
    );
  }

  /// Initiates the OIDC authorization flow.
  ///
  /// On mobile, this should complete and return a [oidc.Credential].
  /// On web, this initiates a browser redirect and the Future might not complete
  /// with a credential in the same app lifecycle, or it might return null/throw.
  /// The result on web is typically handled after a page redirect by [processRedirect].
  Future<oidc.Credential?> authorize();

  /// For web, attempts to process the OIDC response from the redirect URL.
  /// Returns a [oidc.Credential] if successful, null otherwise.
  /// On mobile, this might not be applicable or always return null.
  Future<oidc.Credential?> processRedirect();
}
