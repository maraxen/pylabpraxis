// Business Logic Component for Authentication.
//
// Manages the state of user authentication by responding to authentication events,
// interacting with the AuthRepository, and emitting new authentication states.

import 'dart:async';
import 'package:bloc/bloc.dart';
import 'package:equatable/equatable.dart';
import 'package:flutter/foundation.dart'; // For debugPrint
import 'package:pylabpraxis_flutter/src/data/models/user/user_profile.dart';
import 'package:pylabpraxis_flutter/src/data/repositories/auth_repository.dart';
import 'package:pylabpraxis_flutter/src/core/error/exceptions.dart'; // For AuthException

part 'auth_event.dart';
part 'auth_state.dart';

class AuthBloc extends Bloc<AuthEvent, AuthState> {
  final AuthRepository _authRepository;
  StreamSubscription<UserProfile?>? _userProfileSubscription;

  AuthBloc({required AuthRepository authRepository})
    : _authRepository = authRepository,
      super(AuthInitial()) {
    on<AuthAppStarted>(_onAuthAppStarted);
    on<AuthSignInRequested>(_onAuthSignInRequested);
    on<AuthSignOutRequested>(_onAuthSignOutRequested);
    on<_AuthStatusChanged>(_onAuthStatusChanged);

    // Subscribe to user profile changes from the repository
    _userProfileSubscription = _authRepository.userProfileStream.listen(
      (userProfile) {
        add(_AuthStatusChanged(userProfile));
      },
      onError: (error) {
        // Handle errors from the stream if necessary, though AuthRepository should handle most
        debugPrint('Error in userProfileStream: $error');
        // Optionally, dispatch an error event to the BLoC
        // add(AuthFailureEvent(message: 'Error listening to auth changes'));
      },
    );
  }

  Future<void> _onAuthAppStarted(
    AuthAppStarted event,
    Emitter<AuthState> emit,
  ) async {
    emit(AuthLoading());
    try {
      final isSignedIn = await _authRepository.isSignedIn();
      if (isSignedIn) {
        final userProfile = await _authRepository.getCurrentUser();
        if (userProfile != null) {
          emit(AuthAuthenticated(userProfile: userProfile));
        } else {
          // This case might indicate an issue (e.g., token exists but profile fetch failed)
          // Or it could be that tokens are present but user info needs to be re-fetched via sign-in.
          // For simplicity, treat as unauthenticated if profile is null despite isSignedIn being true.
          // A more robust approach might try to refresh tokens or re-fetch profile here.
          await _authRepository
              .signOut(); // Clean up potentially inconsistent state
          emit(AuthUnauthenticated());
        }
      } else {
        emit(AuthUnauthenticated());
      }
    } catch (e) {
      emit(
        AuthFailure(message: 'Failed to check auth status: ${e.toString()}'),
      );
    }
  }

  Future<void> _onAuthSignInRequested(
    AuthSignInRequested event,
    Emitter<AuthState> emit,
  ) async {
    emit(AuthLoading());
    try {
      // For OIDC, signIn() in the repository/service initiates the browser flow.
      // It doesn't take username/password directly here.
      final userProfile = await _authRepository.signIn();
      emit(AuthAuthenticated(userProfile: userProfile));
    } on AuthException catch (e) {
      emit(AuthFailure(message: e.message));
    } catch (e) {
      emit(
        AuthFailure(
          message:
              'An unexpected error occurred during sign-in: ${e.toString()}',
        ),
      );
    }
  }

  Future<void> _onAuthSignOutRequested(
    AuthSignOutRequested event,
    Emitter<AuthState> emit,
  ) async {
    emit(AuthLoading());
    try {
      await _authRepository.signOut();
      emit(AuthUnauthenticated());
    } on AuthException catch (e) {
      emit(AuthFailure(message: e.message));
    } catch (e) {
      emit(
        AuthFailure(
          message:
              'An unexpected error occurred during sign-out: ${e.toString()}',
        ),
      );
    }
  }

  void _onAuthStatusChanged(_AuthStatusChanged event, Emitter<AuthState> emit) {
    if (event.userProfile != null) {
      emit(AuthAuthenticated(userProfile: event.userProfile!));
    } else {
      emit(AuthUnauthenticated());
    }
  }

  @override
  Future<void> close() {
    _userProfileSubscription?.cancel();
    return super.close();
  }
}
