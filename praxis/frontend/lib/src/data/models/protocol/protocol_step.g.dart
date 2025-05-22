// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'protocol_step.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_ProtocolStep _$ProtocolStepFromJson(Map<String, dynamic> json) =>
    _ProtocolStep(
      id: json['id'] as String,
      name: json['name'] as String,
      description: json['description'] as String?,
      command: json['command'] as String,
      arguments: json['arguments'] as Map<String, dynamic>?,
      estimatedDuration: json['estimated_duration'] as String?,
      order: (json['order'] as num?)?.toInt(),
      skipConditions: json['skipConditions'] as String?,
      dependencies:
          (json['dependencies'] as List<dynamic>?)
              ?.map((e) => e as String)
              .toList(),
      resources:
          (json['resources'] as List<dynamic>?)
              ?.map((e) => e as String)
              .toList(),
      uiHints: json['uiHints'] as Map<String, dynamic>?,
    );

Map<String, dynamic> _$ProtocolStepToJson(_ProtocolStep instance) =>
    <String, dynamic>{
      'id': instance.id,
      'name': instance.name,
      'description': instance.description,
      'command': instance.command,
      'arguments': instance.arguments,
      'estimated_duration': instance.estimatedDuration,
      'order': instance.order,
      'skipConditions': instance.skipConditions,
      'dependencies': instance.dependencies,
      'resources': instance.resources,
      'uiHints': instance.uiHints,
    };
