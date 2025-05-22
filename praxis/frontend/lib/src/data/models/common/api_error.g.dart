// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'api_error.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_ApiError _$ApiErrorFromJson(Map<String, dynamic> json) => _ApiError(
  statusCode: (json['statusCode'] as num?)?.toInt(),
  message: json['message'] as String?,
  detail: json['detail'],
  errors: (json['errors'] as Map<String, dynamic>?)?.map(
    (k, e) =>
        MapEntry(k, (e as List<dynamic>).map((e) => e as String).toList()),
  ),
);

Map<String, dynamic> _$ApiErrorToJson(_ApiError instance) => <String, dynamic>{
  'statusCode': instance.statusCode,
  'message': instance.message,
  'detail': instance.detail,
  'errors': instance.errors,
};
