// Defines the contract for authentication services.
//
// This abstract class serves as an interface for concrete implementations
// that will handle user authentication flows (e.g., OIDC with Keycloak),
// token management, and user session status.

import 'package:pylabpraxis_flutter/src/data/models/user/user_profile.dart';

/// Abstract interface for authentication services.
///
/// Implementations will handle interactions with an authentication provider
/// (like Keycloak via OIDC) to sign in, sign out, manage tokens,
/// and retrieve user information.
abstract class AuthService {
  /// Initiates the sign-in process.
  ///
  /// This typically involves redirecting the user to the authentication provider's
  /// login page and handling the callback to obtain tokens.
  ///
  /// Returns [UserProfile] if sign-in is successful, otherwise throws [AuthException].
  Future<UserProfile?> signIn();

  /// Signs the user out.
  ///
  /// This involves clearing local session data (tokens) and potentially
  /// invalidating the session with the authentication provider.
  /// Throws [AuthException] if sign-out fails.
  Future<void> signOut();

  /// Checks if a user is currently signed in.
  ///
  /// Returns `true` if a valid session (e.g., non-expired access token) exists,
  /// `false` otherwise.
  Future<bool> isSignedIn();

  /// Retrieves the current authenticated user's profile.
  ///
  /// Returns [UserProfile] if the user is signed in, `null` otherwise.
  /// May attempt to fetch from a stored session or an OIDC userinfo endpoint.
  Future<UserProfile?> getCurrentUser();

  /// Retrieves the current access token.
  ///
  /// Returns the access token string if available and valid, `null` otherwise.
  Future<String?> getAccessToken();

  /// Retrieves the current ID token.
  ///
  /// Returns the ID token string if available and valid, `null` otherwise.
  Future<String?> getIdToken();

  /// Attempts to refresh the access token using a stored refresh token.
  ///
  /// Returns the new access token if successful, `null` otherwise.
  /// This method should handle storing the new tokens securely.
  /// Throws [AuthException] if refresh fails and user needs to re-authenticate.
  Future<String?> refreshToken();

  /// A stream that emits the current [UserProfile] or `null` when auth state changes.
  /// This can be used by the UI or BLoCs to react to login/logout events.
  Stream<UserProfile?> get userProfileStream;

  /// Disposes of any resources held by the service, like stream controllers.
  void dispose();
}
