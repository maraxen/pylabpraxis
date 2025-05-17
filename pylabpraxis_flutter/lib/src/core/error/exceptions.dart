// Defines custom exception classes for the application.
//
// These exceptions are used to represent specific error scenarios,
// particularly those related to API interactions and data handling.

/// Base class for all custom exceptions in the application.
abstract class AppException implements Exception {
  final String? _message;
  final StackTrace? _stackTrace;

  AppException([this._message, this._stackTrace]);

  String get message => _message ?? runtimeType.toString();

  @override
  String toString() {
    String result = '${message}';
    if (_stackTrace != null) {
      // result += '\n$_stackTrace'; // Optionally include stacktrace
    }
    return result;
  }
}

/// Exception thrown when an API request fails.
///
/// Attributes:
///   [message] - A human-readable error message.
///   [statusCode] - The HTTP status code from the API response, if available.
///   [errors] - A map of specific field errors, if provided by the API.
class ApiException extends AppException {
  final int? statusCode;
  final Map<String, List<String>>? errors;

  ApiException({
    String? message,
    this.statusCode,
    this.errors,
    StackTrace? stackTrace,
  }) : super(message ?? 'API Error', stackTrace);

  @override
  String toString() {
    String result = super.toString();
    if (statusCode != null) {
      result += ' (Status Code: $statusCode)';
    }
    if (errors != null && errors!.isNotEmpty) {
      result += '\nErrors: $errors';
    }
    return result;
  }
}

/// Exception thrown when there is a server-side error (e.g., 5xx status code).
class ServerException extends ApiException {
  ServerException({
    String? message,
    int? statusCode,
    Map<String, List<String>>? errors,
    StackTrace? stackTrace,
  }) : super(
         message: message ?? 'Server Error',
         statusCode: statusCode,
         errors: errors,
         stackTrace: stackTrace,
       );
}

/// Exception thrown when there is a client-side error with the request (e.g., 4xx status code).
class ClientException extends ApiException {
  ClientException({
    String? message,
    int? statusCode,
    Map<String, List<String>>? errors,
    StackTrace? stackTrace,
  }) : super(
         message: message ?? 'Client Error',
         statusCode: statusCode,
         errors: errors,
         stackTrace: stackTrace,
       );
}

/// Exception thrown when the device is not connected to the internet.
class NetworkException extends AppException {
  NetworkException([String? message, StackTrace? stackTrace])
    : super(message ?? 'No Internet Connection', stackTrace);
}

/// Exception thrown when parsing data fails.
class DataParsingException extends AppException {
  DataParsingException([String? message, StackTrace? stackTrace])
    : super(message ?? 'Data Parsing Error', stackTrace);
}

/// Exception thrown for authentication-related errors.
class AuthException extends AppException {
  AuthException([String? message, StackTrace? stackTrace])
    : super(message ?? 'Authentication Error', stackTrace);
}

/// Exception thrown when a requested resource is not found (e.g., 404 status code).
class NotFoundException extends ClientException {
  NotFoundException({
    String? message,
    Map<String, List<String>>? errors,
    StackTrace? stackTrace,
  }) : super(
         message: message ?? 'Resource Not Found',
         statusCode: 404,
         errors: errors,
         stackTrace: stackTrace,
       );
}

/// Exception thrown when an operation is unauthorized (e.g., 401 status code).
class UnauthorizedException extends ClientException {
  UnauthorizedException({
    String? message,
    Map<String, List<String>>? errors,
    StackTrace? stackTrace,
  }) : super(
         message: message ?? 'Unauthorized',
         statusCode: 401,
         errors: errors,
         stackTrace: stackTrace,
       );
}

/// Exception thrown when an operation is forbidden (e.g., 403 status code).
class ForbiddenException extends ClientException {
  ForbiddenException({
    String? message,
    Map<String, List<String>>? errors,
    StackTrace? stackTrace,
  }) : super(
         message: message ?? 'Forbidden',
         statusCode: 403,
         errors: errors,
         stackTrace: stackTrace,
       );
}
