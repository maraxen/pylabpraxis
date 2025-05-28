import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:praxis_lab_management/src/data/models/protocol/protocol_parameter_detail.dart';
import 'package:praxis_lab_management/src/data/models/protocol/protocol_asset_detail.dart';

part 'protocol_details.freezed.dart';
part 'protocol_details.g.dart';

@freezed
sealed class ProtocolDetails with _$ProtocolDetails {
  const factory ProtocolDetails({
    required String name,
    required String path,
    required String description,
    required Map<String, ProtocolParameterDetail> parameters,
    required List<ProtocolAssetDetail> assets,
    required bool hasAssets,
    required bool hasParameters,
    // Corresponds to 'requires_config' in backend.
    // Based on backend logic: `not (bool(parameters) or bool(assets))`,
    // this field is true if there are NO parameters AND NO assets.
    // Consider renaming to 'isSimple' or 'requiresNoConfiguration' for clarity if appropriate.
    required bool requiresConfig,
  }) = _ProtocolDetails;

  factory ProtocolDetails.fromJson(Map<String, dynamic> json) =>
      _$ProtocolDetailsFromJson(json);
}
