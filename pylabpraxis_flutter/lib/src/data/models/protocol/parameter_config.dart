// Defines the configuration for a protocol parameter.
//
// This class is used to represent the structure and constraints of a parameter
// that can be configured for a protocol. It includes information such as the
// parameter's name, type, description, default value, and any constraints
// that apply to its value.

import 'package:freezed_annotation/freezed_annotation.dart';

part 'parameter_config.freezed.dart';
part 'parameter_config.g.dart';

/// Defines the configuration for a protocol parameter.
///
/// This class is used to represent the structure and constraints of a parameter
/// that can be configured for a protocol. It includes information such as the
/// parameter's name, type, description, default value, and any constraints
/// that apply to its value.
@freezed
sealed class ParameterConfig with _$ParameterConfig {
  /// Default constructor for [ParameterConfig].
  ///
  /// Parameters:
  ///   [name] - The name of the parameter.
  ///   [type] - The data type of the parameter (e.g., 'string', 'integer', 'boolean').
  ///   [description] - A human-readable description of the parameter.
  ///   [defaultValue] - The default value for the parameter.
  ///   [constraints] - A map defining constraints on the parameter's value
  ///                   (e.g., min/max values, allowed choices).
  ///   [required] - A boolean indicating whether the parameter is required.
  ///   [group] - An optional string to group related parameters in the UI.
  ///   [label] - An optional, shorter, human-readable label for the parameter.
  ///   [hidden] - An optional boolean indicating if the parameter should be hidden in the UI.
  const factory ParameterConfig({
    required String name,
    required String type,
    String? description,
    @JsonKey(name: 'default_value') dynamic defaultValue,
    // The 'value' field has been removed as it represents runtime state,
    // not static configuration.
    Map<String, dynamic>? constraints,
    @Default(false) bool required,
    String? group,
    String? label,
    @Default(false) bool hidden,
  }) = _ParameterConfig;

  /// Creates a [ParameterConfig] instance from a JSON map.
  ///
  /// This factory constructor is used by `json_serializable` to deserialize
  /// JSON data into a [ParameterConfig] object.
  factory ParameterConfig.fromJson(Map<String, dynamic> json) =>
      _$ParameterConfigFromJson(json);
}

/// Represents constraints for a parameter of type 'dict' (dictionary).
///
/// This class is used within [ParameterConfig.constraints] when the parameter
/// type is 'dict'. It defines constraints for the keys and values of the
/// dictionary entries.
@freezed
abstract class DictionaryConstraints with _$DictionaryConstraints {
  /// Default constructor for [DictionaryConstraints].
  ///
  /// Parameters:
  ///   [keyConstraints] - Optional [ParameterConfig] defining constraints for dictionary keys.
  ///   [valueConstraints] - Optional [ParameterConfig] defining constraints for dictionary values.
  const factory DictionaryConstraints({
    @JsonKey(name: 'key_constraints') ParameterConfig? keyConstraints,
    @JsonKey(name: 'value_constraints') ParameterConfig? valueConstraints,
  }) = _DictionaryConstraints;

  /// Creates a [DictionaryConstraints] instance from a JSON map.
  factory DictionaryConstraints.fromJson(Map<String, dynamic> json) =>
      _$DictionaryConstraintsFromJson(json);
}

/// Represents constraints for a parameter that references another parameter.
///
/// This class is used within [ParameterConfig.constraints] to indicate that
/// a parameter's value or choices depend on another parameter.
@freezed
abstract class ParamConstraint with _$ParamConstraint {
  /// Default constructor for [ParamConstraint].
  ///
  /// Parameters:
  ///   [param] - The name of the parameter being referenced.
  const factory ParamConstraint({required String param}) = _ParamConstraint;

  /// Creates a [ParamConstraint] instance from a JSON map.
  factory ParamConstraint.fromJson(Map<String, dynamic> json) =>
      _$ParamConstraintFromJson(json);
}
