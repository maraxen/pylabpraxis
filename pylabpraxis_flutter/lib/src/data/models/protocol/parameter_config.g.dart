// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'parameter_config.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_ConstraintConfig _$ConstraintConfigFromJson(Map<String, dynamic> json) =>
    _ConstraintConfig(
      description: json['description'] as String?,
      editable: json['editable'] as bool?,
      creatable: json['creatable'] as bool?,
      minLen: (json['min_len'] as num?)?.toInt(),
      maxLen: (json['max_len'] as num?)?.toInt(),
      regex: json['regex'] as String?,
      minValue: json['min_value'] as num?,
      maxValue: json['max_value'] as num?,
      step: json['step'] as num?,
      array: json['array'] as List<dynamic>?,
      arrayLen:
          json['array_len'] == null
              ? null
              : MinMaxConstraint.fromJson(
                json['array_len'] as Map<String, dynamic>,
              ),
      param: json['param'] as String?,
      keyConstraints:
          json['key_constraints'] == null
              ? null
              : KeyConstraint.fromJson(
                json['key_constraints'] as Map<String, dynamic>,
              ),
      valueConstraints:
          json['value_constraints'] == null
              ? null
              : ValueConstraint.fromJson(
                json['value_constraints'] as Map<String, dynamic>,
              ),
      subvariables: (json['subvariables'] as Map<String, dynamic>?)?.map(
        (k, e) =>
            MapEntry(k, ParameterConfig.fromJson(e as Map<String, dynamic>)),
      ),
      unit: json['unit'] as String?,
      placeholder: json['placeholder'] as String?,
      multiline: json['multiline'] as bool? ?? false,
    );

Map<String, dynamic> _$ConstraintConfigToJson(_ConstraintConfig instance) =>
    <String, dynamic>{
      'description': instance.description,
      'editable': instance.editable,
      'creatable': instance.creatable,
      'min_len': instance.minLen,
      'max_len': instance.maxLen,
      'regex': instance.regex,
      'min_value': instance.minValue,
      'max_value': instance.maxValue,
      'step': instance.step,
      'array': instance.array,
      'array_len': instance.arrayLen,
      'param': instance.param,
      'key_constraints': instance.keyConstraints,
      'value_constraints': instance.valueConstraints,
      'subvariables': instance.subvariables,
      'unit': instance.unit,
      'placeholder': instance.placeholder,
      'multiline': instance.multiline,
    };

_MinMaxConstraint _$MinMaxConstraintFromJson(Map<String, dynamic> json) =>
    _MinMaxConstraint(
      min: (json['min'] as num).toInt(),
      max: (json['max'] as num).toInt(),
    );

Map<String, dynamic> _$MinMaxConstraintToJson(_MinMaxConstraint instance) =>
    <String, dynamic>{'min': instance.min, 'max': instance.max};

_KeyConstraint _$KeyConstraintFromJson(Map<String, dynamic> json) =>
    _KeyConstraint(
      type:
          $enumDecodeNullable(_$ParameterTypeEnumMap, json['type']) ??
          ParameterType.string,
      description: json['description'] as String?,
      array:
          (json['array'] as List<dynamic>?)?.map((e) => e as String).toList(),
      regex: json['regex'] as String?,
      creatable: json['creatable'] as bool? ?? true,
      editable: json['editable'] as bool? ?? true,
      param: json['param'] as String?,
    );

Map<String, dynamic> _$KeyConstraintToJson(_KeyConstraint instance) =>
    <String, dynamic>{
      'type': _$ParameterTypeEnumMap[instance.type]!,
      'description': instance.description,
      'array': instance.array,
      'regex': instance.regex,
      'creatable': instance.creatable,
      'editable': instance.editable,
      'param': instance.param,
    };

const _$ParameterTypeEnumMap = {
  ParameterType.string: 'string',
  ParameterType.integer: 'integer',
  ParameterType.float: 'float',
  ParameterType.boolean: 'boolean',
  ParameterType.array: 'array',
  ParameterType.dictionary: 'dictionary',
};

_ValueConstraint _$ValueConstraintFromJson(Map<String, dynamic> json) =>
    _ValueConstraint(
      type: $enumDecode(_$ParameterTypeEnumMap, json['type']),
      description: json['description'] as String?,
      constraints:
          json['constraints'] == null
              ? null
              : ConstraintConfig.fromJson(
                json['constraints'] as Map<String, dynamic>,
              ),
      editable: json['editable'] as bool? ?? true,
      subvariables: (json['subvariables'] as Map<String, dynamic>?)?.map(
        (k, e) =>
            MapEntry(k, ParameterConfig.fromJson(e as Map<String, dynamic>)),
      ),
      param: json['param'] as String?,
    );

Map<String, dynamic> _$ValueConstraintToJson(_ValueConstraint instance) =>
    <String, dynamic>{
      'type': _$ParameterTypeEnumMap[instance.type]!,
      'description': instance.description,
      'constraints': instance.constraints,
      'editable': instance.editable,
      'subvariables': instance.subvariables,
      'param': instance.param,
    };

_ParameterConfig _$ParameterConfigFromJson(Map<String, dynamic> json) =>
    _ParameterConfig(
      name: json['name'] as String,
      type: $enumDecode(_$ParameterTypeEnumMap, json['type']),
      label: json['label'] as String?,
      description: json['description'] as String?,
      defaultValue: json['default_value'],
      required: json['required'] as bool? ?? false,
      group: json['group'] as String?,
      order: (json['order'] as num?)?.toInt(),
      constraints:
          json['constraints'] == null
              ? null
              : ConstraintConfig.fromJson(
                json['constraints'] as Map<String, dynamic>,
              ),
      ui: json['ui'] as Map<String, dynamic>?,
      advanced: json['advanced'] as bool? ?? false,
      hidden: json['hidden'] as bool? ?? false,
      visibleIf: json['visibleIf'] as Map<String, dynamic>?,
    );

Map<String, dynamic> _$ParameterConfigToJson(_ParameterConfig instance) =>
    <String, dynamic>{
      'name': instance.name,
      'type': _$ParameterTypeEnumMap[instance.type]!,
      'label': instance.label,
      'description': instance.description,
      'default_value': instance.defaultValue,
      'required': instance.required,
      'group': instance.group,
      'order': instance.order,
      'constraints': instance.constraints,
      'ui': instance.ui,
      'advanced': instance.advanced,
      'hidden': instance.hidden,
      'visibleIf': instance.visibleIf,
    };
