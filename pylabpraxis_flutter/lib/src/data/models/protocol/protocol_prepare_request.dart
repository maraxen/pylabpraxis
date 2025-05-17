// Represents the request body for preparing a protocol run.
//
// This model is sent to the backend to initiate the preparation phase
// of a protocol, which typically involves validating parameters,
// checking asset availability, and configuring the workcell.

import 'package:freezed_annotation/freezed_annotation.dart';
import 'deck_layout.dart'; // Import for DeckLayout model

part 'protocol_prepare_request.freezed.dart';
part 'protocol_prepare_request.g.dart';

/// Represents the request body for preparing a protocol run.
///
/// This model is sent to the backend to initiate the preparation phase
/// of a protocol, which typically involves validating parameters,
/// checking asset availability, and configuring the workcell.
@freezed
abstract class ProtocolPrepareRequest with _$ProtocolPrepareRequest {
  /// Default constructor for [ProtocolPrepareRequest].
  ///
  /// Parameters:
  ///   [protocolPath] - The path or identifier of the protocol to prepare.
  ///   [parameters] - A map of parameter names to their configured values.
  ///                  The values can be of various types (string, number, boolean, list, map).
  ///   [assignedAssets] - An optional map of required asset names to their assigned instance IDs or values.
  ///   [deckLayoutPath] - An optional path to a specific deck layout file to be used.
  ///   [deckLayoutContent] - An optional [DeckLayout] object representing the content of a deck layout,
  ///                         if a pre-defined layout is not used or is being overridden.
  ///                         This aligns with the backend's expectation of a structured deck layout.
  const factory ProtocolPrepareRequest({
    @JsonKey(name: 'protocol_path') required String protocolPath,
    required Map<String, dynamic> parameters,
    @JsonKey(name: 'assigned_assets') Map<String, String>? assignedAssets,
    @JsonKey(name: 'deck_layout_path') String? deckLayoutPath,
    @JsonKey(name: 'deck_layout_content') DeckLayout? deckLayoutContent,
  }) = _ProtocolPrepareRequest;

  /// Creates a [ProtocolPrepareRequest] instance from a JSON map.
  ///
  /// This factory constructor is used by `json_serializable` to deserialize
  /// JSON data into a [ProtocolPrepareRequest] object (though typically this
  /// model is serialized to JSON for sending requests).
  factory ProtocolPrepareRequest.fromJson(Map<String, dynamic> json) =>
      _$ProtocolPrepareRequestFromJson(json);
}
