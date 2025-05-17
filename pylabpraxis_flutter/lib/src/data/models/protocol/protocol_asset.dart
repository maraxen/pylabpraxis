// Represents an asset required by a protocol.
//
// Assets can be physical items like labware, reagents, or digital files
// like calibration data or deck layouts.

import 'package:freezed_annotation/freezed_annotation.dart';
import 'parameter_config.dart'; // Import for ParameterConfig

part 'protocol_asset.freezed.dart';
part 'protocol_asset.g.dart';

/// Represents an asset required by a protocol.
///
/// Assets can be physical items like labware, reagents, or digital files
/// like calibration data or deck layouts.
@freezed
abstract class ProtocolAsset with _$ProtocolAsset {
  /// Default constructor for [ProtocolAsset].
  ///
  /// Parameters:
  ///   [name] - The name of the asset.
  ///   [type] - The type of the asset (e.g., 'labware', 'reagent', 'file').
  ///   [description] - An optional description of the asset.
  ///   [required] - A boolean indicating if the asset is mandatory for the protocol.
  ///   [validationConfig] - Optional [ParameterConfig] defining constraints for selecting
  ///                        or validating this asset. This aligns with backend's `RequiredAsset.validation_config`.
  ///   [allowedExtensions] - Optional list of allowed file extensions if the asset is a file.
  ///                         This aligns with backend's `RequiredAsset.allowed_extensions`.
  ///   [contentType] - Optional content type for the asset, an alternative or supplement to allowedExtensions.
  const factory ProtocolAsset({
    required String name,
    required String type,
    String? description,
    @Default(true) bool required,
    @JsonKey(name: 'validation_config') ParameterConfig? validationConfig,
    @JsonKey(name: 'allowed_extensions') List<String>? allowedExtensions,
    @JsonKey(name: 'content_type') String? contentType,
  }) = _ProtocolAsset;

  /// Creates a [ProtocolAsset] instance from a JSON map.
  ///
  /// This factory constructor is used by `json_serializable` to deserialize
  /// JSON data into a [ProtocolAsset] object.
  factory ProtocolAsset.fromJson(Map<String, dynamic> json) =>
      _$ProtocolAssetFromJson(json);
}
