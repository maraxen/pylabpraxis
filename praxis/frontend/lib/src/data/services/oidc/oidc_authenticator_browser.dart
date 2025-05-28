// Browser (Web) specific implementation of OidcAuthenticatorWrapper.
// Manually uses oidc.Flow.authorizationCode and relies on openid_client's
// internal state persistence (localStorage).
// Uses package:web for browser interactions.
// Correctly formats params for flow.callback as Map<String, String>.

import 'package:flutter/foundation.dart'; // For kIsWeb
import 'package:openid_client/openid_client.dart' as oidc;
import 'oidc_authenticator_wrapper.dart';
import 'dart:developer' as developer; // For developer.log
import 'package:web/web.dart'; // Using package:web for window access

class OidcAuthenticatorBrowser implements OidcAuthenticatorWrapper {
  final oidc.Client client;
  final List<String> scopes;
  final Uri redirectUri; // This is the intended redirect_uri (e.g., .../splash)

  OidcAuthenticatorBrowser({
    required this.client,
    required this.scopes,
    required this.redirectUri,
  });

  oidc.Flow _createAndConfigureFlow({String? state}) {
    final processedRedirectUri = Uri.parse(
      redirectUri.toString().split('?')[0],
    );
    final flow = oidc.Flow.authorizationCodeWithPKCE(
      client,
      state: state,
      codeVerifier:
          '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ', // TODO: figure out someway to generate and persist within sessions safely
    );
    flow.redirectUri = processedRedirectUri;
    flow.scopes.addAll(scopes);
    print(
      'OidcAuthBrowser: Created/Configured Flow.authorizationCode with redirectUri: ${flow.redirectUri} and scopes: ${flow.scopes}',
    );
    return flow;
  }

  @override
  Future<oidc.Credential?> authorize() async {
    print(
      'OidcAuthenticatorBrowser: Preparing to authorize. Intended redirectUri: $redirectUri',
    );

    final flow = _createAndConfigureFlow();
    final authUrl = flow.authenticationUri;

    print('OidcAuthenticatorBrowser: Flow prepared. State: ${flow.state}');
    print(
      'OidcAuthenticatorBrowser: Full Authentication URL for redirect: ${authUrl.toString()}',
    );

    window.location.assign(authUrl.toString());
    return null;
  }

  @override
  Future<oidc.Credential?> processRedirect() async {
    final currentUri = Uri.parse(window.location.href);
    print(
      'OidcAuthenticatorBrowser: Processing redirect. Current window.location.href: $currentUri',
    );
    final stateFromUri = currentUri.queryParameters['state'];
    final flow = _createAndConfigureFlow(state: stateFromUri);

    // Get all query parameters as Map<String, List<String>>
    final queryParamsAll = currentUri.queryParametersAll;

    // Convert to Map<String, String> for flow.callback, taking the first value for each key.
    // This matches the signature: Future<Credential> callback(Map<String, String> response)
    final Map<String, String> paramsForCallback = queryParamsAll.map(
      (key, value) => MapEntry(key, value.isNotEmpty ? value.first : ''),
    );

    if (paramsForCallback.containsKey('code') &&
        paramsForCallback.containsKey('state')) {
      print(
        'OidcAuthenticatorBrowser: Found "code" (${paramsForCallback['code']}) and "state" (${paramsForCallback['state']}) in query parameters. Processing OIDC callback with Map<String, String>.',
      );
      try {
        final credential = await flow.callback(paramsForCallback);
        print(
          'OidcAuthenticatorBrowser: Credential successfully obtained via flow.callback.',
        );
        print(
          'OidcAuthenticatorBrowser: Credential details: ${credential.toJson()}',
        );
        return credential;
      } catch (e, s) {
        print(
          'OidcAuthenticatorBrowser: Error during flow.callback: $e\nStack: $s',
        );
        if (e.toString().toLowerCase().contains("state does not match")) {
          print(
            'OidcAuthenticatorBrowser: STATE MISMATCH CONFIRMED. URL State: "${paramsForCallback['state']}". Expected state was not found or did not match what openid_client stored/retrieved.',
          );
        }
        rethrow;
      }
    } else {
      print(
        'OidcAuthenticatorBrowser: "code" or "state" missing in query parameters. Not a valid Authorization Code callback. URL: $currentUri. Parsed params for callback: $paramsForCallback',
      );
      if (paramsForCallback.containsKey('error')) {
        final error = paramsForCallback['error'];
        final errorDescription = paramsForCallback['error_description'];
        print(
          'OidcAuthenticatorBrowser: OIDC error in redirect query: $error, Description: $errorDescription',
        );
        throw oidc.OpenIdException(error, errorDescription ?? '');
      }
      return null;
    }
  }
}
