// lib/src/data/repositories/auth_repository.dart

import '../services/auth_service.dart';

// Interface for Authentication Repository
abstract class AuthRepository {
  Future<bool> get isSignedIn;
  Future<void> signIn({required String username, required String password});
  Future<void> signOut();
}

// Implementation of AuthRepository
class AuthRepositoryImpl implements AuthRepository {
  final AuthService _authService;

  AuthRepositoryImpl({required AuthService authService})
    : _authService = authService;

  @override
  Future<bool> get isSignedIn => _authService.isSignedIn();

  @override
  Future<void> signIn({required String username, required String password}) =>
      _authService.signIn(username: username, password: password);

  @override
  Future<void> signOut() => _authService.signOut();
}
