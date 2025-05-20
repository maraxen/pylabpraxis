// Defines the configuration for a protocol parameter.
//
// This class is used to represent the structure and constraints of a parameter
// that can be configured for a protocol. It includes information such as the
// parameter's name, type, description, default value, and any constraints
// that apply to its value.

import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:pylabpraxis_flutter/src/data/models/protocol/parameter_constraints.dart';

part 'parameter_config.freezed.dart';
part 'parameter_config.g.dart';

@freezed
sealed class ParameterConfig with _$ParameterConfig {
  const factory ParameterConfig({
    required String type,
    ParameterConstraints? constraints,
    String? displayName,
    String? description,
    dynamic defaultValue,
    String? group,
  }) = _ParameterConfig;

  factory ParameterConfig.fromJson(Map<String, dynamic> json) =>
      _$ParameterConfigFromJson(json);
}

@freezed
sealed class ParameterDefinition with _$ParameterDefinition {
  const factory ParameterDefinition({
    required String name,
    String? displayName,
    String? description,
    dynamic defaultValue,
    required ParameterConfig config,
  }) = _ParameterDefinition;

  factory ParameterDefinition.fromJson(Map<String, dynamic> json) =>
      _$ParameterDefinitionFromJson(json);
}

// Extension to safely access config properties from ParameterConfig
extension ParameterConfigExtension on ParameterConfig {
  String get displayName_ => displayName ?? '';
  String get description_ => description ?? '';
}
