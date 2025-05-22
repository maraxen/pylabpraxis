// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'protocol_hardware.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_ProtocolHardware _$ProtocolHardwareFromJson(Map<String, dynamic> json) =>
    _ProtocolHardware(
      name: json['name'] as String,
      type: json['type'] as String,
      configuration: json['configuration'] as Map<String, dynamic>?,
      required: json['required'] as bool? ?? true,
      description: json['description'] as String?,
    );

Map<String, dynamic> _$ProtocolHardwareToJson(_ProtocolHardware instance) =>
    <String, dynamic>{
      'name': instance.name,
      'type': instance.type,
      'configuration': instance.configuration,
      'required': instance.required,
      'description': instance.description,
    };
