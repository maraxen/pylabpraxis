// FILE: lib/src/data/models/protocol/resource_definition.dart
// Purpose: Defines the structure for a resource definition.
// Corresponds to: ResourceDefinition in protocol.models.ts

import 'package:freezed_annotation/freezed_annotation.dart';

part 'resource_definition.freezed.dart';
part 'resource_definition.g.dart';

@freezed
abstract class ResourceDefinition with _$ResourceDefinition {
  const factory ResourceDefinition({
    // Unique identifier for the resource definition (e.g., 'opentrons_96_tiprack_300ul').
    required String id,
    // Human-readable display name.
    @JsonKey(name: 'display_name') String? displayName,
    // Version of the resource definition.
    int? version,
    // Namespace of the resource (e.g., 'opentrons').
    String? namespace,
    // Category of resource (e.g., 'tipRack', 'wellPlate', 'reservoir').
    String? category,
    // Dimensions of the resource.
    Map<String, double>?
    dimensions, // e.g., { "xDimension": 127.76, "yDimension": 85.48, "zDimension": 14.7 }
    // Well definitions (if applicable).
    Map<String, WellDefinition>? wells, // Keyed by well name e.g., "A1"
    // Ordering of wells (e.g., column-wise or row-wise).
    List<List<String>>? ordering,
    // Generic metadata.
    Map<String, dynamic>? metadata,
    // Brand of the resource.
    String? brand,
    // Specific model or part number.
    String? model,
  }) = _ResourceDefinition;

  factory ResourceDefinition.fromJson(Map<String, dynamic> json) =>
      _$ResourceDefinitionFromJson(json);
}

@freezed
abstract class WellDefinition with _$WellDefinition {
  const factory WellDefinition({
    // Depth of the well in mm.
    double? depth,
    // Total liquid volume of the well in µL.
    double? totalLiquidVolume,
    // Shape of the well (e.g., 'circular', 'rectangular').
    String? shape,
    // Diameter of the well in mm (if circular).
    double? diameter,
    // X dimension of the well in mm (if rectangular).
    double? xDimension,
    // Y dimension of the well in mm (if rectangular).
    double? yDimension,
    // X-coordinate of the well's center relative to the resource origin.
    required double x,
    // Y-coordinate of the well's center relative to the resource origin.
    required double y,
    // Z-coordinate of the well's bottom relative to the resource origin.
    double? z,
  }) = _WellDefinition;

  factory WellDefinition.fromJson(Map<String, dynamic> json) =>
      _$WellDefinitionFromJson(json);
}
