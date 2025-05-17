// FILE: lib/src/data/models/protocol/protocol_asset.dart
// Purpose: Defines the structure for a protocol asset.
// Corresponds to: ProtocolAsset in protocol.models.ts

import 'package:freezed_annotation/freezed_annotation.dart';

part 'protocol_asset.freezed.dart';
part 'protocol_asset.g.dart';

@freezed
abstract class ProtocolAsset with _$ProtocolAsset {
  const factory ProtocolAsset({
    // A unique name or identifier for the asset within the protocol.
    required String name,
    // The type of asset (e.g., 'labware', 'reagent', 'instrument_module').
    required String type,
    // A human-readable description of the asset and its role.
    String? description,
    // Indicates if this asset must be assigned by the user.
    @Default(false) bool required,
    // Optional: Specific constraints or accepted values for this asset.
    // This could be a list of IDs, a type pattern, etc.
    // For simplicity, keeping as dynamic or string for now.
    // Could be a more specific type if asset constraints become complex.
    dynamic constraints,
    // Optional: The default value or assignment for this asset, if any.
    @JsonKey(name: 'default_value') String? defaultValue,
    // Optional: Current value assigned by the user during configuration.
    String? value,
  }) = _ProtocolAsset;

  // Factory constructor for deserializing JSON.
  factory ProtocolAsset.fromJson(Map<String, dynamic> json) =>
      _$ProtocolAssetFromJson(json);
}
