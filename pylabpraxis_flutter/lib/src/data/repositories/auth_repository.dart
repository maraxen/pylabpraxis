// Defines the contract for authentication-related data operations.
//
// This abstract class serves as an interface for concrete repository
// implementations that will interact with authentication services (like AuthService)
// to manage user sessions, tokens, and profile data.

import 'package:pylabpraxis_flutter/src/data/models/user/user_profile.dart';
import 'package:pylabpraxis_flutter/src/data/services/auth_service.dart'; // Import AuthService

/// Abstract interface for authentication repositories.
///
/// Repositories are responsible for coordinating data operations between
/// data sources (like API services or local storage) and the application's
/// business logic (e.g., BLoCs).
abstract class AuthRepository {
  /// Attempts to sign in the user.
  ///
  /// Returns [UserProfile] on successful sign-in.
  /// Throws [AuthException] or other [AppException] on failure.
  Future<UserProfile> signIn();

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
}

/// Concrete implementation of [AuthRepository].
///
/// This class uses an [AuthService] to perform authentication operations.
class AuthRepositoryImpl implements AuthRepository {
  final AuthService _authService;

  AuthRepositoryImpl({required AuthService authService})
    : _authService = authService;

  @override
  Future<UserProfile> signIn() async {
    try {
      return await _authService.signIn();
    } catch (e) {
      // Log or handle specific exceptions if needed before rethrowing
      rethrow; // Propagate the exception (already an AppException or similar)
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
}
