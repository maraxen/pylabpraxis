// Defines the contract for authentication services.
//
// This abstract class serves as an interface for concrete implementations
// that will handle user authentication flows (e.g., OIDC with Keycloak),
// token management, and user session status.

import 'package:praxis_lab_management/src/data/models/user/user_profile.dart';

/// Abstract interface for authentication services.
///
/// Implementations will handle interactions with an authentication provider
/// (like Keycloak via OIDC) to sign in, sign out, manage tokens,
/// and retrieve user information.
abstract class AuthService {
  /// Initiates the sign-in process.
  ///
  /// For mobile, this should complete the flow and return a [UserProfile] or throw.
  /// For web, this initiates a redirect. The method might return `null` or throw
  /// a specific exception to indicate a redirect has started. The actual
  /// [UserProfile] is obtained after the redirect via [completeWebSignInOnRedirect].
  Future<UserProfile?> signIn();

  /// For web platform, this method should be called when the app (re)loads
  /// to check if the current URL is the result of an OIDC redirect.
  /// If so, it processes the authentication response and returns [UserProfile].
  /// Returns `null` if not a redirect or if processing fails.
  /// On mobile, this method might do nothing or return null.
  Future<UserProfile?> completeWebSignInOnRedirect();

  /// Signs the user out.
  ///
  /// This involves clearing local session data (tokens) and potentially
  /// invalidating the session with the authentication provider.
  /// Throws [AuthException] if sign-out fails (though local clearing should always happen).
  Future<void> signOut();

  /// Checks if a user is currently signed in (e.g., has a valid, non-expired token).
  /// May attempt a silent token refresh if applicable.
  Future<bool> isSignedIn();

  /// Retrieves the current authenticated user's profile from local storage.
  /// Does not typically make a network request unless essential for validation.
  Future<UserProfile?> getCurrentUser();

  /// Retrieves the current access token.
  /// Should ideally check [isSignedIn] first or be called after confirming sign-in.
  Future<String?> getAccessToken();

  /// Retrieves the current ID token.
  /// Should ideally check [isSignedIn] first or be called after confirming sign-in.
  Future<String?> getIdToken();

  /// Attempts to refresh the access token using a stored refresh token.
  ///
  /// Returns the new access token if successful, `null` or throws [AuthException] otherwise.
  /// This method should handle storing the new tokens securely and updating user profile.
  Future<String?> refreshToken();

  /// A stream that emits the current [UserProfile] or `null` when auth state changes.
  /// This can be used by the UI or BLoCs to react to login/logout events.
  Stream<UserProfile?> get userProfileStream;

  /// Disposes of any resources held by the service, like stream controllers.
  void dispose();
}
