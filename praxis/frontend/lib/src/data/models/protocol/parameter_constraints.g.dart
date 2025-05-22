// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'parameter_constraints.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_ParameterConstraintsBase _$ParameterConstraintsBaseFromJson(
  Map<String, dynamic> json,
) => _ParameterConstraintsBase(
  required_: json['_required'] as bool?,
  type: json['type'] as String?,
  minValue: json['minValue'] as num?,
  maxValue: json['maxValue'] as num?,
  step: json['step'] as num?,
  minLength: (json['minLength'] as num?)?.toInt(),
  maxLength: (json['maxLength'] as num?)?.toInt(),
  regex: json['regex'] as String?,
  regexDescription: json['regexDescription'] as String?,
  minItems: (json['minItems'] as num?)?.toInt(),
  maxItems: (json['maxItems'] as num?)?.toInt(),
  minProperties: (json['minProperties'] as num?)?.toInt(),
  maxProperties: (json['maxProperties'] as num?)?.toInt(),
  array: (json['array'] as List<dynamic>?)?.map((e) => e as String).toList(),
  items: json['items'] as Map<String, dynamic>?,
  uniqueItems: json['uniqueItems'] as bool?,
  creatable: json['creatable'] as bool?,
  editable: json['editable'] as bool?,
  defaultValue: json['defaultValue'],
);

Map<String, dynamic> _$ParameterConstraintsBaseToJson(
  _ParameterConstraintsBase instance,
) => <String, dynamic>{
  '_required': instance.required_,
  'type': instance.type,
  'minValue': instance.minValue,
  'maxValue': instance.maxValue,
  'step': instance.step,
  'minLength': instance.minLength,
  'maxLength': instance.maxLength,
  'regex': instance.regex,
  'regexDescription': instance.regexDescription,
  'minItems': instance.minItems,
  'maxItems': instance.maxItems,
  'minProperties': instance.minProperties,
  'maxProperties': instance.maxProperties,
  'array': instance.array,
  'items': instance.items,
  'uniqueItems': instance.uniqueItems,
  'creatable': instance.creatable,
  'editable': instance.editable,
  'defaultValue': instance.defaultValue,
};

_ParameterConstraints _$ParameterConstraintsFromJson(
  Map<String, dynamic> json,
) => _ParameterConstraints(
  required_: json['_required'] as bool?,
  type: json['type'] as String?,
  minValue: json['minValue'] as num?,
  maxValue: json['maxValue'] as num?,
  step: json['step'] as num?,
  minLength: (json['minLength'] as num?)?.toInt(),
  maxLength: (json['maxLength'] as num?)?.toInt(),
  regex: json['regex'] as String?,
  regexDescription: json['regexDescription'] as String?,
  minItems: (json['minItems'] as num?)?.toInt(),
  maxItems: (json['maxItems'] as num?)?.toInt(),
  minProperties: (json['minProperties'] as num?)?.toInt(),
  maxProperties: (json['maxProperties'] as num?)?.toInt(),
  array: (json['array'] as List<dynamic>?)?.map((e) => e as String).toList(),
  items: json['items'] as Map<String, dynamic>?,
  creatable: json['creatable'] as bool?,
  editable: json['editable'] as bool?,
  uniqueItems: json['uniqueItems'] as bool?,
  valueConstraints:
      json['valueConstraints'] == null
          ? null
          : ParameterConstraintsBase.fromJson(
            json['valueConstraints'] as Map<String, dynamic>,
          ),
  keyConstraints:
      json['keyConstraints'] == null
          ? null
          : ParameterConstraintsBase.fromJson(
            json['keyConstraints'] as Map<String, dynamic>,
          ),
  defaultValue: json['defaultValue'],
);

Map<String, dynamic> _$ParameterConstraintsToJson(
  _ParameterConstraints instance,
) => <String, dynamic>{
  '_required': instance.required_,
  'type': instance.type,
  'minValue': instance.minValue,
  'maxValue': instance.maxValue,
  'step': instance.step,
  'minLength': instance.minLength,
  'maxLength': instance.maxLength,
  'regex': instance.regex,
  'regexDescription': instance.regexDescription,
  'minItems': instance.minItems,
  'maxItems': instance.maxItems,
  'minProperties': instance.minProperties,
  'maxProperties': instance.maxProperties,
  'array': instance.array,
  'items': instance.items,
  'creatable': instance.creatable,
  'editable': instance.editable,
  'uniqueItems': instance.uniqueItems,
  'valueConstraints': instance.valueConstraints,
  'keyConstraints': instance.keyConstraints,
  'defaultValue': instance.defaultValue,
};
