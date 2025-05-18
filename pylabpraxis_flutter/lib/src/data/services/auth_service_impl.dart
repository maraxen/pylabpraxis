// Concrete implementation of the [AuthService] using openid_client and flutter_secure_storage.
//
// This class handles OIDC authentication with Keycloak, secure token storage,
// token refresh, and user profile management, with platform-specific logic
// for web and mobile OIDC flows.

import 'dart:async';
import 'dart:convert'; // For jsonDecode
import 'package:flutter/foundation.dart'; // For kIsWeb, debugPrint
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:openid_client/openid_client.dart' as oidc;
// Conditional import for platform-specific Authenticator
import 'package:openid_client/openid_client_io.dart' as io_authenticator;
import 'package:openid_client/openid_client_browser.dart'
    as browser_authenticator;

import 'package:pylabpraxis_flutter/src/core/error/exceptions.dart';
import 'package:pylabpraxis_flutter/src/data/models/user/user_profile.dart';
import 'auth_service.dart';
import 'package:url_launcher/url_launcher.dart';

// Keycloak Configuration
const String _keycloakBaseUrl = 'http://localhost:8080';
const String _keycloakRealm = 'praxis';
const String _keycloakClientId =
    'pylabpraxis-flutter'; // Ensure this client ID exists in Keycloak

// --- Redirect URI Configuration ---

const String _mobileRedirectScheme = 'pylabpraxis';

const String _mobileRedirectHost = 'auth';

const String _webRedirectPath =
    '/auth-callback.html'; // Ensure this HTML file exists in web/
const String _mobileRedirectPath = '/callback';

class AuthServiceImpl implements AuthService {
  final FlutterSecureStorage _secureStorage;
  oidc.Issuer? _issuer;
  oidc.Client? _client;

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
      var uri = Uri.parse('$_keycloakBaseUrl/realms/$_keycloakRealm');
      // For Android emulator to connect to localhost on host machine
      if (!kIsWeb && defaultTargetPlatform == TargetPlatform.android) {
        uri = uri.replace(host: '10.0.2.2');
      }
      _issuer = await oidc.Issuer.discover(uri);
      _client = oidc.Client(_issuer!, _keycloakClientId);
      // Attempt to load user profile on initialization if tokens exist
      // Also, for web, check if this load is due to a redirect
      await _loadUserProfileFromStorage();
      if (kIsWeb) {
        // If on web, also try to complete any pending sign-in from a redirect
        // This is typically called when the app first loads or reloads after redirect.
        await completeWebSignInOnRedirect();
      }
    } catch (e, s) {
      debugPrint('AuthService Initialization Error: $e\n$s');
      _userProfileController.addError(
        AuthException('AuthService initialization failed: $e'),
      );
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
        await _clearSession();
      }
    } else {
      _userProfileController.add(null);
    }
  }

  Uri _getPlatformRedirectUri() {
    if (kIsWeb) {
      // Use Uri.base to construct the redirect URI based on where the app is currently hosted
      // This helps with dynamic ports during development.
      // The path /auth-callback.html should be consistent.
      return Uri.base.replace(path: _webRedirectPath);
    } else {
      return Uri(
        scheme: _mobileRedirectScheme,
        host: _mobileRedirectHost,
        path: _mobileRedirectPath,
      );
    }
  }

  // Helper to launch URL, common for mobile
  Future<void> _launchUrlForMobile(String url) async {
    final uri = Uri.parse(url);
    if (!await launchUrl(uri, mode: LaunchMode.externalApplication)) {
      throw AuthException('Could not launch $url');
    }
  }

  /// Processes a credential to extract tokens and user info, then stores them.
  Future<UserProfile> _processCredential(oidc.Credential credential) async {
    final tokenResponse = await credential.getTokenResponse();
    final accessToken = tokenResponse.accessToken;
    final idTokenString =
        credential.idToken.toCompactSerialization(); // Get compact JWT string
    final refreshToken = tokenResponse.refreshToken;

    if (accessToken == null || idTokenString.isEmpty) {
      throw AuthException(
        'Authentication failed: Missing tokens after processing credential.',
      );
    }

    await _secureStorage.write(key: _accessTokenKey, value: accessToken);
    await _secureStorage.write(key: _idTokenKey, value: idTokenString);
    if (refreshToken != null) {
      await _secureStorage.write(key: _refreshTokenKey, value: refreshToken);
    }

    final userInfo = await credential.getUserInfo();
    final userProfile = UserProfile.fromJson(userInfo.toJson());

    await _secureStorage.write(
      key: _userProfileKey,
      value: jsonEncode(userProfile.toJson()),
    );
    _userProfileController.add(userProfile); // Notify listeners
    return userProfile;
  }

  @override
  Future<UserProfile?> signIn() async {
    // Changed to UserProfile? to accommodate web
    if (_client == null) {
      await _initialize();
      if (_client == null) throw AuthException('Auth client not initialized.');
    }

    if (kIsWeb) {
      // For Web: Initiate redirect, result handled by completeWebSignInOnRedirect on app (re)load.
      final webAuthenticator = browser_authenticator.Authenticator(
        _client!,
        scopes: ['openid', 'profile', 'email', 'roles'],
        // redirectUri is not directly passed to browser.Authenticator;
        // it uses the client's configured redirectUris and window.location.
        // Ensure `_getPlatformRedirectUri()` for web is registered in Keycloak.
      );
      // This call navigates the browser away.
      webAuthenticator.authorize();
      // On web, signIn() initiates the redirect. It doesn't complete with UserProfile here.
      // Return null or throw a specific "Redirecting" signal if needed by BLoC.
      // For now, returning null implies the process isn't complete in this call.
      return null;
    } else {
      // For Mobile: Full authentication flow in this call.
      final mobileRedirectUri = _getPlatformRedirectUri();
      final ioAuth = io_authenticator.Authenticator(
        _client!,
        scopes: ['openid', 'profile', 'email', 'roles'],
        redirectUri: mobileRedirectUri,
        port: 4000, // Port for the local redirect listener on mobile.
        // Can be any available port. Keycloak redirects to `customScheme://host/path`
        // and the local server listens on `http://localhost:port` for that.
        urlLancher:
            _launchUrlForMobile, // Corrected typo from library: urlLancher
      );
      final credential = await ioAuth.authorize();
      // Close in-app browser if applicable (url_launcher usually handles return)
      // if (defaultTargetPlatform == TargetPlatform.ios || defaultTargetPlatform == TargetPlatform.android) {
      //   await closeInAppWebView(); // If using a package that needs manual closing
      // }
      return await _processCredential(credential);
    }
  }

  @override
  Future<UserProfile?> completeWebSignInOnRedirect() async {
    if (!kIsWeb || _client == null) return null;
    debugPrint("Attempting to complete web sign-in on redirect...");

    final webAuthenticator = browser_authenticator.Authenticator(
      _client!,
      scopes: ['openid', 'profile', 'email', 'roles'],
    );

    try {
      // .credential getter checks if the current URL contains auth response.
      final credential = await webAuthenticator.credential;
      if (credential != null) {
        debugPrint("Web redirect: Credential found!");
        return await _processCredential(credential);
      } else {
        debugPrint("Web redirect: No credential found in current URL.");
      }
    } on oidc.OpenIdException catch (e) {
      debugPrint(
        "OIDC error completing web sign-in: ${e.message} (Type: ${e.code})",
      );
      // "interaction_required", "login_required", "access_denied" are common if not an actual callback.
      if (e.code != "interaction_required" &&
          e.code != "login_required" &&
          e.code != "access_denied") {
        _userProfileController.addError(
          AuthException("Web redirect error: ${e.message}"),
        );
      }
    } catch (e, s) {
      debugPrint("Generic error completing web sign-in: $e\n$s");
      _userProfileController.addError(
        AuthException("Web redirect processing failed: $e"),
      );
    }
    return null;
  }

  @override
  Future<void> signOut() async {
    final String? idTokenHint = await _secureStorage.read(key: _idTokenKey);
    final currentPlatformRedirectUri = _getPlatformRedirectUri();

    await _clearSession();

    if (_issuer == null) {
      debugPrint('Cannot perform server logout: OIDC issuer not initialized.');
      return;
    }

    Uri? endSessionEndpoint = _issuer!.metadata.endSessionEndpoint;
    if (endSessionEndpoint == null) {
      debugPrint(
        'end_session_endpoint not found. Using fallback logout URL construction.',
      );
      endSessionEndpoint = Uri.parse(
        '$_keycloakBaseUrl/realms/$_keycloakRealm/protocol/openid-connect/logout',
      );
    }

    // For web, post_logout_redirect_uri should be the app's main page or login page.
    // For mobile, redirecting back to a custom scheme after logout might not always work
    // or be desired, sometimes just closing the browser tab is enough.
    // Keycloak needs a registered post_logout_redirect_uri.
    final postLogoutRedirect =
        kIsWeb ? currentPlatformRedirectUri.replace(path: '/') : null;

    Map<String, String> queryParams = {};
    if (idTokenHint != null) queryParams['id_token_hint'] = idTokenHint;
    if (postLogoutRedirect != null)
      queryParams['post_logout_redirect_uri'] = postLogoutRedirect.toString();
    // For some Keycloak versions/configs, 'client_id' might be needed or 'redirect_uri' as post_logout_redirect_uri
    // queryParams['client_id'] = _keycloakClientId;

    final logoutUrl = endSessionEndpoint.replace(
      queryParameters: queryParams.isNotEmpty ? queryParams : null,
    );

    try {
      if (await canLaunchUrl(logoutUrl)) {
        await launchUrl(logoutUrl, mode: LaunchMode.externalApplication);
      } else {
        debugPrint('Could not launch Keycloak logout URL: $logoutUrl');
      }
    } catch (e, s) {
      debugPrint('Error during server logout attempt: $e\n$s');
    }
  }

  Future<void> _clearSession() async {
    await _secureStorage.delete(key: _accessTokenKey);
    await _secureStorage.delete(key: _idTokenKey);
    await _secureStorage.delete(key: _refreshTokenKey);
    await _secureStorage.delete(key: _userProfileKey);
    _userProfileController.add(null);
    debugPrint('Local session cleared.');
  }

  @override
  Future<bool> isSignedIn() async {
    final accessToken = await _secureStorage.read(key: _accessTokenKey);
    if (accessToken == null) return false;

    final idTokenString = await getIdToken();
    if (idTokenString != null) {
      try {
        final idToken = oidc.IdToken.unverified(idTokenString);
        final expiration = idToken.claims.expiry;
        if (expiration.isBefore(
          DateTime.now().toUtc().add(const Duration(seconds: 10)),
        )) {
          // 10s buffer
          debugPrint('ID token is expired or about to expire.');
          // Attempt a silent refresh if a refresh token exists
          if (await _secureStorage.read(key: _refreshTokenKey) != null) {
            try {
              final newAccessToken = await refreshToken();
              return newAccessToken != null; // Signed in if refresh succeeded
            } catch (e) {
              debugPrint("Silent refresh failed during isSignedIn check: $e");
              await _clearSession();
              return false;
            }
          }
          await _clearSession(); // No refresh token, or refresh failed
          return false;
        }
        return true;
      } catch (e) {
        debugPrint('Error parsing ID token for expiration check: $e');
        await _clearSession();
        return false;
      }
    }
    // If only access token exists but no id token (should not happen in OIDC normally)
    // or if id token check fails, consider not signed in.
    await _clearSession();
    return false;
  }

  @override
  Future<UserProfile?> getCurrentUser() async {
    // Check if signed in first, this might trigger a refresh if token is near expiry
    if (!await isSignedIn()) {
      return null;
    }
    final userJson = await _secureStorage.read(key: _userProfileKey);
    if (userJson != null) {
      try {
        return UserProfile.fromJson(
          jsonDecode(userJson) as Map<String, dynamic>,
        );
      } catch (e) {
        debugPrint('Error decoding stored user profile: $e');
        await _clearSession();
        return null;
      }
    }
    // If user profile is somehow missing but tokens are valid, try to refetch.
    // This might happen if storage was cleared partially.
    // For simplicity, current implementation relies on profile being stored during login/refresh.
    return null;
  }

  @override
  Future<String?> getAccessToken() async {
    if (!await isSignedIn()) return null; // Check and refresh if needed
    return _secureStorage.read(key: _accessTokenKey);
  }

  @override
  Future<String?> getIdToken() async {
    if (!await isSignedIn()) return null; // Check and refresh if needed
    return _secureStorage.read(key: _idTokenKey);
  }

  @override
  Future<String?> refreshToken() async {
    if (_client == null) {
      await _initialize();
      if (_client == null) {
        throw AuthException('Auth client not initialized for token refresh.');
      }
    }
    final storedRefreshToken = await _secureStorage.read(key: _refreshTokenKey);
    if (storedRefreshToken == null) {
      await _clearSession();
      throw AuthException('No refresh token available. Please sign in again.');
    }

    try {
      final credential = _client!.createCredential(
        refreshToken: storedRefreshToken,
      );

      final refreshedTokenResponse = await credential.getTokenResponse();

      final newAccessToken = refreshedTokenResponse.accessToken;
      final newIdTokenString =
          refreshedTokenResponse.idToken.toCompactSerialization();
      final newRefreshToken =
          refreshedTokenResponse
              .refreshToken; // Keycloak might return a new one

      if (newAccessToken == null) {
        await _clearSession();
        throw AuthException(
          'Token refresh failed to provide a new access token.',
        );
      }

      await _secureStorage.write(key: _accessTokenKey, value: newAccessToken);
      await _secureStorage.write(key: _idTokenKey, value: newIdTokenString);
      if (newRefreshToken != null) {
        await _secureStorage.write(
          key: _refreshTokenKey,
          value: newRefreshToken,
        );
      }

      // Update user profile after successful refresh
      final oidc.UserInfo userInfo = await credential.getUserInfo();
      final userProfile = UserProfile.fromJson(userInfo.toJson());
      await _secureStorage.write(
        key: _userProfileKey,
        value: jsonEncode(userProfile.toJson()),
      );
      _userProfileController.add(userProfile);

      debugPrint('Token refreshed successfully.');
      return newAccessToken;
    } on oidc.OpenIdException catch (e) {
      debugPrint(
        'OpenIdException during token refresh: ${e.message} (Type: ${e.code})',
      );
      if (e.code == 'invalid_grant') {
        await _clearSession(); // Refresh token is invalid or expired
        throw AuthException('Session expired. Please sign in again.');
      }
      // For other OIDC errors during refresh, also clear session as it's likely unrecoverable
      await _clearSession();
      throw AuthException(
        'Token refresh failed: ${e.message}. Please sign in again.',
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
