// FILE: lib/src/data/models/protocol/protocol_details.dart
// Purpose: Defines the detailed structure of a protocol, including all its components.
// Corresponds to: ProtocolDetails in protocol.models.ts

import 'package:freezed_annotation/freezed_annotation.dart';

import './protocol_info.dart';
import './parameter_config.dart';
import './protocol_asset.dart';
import './protocol_step.dart';
import './protocol_hardware.dart';
import './deck_layout.dart'; // If you have a DeckLayout model

part 'protocol_details.freezed.dart';
part 'protocol_details.g.dart';

@freezed
abstract class ProtocolDetails with _$ProtocolDetails {
  const factory ProtocolDetails({
    // Basic information about the protocol, can be embedded or referenced.
    // Embedding ProtocolInfo directly using a spread operator in Freezed
    // is not directly supported for the constructor.
    // Instead, we list its fields or have a dedicated 'info' field.
    // For simplicity and direct mapping, let's include ProtocolInfo fields,
    // or have an 'info' field of type ProtocolInfo.
    // Option 1: Dedicated 'info' field
    required ProtocolInfo info,

    // Option 2: Flattened fields (if you prefer direct access, but less clean)
    // required String name,
    // required String path,
    // required String description,
    // String? version,
    // @JsonKey(name: 'last_modified') DateTime? lastModified,
    // List<String>? tags,
    // ... other fields from ProtocolInfo

    // Parameters required by the protocol.
    // The key is the parameter name.
    required Map<String, ParameterConfig> parameters,

    // Assets (labware, reagents, etc.) required or used by the protocol.
    List<ProtocolAsset>? assets,

    // Steps involved in executing the protocol.
    List<ProtocolStep>? steps,

    // Hardware requirements or configurations.
    List<ProtocolHardware>? hardware,

    // Deck layout configuration for the protocol.
    // This might be optional or could be a specific structure.
    DeckLayout? deckLayout, // Assuming you have a DeckLayout model
    // Schema version for the protocol definition itself.
    String? schemaVersion,

    // Any other global metadata specific to the protocol's execution or definition.
    Map<String, dynamic>? metadata,

    // Entry points or commands that can be run (e.g. "run", "calibrate")
    // The key could be the command name, value could be details or entry step ID.
    Map<String, dynamic>? commands,

    // Authorship and contact information.
    String? author, // Redundant if in ProtocolInfo, but sometimes present
    String? email,

    // Organization or lab associated with the protocol.
    String? organization,

    // Publication or reference links.
    List<String>? publications,

    // Changelog or version history notes.
    String? changelog,
  }) = _ProtocolDetails;

  factory ProtocolDetails.fromJson(Map<String, dynamic> json) =>
      _$ProtocolDetailsFromJson(json);
}
