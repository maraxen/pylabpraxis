// FILE: lib/src/data/models/protocol/deck_layout.dart
// Purpose: Defines the deck layout for a protocol run.
// Corresponds to: DeckLayout in protocol.models.ts

import 'package:freezed_annotation/freezed_annotation.dart';
import './resource_definition.dart'; // Assuming ResourceDefinition is in a separate file

part 'deck_layout.freezed.dart';
part 'deck_layout.g.dart';

@freezed
abstract class DeckLayout with _$DeckLayout {
  const factory DeckLayout({
    // Unique identifier for this deck layout configuration.
    String? id,
    // Human-readable name for the deck layout.
    String? name,
    // List of resource items placed on the deck.
    List<DeckItem>? items,
    // Optional: schema version for the deck layout definition.
    String? schemaVersion,
    // Optional: metadata about the robot or deck type.
    Map<String, dynamic>?
    robot, // e.g., { "model": "OT-2", "deckId": "ot2_standard" }
    List<String>?
    positions, // List of positions on the deck currently placeholders
    // TODO: DL1: Generally align with PLR and Populate with items and positions consistent with PLR serialization
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
    // The ID of the resource definition being used.
    @JsonKey(name: 'resource_definition_accession_id')
    required String resourceDefinitionId,
    // Optional: A specific resource definition, if not just referencing by ID.
    // This could be embedded or fetched separately.
    @JsonKey(name: 'resource_definition')
    ResourceDefinition? resourceDefinition,
    // Human-readable display name for this item in this context.
    @JsonKey(name: 'display_name') String? displayName,
  }) = _DeckItem;

  factory DeckItem.fromJson(Map<String, dynamic> json) =>
      _$DeckItemFromJson(json);
}
