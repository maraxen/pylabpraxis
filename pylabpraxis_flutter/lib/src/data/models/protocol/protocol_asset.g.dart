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
      required: json['required'] as bool? ?? true,
      validationConfig:
          json['validation_config'] == null
              ? null
              : ParameterConfig.fromJson(
                json['validation_config'] as Map<String, dynamic>,
              ),
      allowedExtensions:
          (json['allowed_extensions'] as List<dynamic>?)
              ?.map((e) => e as String)
              .toList(),
      contentType: json['content_type'] as String?,
    );

Map<String, dynamic> _$ProtocolAssetToJson(_ProtocolAsset instance) =>
    <String, dynamic>{
      'name': instance.name,
      'type': instance.type,
      'description': instance.description,
      'required': instance.required,
      'validation_config': instance.validationConfig,
      'allowed_extensions': instance.allowedExtensions,
      'content_type': instance.contentType,
    };
