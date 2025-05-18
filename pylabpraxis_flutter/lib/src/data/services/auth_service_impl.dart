// Concrete implementation of the [AuthService] using openid_client and flutter_secure_storage.
//
// This class handles OIDC authentication with Keycloak, secure token storage,
// token refresh, and user profile management.

import 'dart:async';
import 'dart:convert'; // For jsonDecode
import 'package:flutter/foundation.dart'; // For kIsWeb
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:openid_client/openid_client.dart' as oidc;
import 'package:openid_client/openid_client_io.dart'
    if (dart.library.html) 'package:openid_client/openid_client_browser.dart'
    as oidc_platform;
import 'package:pylabpraxis_flutter/src/core/error/exceptions.dart';
import 'package:pylabpraxis_flutter/src/data/models/user/user_profile.dart';
import 'auth_service.dart';
import 'package:url_launcher/url_launcher.dart';

// Keycloak Configuration (Replace with your actual values)
// These should ideally be sourced from a configuration file or environment variables.
const String _keycloakBaseUrl =
    'http://localhost:8080'; // Your Keycloak base URL
const String _keycloakRealm = 'praxis'; // Your Keycloak realm
const String _keycloakClientId =
    'pylabpraxis-flutter'; // Your Keycloak client ID for Flutter

// For mobile, this needs to be a custom scheme registered in your app.
// For web, this is a standard HTTP URL.
const String _keycloakRedirectScheme = kIsWeb ? 'http' : 'pylabpraxis';
const String _keycloakRedirectHost =
    kIsWeb ? 'localhost:3000' : 'auth'; // Or your web app's host/port
const String _keycloakRedirectPath =
    kIsWeb ? '/auth-callback.html' : '/callback';

class AuthServiceImpl implements AuthService {
  final FlutterSecureStorage _secureStorage;
  oidc.Issuer? _issuer;
  oidc.Client? _client;

  // Stream controller for user profile changes
  final StreamController<UserProfile?> _userProfileController =
      StreamController<UserProfile?>.broadcast();

  static const String _accessTokenKey = 'access_token';
  static const String _idTokenKey = 'id_token';
  static const String _refreshTokenKey = 'refresh_token';
  static const String _userProfileKey = 'user_profile';

  AuthServiceImpl({required FlutterSecureStorage secureStorage})
    : _secureStorage = secureStorage {
    _initialize();
  }

  Future<void> _initialize() async {
    try {
      final uri = Uri.parse('$_keycloakBaseUrl/realms/$_keycloakRealm');
      _issuer = await oidc.Issuer.discover(uri);
      _client = oidc.Client(
        _issuer!,
        _keycloakClientId,
        // No client secret for public clients (PKCE is used)
      );
      await _loadUserProfileFromStorage(); // Ensure this await is here if it was missing
    } catch (e, s) {
      debugPrint('AuthService Initialization Error: $e\n$s');
      // Handle initialization failure, maybe set a flag or notify
    }
  }

  Future<void> _loadUserProfileFromStorage() async {
    final userJson = await _secureStorage.read(key: _userProfileKey);
    if (userJson != null) {
      try {
        final userMap = jsonDecode(userJson) as Map<String, dynamic>;
        _userProfileController.add(UserProfile.fromJson(userMap));
      } catch (e) {
        debugPrint('Failed to load user profile from storage: $e');
        await _clearSession(); // Clear potentially corrupt data
      }
    } else {
      _userProfileController.add(null);
    }
  }

  Uri get _redirectUri {
    if (kIsWeb) {
      // For web, ensure the port is included if not standard (80/443)
      // This should match exactly what's configured in Keycloak
      final currentUri = Uri.base;
      // Use a fixed redirect URI for web to simplify Keycloak config
      return Uri(
        scheme: 'http',
        host: 'localhost',
        port: currentUri.port,
        path: '/auth-callback.html',
      );
    } else {
      // For mobile
      return Uri(
        scheme: _keycloakRedirectScheme,
        host: _keycloakRedirectHost,
        path: _keycloakRedirectPath,
      );
    }
  }

  @override
  Future<UserProfile> signIn() async {
    if (_issuer == null || _client == null) {
      await _initialize(); // Ensure client is initialized
      if (_issuer == null || _client == null) {
        throw AuthException(
          'Authentication service not initialized. Please try again.',
        );
      }
    }

    try {
      final authenticator = oidc_platform.Authenticator(
        _client!,
        scopes: ['openid', 'profile', 'email', 'roles'], // Standard OIDC scopes
        redirectUri: _redirectUri, // This is now a required named parameter
        urlLancher: (String url) async {
          // Corrected parameter name: urlLauncher
          final uri = Uri.parse(url);
          // For web, the library might handle the redirect itself.
          // For mobile, url_launcher opens the system browser or an in-app browser tab.
          if (!await launchUrl(uri, mode: LaunchMode.externalApplication)) {
            throw AuthException('Could not launch $url');
          }
        },
      );

      final oidc.Credential credential = await authenticator.authorize();
      // Close the in-app browser if it was used (primarily for mobile)
      if (kIsWeb == false) {
        // On mobile, if using an in-app browser tab, it might need to be closed.
        // `openid_client_io` with `url_launcher` usually handles this by returning to the app.
        // If using a package like `flutter_custom_tabs` or `flutter_inappwebview`,
        // you might need specific code here to close it.
        // For now, assume url_launcher handles the return correctly.
        // await closeInAppWebView(); // Example if using a custom webview
      }

      // Extract tokens and user info
      final oidc.TokenResponse tokenResponse =
          await credential.getTokenResponse();
      final String? accessToken = tokenResponse.accessToken;
      final String idToken = credential.idToken.toCompactSerialization();
      final String? refreshToken = tokenResponse.refreshToken;

      if (accessToken == null || idToken.isEmpty) {
        throw AuthException('Authentication failed: Missing tokens.');
      }

      await _secureStorage.write(key: _accessTokenKey, value: accessToken);
      await _secureStorage.write(key: _idTokenKey, value: idToken);
      if (refreshToken != null) {
        await _secureStorage.write(key: _refreshTokenKey, value: refreshToken);
      }

      final oidc.UserInfo userInfo = await credential.getUserInfo();
      final userProfile = UserProfile.fromJson(userInfo.toJson());

      await _secureStorage.write(
        key: _userProfileKey,
        value: jsonEncode(userProfile.toJson()),
      );
      _userProfileController.add(userProfile);

      return userProfile;
    } on oidc.OpenIdException catch (e, s) {
      debugPrint('OIDC SignIn Error: ${e.toString()}\n$s');
      throw AuthException(
        'Authentication failed: ${e.message} (${e.runtimeType})',
      );
    } catch (e, s) {
      debugPrint('SignIn Error: $e\n$s');
      throw AuthException(
        'An unexpected error occurred during sign-in: ${e.toString()}',
      );
    }
  }

  @override
  Future<void> signOut() async {
    if (_issuer == null || _client == null) {
      // Not much to do if not initialized, but ensure local is cleared.
      await _clearSession();
      return;
    }
    try {
      final idTokenHint = await _secureStorage.read(key: _idTokenKey);
      await _clearSession(); // Clear local tokens first

      if (idTokenHint != null) {
        // Check if issuer metadata contains end_session_endpoint
        final metadata = _issuer!.metadata;
        final endSessionEndpoint =
            metadata.endSessionEndpoint ??
            Uri.parse(
              '$_keycloakBaseUrl/realms/$_keycloakRealm/protocol/openid-connect/logout',
            );

        // Construct the logout URL
        final logoutUrl = endSessionEndpoint.replace(
          queryParameters: {
            'id_token_hint': idTokenHint,
            'post_logout_redirect_uri': _redirectUri.toString(),
          },
        );

        if (await canLaunchUrl(logoutUrl)) {
          await launchUrl(logoutUrl, mode: LaunchMode.externalApplication);
        } else {
          debugPrint('Could not launch Keycloak logout URL');
        }
      }
    } catch (e, s) {
      debugPrint('SignOut Error: $e\n$s');
      // Don't throw an exception if logout fails, as local session is cleared.
      // User will appear logged out in the app.
    }
  }

  Future<void> _clearSession() async {
    await _secureStorage.delete(key: _accessTokenKey);
    await _secureStorage.delete(key: _idTokenKey);
    await _secureStorage.delete(key: _refreshTokenKey);
    await _secureStorage.delete(key: _userProfileKey);
    _userProfileController.add(null);
  }

  @override
  Future<bool> isSignedIn() async {
    final accessToken = await _secureStorage.read(key: _accessTokenKey);
    if (accessToken == null) return false;

    // Optionally, add token expiration check here if not handled by interceptor
    // For simplicity, we assume a token means signed in for now.
    // Proper check would involve decoding JWT and checking 'exp' claim.
    // final idToken = await getIdToken();
    // if (idToken != null) {
    //   try {
    //     final decoded = oidc.IdToken.parseJwt(idToken);
    //     return decoded.isExpired == false;
    //   } catch (e) {
    //     return false; // Invalid token
    //   }
    // }
    return true;
  }

  @override
  Future<UserProfile?> getCurrentUser() async {
    final userJson = await _secureStorage.read(key: _userProfileKey);
    if (userJson != null) {
      try {
        return UserProfile.fromJson(
          jsonDecode(userJson) as Map<String, dynamic>,
        );
      } catch (e) {
        debugPrint('Error decoding stored user profile: $e');
        await _clearSession(); // Clear potentially corrupt data
        return null;
      }
    }
    return null;
  }

  @override
  Future<String?> getAccessToken() {
    return _secureStorage.read(key: _accessTokenKey);
  }

  @override
  Future<String?> getIdToken() {
    return _secureStorage.read(key: _idTokenKey);
  }

  @override
  Future<String?> refreshToken() async {
    if (_client == null) {
      throw AuthException('Auth client not initialized for token refresh.');
    }
    final storedRefreshToken = await _secureStorage.read(key: _refreshTokenKey);
    if (storedRefreshToken == null) {
      // No refresh token, user needs to sign in again.
      await _clearSession();
      throw AuthException('No refresh token available. Please sign in again.');
    }

    try {
      final credential = _client!.createCredential(
        refreshToken: storedRefreshToken,
      );
      final tokenResponse = await credential.getTokenResponse();

      // Check if the new access token is valid
      if (tokenResponse.accessToken == null) {
        await _clearSession(); // Clear session if refresh fails
        throw AuthException(
          'Token refresh failed to provide a new access token.',
        );
      }

      final newAccessToken = tokenResponse.accessToken;
      final newIdToken = tokenResponse.idToken.toCompactSerialization();
      final newRefreshToken = tokenResponse.refreshToken;

      if (newAccessToken == null) {
        await _clearSession(); // Clear session if refresh fails to get new access token
        throw AuthException(
          'Token refresh failed to provide a new access token.',
        );
      }

      await _secureStorage.write(key: _accessTokenKey, value: newAccessToken);
      await _secureStorage.write(key: _idTokenKey, value: newIdToken);

      if (newRefreshToken != null) {
        await _secureStorage.write(
          key: _refreshTokenKey,
          value: newRefreshToken,
        );
      } else {
        // If Keycloak doesn't return a new refresh token (e.g. "Refresh token reuse" is off)
        // keep the old one, or clear it if your policy requires it.
        // For simplicity, we assume a new one might be returned. If not, the old one remains.
      }

      // Optionally, re-fetch user info if it might change or if needed
      // final userInfo = await newCredential.getUserInfo();
      // final userProfile = UserProfile.fromJson(userInfo.toJson());
      // await _secureStorage.write(key: _userProfileKey, value: jsonEncode(userProfile.toJson()));
      // _userProfileController.add(userProfile);

      debugPrint('Token refreshed successfully.');
      return newAccessToken;
    } on oidc.OpenIdException catch (e) {
      debugPrint('OpenIdException during token refresh: ${e.message}');
      await _clearSession(); // Critical failure, clear session
      throw AuthException(
        'Session expired or invalid. Please sign in again. (Refresh Error: ${e.message})',
      );
    } catch (e, s) {
      debugPrint('Unexpected error during token refresh: $e\n$s');
      await _clearSession();
      throw AuthException(
        'An unexpected error occurred during token refresh. Please sign in again.',
      );
    }
  }

  @override
  Stream<UserProfile?> get userProfileStream => _userProfileController.stream;

  @override
  void dispose() {
    _userProfileController.close();
  }
}
