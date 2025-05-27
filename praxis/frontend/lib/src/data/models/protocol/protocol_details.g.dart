// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'protocol_details.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_ProtocolDetails _$ProtocolDetailsFromJson(Map<String, dynamic> json) =>
    _ProtocolDetails(
      info: ProtocolInfo.fromJson(json['info'] as Map<String, dynamic>),
      parameters: (json['parameters'] as Map<String, dynamic>).map(
        (k, e) =>
            MapEntry(k, ParameterConfig.fromJson(e as Map<String, dynamic>)),
      ),
      assets:
          (json['assets'] as List<dynamic>?)
              ?.map((e) => ProtocolAsset.fromJson(e as Map<String, dynamic>))
              .toList(),
      steps:
          (json['steps'] as List<dynamic>?)
              ?.map((e) => ProtocolStep.fromJson(e as Map<String, dynamic>))
              .toList(),
      hardware:
          (json['hardware'] as List<dynamic>?)
              ?.map((e) => ProtocolHardware.fromJson(e as Map<String, dynamic>))
              .toList(),
      deckLayout:
          json['deckLayout'] == null
              ? null
              : DeckLayout.fromJson(json['deckLayout'] as Map<String, dynamic>),
      schemaVersion: json['schemaVersion'] as String?,
      metadata: json['metadata'] as Map<String, dynamic>?,
      commands: json['commands'] as Map<String, dynamic>?,
      author: json['author'] as String?,
      email: json['email'] as String?,
      organization: json['organization'] as String?,
      publications:
          (json['publications'] as List<dynamic>?)
              ?.map((e) => e as String)
              .toList(),
      changelog: json['changelog'] as String?,
    );

Map<String, dynamic> _$ProtocolDetailsToJson(_ProtocolDetails instance) =>
    <String, dynamic>{
      'info': instance.info,
      'parameters': instance.parameters,
      'assets': instance.assets,
      'steps': instance.steps,
      'hardware': instance.hardware,
      'deckLayout': instance.deckLayout,
      'schemaVersion': instance.schemaVersion,
      'metadata': instance.metadata,
      'commands': instance.commands,
      'author': instance.author,
      'email': instance.email,
      'organization': instance.organization,
      'publications': instance.publications,
      'changelog': instance.changelog,
    };
