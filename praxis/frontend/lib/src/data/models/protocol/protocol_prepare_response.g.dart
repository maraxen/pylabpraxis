// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'protocol_prepare_response.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_ProtocolPrepareResponse _$ProtocolPrepareResponseFromJson(
  Map<String, dynamic> json,
) => _ProtocolPrepareResponse(
  status: json['status'] as String,
  config: json['config'] as Map<String, dynamic>,
  errors: (json['errors'] as List<dynamic>?)?.map((e) => e as String).toList(),
  assetSuggestions: json['assetSuggestions'] as Map<String, dynamic>?,
);

Map<String, dynamic> _$ProtocolPrepareResponseToJson(
  _ProtocolPrepareResponse instance,
) => <String, dynamic>{
  'status': instance.status,
  'config': instance.config,
  'errors': instance.errors,
  'assetSuggestions': instance.assetSuggestions,
};
