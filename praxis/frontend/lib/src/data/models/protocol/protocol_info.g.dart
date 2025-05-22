// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'protocol_info.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_ProtocolInfo _$ProtocolInfoFromJson(Map<String, dynamic> json) =>
    _ProtocolInfo(
      name: json['name'] as String,
      path: json['path'] as String,
      description: json['description'] as String,
      version: json['version'] as String?,
      lastModified:
          json['last_modified'] == null
              ? null
              : DateTime.parse(json['last_modified'] as String),
      tags: (json['tags'] as List<dynamic>?)?.map((e) => e as String).toList(),
      author: json['author'] as String?,
      license: json['license'] as String?,
      createdDate:
          json['created_date'] == null
              ? null
              : DateTime.parse(json['created_date'] as String),
      category: json['category'] as String?,
      metadata: json['metadata'] as Map<String, dynamic>?,
      isFavorite: json['is_favorite'] as bool?,
      runCount: (json['run_count'] as num?)?.toInt(),
      averageRating: (json['average_rating'] as num?)?.toDouble(),
      estimatedDuration: json['estimated_duration'] as String?,
      complexity: $enumDecodeNullable(
        _$ProtocolComplexityEnumMap,
        json['complexity'],
      ),
      iconUrl: json['icon_url'] as String?,
    );

Map<String, dynamic> _$ProtocolInfoToJson(_ProtocolInfo instance) =>
    <String, dynamic>{
      'name': instance.name,
      'path': instance.path,
      'description': instance.description,
      'version': instance.version,
      'last_modified': instance.lastModified?.toIso8601String(),
      'tags': instance.tags,
      'author': instance.author,
      'license': instance.license,
      'created_date': instance.createdDate?.toIso8601String(),
      'category': instance.category,
      'metadata': instance.metadata,
      'is_favorite': instance.isFavorite,
      'run_count': instance.runCount,
      'average_rating': instance.averageRating,
      'estimated_duration': instance.estimatedDuration,
      'complexity': _$ProtocolComplexityEnumMap[instance.complexity],
      'icon_url': instance.iconUrl,
    };

const _$ProtocolComplexityEnumMap = {
  ProtocolComplexity.low: 'low',
  ProtocolComplexity.medium: 'medium',
  ProtocolComplexity.high: 'high',
};
