// lib/src/features/auth/application/bloc/auth_state.dart
part of 'auth_bloc.dart'; // Assuming auth_bloc.dart is in the same directory

abstract class AuthState extends Equatable {
  const AuthState();

  @override
  List<Object?> get props => [];
}

// Initial state, authentication status unknown
class AuthInitial extends AuthState {}

// State when user is authenticated
class AuthAuthenticated extends AuthState {
  // final User user; // You might have a User model
  // const AuthAuthenticated({required this.user});
  // @override
  // List<Object?> get props => [user];
}

// State when user is not authenticated
class AuthUnauthenticated extends AuthState {}

// State when authentication is in progress
class AuthLoading extends AuthState {}

// State when an authentication error has occurred
class AuthFailure extends AuthState {
  final String message;

  const AuthFailure({required this.message});

  @override
  List<Object?> get props => [message];
}
