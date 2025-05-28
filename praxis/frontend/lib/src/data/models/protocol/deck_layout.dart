// FILE: lib/src/data/models/protocol/deck_layout.dart
// Purpose: Defines the deck layout for a protocol run.
// Corresponds to: DeckLayout in protocol.models.ts

import 'package:freezed_annotation/freezed_annotation.dart';
import './labware_definition.dart'; // Assuming LabwareDefinition is in a separate file

part 'deck_layout.freezed.dart';
part 'deck_layout.g.dart';

@freezed
abstract class DeckLayout with _$DeckLayout {
  const factory DeckLayout({
    // Unique identifier for this deck layout configuration.
    String? id,
    // Human-readable name for the deck layout.
    String? name,
    // List of labware items placed on the deck.
    List<DeckItem>? items,
    // Optional: schema version for the deck layout definition.
    String? schemaVersion,
    // Optional: metadata about the robot or deck type.
    Map<String, dynamic>?
    robot, // e.g., { "model": "OT-2", "deckId": "ot2_standard" }

    // TODO: DL1: Populate with items and positions consistent with PLR serialization
  }) = _DeckLayout;

  factory DeckLayout.fromJson(Map<String, dynamic> json) =>
      _$DeckLayoutFromJson(json);
}

@freezed
abstract class DeckItem with _$DeckItem {
  const factory DeckItem({
    // Unique ID for this item on the deck.
    required String id,
    // The slot on the deck where this item is placed (e.g., "1", "A1").
    required String slot,
    // The ID of the labware definition being used.
    @JsonKey(name: 'labware_definition_id') required String labwareDefinitionId,
    // Optional: A specific labware definition, if not just referencing by ID.
    // This could be embedded or fetched separately.
    @JsonKey(name: 'labware_definition') LabwareDefinition? labwareDefinition,
    // Human-readable display name for this item in this context.
    @JsonKey(name: 'display_name') String? displayName,
  }) = _DeckItem;

  factory DeckItem.fromJson(Map<String, dynamic> json) =>
      _$DeckItemFromJson(json);
}
