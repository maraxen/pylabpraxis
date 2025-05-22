// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'labware_definition.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_LabwareDefinition _$LabwareDefinitionFromJson(
  Map<String, dynamic> json,
) => _LabwareDefinition(
  id: json['id'] as String,
  displayName: json['display_name'] as String?,
  version: (json['version'] as num?)?.toInt(),
  namespace: json['namespace'] as String?,
  category: json['category'] as String?,
  dimensions: (json['dimensions'] as Map<String, dynamic>?)?.map(
    (k, e) => MapEntry(k, (e as num).toDouble()),
  ),
  wells: (json['wells'] as Map<String, dynamic>?)?.map(
    (k, e) => MapEntry(k, WellDefinition.fromJson(e as Map<String, dynamic>)),
  ),
  ordering:
      (json['ordering'] as List<dynamic>?)
          ?.map((e) => (e as List<dynamic>).map((e) => e as String).toList())
          .toList(),
  metadata: json['metadata'] as Map<String, dynamic>?,
  brand: json['brand'] as String?,
  model: json['model'] as String?,
);

Map<String, dynamic> _$LabwareDefinitionToJson(_LabwareDefinition instance) =>
    <String, dynamic>{
      'id': instance.id,
      'display_name': instance.displayName,
      'version': instance.version,
      'namespace': instance.namespace,
      'category': instance.category,
      'dimensions': instance.dimensions,
      'wells': instance.wells,
      'ordering': instance.ordering,
      'metadata': instance.metadata,
      'brand': instance.brand,
      'model': instance.model,
    };

_WellDefinition _$WellDefinitionFromJson(Map<String, dynamic> json) =>
    _WellDefinition(
      depth: (json['depth'] as num?)?.toDouble(),
      totalLiquidVolume: (json['totalLiquidVolume'] as num?)?.toDouble(),
      shape: json['shape'] as String?,
      diameter: (json['diameter'] as num?)?.toDouble(),
      xDimension: (json['xDimension'] as num?)?.toDouble(),
      yDimension: (json['yDimension'] as num?)?.toDouble(),
      x: (json['x'] as num).toDouble(),
      y: (json['y'] as num).toDouble(),
      z: (json['z'] as num?)?.toDouble(),
    );

Map<String, dynamic> _$WellDefinitionToJson(_WellDefinition instance) =>
    <String, dynamic>{
      'depth': instance.depth,
      'totalLiquidVolume': instance.totalLiquidVolume,
      'shape': instance.shape,
      'diameter': instance.diameter,
      'xDimension': instance.xDimension,
      'yDimension': instance.yDimension,
      'x': instance.x,
      'y': instance.y,
      'z': instance.z,
    };
