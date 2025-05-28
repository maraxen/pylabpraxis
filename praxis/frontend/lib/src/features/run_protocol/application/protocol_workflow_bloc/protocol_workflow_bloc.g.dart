// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'protocol_workflow_bloc.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_ProtocolWorkflowState _$ProtocolWorkflowStateFromJson(
  Map<String, dynamic> json,
) => _ProtocolWorkflowState(
  currentStep: $enumDecode(_$WorkflowStepEnumMap, json['currentStep']),
  selectedProtocolInfo:
      json['selectedProtocolInfo'] == null
          ? null
          : ProtocolInfo.fromJson(
            json['selectedProtocolInfo'] as Map<String, dynamic>,
          ),
  selectedProtocolDetails:
      json['selectedProtocolDetails'] == null
          ? null
          : ProtocolDetails.fromJson(
            json['selectedProtocolDetails'] as Map<String, dynamic>,
          ),
  configuredParameters: json['configuredParameters'] as Map<String, dynamic>?,
  assignedAssets: (json['assignedAssets'] as Map<String, dynamic>?)?.map(
    (k, e) => MapEntry(k, e as String),
  ),
  deckLayoutName: json['deckLayoutName'] as String?,
  preparedBackendConfig: json['preparedBackendConfig'] as Map<String, dynamic>?,
  protocolStartResponse:
      json['protocolStartResponse'] == null
          ? null
          : ProtocolStatusResponse.fromJson(
            json['protocolStartResponse'] as Map<String, dynamic>,
          ),
  isLoading: json['isLoading'] as bool? ?? false,
  error: json['error'] as String?,
  isCurrentStepDataValid: json['isCurrentStepDataValid'] as bool? ?? false,
  parametersCompletionPercent:
      (json['parametersCompletionPercent'] as num?)?.toDouble() ?? 0.0,
  navigationReturnTarget: $enumDecodeNullable(
    _$WorkflowStepEnumMap,
    json['navigationReturnTarget'],
  ),
);

Map<String, dynamic> _$ProtocolWorkflowStateToJson(
  _ProtocolWorkflowState instance,
) => <String, dynamic>{
  'currentStep': _$WorkflowStepEnumMap[instance.currentStep]!,
  'selectedProtocolInfo': instance.selectedProtocolInfo,
  'selectedProtocolDetails': instance.selectedProtocolDetails,
  'configuredParameters': instance.configuredParameters,
  'assignedAssets': instance.assignedAssets,
  'deckLayoutName': instance.deckLayoutName,
  'preparedBackendConfig': instance.preparedBackendConfig,
  'protocolStartResponse': instance.protocolStartResponse,
  'isLoading': instance.isLoading,
  'error': instance.error,
  'isCurrentStepDataValid': instance.isCurrentStepDataValid,
  'parametersCompletionPercent': instance.parametersCompletionPercent,
  'navigationReturnTarget':
      _$WorkflowStepEnumMap[instance.navigationReturnTarget],
};

const _$WorkflowStepEnumMap = {
  WorkflowStep.protocolSelection: 'protocolSelection',
  WorkflowStep.parameterConfiguration: 'parameterConfiguration',
  WorkflowStep.assetAssignment: 'assetAssignment',
  WorkflowStep.deckConfiguration: 'deckConfiguration',
  WorkflowStep.reviewAndPrepare: 'reviewAndPrepare',
  WorkflowStep.startProtocol: 'startProtocol',
  WorkflowStep.workflowComplete: 'workflowComplete',
};
