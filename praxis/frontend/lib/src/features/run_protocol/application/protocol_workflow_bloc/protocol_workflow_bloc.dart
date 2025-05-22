import 'dart:async';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:file_picker/file_picker.dart';
import 'package:pylabpraxis_flutter/src/data/models/protocol/protocol_info.dart';
import 'package:pylabpraxis_flutter/src/data/models/protocol/protocol_details.dart';
import 'package:pylabpraxis_flutter/src/data/models/protocol/protocol_status_response.dart';
import 'package:pylabpraxis_flutter/src/data/repositories/protocol_repository.dart';
import 'package:pylabpraxis_flutter/src/features/run_protocol/domain/workflow_step.dart';

import 'package:pylabpraxis_flutter/src/features/run_protocol/application/protocols_discovery_bloc/protocols_discovery_bloc.dart';
import 'package:pylabpraxis_flutter/src/features/run_protocol/application/protocol_parameters_bloc/protocol_parameters_bloc.dart';
import 'package:pylabpraxis_flutter/src/features/run_protocol/application/protocol_assets_bloc/protocol_assets_bloc.dart';
import 'package:pylabpraxis_flutter/src/features/run_protocol/application/deck_configuration_bloc/deck_configuration_bloc.dart';
import 'package:pylabpraxis_flutter/src/features/run_protocol/application/protocol_review_bloc/protocol_review_bloc.dart';
import 'package:pylabpraxis_flutter/src/features/run_protocol/application/protocol_start_bloc/protocol_start_bloc.dart';
import 'package:pylabpraxis_flutter/src/features/run_protocol/domain/review_data_bundle.dart';

part 'protocol_workflow_event.dart';
part 'protocol_workflow_state.dart';
part 'protocol_workflow_bloc.freezed.dart';

class ProtocolWorkflowBloc
    extends Bloc<ProtocolWorkflowEvent, ProtocolWorkflowState> {
  final ProtocolRepository _protocolRepository;

  final ProtocolsDiscoveryBloc? _protocolsDiscoveryBloc;
  final ProtocolParametersBloc _protocolParametersBloc;
  final ProtocolAssetsBloc _protocolAssetsBloc;
  final DeckConfigurationBloc _deckConfigurationBloc;
  final ProtocolReviewBloc _protocolReviewBloc;
  final ProtocolStartBloc _protocolStartBloc;

  StreamSubscription<ProtocolParametersState>? _parametersBlocSubscription;

  ProtocolWorkflowBloc({
    required ProtocolRepository protocolRepository,
    required ProtocolsDiscoveryBloc protocolsDiscoveryBloc,
    required ProtocolParametersBloc protocolParametersBloc,
    required ProtocolAssetsBloc protocolAssetsBloc,
    required DeckConfigurationBloc deckConfigurationBloc,
    required ProtocolReviewBloc protocolReviewBloc,
    required ProtocolStartBloc protocolStartBloc,
  }) : _protocolRepository = protocolRepository,
       _protocolsDiscoveryBloc = protocolsDiscoveryBloc,
       _protocolParametersBloc = protocolParametersBloc,
       _protocolAssetsBloc = protocolAssetsBloc,
       _deckConfigurationBloc = deckConfigurationBloc,
       _protocolReviewBloc = protocolReviewBloc,
       _protocolStartBloc = protocolStartBloc,
       super(ProtocolWorkflowState.initial()) {
    on<InitializeWorkflow>(_onInitializeWorkflow);
    on<ProtocolSelectedInWorkflow>(_onProtocolSelectedInWorkflow);
    on<_ProtocolDetailsFetched>(_onProtocolDetailsFetched);
    on<_ProtocolDetailsFetchFailed>(_onProtocolDetailsFetchFailed);
    on<ParametersSubmittedToWorkflow>(_onParametersSubmitted);
    on<AssetsSubmittedToWorkflow>(_onAssetsSubmitted);
    on<DeckConfigSubmittedToWorkflow>(_onDeckConfigSubmitted);
    on<ProtocolSuccessfullyPrepared>(_onProtocolSuccessfullyPrepared);
    on<ProtocolSuccessfullyStarted>(_onProtocolSuccessfullyStarted);
    on<ProceedToNextStep>(_onProceedToNextStep);
    on<GoToStep>(_onGoToStep);
    on<ResetWorkflow>(_onResetWorkflow);
    on<UpdateStepValidity>(_onUpdateStepValidity);
    on<UpdateParametersProgress>(_onUpdateParametersProgress);

    // Fix the subscription to use the new getters and properly check the state type
    _parametersBlocSubscription = _protocolParametersBloc.stream.listen((
      paramState,
    ) {
      // Use the bloc's helper getters for simpler, safer access to state properties
      add(
        UpdateParametersProgress(
          completionPercent: _protocolParametersBloc.completionPercent,
        ),
      );

      if (state.currentStep == WorkflowStep.parameterConfiguration) {
        add(UpdateStepValidity(isValid: _protocolParametersBloc.isFormValid));
      }
    });
  }

  @override
  Future<void> close() {
    _parametersBlocSubscription?.cancel();
    return super.close();
  }

  void _onInitializeWorkflow(
    InitializeWorkflow event,
    Emitter<ProtocolWorkflowState> emit,
  ) {
    emit(ProtocolWorkflowState.initial());
    _protocolsDiscoveryBloc?.add(const FetchDiscoveredProtocols());
    _protocolParametersBloc.add(
      const LoadProtocolParameters(
        protocolDetails: ProtocolDetails(
          info: ProtocolInfo(name: '', version: '', path: '', description: ''),
          parameters: {},
        ),
      ),
    );
    _protocolAssetsBloc.add(
      const LoadRequiredAssets(assetsFromProtocolDetails: []),
    );
    _deckConfigurationBloc.add(const InitializeDeckConfiguration());
    _protocolReviewBloc.add(const ResetReview());
    _protocolStartBloc.add(const ResetStart());
  }

  void _onUpdateParametersProgress(
    UpdateParametersProgress event,
    Emitter<ProtocolWorkflowState> emit,
  ) {
    emit(state.copyWith(parametersCompletionPercent: event.completionPercent));
  }

  Future<void> _onProtocolSelectedInWorkflow(
    ProtocolSelectedInWorkflow event,
    Emitter<ProtocolWorkflowState> emit,
  ) async {
    emit(
      state.copyWith(
        selectedProtocolInfo: event.selectedProtocol,
        isLoading: true,
        error: null,
        isCurrentStepDataValid: true, // Selection made, now fetch details
        parametersCompletionPercent: 0.0,
        // navigationReturnTarget: null, // Clear return target if starting new protocol selection
      ),
    );
    try {
      final details = await _protocolRepository.getProtocolDetails(
        event.selectedProtocol.path,
      );
      add(_ProtocolDetailsFetched(protocolDetails: details));
    } catch (e) {
      add(_ProtocolDetailsFetchFailed(error: e.toString()));
    }
  }

  void _onProtocolDetailsFetched(
    _ProtocolDetailsFetched event,
    Emitter<ProtocolWorkflowState> emit,
  ) {
    emit(
      state.copyWith(
        selectedProtocolDetails: event.protocolDetails,
        isLoading: false,
      ),
    );
    _protocolParametersBloc.add(
      LoadProtocolParameters(
        protocolDetails: event.protocolDetails,
        // If returning to params from review, existingConfiguredParameters should be passed
        existingConfiguredParameters:
            state.navigationReturnTarget == WorkflowStep.reviewAndPrepare
                ? state.configuredParameters
                : null,
      ),
    );

    // If we were editing and returning to review, go there. Otherwise, proceed normally.
    if (state.navigationReturnTarget == WorkflowStep.reviewAndPrepare &&
        state.currentStep == WorkflowStep.protocolSelection) {
      add(GoToStep(targetStep: WorkflowStep.reviewAndPrepare));
      // navigationReturnTarget will be cleared in _onGoToStep or when review is reloaded
    } else {
      add(const ProceedToNextStep());
    }
  }

  void _onProtocolDetailsFetchFailed(
    _ProtocolDetailsFetchFailed event,
    Emitter<ProtocolWorkflowState> emit,
  ) {
    emit(
      state.copyWith(
        isLoading: false,
        error: 'Failed to load protocol details: ${event.error}',
        isCurrentStepDataValid: false,
      ),
    );
  }

  void _onParametersSubmitted(
    ParametersSubmittedToWorkflow event,
    Emitter<ProtocolWorkflowState> emit,
  ) {
    final returnTarget = state.navigationReturnTarget;
    emit(
      state.copyWith(
        configuredParameters: event.parameters,
        navigationReturnTarget: null, // Clear after using
      ),
    );

    if (returnTarget == WorkflowStep.reviewAndPrepare) {
      add(GoToStep(targetStep: WorkflowStep.reviewAndPrepare));
    } else {
      if (state.selectedProtocolDetails?.assets != null &&
          state.selectedProtocolDetails!.assets!.isNotEmpty) {
        _protocolAssetsBloc.add(
          LoadRequiredAssets(
            assetsFromProtocolDetails: state.selectedProtocolDetails!.assets!,
            existingAssignments:
                state.assignedAssets, // Pass existing if any (for re-editing)
          ),
        );
      }
      add(const ProceedToNextStep());
    }
  }

  void _onAssetsSubmitted(
    AssetsSubmittedToWorkflow event,
    Emitter<ProtocolWorkflowState> emit,
  ) {
    final returnTarget = state.navigationReturnTarget;
    emit(
      state.copyWith(
        assignedAssets: event.assets,
        navigationReturnTarget: null,
      ),
    );

    if (returnTarget == WorkflowStep.reviewAndPrepare) {
      add(GoToStep(targetStep: WorkflowStep.reviewAndPrepare));
    } else {
      _deckConfigurationBloc.add(
        InitializeDeckConfiguration(
          initialSelectedLayoutName: state.deckLayoutName,
          initialPickedFile: state.uploadedDeckFile,
        ),
      );
      if (_deckConfigurationBloc.state is DeckConfigurationInitial) {
        _deckConfigurationBloc.add(const FetchAvailableDeckLayouts());
      }
      add(const ProceedToNextStep());
    }
  }

  void _onDeckConfigSubmitted(
    DeckConfigSubmittedToWorkflow event,
    Emitter<ProtocolWorkflowState> emit,
  ) {
    final returnTarget = state.navigationReturnTarget;
    final bool isValid =
        (event.layoutName != null && event.layoutName!.isNotEmpty) ||
        event.uploadedFile != null;

    emit(
      state.copyWith(
        deckLayoutName: event.layoutName,
        uploadedDeckFile: event.uploadedFile,
        isCurrentStepDataValid: isValid, // Update validity based on submission
        navigationReturnTarget: null,
      ),
    );
    // No need to call UpdateStepValidity here as we set it directly.

    if (returnTarget == WorkflowStep.reviewAndPrepare) {
      add(GoToStep(targetStep: WorkflowStep.reviewAndPrepare));
    } else {
      // This will be called by ProceedToNextStep if data is valid
      // _loadReviewDataAndProceed(emit); // Refactored to be part of ProceedToNextStep logic
      add(const ProceedToNextStep());
    }
  }

  void _loadReviewDataAndProceed(Emitter<ProtocolWorkflowState> emit) {
    if (state.selectedProtocolInfo != null &&
        state.configuredParameters != null &&
        state.assignedAssets != null) {
      final reviewData = ReviewDataBundle(
        selectedProtocolInfo: state.selectedProtocolInfo!,
        configuredParameters: state.configuredParameters!,
        assignedAssets: state.assignedAssets!,
        deckLayoutName: state.deckLayoutName,
        uploadedDeckFile: state.uploadedDeckFile,
      );
      _protocolReviewBloc.add(LoadReviewData(reviewData: reviewData));
      emit(
        state.copyWith(isCurrentStepDataValid: true),
      ); // Review screen is valid to view
    } else {
      // This case should ideally not be reached if previous steps ensure data.
      // emit(state.copyWith(error: "Cannot proceed to review: Missing data.", isCurrentStepDataValid: false));
    }
  }

  void _onProtocolSuccessfullyPrepared(
    ProtocolSuccessfullyPrepared event,
    Emitter<ProtocolWorkflowState> emit,
  ) {
    emit(
      state.copyWith(
        preparedBackendConfig: event.preparedConfig,
        isCurrentStepDataValid:
            true, // Review step is done, this step (Prepare) is valid
      ),
    );
    _protocolStartBloc.add(
      InitializeStartScreen(preparedConfig: event.preparedConfig),
    );
    add(const ProceedToNextStep());
  }

  void _onProtocolSuccessfullyStarted(
    ProtocolSuccessfullyStarted event,
    Emitter<ProtocolWorkflowState> emit,
  ) {
    emit(
      state.copyWith(
        protocolStartResponse: event.response,
        currentStep: WorkflowStep.workflowComplete,
        isCurrentStepDataValid: true,
        navigationReturnTarget: null, // Ensure cleared on completion
      ),
    );
  }

  void _onProceedToNextStep(
    ProceedToNextStep event,
    Emitter<ProtocolWorkflowState> emit,
  ) {
    if (!state.isCurrentStepDataValid &&
        state.currentStep != WorkflowStep.protocolSelection) {
      // If current step data is not valid (and it's not the first step where selection drives validity),
      // do not automatically proceed. UI should prevent this.
      // However, if an edit flow just completed and returned to review, review step might auto-proceed if all is well.
      return;
    }

    WorkflowStep nextStep = state.currentStep;
    bool nextStepInitialValidity = false;

    switch (state.currentStep) {
      case WorkflowStep.protocolSelection:
        if (state.selectedProtocolDetails != null) {
          nextStep = WorkflowStep.parameterConfiguration;
          // Validity will be updated by listener to _protocolParametersBloc
        } else {
          return;
        }
        break;
      case WorkflowStep.parameterConfiguration:
        if (state.selectedProtocolDetails?.assets != null &&
            state.selectedProtocolDetails!.assets!.isNotEmpty) {
          nextStep = WorkflowStep.assetAssignment;
          _protocolAssetsBloc.add(
            LoadRequiredAssets(
              assetsFromProtocolDetails: state.selectedProtocolDetails!.assets!,
              existingAssignments: state.assignedAssets, // For re-editing
            ),
          );
        } else {
          nextStep = WorkflowStep.deckConfiguration;
          _deckConfigurationBloc.add(
            InitializeDeckConfiguration(
              initialSelectedLayoutName: state.deckLayoutName,
              initialPickedFile: state.uploadedDeckFile,
            ),
          );
          if (_deckConfigurationBloc.state is DeckConfigurationInitial) {
            _deckConfigurationBloc.add(const FetchAvailableDeckLayouts());
          }
        }
        break;
      case WorkflowStep.assetAssignment:
        nextStep = WorkflowStep.deckConfiguration;
        _deckConfigurationBloc.add(
          InitializeDeckConfiguration(
            initialSelectedLayoutName: state.deckLayoutName,
            initialPickedFile: state.uploadedDeckFile,
          ),
        );
        if (_deckConfigurationBloc.state is DeckConfigurationInitial) {
          _deckConfigurationBloc.add(const FetchAvailableDeckLayouts());
        }
        break;
      case WorkflowStep.deckConfiguration:
        nextStep = WorkflowStep.reviewAndPrepare;
        _loadReviewDataAndProceed(
          emit,
        ); // This will set isCurrentStepDataValid for review
        nextStepInitialValidity =
            state
                .isCurrentStepDataValid; // Carry over validity from _loadReviewDataAndProceed
        break;
      case WorkflowStep.reviewAndPrepare:
        if (state.preparedBackendConfig != null) {
          nextStep = WorkflowStep.startProtocol;
          _protocolStartBloc.add(
            InitializeStartScreen(preparedConfig: state.preparedBackendConfig!),
          );
          nextStepInitialValidity = true;
        } else {
          return;
        }
        break;
      case WorkflowStep.startProtocol:
        return;
      case WorkflowStep.workflowComplete:
        return;
    }
    emit(
      state.copyWith(
        currentStep: nextStep,
        isCurrentStepDataValid: nextStepInitialValidity,
        isLoading: false,
        error: null,
        navigationReturnTarget:
            null, // Clear return target on normal progression
      ),
    );
  }

  void _onGoToStep(GoToStep event, Emitter<ProtocolWorkflowState> emit) {
    WorkflowStep? returnTarget = state.navigationReturnTarget;
    if (event.fromReviewScreen &&
        state.currentStep == WorkflowStep.reviewAndPrepare) {
      returnTarget = WorkflowStep.reviewAndPrepare;
    } else if (state.currentStep == event.targetStep) {
      // Already on the target step
      returnTarget =
          null; // Don't set return target if just re-evaluating current step
    }

    bool targetStepValidity = false;

    // Re-initialize child BLoCs with existing data from workflow state
    switch (event.targetStep) {
      case WorkflowStep.protocolSelection:
        targetStepValidity = state.selectedProtocolInfo != null;
        _protocolsDiscoveryBloc?.add(const FetchDiscoveredProtocols());
        emit(
          state.copyWith(
            currentStep: event.targetStep,
            isCurrentStepDataValid: targetStepValidity,
            navigationReturnTarget:
                returnTarget, // Preserve if navigating for edit
            error: null,
            // Do NOT clear subsequent data if just going back to edit,
            // only if starting a new protocol selection from scratch (handled by ResetWorkflow or ProtocolSelected)
          ),
        );
        break;
      case WorkflowStep.parameterConfiguration:
        if (state.selectedProtocolDetails != null) {
          _protocolParametersBloc.add(
            LoadProtocolParameters(
              protocolDetails: state.selectedProtocolDetails!,
              existingConfiguredParameters:
                  state.configuredParameters, // Pass existing data
            ),
          );
          // Validity will be updated by the listener
        } else {
          add(const GoToStep(targetStep: WorkflowStep.protocolSelection));
          return;
        }
        emit(
          state.copyWith(
            currentStep: event.targetStep,
            navigationReturnTarget: returnTarget,
            error: null,
          ),
        );
        break;
      case WorkflowStep.assetAssignment:
        if (state.selectedProtocolDetails?.assets != null &&
            state.selectedProtocolDetails!.assets!.isNotEmpty) {
          _protocolAssetsBloc.add(
            LoadRequiredAssets(
              assetsFromProtocolDetails: state.selectedProtocolDetails!.assets!,
              existingAssignments: state.assignedAssets,
            ),
          );
          final assetState = _protocolAssetsBloc.state;
          targetStepValidity =
              assetState is ProtocolAssetsLoaded && assetState.isValid;
        } else {
          targetStepValidity = true;
        } // No assets, step is valid
        emit(
          state.copyWith(
            currentStep: event.targetStep,
            isCurrentStepDataValid: targetStepValidity,
            navigationReturnTarget: returnTarget,
            error: null,
          ),
        );
        break;
      case WorkflowStep.deckConfiguration:
        _deckConfigurationBloc.add(
          InitializeDeckConfiguration(
            initialSelectedLayoutName: state.deckLayoutName,
            initialPickedFile: state.uploadedDeckFile,
          ),
        );
        if (_deckConfigurationBloc.state is DeckConfigurationInitial ||
            (_deckConfigurationBloc.state is DeckConfigurationLoaded &&
                (_deckConfigurationBloc.state as DeckConfigurationLoaded)
                    .availableLayouts
                    .isEmpty)) {
          _deckConfigurationBloc.add(const FetchAvailableDeckLayouts());
        }
        final deckState = _deckConfigurationBloc.state;
        targetStepValidity =
            deckState is DeckConfigurationLoaded && deckState.isSelectionValid;
        emit(
          state.copyWith(
            currentStep: event.targetStep,
            isCurrentStepDataValid: targetStepValidity,
            navigationReturnTarget: returnTarget,
            error: null,
          ),
        );
        break;
      case WorkflowStep.reviewAndPrepare:
        if (state.selectedProtocolInfo != null &&
            state.configuredParameters != null &&
            state.assignedAssets != null) {
          final reviewData = ReviewDataBundle(
            selectedProtocolInfo: state.selectedProtocolInfo!,
            configuredParameters: state.configuredParameters!,
            assignedAssets: state.assignedAssets!,
            deckLayoutName: state.deckLayoutName,
            uploadedDeckFile: state.uploadedDeckFile,
          );
          _protocolReviewBloc.add(LoadReviewData(reviewData: reviewData));
          targetStepValidity = true;
        } else {
          add(const GoToStep(targetStep: WorkflowStep.deckConfiguration));
          return;
        }
        emit(
          state.copyWith(
            currentStep: event.targetStep,
            isCurrentStepDataValid: targetStepValidity,
            navigationReturnTarget: null, // Reached review, clear return target
            error: null,
          ),
        );
        break;
      default: // e.g. startProtocol, workflowComplete - usually not navigated to with GoToStep for editing
        emit(
          state.copyWith(
            currentStep: event.targetStep,
            navigationReturnTarget: returnTarget,
            error: null,
          ),
        );
        break;
    }
  }

  void _onResetWorkflow(
    ResetWorkflow event,
    Emitter<ProtocolWorkflowState> emit,
  ) {
    emit(ProtocolWorkflowState.initial());
    _protocolsDiscoveryBloc?.add(const FetchDiscoveredProtocols());
    _protocolParametersBloc.add(
      const LoadProtocolParameters(
        protocolDetails: ProtocolDetails(
          info: ProtocolInfo(name: '', version: '', path: '', description: ''),
          parameters: {},
        ),
      ),
    );
    _deckConfigurationBloc.add(const InitializeDeckConfiguration());
    _protocolReviewBloc.add(const ResetReview());
    _protocolStartBloc.add(const ResetStart());
  }

  void _onUpdateStepValidity(
    UpdateStepValidity event,
    Emitter<ProtocolWorkflowState> emit,
  ) {
    emit(state.copyWith(isCurrentStepDataValid: event.isValid));
  }
}
