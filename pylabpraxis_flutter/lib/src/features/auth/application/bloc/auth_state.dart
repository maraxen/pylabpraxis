// lib/src/features/auth/application/bloc/auth_state.dart
part of 'auth_bloc.dart'; // Ensures this file is part of the AuthBloc library

/// Base class for all authentication states.
/// Uses [Equatable] for easy value comparison.
abstract class AuthState extends Equatable {
  const AuthState();

  @override
  List<Object?> get props => [];
}

/// Initial state of the [AuthBloc], indicating that the authentication
/// status has not yet been determined.
class AuthInitial extends AuthState {}

/// State indicating that the user is successfully authenticated.
///
/// Contains the [UserProfile] of the authenticated user.
class AuthAuthenticated extends AuthState {
  final UserProfile userProfile;

  const AuthAuthenticated({required this.userProfile});

  @override
  List<Object?> get props => [userProfile];

  @override
  String toString() => 'AuthAuthenticated { userProfile: ${userProfile.id} }';
}

/// State indicating that the user is not authenticated.
class AuthUnauthenticated extends AuthState {}

/// State indicating that an authentication process (e.g., sign-in, sign-out,
/// checking status) is currently in progress.
class AuthLoading extends AuthState {}

/// State indicating that an error occurred during an authentication process.
///
/// Contains an error [message] describing the failure.
class AuthFailure extends AuthState {
  final String message;

  const AuthFailure({required this.message});

  @override
  List<Object?> get props => [message];

  @override
  String toString() => 'AuthFailure { message: $message }';
}
