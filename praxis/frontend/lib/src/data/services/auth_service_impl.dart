// Concrete implementation of the [AuthService] using openid_client and flutter_secure_storage.
//
// This class handles OIDC authentication with Keycloak, and uses flutter_secure_storage
// for token and user profile persistence across all platforms (mobile and web).
// For web, it utilizes WebCrypto via flutter_secure_storage's experimental web implementation.
// It uses a platform-specific OIDC authenticator wrapper.

import 'dart:async';
import 'dart:developer' as developer;
import 'dart:convert'; // For jsonDecode
import 'package:flutter/foundation.dart'; // For kIsWeb, debugPrint, defaultTargetPlatform
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:openid_client/openid_client.dart' as oidc;
// Import the OidcAuthenticatorWrapper via the stub file
import 'oidc/oidc_authenticator.dart';
import 'package:praxis_lab_management/src/core/error/exceptions.dart';
import 'package:praxis_lab_management/src/data/models/user/user_profile.dart';
import 'auth_service.dart';
import 'package:url_launcher/url_launcher.dart'; // Still needed for explicit logout launch

// Keycloak Configuration
const String _keycloakBaseUrl = 'http://localhost:8080';
const String _keycloakRealm = 'praxis';
const String _keycloakClientId = 'praxis-flutter';

// --- Redirect URI Configuration ---
const String _mobileRedirectScheme = 'pylabpraxis';
const String _mobileRedirectHost = 'auth';
const String _mobileRedirectPath = '/callback';

const String _webRedirectPath =
    '/splash'; // Ensure this HTML file exists in web/

class AuthServiceImpl implements AuthService {
  final FlutterSecureStorage _secureStorage;

  oidc.Issuer? _issuer;
  oidc.Client? _client;
  OidcAuthenticatorWrapper? _authenticatorWrapper; // Instance of the wrapper

  final StreamController<UserProfile?> _userProfileController =
      StreamController<UserProfile?>.broadcast();

  // Keys for FlutterSecureStorage (used for all platforms)
  static const String _storageAccessTokenKey = 'access_token';
  static const String _storageIdTokenKey = 'id_token';
  static const String _storageRefreshTokenKey = 'refresh_token';
  static const String _storageUserProfileKey = 'user_profile';

  AuthServiceImpl({
    required FlutterSecureStorage secureStorage,
  }) // Made secureStorage required
  : _secureStorage = secureStorage {
    _initialize();
  }

  Future<void> _initialize() async {
    debugPrint("AuthService: Initializing...");
    try {
      var uri = Uri.parse('$_keycloakBaseUrl/realms/$_keycloakRealm');
      if (!kIsWeb && defaultTargetPlatform == TargetPlatform.android) {
        uri = uri.replace(host: '10.0.2.2');
        debugPrint(
          "AuthService: Android emulator detected, using host 10.0.2.2 for Keycloak discovery.",
        );
      }
      _issuer = await oidc.Issuer.discover(uri);
      _client = oidc.Client(_issuer!, _keycloakClientId);
      debugPrint("AuthService: OIDC Issuer and Client initialized.");
      debugPrint(
        "AuthService: Using FlutterSecureStorage instance: $_secureStorage",
      );
      // Log web options if on web
      // Note: We can't directly access webOptions from the instance here easily.
      // This check should be done where FlutterSecureStorage is instantiated.
      if (kIsWeb) {
        debugPrint(
          "AuthService (Web): Ensure FlutterSecureStorage was initialized with valid WebOptions (wrapKey, wrapKeyIv) in your DI setup (e.g., main.dart).",
        );
      }

      if (_client != null) {
        _authenticatorWrapper = OidcAuthenticatorWrapper(
          client: _client!,
          scopes: ['openid', 'profile', 'email', 'roles'],
          redirectUri: _getPlatformRedirectUri(),
          port: 4000,
        );
        debugPrint("AuthService: OIDC Authenticator Wrapper created.");
      } else {
        debugPrint(
          "AuthService: OIDC Client failed to initialize. Cannot create Authenticator Wrapper.",
        );
        throw StateError("OIDC Client failed to initialize.");
      }

      await _loadUserProfileFromStorage();

      if (kIsWeb) {
        debugPrint(
          "AuthService: Web platform detected. Checking for redirect result...",
        );
        await completeWebSignInOnRedirect();
      }
      debugPrint(
        "AuthService: Initialization complete. Current user profile on stream: ${await _userProfileController.stream.firstWhere((element) => true, orElse: () => null)}",
      );
    } catch (e, s) {
      debugPrint('AuthService Initialization Error: $e\n$s');
      _userProfileController.addError(
        AuthException('AuthService initialization failed: $e'),
      );
    }
  }

  Future<void> _loadUserProfileFromStorage() async {
    debugPrint(
      "AuthService: Attempting to load user profile from flutter_secure_storage...",
    );
    try {
      final userJson = await _secureStorage.read(key: _storageUserProfileKey);
      if (userJson != null) {
        final userMap = jsonDecode(userJson) as Map<String, dynamic>;
        final userProfile = UserProfile.fromJson(userMap);
        _userProfileController.add(userProfile);
        debugPrint(
          "AuthService: Loaded profile from storage: ${userProfile.name}",
        );
      } else {
        _userProfileController.add(null);
        debugPrint("AuthService: No user profile found in storage.");
      }
    } catch (e, s) {
      debugPrint(
        'AuthService: Error loading user profile from storage: $e\nStack trace:\n$s',
      );
      await _clearSession();
      _userProfileController.add(null);
    }
  }

  Uri _getPlatformRedirectUri() {
    final currentBase = Uri.base;
    print(
      'AuthServiceImpl._getPlatformRedirectUri: Uri.base is "$currentBase"',
    );
    developer.log(
      'AuthServiceImpl._getPlatformRedirectUri: Uri.base is "$currentBase"',
      name: 'AuthService',
    );
    Uri platformRedirectUri;
    if (kIsWeb) {
      platformRedirectUri = currentBase.replace(path: _webRedirectPath);
    } else {
      // ... mobile logic ...
      platformRedirectUri = Uri(
        // Example for mobile
        scheme: _mobileRedirectScheme, // Make sure these are defined
        host: _mobileRedirectHost, // Make sure these are defined
        path: _mobileRedirectPath, // Make sure these are defined
      );
    }
    print(
      'AuthServiceImpl._getPlatformRedirectUri: Calculated redirect URI is "$platformRedirectUri"',
    );
    developer.log(
      'AuthServiceImpl._getPlatformRedirectUri: Calculated redirect URI is "$platformRedirectUri"',
      name: 'AuthService',
    );
    return platformRedirectUri;
  }

  Future<UserProfile> _processCredential(oidc.Credential credential) async {
    debugPrint("AuthService: Processing new credential...");
    final tokenResponse = await credential.getTokenResponse();
    debugPrint("AuthService: Token response received.");
    debugPrint(
      "AuthService: Token response received: ${tokenResponse.toJson()}",
    ); // Log token response
    final accessToken = tokenResponse.accessToken;
    if (accessToken == null) {
      debugPrint(
        "AuthService: Access token is null. Cannot process credential.",
      );
      throw AuthException('Access token is null. Cannot process credential.');
    }
    final idTokenString = credential.idToken.toCompactSerialization();
    if (idTokenString.isEmpty) {
      debugPrint(
        "AuthService: ID token string is empty. Cannot process credential.",
      );
      throw AuthException(
        'ID token string is empty. Cannot process credential.',
      );
    }
    final refreshToken = tokenResponse.refreshToken;
    debugPrint("AuthService: refreshToken: $refreshToken");

    debugPrint("AuthService: AccessToken: $accessToken");
    debugPrint(
      "AuthService: IdTokenString: ${idTokenString.isNotEmpty ? "Present" : "EMPTY"}",
    );
    debugPrint(
      "AuthService: RefreshToken: ${refreshToken != null ? "Present" : "NULL"}",
    );

    if (idTokenString.isEmpty) {
      debugPrint(
        "AuthService: Authentication failed - missing critical tokens (access or ID) after processing credential.",
      );
      throw AuthException(
        'Authentication failed: Missing critical tokens after processing credential.',
      );
    }

    final userInfo = await credential.getUserInfo();
    final userInfoJson = userInfo.toJson();
    debugPrint(
      "AuthService: Raw UserInfo from OIDC provider: $userInfoJson",
    ); // Log raw user info

    final UserProfile userProfile;
    try {
      userProfile = UserProfile.fromJson(userInfoJson);
      debugPrint(
        "AuthService: User profile successfully parsed: ${userProfile.name}",
      );
    } catch (e, s) {
      debugPrint(
        "AuthService: Error parsing UserInfo into UserProfile: $e\nStack trace:\n$s",
      );
      throw AuthException("Failed to parse user profile: $e");
    }

    try {
      await _secureStorage.write(
        key: _storageAccessTokenKey,
        value: accessToken,
      );
      await _secureStorage.write(key: _storageIdTokenKey, value: idTokenString);
      if (refreshToken != null) {
        await _secureStorage.write(
          key: _storageRefreshTokenKey,
          value: refreshToken,
        );
      } else {
        // Explicitly delete if null to avoid old refresh token issues, or ensure it's handled if nullable.
        // For now, we only write if not null. If it should clear an old one, add delete here.
        await _secureStorage.delete(key: _storageRefreshTokenKey);
        debugPrint(
          "AuthService: No refresh token in this credential, ensuring any old one is cleared from storage.",
        );
      }
      await _secureStorage.write(
        key: _storageUserProfileKey,
        value: jsonEncode(
          userProfile.toJson(),
        ), // toJson on your UserProfile model
      );
      debugPrint(
        "AuthService: Tokens and profile stored in flutter_secure_storage.",
      );
    } catch (e, s) {
      debugPrint(
        "AuthService: Error writing to flutter_secure_storage: $e\nStack trace:\n$s",
      );
      throw AuthException("Failed to store session: $e");
    }

    _userProfileController.add(userProfile);
    return userProfile;
  }

  @override
  Future<UserProfile?> signIn() async {
    // ... (no changes in this part, keep as is)
    if (_authenticatorWrapper == null) {
      debugPrint(
        "AuthService: Authenticator wrapper not initialized. Re-initializing...",
      );
      await _initialize();
      if (_authenticatorWrapper == null) {
        debugPrint(
          "AuthService: FATAL - Auth service/wrapper still not initialized after re-attempt.",
        );
        throw AuthException('Auth service/wrapper not initialized.');
      }
    }
    debugPrint("AuthService: Initiating sign-in flow...");
    try {
      final credential = await _authenticatorWrapper!.authorize();
      if (credential != null) {
        debugPrint(
          "AuthService: Credential received directly from authorize() (likely mobile). Processing...",
        );
        return await _processCredential(credential);
      }
      debugPrint(
        "AuthService: authorize() returned null (likely web redirect initiated). Waiting for redirect completion.",
      );
      return null;
    } on oidc.OpenIdException catch (e, s) {
      debugPrint(
        'AuthService: OIDC SignIn Error: ${e.toString()}\nStack trace:\n$s',
      );
      String errorMessage = 'Authentication error: ${e.message}';
      if (e.code != null) errorMessage += ' (Code: ${e.code})';
      throw AuthException(errorMessage);
    } catch (e, s) {
      debugPrint('AuthService: Generic SignIn Error: $e\nStack trace:\n$s');
      throw AuthException(
        'An unexpected error occurred during sign-in: ${e.toString()}',
      );
    }
  }

  @override
  Future<UserProfile?> completeWebSignInOnRedirect() async {
    if (!kIsWeb || _authenticatorWrapper == null) {
      return null;
    }
    debugPrint(
      "AuthService (Web): Attempting to complete web sign-in on redirect...",
    );

    try {
      final credential = await _authenticatorWrapper!.processRedirect();
      if (credential != null) {
        debugPrint(
          "AuthService (Web): Credential found from redirect! Processing...",
        );
        return await _processCredential(credential);
      } else {
        debugPrint(
          "AuthService (Web): No credential found in current URL from redirect. This is normal on initial load or if not an auth callback.",
        );
      }
    } on oidc.OpenIdException catch (e, s) {
      // Added stack trace s
      debugPrint(
        "AuthService (Web): OIDC error completing web sign-in: ${e.message} (Type: ${e.code})\nStack trace:\n$s",
      );
      if (e.code != "interaction_required" &&
          e.code != "login_required" &&
          e.code != "access_denied" &&
          e.message?.contains("No authentication response found in query") ==
              false &&
          e.message?.contains("State mismatch") == false) {
        _userProfileController.addError(
          AuthException(
            "Web redirect OIDC error: ${e.message}. Check console for stack trace.",
          ),
        );
      }
    } catch (e, s) {
      // Added stack trace s
      debugPrint(
        "AuthService (Web): Generic error completing web sign-in: $e\nStack trace:\n$s",
      );
      _userProfileController.addError(
        AuthException(
          "Web redirect processing failed: $e. Check console for stack trace.",
        ),
      );
    }
    return null;
  }

  @override
  Future<void> signOut() async {
    // ... (no changes in this part, keep as is)
    debugPrint("AuthService: Initiating sign-out...");
    String? idTokenHint;
    try {
      idTokenHint = await _secureStorage.read(key: _storageIdTokenKey);
    } catch (e, s) {
      debugPrint(
        "AuthService: Error reading id_token_hint from storage during signout: $e\n$s",
      );
    }

    final currentPlatformRedirectUri = _getPlatformRedirectUri();
    await _clearSession();

    if (_issuer == null) {
      debugPrint(
        'AuthService: Cannot perform server logout: OIDC issuer not initialized.',
      );
      return;
    }

    Uri? endSessionEndpoint = _issuer!.metadata.endSessionEndpoint;
    if (endSessionEndpoint == null) {
      debugPrint(
        'AuthService: end_session_endpoint not found. Using fallback logout URL construction.',
      );
      endSessionEndpoint = Uri.parse(
        '$_keycloakBaseUrl/realms/$_keycloakRealm/protocol/openid-connect/logout',
      );
    }

    final postLogoutRedirect =
        kIsWeb ? currentPlatformRedirectUri.replace(path: '/') : null;
    Map<String, String> queryParams = {};
    if (idTokenHint != null) queryParams['id_token_hint'] = idTokenHint;
    if (postLogoutRedirect != null) {
      queryParams['post_logout_redirect_uri'] = postLogoutRedirect.toString();
    }

    final logoutUrl = endSessionEndpoint.replace(
      queryParameters: queryParams.isNotEmpty ? queryParams : null,
    );
    debugPrint("AuthService: Constructed logout URL: $logoutUrl");

    try {
      if (await canLaunchUrl(logoutUrl)) {
        await launchUrl(
          logoutUrl,
          mode:
              kIsWeb
                  ? LaunchMode.platformDefault
                  : LaunchMode.externalApplication,
          webOnlyWindowName: kIsWeb ? '_self' : null,
        );
        debugPrint("AuthService: Logout URL launched.");
      } else {
        debugPrint(
          'AuthService: Could not launch Keycloak logout URL: $logoutUrl',
        );
      }
    } catch (e, s) {
      debugPrint('AuthService: Error during server logout attempt: $e\n$s');
    }
  }

  Future<void> _clearSession() async {
    // ... (no changes in this part, keep as is)
    try {
      await _secureStorage.delete(key: _storageAccessTokenKey);
      await _secureStorage.delete(key: _storageIdTokenKey);
      await _secureStorage.delete(key: _storageRefreshTokenKey);
      await _secureStorage.delete(key: _storageUserProfileKey);
      debugPrint('AuthService: Session cleared from flutter_secure_storage.');
    } catch (e, s) {
      debugPrint(
        'AuthService: Error clearing session from flutter_secure_storage: $e\n$s',
      );
    }
    _userProfileController.add(null);
  }

  @override
  Future<bool> isSignedIn() async {
    // ... (no changes in this part, keep as is)
    debugPrint("AuthService: Checking isSignedIn status...");
    String? accessToken;
    String? idTokenString;
    String? refreshTokenString;

    try {
      accessToken = await _secureStorage.read(key: _storageAccessTokenKey);
      idTokenString = await _secureStorage.read(key: _storageIdTokenKey);
      refreshTokenString = await _secureStorage.read(
        key: _storageRefreshTokenKey,
      );
    } catch (e, s) {
      debugPrint(
        "AuthService: Error reading tokens during isSignedIn check: $e\n$s. Assuming not signed in.",
      );
      await _clearSession();
      return false;
    }

    if (accessToken == null || idTokenString == null) {
      debugPrint(
        "AuthService: No access or ID token found. User is not signed in.",
      );
      return false;
    }

    try {
      final idToken = oidc.IdToken.unverified(idTokenString);
      final expiration = idToken.claims.expiry;
      if (expiration.isBefore(
        DateTime.now().toUtc().add(const Duration(seconds: 30)),
      )) {
        debugPrint(
          'AuthService: ID token is expired or about to expire. Attempting refresh.',
        );
        if (refreshTokenString != null) {
          try {
            final newAccessToken = await refreshToken();
            final result = newAccessToken != null;
            debugPrint(
              "AuthService: Token refresh attempt during isSignedIn check result: $result",
            );
            return result;
          } catch (e) {
            debugPrint(
              "AuthService: Silent refresh failed during isSignedIn check: $e. Clearing session.",
            );
            await _clearSession();
            return false;
          }
        } else {
          debugPrint(
            "AuthService: No refresh token available for expired session. Clearing session.",
          );
          await _clearSession();
          return false;
        }
      }
      debugPrint("AuthService: ID token is valid. User is signed in.");
      return true;
    } catch (e, s) {
      // Added stack trace s
      debugPrint(
        'AuthService: Error parsing ID token for expiration check: $e\nStack trace:\n$s. Clearing session.',
      );
      await _clearSession();
      return false;
    }
  }

  @override
  Future<UserProfile?> getCurrentUser() async {
    // ... (no changes in this part, keep as is)
    debugPrint("AuthService: Getting current user...");
    if (!await isSignedIn()) {
      debugPrint("AuthService: Not signed in, cannot get current user.");
      return null;
    }
    try {
      final userJson = await _secureStorage.read(key: _storageUserProfileKey);
      if (userJson != null) {
        final profile = UserProfile.fromJson(
          jsonDecode(userJson) as Map<String, dynamic>,
        );
        debugPrint(
          "AuthService: Returning user profile from storage: ${profile.name}",
        );
        return profile;
      }
      debugPrint(
        "AuthService: User profile JSON not found in storage, though tokens might be valid.",
      );
      return null;
    } catch (e, s) {
      debugPrint(
        'AuthService: Error reading/decoding stored user profile: $e\n$s. Clearing session.',
      );
      await _clearSession();
      return null;
    }
  }

  @override
  Future<String?> getAccessToken() async {
    // ... (no changes in this part, keep as is)
    if (!await isSignedIn()) {
      debugPrint(
        "AuthService: Not signed in or token expired, cannot get access token.",
      );
      return null;
    }
    try {
      return await _secureStorage.read(key: _storageAccessTokenKey);
    } catch (e, s) {
      debugPrint("AuthService: Error reading access token: $e\n$s");
      return null;
    }
  }

  @override
  Future<String?> getIdToken() async {
    // ... (no changes in this part, keep as is)
    if (!await isSignedIn()) {
      debugPrint(
        "AuthService: Not signed in or token expired, cannot get ID token.",
      );
      return null;
    }
    try {
      return await _secureStorage.read(key: _storageIdTokenKey);
    } catch (e, s) {
      debugPrint("AuthService: Error reading ID token: $e\n$s");
      return null;
    }
  }

  @override
  Future<String?> refreshToken() async {
    // ... (no changes in this part, keep as is)
    debugPrint("AuthService: Attempting to refresh token...");
    if (_client == null) {
      debugPrint(
        "AuthService: OIDC client not initialized. Attempting re-initialization for token refresh.",
      );
      await _initialize();
      if (_client == null) {
        debugPrint(
          "AuthService: FATAL - OIDC client still not initialized. Cannot refresh token.",
        );
        throw AuthException('Auth client not initialized for token refresh.');
      }
    }

    String? storedRefreshToken;
    try {
      storedRefreshToken = await _secureStorage.read(
        key: _storageRefreshTokenKey,
      );
    } catch (e, s) {
      debugPrint(
        "AuthService: Error reading refresh token from storage: $e\n$s",
      );
      await _clearSession();
      throw AuthException(
        'Failed to read refresh token. Please sign in again.',
      );
    }

    if (storedRefreshToken == null) {
      debugPrint("AuthService: No refresh token available. Clearing session.");
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
      final newRefreshToken = refreshedTokenResponse.refreshToken;

      if (newAccessToken == null) {
        debugPrint(
          "AuthService: Token refresh failed to provide a new access token. Clearing session.",
        );
        await _clearSession();
        throw AuthException(
          'Token refresh failed to provide a new access token.',
        );
      }

      UserProfile? userProfileToStore;
      try {
        final refreshedUserCredential = _client!.createCredential(
          accessToken: newAccessToken,
          idToken: newIdTokenString,
          refreshToken: newRefreshToken ?? storedRefreshToken,
        );
        final userInfo = await refreshedUserCredential.getUserInfo();
        final userInfoJson = userInfo.toJson();
        debugPrint(
          "AuthService (Refresh): Raw UserInfo from OIDC provider: $userInfoJson",
        );
        userProfileToStore = UserProfile.fromJson(userInfoJson);
      } catch (e, s) {
        debugPrint(
          "AuthService (Refresh): Error parsing UserInfo into UserProfile: $e\nStack trace:\n$s",
        );
        // Decide if this is critical. For now, we'll proceed with token refresh
        // but the profile might not update.
      }

      await _secureStorage.write(
        key: _storageAccessTokenKey,
        value: newAccessToken,
      );
      await _secureStorage.write(
        key: _storageIdTokenKey,
        value: newIdTokenString,
      );
      if (newRefreshToken != null) {
        await _secureStorage.write(
          key: _storageRefreshTokenKey,
          value: newRefreshToken,
        );
      } else {
        // If OIDC provider doesn't roll refresh tokens, the old one might still be valid.
        // Or, if it's one-time use and no new one is issued, this effectively means no more refresh.
        // For safety, if no new refresh token is provided, consider clearing the old one if your policy is strict.
        // However, some providers expect you to reuse the old one if a new one isn't issued.
        // For now, we only write if a new one is present.
        debugPrint(
          "AuthService (Refresh): No new refresh token provided by server.",
        );
      }

      if (userProfileToStore != null) {
        await _secureStorage.write(
          key: _storageUserProfileKey,
          value: jsonEncode(userProfileToStore.toJson()),
        );
        _userProfileController.add(userProfileToStore);
      } else {
        _userProfileController.add(null);
      }

      debugPrint('AuthService: Token refreshed successfully.');
      return newAccessToken;
    } on oidc.OpenIdException catch (e, s) {
      debugPrint(
        'AuthService: OpenIdException during token refresh: ${e.message} (Type: ${e.code})\nStack trace:\n$s',
      );
      if (e.code == 'invalid_grant' ||
          e.message?.toLowerCase().contains("token is expired") == true) {
        debugPrint(
          "AuthService: Refresh token is invalid or expired. Clearing session.",
        );
        await _clearSession();
        throw AuthException(
          'Session expired. Please sign in again. (Reason: ${e.message})',
        );
      }
      await _clearSession();
      throw AuthException(
        'Token refresh failed: ${e.message}. Please sign in again.',
      );
    } catch (e, s) {
      debugPrint(
        'AuthService: Unexpected error during token refresh: $e\nStack trace:\n$s',
      );
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
    debugPrint("AuthService: Disposing...");
    _userProfileController.close();
  }
}
