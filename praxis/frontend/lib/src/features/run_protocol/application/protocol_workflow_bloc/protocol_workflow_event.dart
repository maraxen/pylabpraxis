part of 'protocol_workflow_bloc.dart';

@freezed
sealed class ProtocolWorkflowEvent with _$ProtocolWorkflowEvent {
  /// Initializes the workflow, potentially setting it to the first step.
  const factory ProtocolWorkflowEvent.initializeWorkflow() = InitializeWorkflow;

  /// Dispatched when a protocol is selected on the ProtocolSelectionScreen.
  const factory ProtocolWorkflowEvent.protocolSelected({
    required ProtocolInfo selectedProtocol,
  }) = ProtocolSelectedInWorkflow;

  /// Dispatched when parameters are submitted from the ParameterConfigurationScreen.
  const factory ProtocolWorkflowEvent.parametersSubmitted({
    required Map<String, dynamic> parameters,
  }) = ParametersSubmittedToWorkflow;

  /// Dispatched when asset assignments are submitted from the AssetAssignmentScreen.
  const factory ProtocolWorkflowEvent.assetsSubmittedToWorkflow({
    required Map<String, String> assets,
  }) = AssetsSubmittedToWorkflow;

  /// Dispatched when deck configuration is submitted from the DeckConfigurationScreen.
  const factory ProtocolWorkflowEvent.deckConfigSubmitted({
    String? layoutName,
    PlatformFile? uploadedFile,
  }) = DeckConfigSubmittedToWorkflow;

  /// Dispatched when the protocol preparation is successful (from ProtocolReviewBloc).
  const factory ProtocolWorkflowEvent.protocolPrepared({
    required Map<String, dynamic> preparedConfig,
  }) = ProtocolSuccessfullyPrepared;

  /// Dispatched when the protocol start is successful (from ProtocolStartBloc).
  const factory ProtocolWorkflowEvent.protocolStarted({
    required ProtocolStatusResponse response,
  }) = ProtocolSuccessfullyStarted;

  /// General event to proceed to the next logical step in the workflow.
  const factory ProtocolWorkflowEvent.proceedToNextStep() = ProceedToNextStep;

  /// Event to navigate to a specific target step.
  /// [fromReviewScreen] indicates if this navigation originated from an "Edit" action
  /// on the ReviewAndPrepareScreen, used to handle return navigation.
  const factory ProtocolWorkflowEvent.goToStep({
    required WorkflowStep targetStep,
    @Default(false) bool fromReviewScreen,
  }) = GoToStep;

  /// Event to navigate to the previous step in the workflow.
  const factory ProtocolWorkflowEvent.goToPreviousStep() =
      GoToPreviousStep; // Added

  /// Resets the entire workflow to its initial state, clearing all collected data.
  const factory ProtocolWorkflowEvent.resetWorkflow() = ResetWorkflow;

  /// Internal event to signal that protocol details have been fetched.
  const factory ProtocolWorkflowEvent.protocolDetailsFetched({
    required ProtocolDetails protocolDetails,
  }) = _ProtocolDetailsFetched;

  /// Internal event to signal an error during protocol detail fetching.
  const factory ProtocolWorkflowEvent.protocolDetailsFetchFailed({
    required String error,
  }) = _ProtocolDetailsFetchFailed;

  /// Event to update the validity of the current step's data.
  const factory ProtocolWorkflowEvent.updateStepValidity({
    required bool isValid,
  }) = UpdateStepValidity;

  /// Event to update the parameter completion progress.
  const factory ProtocolWorkflowEvent.updateParametersProgress({
    required double completionPercent,
  }) = UpdateParametersProgress;
}
