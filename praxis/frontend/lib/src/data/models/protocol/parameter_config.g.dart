// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'parameter_config.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_ParameterConfig _$ParameterConfigFromJson(Map<String, dynamic> json) =>
    _ParameterConfig(
      type: json['type'] as String,
      isRequired: json['isRequired'] as bool? ?? false,
      constraints:
          json['constraints'] == null
              ? null
              : ParameterConstraints.fromJson(
                json['constraints'] as Map<String, dynamic>,
              ),
      displayName: json['displayName'] as String?,
      description: json['description'] as String?,
      defaultValue: json['defaultValue'],
      group: json['group'] as String?,
      units: json['units'] as String?,
      examples: json['examples'] as String?,
      format: json['format'] as String?,
    );

Map<String, dynamic> _$ParameterConfigToJson(_ParameterConfig instance) =>
    <String, dynamic>{
      'type': instance.type,
      'isRequired': instance.isRequired,
      'constraints': instance.constraints,
      'displayName': instance.displayName,
      'description': instance.description,
      'defaultValue': instance.defaultValue,
      'group': instance.group,
      'units': instance.units,
      'examples': instance.examples,
      'format': instance.format,
    };

_ParameterDefinition _$ParameterDefinitionFromJson(Map<String, dynamic> json) =>
    _ParameterDefinition(
      name: json['name'] as String,
      displayName: json['displayName'] as String?,
      description: json['description'] as String?,
      defaultValue: json['defaultValue'],
      config: ParameterConfig.fromJson(json['config'] as Map<String, dynamic>),
    );

Map<String, dynamic> _$ParameterDefinitionToJson(
  _ParameterDefinition instance,
) => <String, dynamic>{
  'name': instance.name,
  'displayName': instance.displayName,
  'description': instance.description,
  'defaultValue': instance.defaultValue,
  'config': instance.config,
};
