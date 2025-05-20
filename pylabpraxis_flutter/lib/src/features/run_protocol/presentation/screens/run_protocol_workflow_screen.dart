import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:pylabpraxis_flutter/src/data/repositories/protocol_repository.dart';
import 'package:pylabpraxis_flutter/src/features/run_protocol/application/deck_configuration_bloc/deck_configuration_bloc.dart';
import 'package:pylabpraxis_flutter/src/features/run_protocol/application/protocol_assets_bloc/protocol_assets_bloc.dart';
import 'package:pylabpraxis_flutter/src/features/run_protocol/application/protocol_parameters_bloc/protocol_parameters_bloc.dart';
import 'package:pylabpraxis_flutter/src/features/run_protocol/application/protocol_review_bloc/protocol_review_bloc.dart';
import 'package:pylabpraxis_flutter/src/features/run_protocol/application/protocol_start_bloc/protocol_start_bloc.dart';
import 'package:pylabpraxis_flutter/src/features/run_protocol/application/protocol_workflow_bloc/protocol_workflow_bloc.dart';
import 'package:pylabpraxis_flutter/src/features/run_protocol/application/protocols_discovery_bloc/protocols_discovery_bloc.dart';
import 'package:pylabpraxis_flutter/src/features/run_protocol/domain/workflow_step.dart';

// Import screen widgets
import 'package:pylabpraxis_flutter/src/features/run_protocol/presentation/screens/protocol_selection_screen.dart';
import 'package:pylabpraxis_flutter/src/features/run_protocol/presentation/screens/parameter_configuration_screen.dart';
import 'package:pylabpraxis_flutter/src/features/run_protocol/presentation/screens/asset_assignment_screen.dart';
import 'package:pylabpraxis_flutter/src/features/run_protocol/presentation/screens/deck_configuration_screen.dart';
import 'package:pylabpraxis_flutter/src/features/run_protocol/presentation/screens/review_and_prepare_screen.dart';
import 'package:pylabpraxis_flutter/src/features/run_protocol/presentation/screens/start_protocol_screen.dart';

class RunProtocolWorkflowScreen extends StatelessWidget {
  const RunProtocolWorkflowScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final protocolRepository = RepositoryProvider.of<ProtocolRepository>(
      context,
    );

    // Create instances of child BLoCs first to pass to ProtocolWorkflowBloc
    final protocolsDiscoveryBloc = ProtocolsDiscoveryBloc(
      protocolRepository: protocolRepository,
    );
    final protocolParametersBloc =
        ProtocolParametersBloc(); // Has its own stream listened to by WorkflowBloc
    final protocolAssetsBloc = ProtocolAssetsBloc();
    final deckConfigurationBloc = DeckConfigurationBloc(
      protocolRepository: protocolRepository,
    );
    final protocolReviewBloc = ProtocolReviewBloc(
      protocolRepository: protocolRepository,
    );
    final protocolStartBloc = ProtocolStartBloc(
      protocolRepository: protocolRepository,
    );

    return MultiBlocProvider(
      providers: [
        // Provide child BLoCs for their respective screens
        BlocProvider.value(value: protocolsDiscoveryBloc),
        BlocProvider.value(value: protocolParametersBloc),
        BlocProvider.value(value: protocolAssetsBloc),
        BlocProvider.value(value: deckConfigurationBloc),
        BlocProvider.value(value: protocolReviewBloc),
        BlocProvider.value(value: protocolStartBloc),

        BlocProvider<ProtocolWorkflowBloc>(
          create:
              (context) => ProtocolWorkflowBloc(
                protocolRepository: protocolRepository,
                protocolsDiscoveryBloc: protocolsDiscoveryBloc,
                protocolParametersBloc:
                    protocolParametersBloc, // Instance passed here
                protocolAssetsBloc: protocolAssetsBloc,
                deckConfigurationBloc: deckConfigurationBloc,
                protocolReviewBloc: protocolReviewBloc,
                protocolStartBloc: protocolStartBloc,
              )..add(const InitializeWorkflow()),
        ),
      ],
      child: const _WorkflowView(),
    );
  }
}

class _WorkflowViewState extends State<_WorkflowView> {
  int _workflowStepToIndex(WorkflowStep step) {
    // Ensure workflowComplete isn't counted in displayable step indices if it's handled separately
    if (step == WorkflowStep.workflowComplete) {
      return WorkflowStep.values.length - 1; // Or a specific large number
    }
    return WorkflowStep.values.indexOf(step);
  }

  String _getStepTitle(WorkflowStep step) {
    switch (step) {
      case WorkflowStep.protocolSelection:
        return 'Select Protocol';
      case WorkflowStep.parameterConfiguration:
        return 'Parameters'; // Shorter for progress bar
      case WorkflowStep.assetAssignment:
        return 'Assets'; // Shorter
      case WorkflowStep.deckConfiguration:
        return 'Deck Layout';
      case WorkflowStep.reviewAndPrepare:
        return 'Review'; // Shorter
      case WorkflowStep.startProtocol:
        return 'Start'; // Shorter
      case WorkflowStep.workflowComplete:
        return 'Completed';
      default:
        return 'Unknown';
    }
  }

  Widget _getCurrentStepWidget(WorkflowStep step) {
    switch (step) {
      case WorkflowStep.protocolSelection:
        return const ProtocolSelectionScreen();
      case WorkflowStep.parameterConfiguration:
        return const ParameterConfigurationScreen();
      case WorkflowStep.assetAssignment:
        return const AssetAssignmentScreen();
      case WorkflowStep.deckConfiguration:
        return const DeckConfigurationScreen();
      case WorkflowStep.reviewAndPrepare:
        return const ReviewAndPrepareScreen();
      case WorkflowStep.startProtocol:
        return const StartProtocolScreen();
      default:
        return Center(child: Text('Content for ${step.name}'));
    }
  }

  Widget _buildProgressIndicator(
    BuildContext context,
    ProtocolWorkflowState workflowState,
  ) {
    final currentActualStep = workflowState.currentStep;
    // Filter out workflowComplete for displayable steps in the indicator
    final displayableSteps =
        WorkflowStep.values
            .where((s) => s != WorkflowStep.workflowComplete)
            .toList();
    final totalDisplayableSteps = displayableSteps.length;
    // Find index of currentActualStep within the displayableSteps list
    final currentDisplayableStepIndex = displayableSteps.indexOf(
      currentActualStep,
    );

    final theme = Theme.of(context);

    return Container(
      padding: const EdgeInsets.symmetric(vertical: 16.0, horizontal: 8.0),
      decoration: BoxDecoration(
        color: theme.colorScheme.surfaceContainerLowest,
        border: Border(
          bottom: BorderSide(color: theme.dividerColor.withOpacity(0.5)),
        ),
        boxShadow: [
          BoxShadow(
            color: theme.shadowColor.withOpacity(0.05),
            blurRadius: 3,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceAround,
        children: List.generate(totalDisplayableSteps, (index) {
          final stepEnum =
              displayableSteps[index]; // Use step from displayableSteps
          final isActive = index == currentDisplayableStepIndex;
          final isCompleted = index < currentDisplayableStepIndex;

          Color indicatorColor = theme.colorScheme.outline;
          Color textColor = theme.colorScheme.onSurfaceVariant;
          FontWeight fontWeight = FontWeight.normal;
          double stepProgress = 0.0;

          if (isActive) {
            indicatorColor = theme.colorScheme.primary;
            textColor = theme.colorScheme.primary;
            fontWeight = FontWeight.bold;
            if (stepEnum == WorkflowStep.parameterConfiguration) {
              stepProgress = workflowState.parametersCompletionPercent;
            } else if (workflowState.isCurrentStepDataValid) {
              // For other active steps, if data is valid, show as nearly complete
              stepProgress = 0.9; // Indicate it's active and ready to proceed
            } else {
              stepProgress = 0.1; // Active but not yet valid
            }
          } else if (isCompleted) {
            indicatorColor = theme.colorScheme.primary;
            textColor = theme.colorScheme.onSurface;
            stepProgress = 1.0;
          } else {
            // Upcoming step
            indicatorColor = theme.colorScheme.outline.withOpacity(0.7);
            textColor = theme.colorScheme.onSurfaceVariant.withOpacity(0.7);
            stepProgress = 0.0;
          }

          return Expanded(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Stack(
                  alignment: Alignment.center,
                  children: [
                    SizedBox(
                      width: 32,
                      height: 32, // Slightly larger progress circle
                      child: CircularProgressIndicator(
                        value: stepProgress,
                        strokeWidth: 3.0, // Slightly thicker
                        backgroundColor: indicatorColor.withOpacity(0.15),
                        valueColor: AlwaysStoppedAnimation<Color>(
                          indicatorColor,
                        ),
                      ),
                    ),
                    Icon(
                      isCompleted
                          ? Icons.check_circle_rounded
                          : (isActive
                              ? Icons.edit_note_rounded
                              : Icons.circle_outlined),
                      size: 20.0,
                      color:
                          (isActive && stepProgress < 0.9 && stepProgress > 0.0)
                              ? indicatorColor.withOpacity(0.7)
                              : indicatorColor, // Dim icon if progress is partial but active
                    ),
                  ],
                ),
                const SizedBox(height: 6.0),
                Text(
                  _getStepTitle(stepEnum),
                  textAlign: TextAlign.center,
                  style: theme.textTheme.labelSmall?.copyWith(
                    color: textColor,
                    fontWeight: fontWeight,
                    letterSpacing: 0.2,
                  ),
                  maxLines: 1, // Prefer single line for progress bar titles
                  overflow: TextOverflow.ellipsis,
                ),
              ],
            ),
          );
        }),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return BlocBuilder<ProtocolWorkflowBloc, ProtocolWorkflowState>(
      builder: (context, workflowState) {
        final workflowBloc = context.read<ProtocolWorkflowBloc>();
        // Use currentDisplayableStepIndex for UI logic regarding steps array
        final displayableSteps =
            WorkflowStep.values
                .where((s) => s != WorkflowStep.workflowComplete)
                .toList();
        final currentDisplayableStepIndex = displayableSteps.indexOf(
          workflowState.currentStep,
        );

        final theme = Theme.of(context);

        if (workflowState.currentStep == WorkflowStep.workflowComplete) {
          return Scaffold(
            appBar: AppBar(
              title: const Text('Workflow Complete'),
              automaticallyImplyLeading: false,
            ),
            body: Center(
              child: Padding(
                padding: const EdgeInsets.all(24.0),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(
                      Icons.check_circle_outline_rounded,
                      color: Theme.of(context).colorScheme.primary,
                      size: 80,
                    ),
                    const SizedBox(height: 24),
                    Text(
                      'Protocol Workflow Finished!',
                      style: Theme.of(
                        context,
                      ).textTheme.headlineMedium?.copyWith(
                        color: Theme.of(context).colorScheme.primary,
                      ),
                      textAlign: TextAlign.center,
                    ),
                    if (workflowState.protocolStartResponse != null)
                      Padding(
                        padding: const EdgeInsets.only(top: 16.0),
                        child: Text(
                          'Run ID: ${workflowState.protocolStartResponse!.runId}',
                          style: Theme.of(context).textTheme.titleMedium,
                        ),
                      ),
                    const SizedBox(height: 40),
                    ElevatedButton.icon(
                      icon: const Icon(Icons.refresh_rounded),
                      label: const Text('Run Another Protocol'),
                      style: ElevatedButton.styleFrom(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 24,
                          vertical: 12,
                        ),
                        textStyle: Theme.of(context).textTheme.labelLarge,
                      ),
                      onPressed: () {
                        workflowBloc.add(const ResetWorkflow());
                      },
                    ),
                    const SizedBox(height: 16),
                    TextButton(
                      onPressed: () {
                        Navigator.of(
                          context,
                        ).popUntil((route) => route.isFirst);
                      },
                      child: const Text('Go to Dashboard'),
                    ),
                  ],
                ),
              ),
            ),
          );
        }

        return Scaffold(
          appBar: AppBar(
            title: Text(_getStepTitle(workflowState.currentStep)),
            leading:
                currentDisplayableStepIndex > 0
                    ? IconButton(
                      icon: const Icon(Icons.arrow_back_ios_new_rounded),
                      onPressed: () {
                        if (currentDisplayableStepIndex > 0) {
                          WorkflowStep targetStep =
                              displayableSteps[currentDisplayableStepIndex - 1];
                          // Skip asset assignment if it was skipped going forward
                          if (targetStep == WorkflowStep.assetAssignment &&
                              (workflowState.selectedProtocolDetails?.assets ==
                                      null ||
                                  workflowState
                                      .selectedProtocolDetails!
                                      .assets!
                                      .isEmpty) &&
                              currentDisplayableStepIndex - 2 >= 0) {
                            targetStep =
                                displayableSteps[currentDisplayableStepIndex -
                                    2];
                          }
                          workflowBloc.add(
                            GoToStep(
                              targetStep: targetStep,
                              fromReviewScreen:
                                  workflowState.navigationReturnTarget ==
                                  WorkflowStep.reviewAndPrepare,
                            ),
                          );
                        }
                      },
                    )
                    : null,
            actions: [
              if (workflowState.currentStep != WorkflowStep.workflowComplete)
                TextButton(
                  onPressed: () {
                    showDialog(
                      context: context,
                      builder: (BuildContext dialogContext) {
                        return AlertDialog(
                          title: const Text('Cancel Workflow?'),
                          content: const Text(
                            'Are you sure you want to cancel and exit this workflow? All progress will be lost.',
                          ),
                          actions: <Widget>[
                            TextButton(
                              child: const Text('No'),
                              onPressed: () {
                                Navigator.of(dialogContext).pop();
                              },
                            ),
                            TextButton(
                              child: Text(
                                'Yes, Cancel',
                                style: TextStyle(
                                  color: Theme.of(context).colorScheme.error,
                                ),
                              ),
                              onPressed: () {
                                Navigator.of(dialogContext).pop();
                                workflowBloc.add(const ResetWorkflow());
                                Navigator.of(context).pop();
                              },
                            ),
                          ],
                        );
                      },
                    );
                  },
                  child: Text(
                    'CANCEL',
                    style: TextStyle(
                      color: Theme.of(context).colorScheme.error,
                    ),
                  ),
                ),
            ],
          ),
          body: Column(
            children: [
              _buildProgressIndicator(context, workflowState),
              if (workflowState.isLoading &&
                  workflowState.currentStep != WorkflowStep.protocolSelection)
                const LinearProgressIndicator(minHeight: 2),
              if (workflowState.error != null)
                Container(
                  width: double.infinity, // Ensure it takes full width
                  padding: const EdgeInsets.symmetric(
                    horizontal: 16.0,
                    vertical: 10.0,
                  ),
                  color: Theme.of(context).colorScheme.errorContainer,
                  child: Row(
                    children: [
                      Icon(
                        Icons.error_outline_rounded,
                        color: Theme.of(context).colorScheme.onErrorContainer,
                      ),
                      const SizedBox(width: 10),
                      Expanded(
                        child: Text(
                          workflowState.error!,
                          style: TextStyle(
                            color:
                                Theme.of(context).colorScheme.onErrorContainer,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              Expanded(
                child: AnimatedSwitcher(
                  duration: const Duration(milliseconds: 250),
                  transitionBuilder: (
                    Widget child,
                    Animation<double> animation,
                  ) {
                    return FadeTransition(
                      opacity: animation,
                      child: SlideTransition(
                        // Add slide transition
                        position: Tween<Offset>(
                          begin: const Offset(0.05, 0.0), // Slide from right
                          end: Offset.zero,
                        ).animate(animation),
                        child: child,
                      ),
                    );
                  },
                  child: Container(
                    key: ValueKey<WorkflowStep>(workflowState.currentStep),
                    child: _getCurrentStepWidget(workflowState.currentStep),
                  ),
                ),
              ),
            ],
          ),
          bottomNavigationBar:
              workflowState.currentStep != WorkflowStep.workflowComplete
                  ? _buildBottomNavigationBar(context, workflowState)
                  : null,
        );
      },
    );
  }

  Widget _buildBottomNavigationBar(
    BuildContext context,
    ProtocolWorkflowState workflowState,
  ) {
    final workflowBloc = context.read<ProtocolWorkflowBloc>();
    final displayableSteps =
        WorkflowStep.values
            .where((s) => s != WorkflowStep.workflowComplete)
            .toList();
    final currentDisplayableStepIndex = displayableSteps.indexOf(
      workflowState.currentStep,
    );
    final theme = Theme.of(context);

    String nextButtonText = 'NEXT';
    IconData nextButtonIcon = Icons.arrow_forward_ios_rounded;

    if (workflowState.currentStep == WorkflowStep.reviewAndPrepare) {
      nextButtonText = 'PREPARE';
      nextButtonIcon = Icons.settings_applications_rounded;
    } else if (workflowState.currentStep == WorkflowStep.startProtocol) {
      nextButtonText = 'START EXECUTION';
      nextButtonIcon = Icons.play_arrow_rounded;
    } else if (currentDisplayableStepIndex == displayableSteps.length - 1 &&
        workflowState.currentStep != WorkflowStep.startProtocol) {
      nextButtonText =
          'REVIEW'; // Assuming last step before review is review itself or leads to it
    }

    return BottomAppBar(
      padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 8.0),
      elevation: 4,
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: <Widget>[
          if (currentDisplayableStepIndex > 0)
            OutlinedButton.icon(
              icon: const Icon(Icons.arrow_back_ios_new_rounded, size: 18),
              label: const Text('BACK'),
              style: OutlinedButton.styleFrom(
                padding: const EdgeInsets.symmetric(
                  horizontal: 20,
                  vertical: 10,
                ),
                textStyle: theme.textTheme.labelLarge,
                side: BorderSide(color: theme.colorScheme.outline),
              ),
              onPressed:
                  workflowState.isLoading
                      ? null
                      : () {
                        WorkflowStep targetStep =
                            displayableSteps[currentDisplayableStepIndex - 1];
                        if (targetStep == WorkflowStep.assetAssignment &&
                            (workflowState.selectedProtocolDetails?.assets ==
                                    null ||
                                workflowState
                                    .selectedProtocolDetails!
                                    .assets!
                                    .isEmpty) &&
                            currentDisplayableStepIndex - 2 >= 0) {
                          targetStep =
                              displayableSteps[currentDisplayableStepIndex - 2];
                        }
                        workflowBloc.add(
                          GoToStep(
                            targetStep: targetStep,
                            fromReviewScreen:
                                workflowState.navigationReturnTarget ==
                                WorkflowStep.reviewAndPrepare,
                          ),
                        );
                      },
            )
          else
            const SizedBox(width: 0),

          const Spacer(),

          ElevatedButton.icon(
            icon:
                workflowState.isLoading &&
                        workflowState.currentStep !=
                            WorkflowStep
                                .reviewAndPrepare // Don't show spinner for prepare, review bloc handles its own
                    ? Container(
                      width: 20,
                      height: 20,
                      padding: const EdgeInsets.all(2.0),
                      child: CircularProgressIndicator(
                        strokeWidth: 2.5,
                        color: theme.colorScheme.onPrimary,
                      ),
                    )
                    : Icon(nextButtonIcon, size: 20),
            label: Text(nextButtonText),
            onPressed:
                (workflowState.isCurrentStepDataValid &&
                        !workflowState.isLoading)
                    ? () {
                      workflowBloc.add(const ProceedToNextStep());
                    }
                    : null,
            style: ElevatedButton.styleFrom(
              padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
              textStyle: theme.textTheme.labelLarge?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
        ],
      ),
    );
  }
}

// Add to ProtocolWorkflowEvent in protocol_workflow_event.dart
// const factory ProtocolWorkflowEvent.updateParametersProgress({
//   required double completionPercent,
// }) = UpdateParametersProgress;

// Add to GoToStep event in protocol_workflow_event.dart
// final bool fromReviewScreen; (add as @Default(false) bool fromReviewScreen)

// Add to ProtocolWorkflowState in protocol_workflow_state.dart
// final WorkflowStep? navigationReturnTarget;
