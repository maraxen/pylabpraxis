import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:praxis_lab_management/src/data/models/protocol/parameter_constraints.dart';

part 'parameter_config.freezed.dart';
part 'parameter_config.g.dart';

@freezed
sealed class ParameterConfig with _$ParameterConfig {
  const factory ParameterConfig({
    required String type,
    @Default(false) bool isRequired,
    ParameterConstraints? constraints,
    String? displayName,
    String? description,
    dynamic defaultValue,
    String? group,
    String? units,
    String? examples,
    String? format,
  }) = _ParameterConfig;

  factory ParameterConfig.fromJson(Map<String, dynamic> json) =>
      _$ParameterConfigFromJson(json);
}

// No changes needed for ParameterDefinition or ParameterConfigExtension
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

extension ParameterConfigExtension on ParameterConfig {
  String get displayName_ => displayName ?? '';
  String get description_ => description ?? '';
}
