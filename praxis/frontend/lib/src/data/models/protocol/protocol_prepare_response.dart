import 'package:freezed_annotation/freezed_annotation.dart';

part 'protocol_prepare_response.freezed.dart';
part 'protocol_prepare_response.g.dart';

@freezed
sealed class ProtocolPrepareResponse with _$ProtocolPrepareResponse {
  const factory ProtocolPrepareResponse({
    required String status, // "ready" or "invalid"
    required Map<String, dynamic> config,
    List<String>? errors,
    Map<String, dynamic>? assetSuggestions,
  }) = _ProtocolPrepareResponse;

  factory ProtocolPrepareResponse.fromJson(Map<String, dynamic> json) =>
      _$ProtocolPrepareResponseFromJson(json);
}
