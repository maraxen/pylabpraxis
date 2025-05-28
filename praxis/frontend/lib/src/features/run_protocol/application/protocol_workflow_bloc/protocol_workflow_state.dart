part of 'protocol_workflow_bloc.dart';

@freezed
abstract class ProtocolWorkflowState with _$ProtocolWorkflowState {
  const factory ProtocolWorkflowState({
    required WorkflowStep currentStep,
    ProtocolInfo? selectedProtocolInfo,
    @ProtocolDetailsConverter() ProtocolDetails? selectedProtocolDetails,
    Map<String, dynamic>? configuredParameters,
    Map<String, String>? assignedAssets,
    String? deckLayoutName,
    @JsonKey(includeFromJson: false, includeToJson: false)
    PlatformFile? uploadedDeckFile, // Excluded from serialization
    Map<String, dynamic>? preparedBackendConfig,
    ProtocolStatusResponse? protocolStartResponse,
    @Default(false) bool isLoading,
    String? error,
    @Default(false) bool isCurrentStepDataValid,
    @Default(0.0) double parametersCompletionPercent,
    WorkflowStep? navigationReturnTarget,
    required List<WorkflowStep> history,
  }) = _ProtocolWorkflowState;

  factory ProtocolWorkflowState.initial() => const _ProtocolWorkflowState(
    currentStep: WorkflowStep.protocolSelection,
    history: [WorkflowStep.protocolSelection],
    isLoading: false,
    isCurrentStepDataValid: false,
    parametersCompletionPercent: 0.0,
    selectedProtocolInfo: null,
    selectedProtocolDetails: null,
    configuredParameters: {},
    assignedAssets: {},
    deckLayoutName: null,
    uploadedDeckFile: null,
    preparedBackendConfig: null,
    protocolStartResponse: null,
    navigationReturnTarget: null,
  );

  factory ProtocolWorkflowState.fromJson(Map<String, dynamic> json) =>
      _$ProtocolWorkflowStateFromJson(json);
}
