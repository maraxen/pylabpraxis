// lib/src/features/auth/application/bloc/auth_event.dart
part of 'auth_bloc.dart'; // Assuming auth_bloc.dart is in the same directory

abstract class AuthEvent extends Equatable {
  const AuthEvent();

  @override
  List<Object?> get props => [];
}

// Event triggered when the app starts to check authentication status
class AuthAppStarted extends AuthEvent {}

// Event triggered when a user attempts to sign in
class AuthSignInRequested extends AuthEvent {
  final String username;
  final String password;

  const AuthSignInRequested({required this.username, required this.password});

  @override
  List<Object?> get props => [username, password];
}

// Event triggered when a user signs out
class AuthSignOutRequested extends AuthEvent {}
