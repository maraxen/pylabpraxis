// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'protocol_prepare_request.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_ProtocolPrepareRequest _$ProtocolPrepareRequestFromJson(
  Map<String, dynamic> json,
) => _ProtocolPrepareRequest(
  protocolId: json['protocol_accession_id'] as String,
  params: json['params'] as Map<String, dynamic>?,
  assets: (json['assets'] as Map<String, dynamic>?)?.map(
    (k, e) => MapEntry(k, e as String),
  ),
  deckLayoutName: json['deck_layout_name'] as String?,
  deckLayoutContent: json['deck_layout_content'] as Map<String, dynamic>?,
);

Map<String, dynamic> _$ProtocolPrepareRequestToJson(
  _ProtocolPrepareRequest instance,
) => <String, dynamic>{
  'protocol_accession_id': instance.protocolId,
  'params': instance.params,
  'assets': instance.assets,
  'deck_layout_name': instance.deckLayoutName,
  'deck_layout_content': instance.deckLayoutContent,
};
