// Concrete implementation of the [AuthService] using openid_client and flutter_secure_storage.
//
// This class handles OIDC authentication with Keycloak, secure token storage,
// token refresh, and user profile management, using a platform-specific
// OIDC authenticator wrapper.

import 'dart:async';
import 'dart:convert'; // For jsonDecode
import 'package:flutter/foundation.dart'; // For kIsWeb, debugPrint, defaultTargetPlatform
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:openid_client/openid_client.dart' as oidc;
// Import the OidcAuthenticatorWrapper via the stub file
import 'oidc/oidc_authenticator.dart';
import 'package:pylabpraxis_flutter/src/core/error/exceptions.dart';
import 'package:pylabpraxis_flutter/src/data/models/user/user_profile.dart';
import 'auth_service.dart';
import 'package:url_launcher/url_launcher.dart'; // Still needed for explicit logout launch

// Keycloak Configuration
const String _keycloakBaseUrl = 'http://localhost:8080';
const String _keycloakRealm = 'praxis';
const String _keycloakClientId = 'pylabpraxis-flutter';

// --- Redirect URI Configuration ---
const String _mobileRedirectScheme = 'pylabpraxis';
const String _mobileRedirectHost = 'auth';
const String _mobileRedirectPath = '/callback';

const String _webRedirectPath =
    '/auth-callback.html'; // Ensure this HTML file exists in web/

class AuthServiceImpl implements AuthService {
  final FlutterSecureStorage _secureStorage;
  oidc.Issuer? _issuer;
  oidc.Client? _client;
  OidcAuthenticatorWrapper? _authenticatorWrapper; // Instance of the wrapper

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
      if (!kIsWeb && defaultTargetPlatform == TargetPlatform.android) {
        uri = uri.replace(host: '10.0.2.2');
      }
      _issuer = await oidc.Issuer.discover(uri);
      _client = oidc.Client(_issuer!, _keycloakClientId);

      // Instantiate the platform-specific wrapper using the factory constructor
      if (_client != null) {
        _authenticatorWrapper = OidcAuthenticatorWrapper(
          client: _client!,
          scopes: ['openid', 'profile', 'email', 'roles'],
          redirectUri:
              _getPlatformRedirectUri(), // Pass it always; IO impl will use it.
          port: 4000, // Pass it always; IO impl will use it.
        );
      } else {
        throw StateError("OIDC Client failed to initialize.");
      }

      await _loadUserProfileFromStorage();
      if (kIsWeb) {
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
      return Uri.base.replace(path: _webRedirectPath);
    } else {
      return Uri(
        scheme: _mobileRedirectScheme,
        host: _mobileRedirectHost,
        path: _mobileRedirectPath,
      );
    }
  }

  Future<UserProfile> _processCredential(oidc.Credential credential) async {
    // This method remains largely the same
    final tokenResponse = await credential.getTokenResponse();
    final accessToken = tokenResponse.accessToken;
    final idTokenString = credential.idToken.toCompactSerialization();
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
    _userProfileController.add(userProfile);
    return userProfile;
  }

  @override
  Future<UserProfile?> signIn() async {
    if (_authenticatorWrapper == null) {
      await _initialize(); // Ensure wrapper is created
      if (_authenticatorWrapper == null) {
        throw AuthException('Auth service/wrapper not initialized.');
      }
    }

    try {
      final credential = await _authenticatorWrapper!.authorize();
      if (credential != null) {
        // Typically for mobile
        return await _processCredential(credential);
      }
      // For web, authorize() initiates redirect and credential will be null here.
      // completeWebSignInOnRedirect will handle it.
      return null;
    } on oidc.OpenIdException catch (e, s) {
      debugPrint('OIDC SignIn Error: ${e.toString()}\n$s');
      String errorMessage = 'Authentication error';
      throw AuthException(errorMessage);
    } catch (e, s) {
      debugPrint('SignIn Error: $e\n$s');
      throw AuthException(
        'An unexpected error occurred during sign-in: ${e.toString()}',
      );
    }
  }

  @override
  Future<UserProfile?> completeWebSignInOnRedirect() async {
    if (!kIsWeb || _authenticatorWrapper == null) return null;
    debugPrint("Attempting to complete web sign-in on redirect...");

    try {
      final credential = await _authenticatorWrapper!.processRedirect();
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

  // signOut, _clearSession, isSignedIn, getCurrentUser, getAccessToken, getIdToken, refreshToken, userProfileStream, dispose
  // methods remain largely the same as in the previous version of AuthServiceImpl,
  // but ensure they use _client and _issuer which are initialized.
  // Refresh token might also use _client.createCredential directly.

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
      // Construct a common logout URL if not in metadata
      endSessionEndpoint = Uri.parse(
        '$_keycloakBaseUrl/realms/$_keycloakRealm/protocol/openid-connect/logout',
      );
    }

    final postLogoutRedirect =
        kIsWeb ? currentPlatformRedirectUri.replace(path: '/') : null;

    Map<String, String> queryParams = {};
    if (idTokenHint != null) queryParams['id_token_hint'] = idTokenHint;
    // Keycloak requires post_logout_redirect_uri to be registered in the client settings if used.
    if (postLogoutRedirect != null) {
      queryParams['post_logout_redirect_uri'] = postLogoutRedirect.toString();
    }
    // queryParams['client_id'] = _keycloakClientId; // Sometimes needed

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

    final idTokenString =
        await getIdTokenFromStorage(); // Use a direct storage read
    if (idTokenString != null) {
      try {
        final idToken = oidc.IdToken.unverified(
          idTokenString,
        ); // Parse without verification for exp check
        final expiration = idToken.claims.expiry;
        if (expiration.isBefore(
          DateTime.now().toUtc().add(const Duration(seconds: 10)),
        )) {
          debugPrint(
            'ID token is expired or about to expire. Attempting refresh.',
          );
          if (await _secureStorage.read(key: _refreshTokenKey) != null) {
            try {
              final newAccessToken = await refreshToken();
              return newAccessToken != null;
            } catch (e) {
              debugPrint("Silent refresh failed during isSignedIn check: $e");
              await _clearSession();
              return false;
            }
          }
          await _clearSession();
          return false;
        }
        return true;
      } catch (e) {
        debugPrint('Error parsing ID token for expiration check: $e');
        await _clearSession();
        return false;
      }
    }
    await _clearSession();
    return false;
  }

  Future<String?> getIdTokenFromStorage() {
    // Helper for direct storage access
    return _secureStorage.read(key: _idTokenKey);
  }

  @override
  Future<UserProfile?> getCurrentUser() async {
    if (!await isSignedIn()) {
      // This now includes a potential refresh
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
    // If profile is missing but tokens are valid (e.g. after refresh without profile re-fetch in some flows)
    // one might try to fetch it here, but for now, rely on it being stored.
    return null;
  }

  @override
  Future<String?> getAccessToken() async {
    if (!await isSignedIn()) return null;
    return _secureStorage.read(key: _accessTokenKey);
  }

  @override
  Future<String?> getIdToken() async {
    if (!await isSignedIn()) return null;
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

      final refreshedTokenResponse =
          await credential.getTokenResponse(); // This might throw if invalid

      final newAccessToken = refreshedTokenResponse.accessToken;
      final newIdTokenString =
          refreshedTokenResponse.idToken.toCompactSerialization();
      final newRefreshToken = refreshedTokenResponse.refreshToken;

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
      final refreshedCredential = _client!.createCredential(
        refreshToken: storedRefreshToken,
      );

      final userInfo = await refreshedCredential.getUserInfo();
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
        await _clearSession();
        throw AuthException('Session expired. Please sign in again.');
      }
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
