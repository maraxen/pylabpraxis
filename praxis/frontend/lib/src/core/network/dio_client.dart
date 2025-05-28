// Configures and provides a Dio HTTP client instance for API communication.
//
// This class sets up base options, interceptors for logging, error handling,
// and potentially authentication token management.

import 'dart:async';
import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart'; // For kDebugMode
import 'package:praxis_lab_management/src/core/error/exceptions.dart';
import 'package:praxis_lab_management/src/data/models/common/api_error.dart';
import 'package:praxis_lab_management/src/data/services/auth_service.dart'; // Import AuthService

class DioClient {
  late final Dio _dio;
  final AuthService _authService; // Added AuthService

  // TODO: Replace with your actual base URL from a config file or environment variable
  static const String _baseUrl = 'http://localhost:8000/api/v1';

  DioClient({required AuthService authService}) : _authService = authService {
    // AuthService injected
    _dio = Dio(
      BaseOptions(
        baseUrl: _baseUrl,
        connectTimeout: Duration(seconds: 15), // Increased timeout
        receiveTimeout: Duration(seconds: 15), // Increased timeout
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
      ),
    );

    _dio.interceptors.addAll([
      AuthInterceptor(
        dio: _dio,
        authService: _authService,
      ), // AuthInterceptor added
      LoggingInterceptor(),
      ErrorInterceptor(),
    ]);
  }

  Dio get dio => _dio;

  static String get baseUrl => _baseUrl;
}

/// Interceptor for logging API requests and responses.
/// Only logs in debug mode.
class LoggingInterceptor extends Interceptor {
  @override
  void onRequest(RequestOptions options, RequestInterceptorHandler handler) {
    if (kDebugMode) {
      debugPrint(
        '--> ${options.method.toUpperCase()} ${options.baseUrl}${options.path}',
      );
      debugPrint('Headers:');
      options.headers.forEach((k, v) => debugPrint('$k: $v'));
      if (options.queryParameters.isNotEmpty) {
        debugPrint('queryParameters:');
        options.queryParameters.forEach((k, v) => debugPrint('$k: $v'));
      }
      if (options.data != null) {
        debugPrint('Body: ${options.data}');
      }
      debugPrint('--> END ${options.method.toUpperCase()}');
    }
    super.onRequest(options, handler);
  }

  @override
  void onResponse(Response response, ResponseInterceptorHandler handler) {
    if (kDebugMode) {
      debugPrint(
        '<-- ${response.statusCode} ${response.requestOptions.method.toUpperCase()} ${response.requestOptions.baseUrl}${response.requestOptions.path}',
      );
      // debugPrint('Response: ${response.data}'); // Can be too verbose
      debugPrint('<-- END HTTP');
    }
    super.onResponse(response, handler);
  }

  @override
  void onError(DioException err, ErrorInterceptorHandler handler) {
    if (kDebugMode) {
      debugPrint(
        '<-- ${err.message} ${err.response?.requestOptions.method.toUpperCase()} ${err.response?.requestOptions.baseUrl}${err.response?.requestOptions.path}',
      );
      if (err.response != null) {
        debugPrint('Error Response Status: ${err.response?.statusCode}');
        debugPrint('Error Response Data: ${err.response?.data}');
      } else {
        debugPrint('Error without response: ${err.type}');
      }
      debugPrint('<-- END ERROR');
    }
    super.onError(err, handler);
  }
}

/// Interceptor for handling API errors and converting them to custom exceptions.
class ErrorInterceptor extends Interceptor {
  @override
  void onError(DioException err, ErrorInterceptorHandler handler) {
    final response = err.response;
    final requestOptions = err.requestOptions;

    if (err.error is AppException) {
      // If the error is already an AppException (e.g. from AuthInterceptor), pass it through.
      return handler.reject(
        DioException(
          requestOptions: requestOptions,
          response: response,
          error: err.error, // Keep the original AppException
          type: err.type,
        ),
      );
    }

    if (response != null) {
      final int statusCode = response.statusCode ?? 0;
      ApiError? apiError;
      try {
        if (response.data is Map<String, dynamic>) {
          apiError = ApiError.fromJson(response.data as Map<String, dynamic>);
        } else if (response.data is String && response.data.isNotEmpty) {
          apiError = ApiError(message: response.data, statusCode: statusCode);
        }
      } catch (e) {
        debugPrint('Failed to parse ApiError from response.data: $e');
      }

      final String message =
          apiError?.message ??
          apiError?.detail?.toString() ??
          (response.data is String && response.data.isNotEmpty
              ? response.data
              : null) ??
          err.message ??
          'Unknown API Error';
      final Map<String, List<String>>? errors = apiError?.errors;

      AppException exceptionToThrow;

      switch (statusCode) {
        case 400:
          exceptionToThrow = ClientException(
            message: message,
            statusCode: statusCode,
            errors: errors,
            stackTrace: err.stackTrace,
          );
          break;
        case 401:
          exceptionToThrow = UnauthorizedException(
            message: message,
            errors: errors,
            stackTrace: err.stackTrace,
          );
          break;
        case 403:
          exceptionToThrow = ForbiddenException(
            message: message,
            errors: errors,
            stackTrace: err.stackTrace,
          );
          break;
        case 404:
          exceptionToThrow = NotFoundException(
            message: message,
            errors: errors,
            stackTrace: err.stackTrace,
          );
          break;
        case >= 500:
          exceptionToThrow = ServerException(
            message: message,
            statusCode: statusCode,
            errors: errors,
            stackTrace: err.stackTrace,
          );
          break;
        default:
          exceptionToThrow = ApiException(
            message: message,
            statusCode: statusCode,
            errors: errors,
            stackTrace: err.stackTrace,
          );
      }

      return handler.reject(
        DioException(
          requestOptions: requestOptions,
          response: response,
          error: exceptionToThrow,
          type: err.type,
        ),
      );
    } else {
      // Handle network errors or other Dio errors without a response
      if (err.type == DioExceptionType.connectionTimeout ||
          err.type == DioExceptionType.sendTimeout ||
          err.type == DioExceptionType.receiveTimeout ||
          err.type == DioExceptionType.connectionError ||
          err.type == DioExceptionType.unknown /* Often for no internet */ ) {
        return handler.reject(
          DioException(
            requestOptions: requestOptions,
            error: NetworkException(
              'Connection problem: ${err.message}',
              err.stackTrace,
            ),
            type: err.type,
          ),
        );
      }
    }
    // If not handled, create a generic ApiException
    super.onError(err, handler);
  }
}

/// Interceptor for adding Authorization header and handling token refresh.
class AuthInterceptor extends Interceptor {
  final Dio dio; // Instance of Dio to retry requests
  final AuthService authService;

  AuthInterceptor({required this.dio, required this.authService});

  // A simple mechanism to prevent multiple token refresh attempts simultaneously
  static bool _isRefreshing = false;
  // Completer to allow subsequent requests to wait for the refresh to finish
  static Completer<String?>? _refreshCompleter;

  @override
  Future<void> onRequest(
    RequestOptions options,
    RequestInterceptorHandler handler,
  ) async {
    // Check if the request requires authentication (e.g., based on path or a flag in options.extra)
    // For simplicity, let's assume all requests except auth-related ones need a token.
    // You might want more sophisticated logic here, e.g. checking options.extra['requiresAuth'] == true
    if (!options.path.contains('/auth/')) {
      // Example: don't add token to auth paths
      final String? token = await authService.getAccessToken();
      if (token != null) {
        options.headers['Authorization'] = 'Bearer $token';
      }
    }
    super.onRequest(options, handler);
  }

  @override
  Future<void> onError(
    DioException err,
    ErrorInterceptorHandler handler,
  ) async {
    if (err.response?.statusCode == 401) {
      // If it's a 401, try to refresh the token
      if (_isRefreshing) {
        // If already refreshing, wait for the current refresh to complete
        try {
          final String? newToken = await _refreshCompleter?.future;
          if (newToken != null) {
            err.requestOptions.headers['Authorization'] = 'Bearer $newToken';
            final Response response = await dio.fetch(err.requestOptions);
            return handler.resolve(response);
          } else {
            // Refresh failed in the original attempt
            await authService.signOut(); // Ensure user is signed out
            return handler.reject(
              DioException(
                requestOptions: err.requestOptions,
                error: AuthException(
                  'Session expired. Please sign in again. (Queued refresh failed)',
                ),
                response: err.response,
              ),
            );
          }
        } catch (e) {
          await authService.signOut();
          return handler.reject(
            DioException(
              requestOptions: err.requestOptions,
              error: AuthException(
                'Session expired. Please sign in again. (Error during queued refresh)',
              ),
              response: err.response,
            ),
          );
        }
      }

      _isRefreshing = true;
      _refreshCompleter = Completer<String?>();

      try {
        final String? newToken = await authService.refreshToken();
        _isRefreshing = false;
        _refreshCompleter!.complete(newToken);

        if (newToken != null) {
          // Update the request header with the new token
          err.requestOptions.headers['Authorization'] = 'Bearer $newToken';
          // Retry the request
          final Response response = await dio.fetch(err.requestOptions);
          return handler.resolve(response);
        } else {
          // If refresh failed (e.g., refresh token also expired)
          await authService
              .signOut(); // Or trigger AuthUnauthenticated state via BLoC
          return handler.reject(
            DioException(
              requestOptions: err.requestOptions,
              error: AuthException('Session expired. Please sign in again.'),
              response: err.response,
            ),
          );
        }
      } catch (e) {
        _isRefreshing = false;
        if (!_refreshCompleter!.isCompleted) {
          _refreshCompleter!.completeError(e);
        }
        await authService.signOut();
        return handler.reject(
          DioException(
            requestOptions: err.requestOptions,
            error: AuthException(
              'Failed to refresh token. Please sign in again. Error: ${e.toString()}',
            ),
            response: err.response,
          ),
        );
      }
    }
    // For other errors, just pass them along to the ErrorInterceptor
    super.onError(err, handler);
  }
}
