import 'dart:async';
// Will be replaced by hydrated_bloc
import 'package:hydrated_bloc/hydrated_bloc.dart'; // Added for HydratedBloc
import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:file_picker/file_picker.dart';
import 'package:praxis_lab_management/src/data/models/protocol/protocol_info.dart';
import 'package:praxis_lab_management/src/data/models/protocol/protocol_details.dart';
import 'package:praxis_lab_management/src/data/models/protocol/protocol_status_response.dart';
import 'package:praxis_lab_management/src/data/repositories/protocol_repository.dart';
import 'package:praxis_lab_management/src/data/models/protocol/protocol_asset.dart';
import 'package:praxis_lab_management/src/features/run_protocol/application/protocol_workflow_bloc/protocol_details_converter.dart';
import 'package:praxis_lab_management/src/features/run_protocol/domain/workflow_step.dart';

// Child BLoCs (assuming they are not hydrated, or managed separately)
import 'package:praxis_lab_management/src/features/run_protocol/application/protocols_discovery_bloc/protocols_discovery_bloc.dart';
import 'package:praxis_lab_management/src/features/run_protocol/application/protocol_parameters_bloc/protocol_parameters_bloc.dart';
import 'package:praxis_lab_management/src/features/run_protocol/application/protocol_assets_bloc/protocol_assets_bloc.dart';
import 'package:praxis_lab_management/src/features/run_protocol/application/deck_instance_bloc/deck_instance_bloc.dart';
import 'package:praxis_lab_management/src/features/run_protocol/application/protocol_review_bloc/protocol_review_bloc.dart';
import 'package:praxis_lab_management/src/features/run_protocol/application/protocol_start_bloc/protocol_start_bloc.dart';
import 'package:praxis_lab_management/src/features/run_protocol/domain/review_data_bundle.dart';

part 'protocol_workflow_event.dart';
part 'protocol_workflow_state.dart';
part 'protocol_workflow_bloc.freezed.dart';
part 'protocol_workflow_bloc.g.dart';

class ProtocolWorkflowBloc
    extends HydratedBloc<ProtocolWorkflowEvent, ProtocolWorkflowState> {
  // Changed to HydratedBloc
  final ProtocolRepository _protocolRepository;

  // Child BLoCs - These are not persisted as part of ProtocolWorkflowBloc's state.
  // Their state should be re-initialized or managed independently if persistence is needed for them.
  final ProtocolsDiscoveryBloc? _protocolsDiscoveryBloc;
  final ProtocolParametersBloc _protocolParametersBloc;
  final ProtocolAssetsBloc _protocolAssetsBloc;
  final DeckInstanceBloc _deckConfigurationBloc;
  final ProtocolReviewBloc _protocolReviewBloc;
  final ProtocolStartBloc _protocolStartBloc;

  StreamSubscription<ProtocolParametersState>? _parametersBlocSubscription;

  ProtocolWorkflowBloc({
    required ProtocolRepository protocolRepository,
    required ProtocolsDiscoveryBloc protocolsDiscoveryBloc,
    required ProtocolParametersBloc protocolParametersBloc,
    required ProtocolAssetsBloc protocolAssetsBloc,
    required DeckInstanceBloc deckConfigurationBloc,
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
    // Initial state setup
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

    _parametersBlocSubscription = _protocolParametersBloc.stream.listen((
      paramState,
    ) {
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

  // --- HydratedBloc Overrides ---
  @override
  ProtocolWorkflowState? fromJson(Map<String, dynamic> json) {
    try {
      return ProtocolWorkflowState.fromJson(json);
    } catch (e) {
      // Log error, or return null/initial state if deserialization fails
      print('Error deserializing ProtocolWorkflowState: $e');
      return null;
    }
  }

  @override
  Map<String, dynamic>? toJson(ProtocolWorkflowState state) {
    try {
      return state.toJson();
    } catch (e) {
      // Log error, or return null if serialization fails
      print('Error serializing ProtocolWorkflowState: $e');
      return null;
    }
  }
  // --- End HydratedBloc Overrides ---

  void _onInitializeWorkflow(
    InitializeWorkflow event,
    Emitter<ProtocolWorkflowState> emit,
  ) {
    if (state == ProtocolWorkflowState.initial()) {
      emit(
        ProtocolWorkflowState.initial(),
      ); // Ensure clean slate if truly initial
      _protocolsDiscoveryBloc?.add(const FetchDiscoveredProtocols());
    }

    // Initialize child BLoCs with the current state

    if (state.selectedProtocolDetails != null) {
      _protocolParametersBloc.add(
        LoadProtocolParameters(
          protocolDetails: state.selectedProtocolDetails!,
          existingConfiguredParameters: state.configuredParameters,
        ),
      );
      _protocolAssetsBloc.add(
        LoadRequiredAssets(
          assetsFromProtocolDetails:
              state.selectedProtocolDetails!.assets
                  .map(
                    (assetDetail) => ProtocolAsset(
                      name: assetDetail.name,
                      type: assetDetail.type,
                      description: assetDetail.description,
                      required: assetDetail.required,
                    ),
                  )
                  .toList(),
          existingAssignments: state.assignedAssets,
        ),
      );
    } else {
      // Default initialization if no protocol details are loaded (e.g. fresh start)
      _protocolParametersBloc.add(
        const LoadProtocolParameters(
          protocolDetails: ProtocolDetails(
            // Dummy details
            name: '',
            path: '',
            description: '',
            parameters: {},
            assets: [],
            hasAssets: false,
            hasParameters: false,
            requiresConfig: true,
          ),
        ),
      );
      _protocolAssetsBloc.add(
        const LoadRequiredAssets(assetsFromProtocolDetails: []),
      );
    }

    _deckConfigurationBloc.add(
      InitializeDeckInstance(
        initialSelectedLayoutName: state.deckLayoutName,
        // uploadedDeckFile is not persisted, so it will be null here on hydration
        initialPickedFile: state.uploadedDeckFile,
      ),
    );
    if (_deckConfigurationBloc.state is DeckInstanceInitial ||
        state.deckLayoutName == null) {
      _deckConfigurationBloc.add(const FetchAvailableDeckLayouts());
    }

    if (state.currentStep == WorkflowStep.reviewAndPrepare ||
        state.preparedBackendConfig != null) {
      final reviewData = ReviewDataBundle(
        selectedProtocolInfo:
            state.selectedProtocolInfo ??
            const ProtocolInfo(
              name: "Unknown",
              path: "",
              description: "",
              version: "",
            ), // Provide default if null
        configuredParameters: state.configuredParameters ?? {},
        assignedAssets: state.assignedAssets ?? {},
        deckLayoutName: state.deckLayoutName,
        uploadedDeckFile: null, // Not persisted
      );
      _protocolReviewBloc.add(LoadReviewData(reviewData: reviewData));
    } else {
      _protocolReviewBloc.add(const ResetReview());
    }

    if (state.currentStep == WorkflowStep.startProtocol ||
        state.protocolStartResponse != null) {
      if (state.preparedBackendConfig != null) {
        _protocolStartBloc.add(
          InitializeStartScreen(preparedConfig: state.preparedBackendConfig!),
        );
      }
    } else {
      _protocolStartBloc.add(const ResetStart());
    }

    // If after hydration, we are on a step that requires discovery, trigger it.
    if (state.currentStep == WorkflowStep.protocolSelection &&
        state.selectedProtocolInfo == null) {
      _protocolsDiscoveryBloc?.add(const FetchDiscoveredProtocols());
    }
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
        isCurrentStepDataValid: true,
        parametersCompletionPercent: 0.0,
        // Reset downstream data when a new protocol is selected
        selectedProtocolDetails: null,
        configuredParameters: null,
        assignedAssets: null,
        deckLayoutName: null,
        uploadedDeckFile: null,
        preparedBackendConfig: null,
        protocolStartResponse: null,
        navigationReturnTarget: null,
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
        existingConfiguredParameters:
            state.navigationReturnTarget == WorkflowStep.reviewAndPrepare &&
                    state.currentStep != WorkflowStep.protocolSelection
                ? state.configuredParameters
                : null,
      ),
    );

    if (state.navigationReturnTarget == WorkflowStep.reviewAndPrepare &&
        state.currentStep == WorkflowStep.protocolSelection) {
      // Should be currentStep == parameterConfiguration if editing params
      add(GoToStep(targetStep: WorkflowStep.reviewAndPrepare));
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
        navigationReturnTarget: null,
      ),
    );

    if (returnTarget == WorkflowStep.reviewAndPrepare) {
      add(GoToStep(targetStep: WorkflowStep.reviewAndPrepare));
    } else {
      if (state.selectedProtocolDetails?.assets.isNotEmpty ?? false) {
        _protocolAssetsBloc.add(
          LoadRequiredAssets(
            assetsFromProtocolDetails:
                state.selectedProtocolDetails!.assets
                    .map(
                      (assetDetail) => ProtocolAsset(
                        name: assetDetail.name,
                        type: assetDetail.type,
                        description: assetDetail.description,
                        required: assetDetail.required,
                      ),
                    )
                    .toList(),
            existingAssignments: state.assignedAssets,
          ),
        );
      }
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
        InitializeDeckInstance(
          initialSelectedLayoutName: state.deckLayoutName,
          initialPickedFile: null, // uploadedDeckFile is not persisted
        ),
      );
      if (_deckConfigurationBloc.state is DeckInstanceInitial) {
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
        event.uploadedFile != null; // This event carries the live file

    emit(
      state.copyWith(
        deckLayoutName: event.layoutName,
        // uploadedDeckFile is NOT set in state here if it's from event.uploadedFile,
        // because it's not persistable. If event.layoutName is set, that's what we persist.
        // If event.uploadedFile is used, its effects (like name) should be captured in deckLayoutName if applicable.
        // For HydratedBloc, we rely on serializable fields.
        // The actual PlatformFile from event.uploadedFile is transient.
        isCurrentStepDataValid: isValid,
        navigationReturnTarget: null,
      ),
    );

    if (event.uploadedFile != null) {
      // If a file was uploaded, this bloc's state.uploadedDeckFile is ignored for persistence.
      // The DeckInstanceBloc handles the actual upload.
      // We might store the *name* of the uploaded file if that's useful and comes from DeckInstanceBloc.
    }

    if (returnTarget == WorkflowStep.reviewAndPrepare) {
      add(GoToStep(targetStep: WorkflowStep.reviewAndPrepare));
    } else {
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
        uploadedDeckFile: null, // uploadedDeckFile is not persisted
      );
      _protocolReviewBloc.add(LoadReviewData(reviewData: reviewData));
      emit(state.copyWith(isCurrentStepDataValid: true));
    } else {
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
        isCurrentStepDataValid: true,
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
        navigationReturnTarget: null,
      ),
    );
  }

  void _onProceedToNextStep(
    ProceedToNextStep event,
    Emitter<ProtocolWorkflowState> emit,
  ) {
    if (!state.isCurrentStepDataValid &&
        state.currentStep != WorkflowStep.protocolSelection &&
        state.navigationReturnTarget ==
            null // Allow proceeding if returning from edit to review
            ) {
      return;
    }

    WorkflowStep nextStep = state.currentStep;
    bool nextStepInitialValidity = false;

    switch (state.currentStep) {
      case WorkflowStep.protocolSelection:
        if (state.selectedProtocolDetails != null) {
          nextStep = WorkflowStep.parameterConfiguration;
        } else {
          return;
        }
        break;
      case WorkflowStep.parameterConfiguration:
        if (state.selectedProtocolDetails?.assets.isNotEmpty ?? false) {
          nextStep = WorkflowStep.assetAssignment;
          _protocolAssetsBloc.add(
            LoadRequiredAssets(
              assetsFromProtocolDetails:
                  state.selectedProtocolDetails!.assets
                      .map(
                        (assetDetail) => ProtocolAsset(
                          name: assetDetail.name,
                          type: assetDetail.type,
                          description: assetDetail.description,
                          required: assetDetail.required,
                        ),
                      )
                      .toList(),
              existingAssignments: state.assignedAssets,
            ),
          );
        } else {
          nextStep = WorkflowStep.deckConfiguration;
          _deckConfigurationBloc.add(
            InitializeDeckInstance(
              initialSelectedLayoutName: state.deckLayoutName,
              initialPickedFile: null, // Not persisted
            ),
          );
          if (_deckConfigurationBloc.state is DeckInstanceInitial) {
            _deckConfigurationBloc.add(const FetchAvailableDeckLayouts());
          }
        }
        break;
      case WorkflowStep.assetAssignment:
        nextStep = WorkflowStep.deckConfiguration;
        _deckConfigurationBloc.add(
          InitializeDeckInstance(
            initialSelectedLayoutName: state.deckLayoutName,
            initialPickedFile: null, // Not persisted
          ),
        );
        if (_deckConfigurationBloc.state is DeckInstanceInitial) {
          _deckConfigurationBloc.add(const FetchAvailableDeckLayouts());
        }
        break;
      case WorkflowStep.deckConfiguration:
        nextStep = WorkflowStep.reviewAndPrepare;
        _loadReviewDataAndProceed(emit);
        nextStepInitialValidity = state.isCurrentStepDataValid;
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
        navigationReturnTarget: null,
      ),
    );
  }

  void _onGoToStep(GoToStep event, Emitter<ProtocolWorkflowState> emit) {
    WorkflowStep? returnTargetFromOriginalState = state.navigationReturnTarget;

    // Determine if we are navigating away from review to edit something
    WorkflowStep? newNavigationReturnTarget = returnTargetFromOriginalState;
    if (event.fromReviewScreen &&
        state.currentStep == WorkflowStep.reviewAndPrepare) {
      newNavigationReturnTarget = WorkflowStep.reviewAndPrepare;
    } else if (state.currentStep == event.targetStep) {
      // If already on the target step, don't set a new return target unless one was already set for multi-step back.
      // Generally, clicking "edit" on the current step's section in review implies returning to review.
    } else {
      // Otherwise, clear return target if we are not explicitly setting one for an edit flow.
      newNavigationReturnTarget = null;
    }

    bool targetStepValidity = false;

    switch (event.targetStep) {
      case WorkflowStep.protocolSelection:
        targetStepValidity = state.selectedProtocolInfo != null;
        _protocolsDiscoveryBloc?.add(const FetchDiscoveredProtocols());
        break;
      case WorkflowStep.parameterConfiguration:
        if (state.selectedProtocolDetails != null) {
          _protocolParametersBloc.add(
            LoadProtocolParameters(
              protocolDetails: state.selectedProtocolDetails!,
              existingConfiguredParameters: state.configuredParameters,
            ),
          );
        } else {
          // Should not happen if flow is correct
          add(const GoToStep(targetStep: WorkflowStep.protocolSelection));
          return;
        }
        break;
      case WorkflowStep.assetAssignment:
        if (state.selectedProtocolDetails?.assets.isNotEmpty ?? false) {
          _protocolAssetsBloc.add(
            LoadRequiredAssets(
              assetsFromProtocolDetails:
                  state.selectedProtocolDetails!.assets
                      .map(
                        (assetDetail) => ProtocolAsset(
                          name: assetDetail.name,
                          type: assetDetail.type,
                          description: assetDetail.description,
                          required: assetDetail.required,
                        ),
                      )
                      .toList(),
              existingAssignments: state.assignedAssets,
            ),
          );
          final assetState = _protocolAssetsBloc.state;
          targetStepValidity =
              assetState is ProtocolAssetsLoaded && assetState.isValid;
        } else {
          targetStepValidity = true;
        }
        break;
      case WorkflowStep.deckConfiguration:
        _deckConfigurationBloc.add(
          InitializeDeckInstance(
            initialSelectedLayoutName: state.deckLayoutName,
            initialPickedFile: null, // Not persisted
          ),
        );
        if (_deckConfigurationBloc.state is DeckInstanceInitial ||
            (_deckConfigurationBloc.state is DeckInstanceLoaded &&
                (_deckConfigurationBloc.state as DeckInstanceLoaded)
                    .availableLayouts
                    .isEmpty)) {
          _deckConfigurationBloc.add(const FetchAvailableDeckLayouts());
        }
        final deckState = _deckConfigurationBloc.state;
        targetStepValidity =
            deckState is DeckInstanceLoaded && deckState.isSelectionValid;
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
            uploadedDeckFile: null, // Not persisted
          );
          _protocolReviewBloc.add(LoadReviewData(reviewData: reviewData));
          targetStepValidity = true;
          newNavigationReturnTarget =
              null; // Reached review, clear return target
        } else {
          add(
            const GoToStep(targetStep: WorkflowStep.deckConfiguration),
          ); // Go to prev valid step
          return;
        }
        break;
      default:
        break;
    }

    emit(
      state.copyWith(
        currentStep: event.targetStep,
        isCurrentStepDataValid:
            targetStepValidity, // May be updated by child bloc listeners
        navigationReturnTarget: newNavigationReturnTarget,
        error: null,
      ),
    );
  }

  void _onResetWorkflow(
    ResetWorkflow event,
    Emitter<ProtocolWorkflowState> emit,
  ) {
    // This should truly reset the persisted state as well.
    // HydratedBloc will call toJson with the new initial state.
    emit(ProtocolWorkflowState.initial());

    // Re-initialize child BLoCs to their initial states.
    _protocolsDiscoveryBloc?.add(const FetchDiscoveredProtocols());
    _protocolParametersBloc.add(
      LoadProtocolParameters(
        protocolDetails: ProtocolDetails(
          // Dummy details
          name: '',
          path: '',
          description: '',
          parameters: {},
          assets: [],
          hasAssets: false,
          hasParameters: false,
          requiresConfig: true,
        ),
      ),
    );
    _protocolAssetsBloc.add(
      const LoadRequiredAssets(assetsFromProtocolDetails: []),
    );
    _deckConfigurationBloc.add(const InitializeDeckInstance());
    _deckConfigurationBloc.add(
      const FetchAvailableDeckLayouts(),
    ); // Also fetch layouts
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
