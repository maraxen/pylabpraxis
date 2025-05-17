// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'protocol_asset.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_ProtocolAsset _$ProtocolAssetFromJson(Map<String, dynamic> json) =>
    _ProtocolAsset(
      name: json['name'] as String,
      type: json['type'] as String,
      description: json['description'] as String?,
      required: json['required'] as bool? ?? false,
      constraints: json['constraints'],
      defaultValue: json['default_value'] as String?,
      value: json['value'] as String?,
    );

Map<String, dynamic> _$ProtocolAssetToJson(_ProtocolAsset instance) =>
    <String, dynamic>{
      'name': instance.name,
      'type': instance.type,
      'description': instance.description,
      'required': instance.required,
      'constraints': instance.constraints,
      'default_value': instance.defaultValue,
      'value': instance.value,
    };
