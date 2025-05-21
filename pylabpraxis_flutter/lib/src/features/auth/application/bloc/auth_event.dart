part of 'auth_bloc.dart';

abstract class AuthEvent extends Equatable {
  const AuthEvent();

  @override
  List<Object?> get props => [];
}

class AuthAppStarted extends AuthEvent {}

class AuthSignInRequested extends AuthEvent {
  const AuthSignInRequested();

  @override
  List<Object?> get props => [];
}

class AuthSignOutRequested extends AuthEvent {}

class _AuthStatusChanged extends AuthEvent {
  final UserProfile? userProfile;

  const _AuthStatusChanged(this.userProfile);

  @override
  List<Object?> get props => [userProfile];
}
