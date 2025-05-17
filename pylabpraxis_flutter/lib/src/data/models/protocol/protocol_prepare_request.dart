// FILE: lib/src/data/models/protocol/protocol_prepare_request.dart
// Purpose: Defines the request body for preparing a protocol run.
// Corresponds to: ProtocolPrepareRequest in protocol.models.ts

import 'package:freezed_annotation/freezed_annotation.dart';

// Assuming ProtocolParameterValue is dynamic or specific types are handled directly.
// If you have a specific class/union for parameter values, import it here.
// import './protocol_parameter_value.dart';

part 'protocol_prepare_request.freezed.dart';
part 'protocol_prepare_request.g.dart';

@freezed
abstract class ProtocolPrepareRequest with _$ProtocolPrepareRequest {
  const factory ProtocolPrepareRequest({
    // The path or unique identifier of the protocol to be prepared.
    required String protocolPath,

    // The configured parameter values for the protocol run.
    // The keys are parameter names (matching ParameterConfig.name),
    // and values are the user-provided or default values.
    required Map<String, dynamic> parameters,
    // Using dynamic for values as per ProtocolParameterValue
    // Asset assignments made by the user.
    // The key is the asset name (matching ProtocolAsset.name),
    // and the value is the assigned asset ID or resource identifier.
    Map<String, String>? assets,

    // Information about the deck layout to be used.
    // This could be the name/ID of a pre-existing layout or an uploaded layout file.
    // If a new layout is uploaded, this might contain its temporary ID or content.
    // For simplicity, using a map; this could be a more structured object.
    @JsonKey(name: 'deck_layout_config') Map<String, dynamic>? deckLayoutConfig,
    // Example deckLayoutConfig structures:
    // For a named layout: { "name": "my_saved_layout_id" }
    // For an uploaded file: { "file_id": "temp_uploaded_deck_file_id" } or potentially the file content itself if small
    // Or, if the DeckLayout model is directly sent: DeckLayout? deckLayout,

    // Optional: User ID or context for the preparation.
    String? userId,

    // Optional: Any specific run options or overrides.
    Map<String, dynamic>? runOptions,

    // Optional: A user-defined name or label for this specific run.
    String? runLabel,
  }) = _ProtocolPrepareRequest;

  // Factory constructor for deserializing JSON (primarily for testing or if request is ever read).
  factory ProtocolPrepareRequest.fromJson(Map<String, dynamic> json) =>
      _$ProtocolPrepareRequestFromJson(json);
}
