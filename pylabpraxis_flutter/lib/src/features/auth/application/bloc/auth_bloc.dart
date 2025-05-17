// lib/src/features/auth/application/bloc/auth_bloc.dart

import 'package:bloc/bloc.dart';
import 'package:equatable/equatable.dart';
import '../../../../data/repositories/auth_repository.dart'; // Adjusted path

part 'auth_event.dart';
part 'auth_state.dart';

class AuthBloc extends Bloc<AuthEvent, AuthState> {
  final AuthRepository _authRepository;

  AuthBloc({required AuthRepository authRepository})
    : _authRepository = authRepository,
      super(AuthInitial()) {
    on<AuthAppStarted>(_onAppStarted);
    on<AuthSignInRequested>(_onSignInRequested);
    on<AuthSignOutRequested>(_onSignOutRequested);
  }

  Future<void> _onAppStarted(
    AuthAppStarted event,
    Emitter<AuthState> emit,
  ) async {
    emit(AuthLoading());
    try {
      final isSignedIn = await _authRepository.isSignedIn;
      if (isSignedIn) {
        // In a real app, you might fetch user details here
        emit(AuthAuthenticated());
      } else {
        emit(AuthUnauthenticated());
      }
    } catch (e) {
      emit(AuthFailure(message: e.toString()));
    }
  }

  Future<void> _onSignInRequested(
    AuthSignInRequested event,
    Emitter<AuthState> emit,
  ) async {
    emit(AuthLoading());
    try {
      await _authRepository.signIn(
        username: event.username,
        password: event.password,
      );
      // Assuming signIn updates some persistent state that isSignedIn will reflect
      final isSignedIn =
          await _authRepository.isSignedIn; // Re-check or rely on service
      if (isSignedIn) {
        // Or, better, have signIn return user/success status
        emit(AuthAuthenticated());
      } else {
        // This case might occur if signIn is simulated or if it can fail silently
        // For a real app, signIn itself should throw an error on failure.
        emit(const AuthFailure(message: 'Sign in failed. Please try again.'));
      }
    } catch (e) {
      emit(AuthFailure(message: e.toString()));
    }
  }

  Future<void> _onSignOutRequested(
    AuthSignOutRequested event,
    Emitter<AuthState> emit,
  ) async {
    emit(AuthLoading());
    try {
      await _authRepository.signOut();
      emit(AuthUnauthenticated());
    } catch (e) {
      emit(AuthFailure(message: e.toString()));
    }
  }
}
