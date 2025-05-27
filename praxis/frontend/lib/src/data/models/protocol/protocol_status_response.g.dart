// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'protocol_status_response.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_ProtocolStatusResponse _$ProtocolStatusResponseFromJson(
  Map<String, dynamic> json,
) => _ProtocolStatusResponse(
  runId: json['runId'] as String,
  status: $enumDecode(_$RunStatusEnumMap, json['status']),
  message: json['message'] as String?,
  timestamp:
      json['timestamp'] == null
          ? null
          : DateTime.parse(json['timestamp'] as String),
  progress: json['progress'],
  results: json['results'] as Map<String, dynamic>?,
  estimatedTimeRemaining: json['estimated_time_remaining'] as String?,
  logsUrl: json['logsUrl'] as String?,
);

Map<String, dynamic> _$ProtocolStatusResponseToJson(
  _ProtocolStatusResponse instance,
) => <String, dynamic>{
  'runId': instance.runId,
  'status': _$RunStatusEnumMap[instance.status]!,
  'message': instance.message,
  'timestamp': instance.timestamp?.toIso8601String(),
  'progress': instance.progress,
  'results': instance.results,
  'estimated_time_remaining': instance.estimatedTimeRemaining,
  'logsUrl': instance.logsUrl,
};

const _$RunStatusEnumMap = {
  RunStatus.pending: 'pending',
  RunStatus.preparing: 'preparing',
  RunStatus.running: 'running',
  RunStatus.paused: 'paused',
  RunStatus.cancelling: 'cancelling',
  RunStatus.succeeded: 'succeeded',
  RunStatus.failed: 'failed',
  RunStatus.cancelled: 'cancelled',
  RunStatus.unknown: 'unknown',
};
