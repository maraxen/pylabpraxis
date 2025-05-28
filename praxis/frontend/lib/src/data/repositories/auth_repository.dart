// Defines the contract for authentication-related data operations.
//
// This abstract class serves as an interface for concrete repository
// implementations that will interact with authentication services (like AuthService)
// to manage user sessions, tokens, and profile data.

import 'package:praxis_lab_management/src/data/models/user/user_profile.dart';
import 'package:praxis_lab_management/src/data/services/auth_service.dart'; // Import AuthService

/// Abstract interface for authentication repositories.
///
/// Repositories are responsible for coordinating data operations between
/// data sources (like API services or local storage) and the application's
/// business logic (e.g., BLoCs).
abstract class AuthRepository {
  /// Attempts to sign in the user.
  ///
  /// For mobile, this should complete the flow and return a [UserProfile] or throw.
  /// For web, this initiates a redirect. The method might return `null` or throw
  /// a specific exception to indicate a redirect has started.
  Future<UserProfile?> signIn();

  /// For web platform, this method should be called when the app (re)loads
  /// to check if the current URL is the result of an OIDC redirect.
  /// If so, it processes the authentication response and returns [UserProfile].
  /// Returns `null` if not a redirect or if processing fails.
  /// On mobile, this method might do nothing or return null.
  Future<UserProfile?> completeWebSignInOnRedirect();

  /// Signs out the current user.
  ///
  /// Throws [AuthException] or other [AppException] on failure, though
  /// typically sign-out should succeed locally even if remote logout fails.
  Future<void> signOut();

  /// Checks if a user is currently signed in.
  Future<bool> isSignedIn();

  /// Gets the current authenticated user's profile.
  ///
  /// Returns [UserProfile] if available, `null` otherwise.
  Future<UserProfile?> getCurrentUser();

  /// Provides a stream of the user's authentication state ([UserProfile] or `null`).
  Stream<UserProfile?> get userProfileStream;

  /// Disposes of resources if any are held by the repository (e.g., streams from services).
  void dispose();
}

/// Concrete implementation of [AuthRepository].
///
/// This class uses an [AuthService] to perform authentication operations.
class AuthRepositoryImpl implements AuthRepository {
  final AuthService _authService;

  AuthRepositoryImpl({required AuthService authService})
    : _authService = authService;

  @override
  Future<UserProfile?> signIn() async {
    try {
      return await _authService.signIn();
    } catch (e) {
      // Log or handle specific exceptions if needed before rethrowing
      rethrow; // Propagate the exception (already an AppException or similar)
    }
  }

  @override
  Future<UserProfile?> completeWebSignInOnRedirect() async {
    try {
      return await _authService.completeWebSignInOnRedirect();
    } catch (e) {
      rethrow;
    }
  }

  @override
  Future<void> signOut() async {
    try {
      await _authService.signOut();
    } catch (e) {
      rethrow;
    }
  }

  @override
  Future<bool> isSignedIn() async {
    try {
      return await _authService.isSignedIn();
    } catch (e) {
      // Default to false if there's an error checking status
      return false;
    }
  }

  @override
  Future<UserProfile?> getCurrentUser() async {
    try {
      return await _authService.getCurrentUser();
    } catch (e) {
      return null;
    }
  }

  @override
  Stream<UserProfile?> get userProfileStream => _authService.userProfileStream;

  @override
  void dispose() {
    // Call dispose on the AuthService if it has a dispose method.
    // This is important for cleaning up resources like StreamControllers.
    _authService.dispose();
  }
}
