// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'protocol_details.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_ProtocolDetails _$ProtocolDetailsFromJson(Map<String, dynamic> json) =>
    _ProtocolDetails(
      name: json['name'] as String,
      path: json['path'] as String,
      description: json['description'] as String,
      parameters: (json['parameters'] as Map<String, dynamic>).map(
        (k, e) => MapEntry(
          k,
          ProtocolParameterDetail.fromJson(e as Map<String, dynamic>),
        ),
      ),
      assets:
          (json['assets'] as List<dynamic>)
              .map(
                (e) => ProtocolAssetDetail.fromJson(e as Map<String, dynamic>),
              )
              .toList(),
      hasAssets: json['hasAssets'] as bool,
      hasParameters: json['hasParameters'] as bool,
      requiresConfig: json['requiresConfig'] as bool,
    );

Map<String, dynamic> _$ProtocolDetailsToJson(_ProtocolDetails instance) =>
    <String, dynamic>{
      'name': instance.name,
      'path': instance.path,
      'description': instance.description,
      'parameters': instance.parameters,
      'assets': instance.assets,
      'hasAssets': instance.hasAssets,
      'hasParameters': instance.hasParameters,
      'requiresConfig': instance.requiresConfig,
    };
