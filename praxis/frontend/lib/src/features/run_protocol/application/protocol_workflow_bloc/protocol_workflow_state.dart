part of 'protocol_workflow_bloc.dart';

@freezed
abstract class ProtocolWorkflowState with _$ProtocolWorkflowState {
  const factory ProtocolWorkflowState({
    required WorkflowStep currentStep,
    ProtocolInfo? selectedProtocolInfo,
    ProtocolDetails? selectedProtocolDetails,
    Map<String, dynamic>? configuredParameters,
    Map<String, String>? assignedAssets,
    String? deckLayoutName,
    @JsonKey(ignore: true) PlatformFile? uploadedDeckFile, // Excluded from serialization
    Map<String, dynamic>? preparedBackendConfig,
    ProtocolStatusResponse? protocolStartResponse,
    @Default(false) bool isLoading,
    String? error,
    @Default(false) bool isCurrentStepDataValid,
    @Default(0.0) double parametersCompletionPercent,
    WorkflowStep? navigationReturnTarget,
  }) = _ProtocolWorkflowState;

  factory ProtocolWorkflowState.initial() => const ProtocolWorkflowState(
        currentStep: WorkflowStep.protocolSelection,
        isCurrentStepDataValid: false,
        parametersCompletionPercent: 0.0,
        navigationReturnTarget: null,
        // Ensure other nullable fields default to null as intended by freezed
        // selectedProtocolInfo: null,
        // selectedProtocolDetails: null,
        // configuredParameters: null,
        // assignedAssets: null,
        // deckLayoutName: null,
        // uploadedDeckFile: null, // Will be null due to ignore or if not set
        // preparedBackendConfig: null,
        // protocolStartResponse: null,
        // error: null,
      );

  factory ProtocolWorkflowState.fromJson(Map<String, dynamic> json) =>
      _$ProtocolWorkflowStateFromJson(json);
  // toJson method will be generated automatically by freezed
}
