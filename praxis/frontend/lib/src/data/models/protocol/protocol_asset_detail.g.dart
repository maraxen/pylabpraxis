// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'protocol_asset_detail.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_ProtocolAssetDetail _$ProtocolAssetDetailFromJson(Map<String, dynamic> json) =>
    _ProtocolAssetDetail(
      name: json['name'] as String,
      type: json['type'] as String,
      description: json['description'] as String?,
      required: json['required'] as bool,
    );

Map<String, dynamic> _$ProtocolAssetDetailToJson(
  _ProtocolAssetDetail instance,
) => <String, dynamic>{
  'name': instance.name,
  'type': instance.type,
  'description': instance.description,
  'required': instance.required,
};
