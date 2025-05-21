// Business Logic Component for Authentication.
//
// Manages the state of user authentication by responding to authentication events,
// interacting with the AuthRepository, and emitting new authentication states.

import 'dart:async';
import 'package:bloc/bloc.dart';
import 'package:equatable/equatable.dart';
import 'package:flutter/foundation.dart'; // For kIsWeb, debugPrint
import 'package:pylabpraxis_flutter/src/data/models/user/user_profile.dart';
import 'package:pylabpraxis_flutter/src/data/repositories/auth_repository.dart';
import 'package:pylabpraxis_flutter/src/core/error/exceptions.dart';

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

    _userProfileSubscription = _authRepository.userProfileStream.listen(
      (userProfile) => add(_AuthStatusChanged(userProfile)),
      onError: (error) {
        debugPrint('Error in userProfileStream for AuthBloc: $error');
        // Optionally dispatch an AuthFailure event if stream errors are critical
        // add(AuthFailure(message: 'Auth stream error: ${error.toString()}'));
      },
    );
  }

  Future<void> _onAuthAppStarted(
    AuthAppStarted event,
    Emitter<AuthState> emit,
  ) async {
    emit(AuthLoading());
    try {
      UserProfile? userProfile;
      if (kIsWeb) {
        // On web, attempt to complete any pending sign-in from a redirect first.
        debugPrint("AuthAppStarted: Checking for web redirect result...");
        // This method now exists on AuthRepository and its implementation
        userProfile = await _authRepository.completeWebSignInOnRedirect();
        if (userProfile != null) {
          debugPrint("AuthAppStarted: Web redirect processed successfully.");
        } else {
          debugPrint("AuthAppStarted: No user profile from web redirect.");
        }
      }

      // If not already authenticated via redirect (or not on web), check stored session.
      if (userProfile == null) {
        final isSignedIn = await _authRepository.isSignedIn();
        if (isSignedIn) {
          userProfile = await _authRepository.getCurrentUser();
        }
      }

      if (userProfile != null) {
        emit(AuthAuthenticated(userProfile: userProfile));
      } else {
        emit(
          const AuthUnauthenticated(),
        ); // No message needed here for initial check
      }
    } catch (e) {
      debugPrint("Error during AuthAppStarted: ${e.toString()}");
      emit(
        AuthFailure(
          message: 'Failed to initialize auth state: ${e.toString()}',
        ),
      );
    }
  }

  Future<void> _onAuthSignInRequested(
    AuthSignInRequested event,
    Emitter<AuthState> emit,
  ) async {
    emit(AuthLoading());
    try {
      final userProfile = await _authRepository.signIn();
      if (userProfile != null) {
        emit(AuthAuthenticated(userProfile: userProfile));
      } else if (kIsWeb) {
        // On web, if signIn returns null, it indicates a redirect has started.
        // The actual user profile will be handled in the redirect processing.
        // We initiate the redirect and wait for the app to reload or handle it.
        debugPrint(
          "AuthSignInRequested: Web redirect initiated. Awaiting app reload/redirect handling.",
        );
        // Optionally: emit(AuthRedirecting());
      } else {
        // This case (null userProfile on mobile without an exception) would be unexpected.
        emit(
          const AuthFailure(
            message: 'Sign-in process did not complete as expected on mobile.',
          ),
        );
      }
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
      // AuthUnauthenticated will be emitted by _onAuthStatusChanged via the stream
      // after the service clears the session. To be explicit or handle faster UI update:
      emit(
        const AuthUnauthenticated(),
      ); // Corrected: No argument as per the state definition
    } on AuthException catch (e) {
      emit(AuthFailure(message: e.message));
    } catch (e) {
      // Even if server logout fails, local session is cleared.
      // AuthUnauthenticated now supports an optional message.
      emit(
        AuthUnauthenticated(
          message:
              'Local logout successful; server logout may have failed: ${e.toString()}',
        ),
      );
    }
  }

  void _onAuthStatusChanged(_AuthStatusChanged event, Emitter<AuthState> emit) {
    if (event.userProfile != null) {
      // Only emit if the state is actually different or user ID changes
      if (state is! AuthAuthenticated ||
          (state as AuthAuthenticated).userProfile.id !=
              event.userProfile!.id) {
        emit(AuthAuthenticated(userProfile: event.userProfile!));
      }
    } else {
      // Only emit if not already unauthenticated
      if (state is! AuthUnauthenticated) {
        emit(const AuthUnauthenticated());
      }
    }
  }

  @override
  Future<void> close() {
    _userProfileSubscription?.cancel();
    _authRepository.dispose(); // Call dispose on repository
    return super.close();
  }
}
