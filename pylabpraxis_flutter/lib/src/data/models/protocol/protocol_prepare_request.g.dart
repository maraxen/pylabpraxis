// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'protocol_prepare_request.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_ProtocolPrepareRequest _$ProtocolPrepareRequestFromJson(
  Map<String, dynamic> json,
) => _ProtocolPrepareRequest(
  protocolPath: json['protocolPath'] as String,
  parameters: json['parameters'] as Map<String, dynamic>,
  assets: (json['assets'] as Map<String, dynamic>?)?.map(
    (k, e) => MapEntry(k, e as String),
  ),
  deckLayoutConfig: json['deck_layout_config'] as Map<String, dynamic>?,
  userId: json['userId'] as String?,
  runOptions: json['runOptions'] as Map<String, dynamic>?,
  runLabel: json['runLabel'] as String?,
);

Map<String, dynamic> _$ProtocolPrepareRequestToJson(
  _ProtocolPrepareRequest instance,
) => <String, dynamic>{
  'protocolPath': instance.protocolPath,
  'parameters': instance.parameters,
  'assets': instance.assets,
  'deck_layout_config': instance.deckLayoutConfig,
  'userId': instance.userId,
  'runOptions': instance.runOptions,
  'runLabel': instance.runLabel,
};
