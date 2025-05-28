// IO (Mobile) specific implementation of OidcAuthenticatorWrapper.

import 'package:flutter/foundation.dart';
import 'package:openid_client/openid_client.dart' as oidc;
import 'package:openid_client/openid_client_io.dart' as io_authenticator;
import 'package:url_launcher/url_launcher.dart';
import 'package:praxis_lab_management/src/core/error/exceptions.dart';
import 'oidc_authenticator_wrapper.dart';

class OidcAuthenticatorIo implements OidcAuthenticatorWrapper {
  final oidc.Client client;
  final List<String> scopes;
  final Uri redirectUri;
  final int port; // Port for the local redirect listener on mobile

  OidcAuthenticatorIo({
    required this.client,
    required this.scopes,
    required this.redirectUri,
    this.port = 4000, // Default port, can be any available
  });

  Future<void> _urlLauncher(String url) async {
    final uri = Uri.parse(url);
    // On Android, canLaunchUrl might return false for custom schemes if not perfectly set up,
    // but launchUrl might still work.
    if (!kIsWeb && defaultTargetPlatform == TargetPlatform.android) {
      try {
        await launchUrl(uri, mode: LaunchMode.externalApplication);
        return;
      } catch (e) {
        debugPrint(
          "launchUrl directly failed on Android, trying canLaunchUrl as fallback: $e",
        );
        // Fallback to check with canLaunchUrl if direct launch fails, though less common for this to help.
      }
    }
    if (await canLaunchUrl(uri)) {
      await launchUrl(uri, mode: LaunchMode.externalApplication);
    } else {
      throw AuthException('Could not launch $url');
    }
  }

  @override
  Future<oidc.Credential?> authorize() async {
    final authenticator = io_authenticator.Authenticator(
      client,
      scopes: scopes,
      redirectUri: redirectUri,
      port: port,
      urlLancher:
          _urlLauncher, // Note: openid_client_io 0.4.9 has 'urlLancher' typo
    );
    return await authenticator.authorize();
  }

  @override
  Future<oidc.Credential?> processRedirect() async {
    // Not applicable for the IO flow in the same way as web.
    // Authorization is completed within the authorize() call.
    return null;
  }
}
