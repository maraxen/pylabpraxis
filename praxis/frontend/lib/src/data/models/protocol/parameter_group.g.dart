// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'parameter_group.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_ParameterGroup _$ParameterGroupFromJson(Map<String, dynamic> json) =>
    _ParameterGroup(
      name: json['name'] as String,
      displayName: json['displayName'] as String?,
      description: json['description'] as String?,
      parameters:
          (json['parameters'] as List<dynamic>?)
              ?.map(
                (e) => ParameterDefinition.fromJson(e as Map<String, dynamic>),
              )
              .toList() ??
          const [],
    );

Map<String, dynamic> _$ParameterGroupToJson(_ParameterGroup instance) =>
    <String, dynamic>{
      'name': instance.name,
      'displayName': instance.displayName,
      'description': instance.description,
      'parameters': instance.parameters,
    };
