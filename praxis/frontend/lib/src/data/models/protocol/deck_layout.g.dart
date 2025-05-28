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
      'id': instance.id,
      'name': instance.name,
      'items': instance.items,
      'schemaVersion': instance.schemaVersion,
      'robot': instance.robot,
      'positions': instance.positions,
    };

_DeckItem _$DeckItemFromJson(Map<String, dynamic> json) => _DeckItem(
  id: json['id'] as String,
  slot: json['slot'] as String,
  labwareDefinitionId: json['labware_definition_id'] as String,
  labwareDefinition:
      json['labware_definition'] == null
          ? null
          : LabwareDefinition.fromJson(
            json['labware_definition'] as Map<String, dynamic>,
          ),
  displayName: json['display_name'] as String?,
);

Map<String, dynamic> _$DeckItemToJson(_DeckItem instance) => <String, dynamic>{
  'id': instance.id,
  'slot': instance.slot,
  'labware_definition_id': instance.labwareDefinitionId,
  'labware_definition': instance.labwareDefinition,
  'display_name': instance.displayName,
};
