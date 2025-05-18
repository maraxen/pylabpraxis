// Defines the events for the AuthBloc.
// These events trigger state changes related to authentication.

part of 'auth_bloc.dart';

abstract class AuthEvent extends Equatable {
  const AuthEvent();

  @override
  List<Object?> get props => [];
}

/// Event dispatched when the application starts to check the current auth state.
class AuthAppStarted extends AuthEvent {}

/// Event dispatched to request user sign-in.
/// For OIDC, this typically initiates a browser-based authentication flow
/// and does not require username/password parameters directly from the app UI.
class AuthSignInRequested extends AuthEvent {
  // Removed username and password parameters as OIDC flow handles this via browser.
  // If you have a separate direct username/password flow (e.g., ROPC),
  // you would create a different event for that, e.g., AuthDirectSignInRequested.
  const AuthSignInRequested();

  @override
  List<Object?> get props => [];
}

/// Event dispatched to request user sign-out.
class AuthSignOutRequested extends AuthEvent {}

/// Event dispatched when the authentication status changes internally
/// (e.g., after token refresh or user profile update).
class _AuthStatusChanged extends AuthEvent {
  final UserProfile? userProfile; // Can be null if unauthenticated

  const _AuthStatusChanged(this.userProfile);

  @override
  List<Object?> get props => [userProfile];
}
