// lib/src/data/services/oidc/oidc_authenticator.dart

// This file acts as a stub for conditional imports and defines the factory function.

import 'package:flutter/foundation.dart'
    show defaultTargetPlatform, kIsWeb, TargetPlatform;
import 'package:openid_client/openid_client.dart' as oidc;

// Import the interface that this factory will return/implement.
// This ensures OidcAuthenticatorWrapper is a known type within this file.
import 'oidc_authenticator_wrapper.dart';

// Conditionally import the platform-specific implementations.
// The Dart compiler will only include the code for the target platform.
// We use prefixes to avoid naming conflicts if we were to import them directly
// without the conditional logic for some reason (though here, the conditional
// part is key).
import 'oidc_authenticator_io.dart'
    if (dart.library.html) 'oidc_authenticator_unsupported.dart'
    as io_impl;
import 'oidc_authenticator_browser.dart'
    if (dart.library.io) 'oidc_authenticator_unsupported.dart'
    as browser_impl;
// Import the unsupported version directly for a clear fallback.
import 'oidc_authenticator_unsupported.dart' as unsupported_impl;

// Re-export the interface and the platform-specific implementations
// so that consumers importing this stub file can access them if needed,
// though typically they would just use the OidcAuthenticatorWrapper factory.
export 'oidc_authenticator_wrapper.dart';
export 'oidc_authenticator_unsupported.dart'
    if (dart.library.io) 'oidc_authenticator_io.dart'
    if (dart.library.html) 'oidc_authenticator_browser.dart';

/// Factory function to create the appropriate platform-specific OIDC authenticator.
/// This function is called by the factory constructor in [OidcAuthenticatorWrapper].
OidcAuthenticatorWrapper createOidcAuthenticatorWrapper({
  required oidc.Client client,
  required List<String> scopes,
  required Uri redirectUri, // Needed for IO (mobile)
  int? port, // Needed for IO (mobile)
}) {
  if (kIsWeb) {
    // When kIsWeb is true, `browser_impl` will refer to `oidc_authenticator_browser.dart`.
    // The `io_impl` would refer to `oidc_authenticator_unsupported.dart` on web.
    return browser_impl.OidcAuthenticatorBrowser(
      client: client,
      scopes: scopes,
      redirectUri: redirectUri,
    );
  } else if (!kIsWeb && defaultTargetPlatform != TargetPlatform.windows) {
    return io_impl.OidcAuthenticatorIo(
      client: client,
      scopes: scopes,
      redirectUri: redirectUri,
      port: port ?? 4000, // Default port for IO if not specified
    );
  }
  // Fallback for any other unexpected platform (e.g., Fuchsia without specific support, or Windows if not using IO)
  // Or if you have a specific Windows implementation, you'd add another conditional export for it.
  return unsupported_impl.OidcAuthenticatorUnsupported(
    client: client,
    scopes: scopes,
    redirectUri: redirectUri,
    port: port,
  );
}
