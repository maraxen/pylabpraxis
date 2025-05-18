// Fallback implementation for OidcAuthenticatorWrapper on unsupported platforms.
import 'package:openid_client/openid_client.dart' as oidc;
import 'oidc_authenticator_wrapper.dart';

class OidcAuthenticatorUnsupported implements OidcAuthenticatorWrapper {
  OidcAuthenticatorUnsupported({
    required oidc.Client client,
    required List<String> scopes,
    Uri? redirectUri, // Keep params for consistent factory, though unused
    int? port,
  });

  @override
  Future<oidc.Credential?> authorize() async {
    throw UnsupportedError(
      'OIDC Authentication is not supported on this platform.',
    );
  }

  @override
  Future<oidc.Credential?> processRedirect() async {
    throw UnsupportedError(
      'OIDC Authentication is not supported on this platform.',
    );
  }
}
