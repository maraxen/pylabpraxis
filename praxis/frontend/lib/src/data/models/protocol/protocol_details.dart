import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:praxis_lab_management/src/data/models/protocol/parameter_config.dart'; // ADD this import
import 'package:praxis_lab_management/src/data/models/protocol/protocol_asset_detail.dart';

part 'protocol_details.freezed.dart';

@freezed
sealed class ProtocolDetails with _$ProtocolDetails {
  const factory ProtocolDetails({
    required String name,
    required String path,
    required String description,
    required Map<String, ParameterConfig> parameters, // UPDATE this line
    required List<ProtocolAssetDetail> assets,
    required bool hasAssets,
    required bool hasParameters,
    required bool requiresConfig,
  }) = _ProtocolDetails;
}
