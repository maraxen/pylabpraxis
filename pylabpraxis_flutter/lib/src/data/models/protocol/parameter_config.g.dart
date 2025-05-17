// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'parameter_config.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_ParameterConfig _$ParameterConfigFromJson(Map<String, dynamic> json) =>
    _ParameterConfig(
      name: json['name'] as String,
      type: json['type'] as String,
      description: json['description'] as String?,
      defaultValue: json['default_value'],
      constraints: json['constraints'] as Map<String, dynamic>?,
      required: json['required'] as bool? ?? false,
      group: json['group'] as String?,
      label: json['label'] as String?,
      hidden: json['hidden'] as bool? ?? false,
    );

Map<String, dynamic> _$ParameterConfigToJson(_ParameterConfig instance) =>
    <String, dynamic>{
      'name': instance.name,
      'type': instance.type,
      'description': instance.description,
      'default_value': instance.defaultValue,
      'constraints': instance.constraints,
      'required': instance.required,
      'group': instance.group,
      'label': instance.label,
      'hidden': instance.hidden,
    };

_DictionaryConstraints _$DictionaryConstraintsFromJson(
  Map<String, dynamic> json,
) => _DictionaryConstraints(
  keyConstraints:
      json['key_constraints'] == null
          ? null
          : ParameterConfig.fromJson(
            json['key_constraints'] as Map<String, dynamic>,
          ),
  valueConstraints:
      json['value_constraints'] == null
          ? null
          : ParameterConfig.fromJson(
            json['value_constraints'] as Map<String, dynamic>,
          ),
);

Map<String, dynamic> _$DictionaryConstraintsToJson(
  _DictionaryConstraints instance,
) => <String, dynamic>{
  'key_constraints': instance.keyConstraints,
  'value_constraints': instance.valueConstraints,
};

_ParamConstraint _$ParamConstraintFromJson(Map<String, dynamic> json) =>
    _ParamConstraint(param: json['param'] as String);

Map<String, dynamic> _$ParamConstraintToJson(_ParamConstraint instance) =>
    <String, dynamic>{'param': instance.param};
