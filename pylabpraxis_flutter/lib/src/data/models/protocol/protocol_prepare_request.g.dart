// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'protocol_prepare_request.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_ProtocolPrepareRequest _$ProtocolPrepareRequestFromJson(
  Map<String, dynamic> json,
) => _ProtocolPrepareRequest(
  protocolPath: json['protocol_path'] as String,
  parameters: json['parameters'] as Map<String, dynamic>,
  assignedAssets: (json['assigned_assets'] as Map<String, dynamic>?)?.map(
    (k, e) => MapEntry(k, e as String),
  ),
  deckLayoutPath: json['deck_layout_path'] as String?,
  deckLayoutContent:
      json['deck_layout_content'] == null
          ? null
          : DeckLayout.fromJson(
            json['deck_layout_content'] as Map<String, dynamic>,
          ),
);

Map<String, dynamic> _$ProtocolPrepareRequestToJson(
  _ProtocolPrepareRequest instance,
) => <String, dynamic>{
  'protocol_path': instance.protocolPath,
  'parameters': instance.parameters,
  'assigned_assets': instance.assignedAssets,
  'deck_layout_path': instance.deckLayoutPath,
  'deck_layout_content': instance.deckLayoutContent,
};
