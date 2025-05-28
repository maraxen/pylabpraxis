// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'protocol_parameter_detail.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_ProtocolParameterDetail _$ProtocolParameterDetailFromJson(
  Map<String, dynamic> json,
) => _ProtocolParameterDetail(
  paramType: json['paramType'] as String,
  isRequired: json['isRequired'] as bool,
  defaultValue: json['default'],
  description: json['description'] as String?,
  constraints: json['constraints'] as Map<String, dynamic>?,
);

Map<String, dynamic> _$ProtocolParameterDetailToJson(
  _ProtocolParameterDetail instance,
) => <String, dynamic>{
  'paramType': instance.paramType,
  'isRequired': instance.isRequired,
  'default': instance.defaultValue,
  'description': instance.description,
  'constraints': instance.constraints,
};
