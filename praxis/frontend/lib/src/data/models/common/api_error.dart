// Defines a structured error response from the API.
//
// This model is used to parse and represent error details when an API call
// fails, providing a consistent way to handle errors throughout the application.

import 'package:freezed_annotation/freezed_annotation.dart';

part 'api_error.freezed.dart';
part 'api_error.g.dart';

/// Represents a structured error response from the API.
@freezed
abstract class ApiError with _$ApiError {
  /// Default constructor for [ApiError].
  ///
  /// Parameters:
  ///   [statusCode] - The HTTP status code of the error response.
  ///   [message] - A human-readable error message.
  ///   [detail] - Potentially more detailed error information, could be a string or a map.
  ///   [errors] - A map of specific field errors, where keys are field names
  ///              and values are lists of error messages for that field.
  const factory ApiError({
    int? statusCode,
    String? message,
    dynamic detail, // Can be String or Map<String, dynamic> or List<dynamic>
    Map<String, List<String>>? errors,
  }) = _ApiError;

  /// Creates an [ApiError] instance from a JSON map.
  factory ApiError.fromJson(Map<String, dynamic> json) =>
      _$ApiErrorFromJson(json);
}
