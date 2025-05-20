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
    PlatformFile? uploadedDeckFile,
    Map<String, dynamic>? preparedBackendConfig,
    ProtocolStatusResponse? protocolStartResponse,

    @Default(false) bool isLoading,
    String? error,
    @Default(false) bool isCurrentStepDataValid,
    @Default(0.0) double parametersCompletionPercent,

    /// If navigating from ReviewScreen to an edit step, this stores
    /// `WorkflowStep.reviewAndPrepare` to indicate where to return after editing.
    WorkflowStep? navigationReturnTarget,
  }) = _ProtocolWorkflowState;

  factory ProtocolWorkflowState.initial() => const ProtocolWorkflowState(
    currentStep: WorkflowStep.protocolSelection,
    isCurrentStepDataValid: false,
    parametersCompletionPercent: 0.0,
    navigationReturnTarget: null,
  );
}
