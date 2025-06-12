// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'deck_layout.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_DeckLayout _$DeckLayoutFromJson(Map<String, dynamic> json) => _DeckLayout(
  id: json['id'] as String?,
  name: json['name'] as String?,
  items:
      (json['items'] as List<dynamic>?)
          ?.map((e) => DeckItem.fromJson(e as Map<String, dynamic>))
          .toList(),
  schemaVersion: json['schemaVersion'] as String?,
  robot: json['robot'] as Map<String, dynamic>?,
  positions:
      (json['positions'] as List<dynamic>?)?.map((e) => e as String).toList(),
);

Map<String, dynamic> _$DeckLayoutToJson(_DeckLayout instance) =>
    <String, dynamic>{
      'id': instance.accession_id,
      'name': instance.name,
      'items': instance.items,
      'schemaVersion': instance.schemaVersion,
      'robot': instance.robot,
      'positions': instance.positions,
    };

_DeckItem _$DeckItemFromJson(Map<String, dynamic> json) => _DeckItem(
  id: json['id'] as String,
  slot: json['slot'] as String,
  resourceDefinitionId: json['resource_definition_accession_id'] as String,
  resourceDefinition:
      json['resource_definition'] == null
          ? null
          : ResourceDefinition.fromJson(
            json['resource_definition'] as Map<String, dynamic>,
          ),
  displayName: json['display_name'] as String?,
);

Map<String, dynamic> _$DeckItemToJson(_DeckItem instance) => <String, dynamic>{
  'id': instance.accession_id,
  'slot': instance.slot,
  'resource_definition_accession_id': instance.resourceDefinitionId,
  'resource_definition': instance.resourceDefinition,
  'display_name': instance.displayName,
};
