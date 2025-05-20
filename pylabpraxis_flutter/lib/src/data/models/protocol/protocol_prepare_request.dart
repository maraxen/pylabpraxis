import 'package:freezed_annotation/freezed_annotation.dart';

part 'protocol_prepare_request.freezed.dart';
part 'protocol_prepare_request.g.dart';

/// Data Transfer Object (DTO) for requesting the preparation of a protocol run.
/// This model is sent to the backend to configure a protocol before execution.
@freezed
abstract class ProtocolPrepareRequest with _$ProtocolPrepareRequest {
  /// Default constructor for [ProtocolPrepareRequest].
  ///
  /// Requires:
  /// - [protocolId]: The unique identifier of the protocol to be prepared.
  ///
  /// Optional:
  /// - [params]: A map of parameter names to their configured values.
  ///             The backend will use these to override default parameter values.
  ///             The structure of this map should align with the parameter definitions
  ///             of the specified protocol.
  /// - [assets]: A map of asset names (as defined in the protocol) to their
  ///             assigned physical asset IDs or names.
  /// - [deckLayoutName]: The name of a pre-existing deck layout to be used.
  ///                     If provided, `deckLayoutContent` should typically be null.
  /// - [deckLayoutContent]: The actual content of a new or modified deck layout,
  ///                        usually as a JSON map. If provided, `deckLayoutName` might
  ///                        be used as a reference or ignored by the backend if the content
  ///                        is considered an ad-hoc layout.
  const factory ProtocolPrepareRequest({
    /// The ID of the protocol to prepare.
    @JsonKey(name: 'protocol_id') required String protocolId,

    /// Parameters for the protocol run.
    /// The key in the backend JSON is expected to be 'params'.
    @JsonKey(name: 'params') Map<String, dynamic>? params,

    /// Asset assignments for the protocol run.
    Map<String, String>? assets,

    /// Name of the deck layout to use (if selecting an existing one).
    @JsonKey(name: 'deck_layout_name') String? deckLayoutName,

    /// Content of the deck layout (if uploading a new or modified one).
    /// This is expected to be a JSON string or a Map representing the JSON structure.
    @JsonKey(name: 'deck_layout_content')
    Map<String, dynamic>? deckLayoutContent,
  }) = _ProtocolPrepareRequest;

  /// Creates a [ProtocolPrepareRequest] instance from a JSON map.
  factory ProtocolPrepareRequest.fromJson(Map<String, dynamic> json) =>
      _$ProtocolPrepareRequestFromJson(json);
}
