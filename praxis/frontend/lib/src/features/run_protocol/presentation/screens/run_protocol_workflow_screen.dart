import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';
import 'package:praxis_lab_management/src/data/models/protocol/protocol_info.dart';
import 'package:praxis_lab_management/src/features/run_protocol/application/protocol_workflow_bloc/protocol_workflow_bloc.dart';
import 'package:praxis_lab_management/src/features/run_protocol/domain/workflow_step.dart'
    as ws; // aliased
// Import your route name constants
import 'package:praxis_lab_management/src/core/routing/app_go_router.dart';

class RunProtocolWorkflowScreen extends StatefulWidget {
  final ProtocolInfo? protocolInfo; // Received from router's 'extra'
  final Widget
  child; // The current step's screen, provided by GoRouter ShellRoute

  const RunProtocolWorkflowScreen({
    super.key,
    required this.child,
    this.protocolInfo,
  });

  @override
  State<RunProtocolWorkflowScreen> createState() =>
      _RunProtocolWorkflowScreenState();
}

class _RunProtocolWorkflowScreenState extends State<RunProtocolWorkflowScreen> {
  @override
  void initState() {
    super.initState();
    final bloc = context.read<ProtocolWorkflowBloc>();

    if (widget.protocolInfo != null &&
        (bloc.state.selectedProtocolInfo?.path != widget.protocolInfo!.path ||
            bloc.state.currentStep == ws.WorkflowStep.protocolSelection)) {
      bloc.add(
        ProtocolSelectedInWorkflow(selectedProtocol: widget.protocolInfo!),
      );
    } else if (bloc.state.currentStep == ws.WorkflowStep.protocolSelection &&
        widget.protocolInfo == null) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text("No protocol selected. Redirecting..."),
              backgroundColor: Colors.orange,
            ),
          );
          context.goNamed(protocolsRouteName);
        }
      });
    }
  }

  String _routeNameForStep(ws.WorkflowStep step) {
    switch (step) {
      case ws.WorkflowStep.protocolSelection:
        return parameterConfigurationRouteName;
      case ws.WorkflowStep.parameterConfiguration:
        return parameterConfigurationRouteName;
      case ws.WorkflowStep.assetAssignment:
        return assetAssignmentRouteName;
      case ws.WorkflowStep.deckConfiguration:
        return deckConfigurationRouteName;
      case ws.WorkflowStep.reviewAndPrepare:
        return reviewAndPrepareRouteName;
      case ws.WorkflowStep.startProtocol:
        return startProtocolRouteName;
      default:
        return parameterConfigurationRouteName;
    }
  }

  int _currentStepIndex(ws.WorkflowStep currentStep) {
    if (currentStep == ws.WorkflowStep.protocolSelection) return 0;
    if (currentStep == ws.WorkflowStep.parameterConfiguration) return 0;
    if (currentStep == ws.WorkflowStep.assetAssignment) return 1;
    if (currentStep == ws.WorkflowStep.deckConfiguration) return 2;
    if (currentStep == ws.WorkflowStep.reviewAndPrepare) return 3;
    if (currentStep == ws.WorkflowStep.startProtocol) return 4;
    return 0;
  }

  ws.WorkflowStep _stepForIndex(int index) {
    switch (index) {
      case 0:
        return ws.WorkflowStep.parameterConfiguration;
      case 1:
        return ws.WorkflowStep.assetAssignment;
      case 2:
        return ws.WorkflowStep.deckConfiguration;
      case 3:
        return ws.WorkflowStep.reviewAndPrepare;
      case 4:
        return ws.WorkflowStep.startProtocol;
      default:
        return ws.WorkflowStep.parameterConfiguration; // Fallback
    }
  }

  List<Step> _buildSteps(
    BuildContext context,
    ProtocolWorkflowState workflowState,
  ) {
    return [
      Step(
        title: const Text('Parameters'),
        content: Container(),
        isActive:
            workflowState.currentStep.index >=
            ws.WorkflowStep.parameterConfiguration.index,
        state:
            workflowState.currentStep.index >
                    ws.WorkflowStep.parameterConfiguration.index
                ? StepState.complete
                : StepState.indexed,
      ),
      Step(
        title: const Text('Assets'),
        content: Container(),
        isActive:
            workflowState.currentStep.index >=
            ws.WorkflowStep.assetAssignment.index,
        state:
            workflowState.currentStep.index >
                    ws.WorkflowStep.assetAssignment.index
                ? StepState.complete
                : StepState.indexed,
      ),
      Step(
        title: const Text('Deck'),
        content: Container(),
        isActive:
            workflowState.currentStep.index >=
            ws.WorkflowStep.deckConfiguration.index,
        state:
            workflowState.currentStep.index >
                    ws.WorkflowStep.deckConfiguration.index
                ? StepState.complete
                : StepState.indexed,
      ),
      Step(
        title: const Text('Review & Prepare'),
        content: Container(),
        isActive:
            workflowState.currentStep.index >=
            ws.WorkflowStep.reviewAndPrepare.index,
        state:
            workflowState.currentStep.index >
                    ws.WorkflowStep.reviewAndPrepare.index
                ? StepState.complete
                : StepState.indexed,
      ),
      Step(
        title: const Text('Start Protocol'),
        content: Container(),
        isActive:
            workflowState.currentStep.index >=
            ws.WorkflowStep.startProtocol.index,
        state:
            workflowState.currentStep.index >
                    ws.WorkflowStep.startProtocol.index
                ? StepState.complete
                : StepState.indexed,
      ),
    ];
  }

  @override
  Widget build(BuildContext context) {
    return BlocConsumer<ProtocolWorkflowBloc, ProtocolWorkflowState>(
      listener: (context, state) {
        final expectedRouteName = _routeNameForStep(state.currentStep);
        final currentRoute = GoRouterState.of(context);
        final currentRouteName = currentRoute.name;

        if (state.currentStep != ws.WorkflowStep.protocolSelection &&
            state.currentStep != ws.WorkflowStep.workflowComplete &&
            currentRouteName != expectedRouteName) {
          print(
            "BlocListener navigating from $currentRouteName to $expectedRouteName due to BLoC state change.",
          );
          context.goNamed(
            expectedRouteName,
            extra: state.selectedProtocolInfo ?? widget.protocolInfo,
          );
        }

        if (state.currentStep == ws.WorkflowStep.workflowComplete) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text("Protocol workflow completed!"),
              backgroundColor: Colors.green,
            ),
          );
          context.goNamed(protocolsRouteName);
        }
        // Error messages are shown via SnackBar. The error in BLoC state will be cleared
        // on the next successful state transition that emits `error: null`.
        if (state.error != null && state.error!.isNotEmpty) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text(state.error!), backgroundColor: Colors.red),
          );
          // context.read<ProtocolWorkflowBloc>().add(const ClearWorkflowErrorEvent()); // Removed as event doesn't exist
        }
      },
      builder: (context, workflowState) {
        final currentStepDomain = workflowState.currentStep;
        final stepperIndex = _currentStepIndex(currentStepDomain);

        return Scaffold(
          appBar: AppBar(
            title: Text(
              workflowState.selectedProtocolInfo?.name ??
                  widget.protocolInfo?.name ??
                  'Run Protocol',
            ),
            leading: IconButton(
              icon: const Icon(Icons.close),
              onPressed: () {
                context.read<ProtocolWorkflowBloc>().add(const ResetWorkflow());
                context.goNamed(protocolsRouteName);
              },
            ),
          ),
          body: Column(
            children: [
              if (currentStepDomain != ws.WorkflowStep.workflowComplete)
                Stepper(
                  currentStep: stepperIndex,
                  type: StepperType.horizontal,
                  onStepTapped: (stepIndex) {
                    ws.WorkflowStep tappedStepDomain = _stepForIndex(stepIndex);
                    context.read<ProtocolWorkflowBloc>().add(
                      GoToStep(targetStep: tappedStepDomain),
                    );
                  },
                  steps: _buildSteps(context, workflowState),
                  controlsBuilder: (
                    BuildContext context,
                    ControlsDetails details,
                  ) {
                    bool isLastStep =
                        details.currentStep ==
                        _buildSteps(context, workflowState).length - 1;
                    bool canProceed = workflowState.isCurrentStepDataValid;
                    if (workflowState.currentStep ==
                            ws.WorkflowStep.protocolSelection &&
                        workflowState.selectedProtocolInfo == null) {
                      canProceed = false;
                    }

                    return Padding(
                      padding: const EdgeInsets.only(
                        top: 16.0,
                        right: 16.0,
                        left: 16.0,
                      ),
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: <Widget>[
                          if (details.currentStep > 0)
                            OutlinedButton(
                              onPressed: details.onStepCancel,
                              child: const Text('BACK'),
                            )
                          else
                            Container(),

                          ElevatedButton(
                            onPressed:
                                canProceed ? details.onStepContinue : null,
                            child: Text(isLastStep ? 'START PROTOCOL' : 'NEXT'),
                          ),
                        ],
                      ),
                    );
                  },
                  onStepContinue: () {
                    if (workflowState.isCurrentStepDataValid) {
                      context.read<ProtocolWorkflowBloc>().add(
                        const ProceedToNextStep(),
                      );
                    } else {
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(
                          content: Text(
                            "Please complete the current step correctly.",
                          ),
                          backgroundColor: Colors.orange,
                        ),
                      );
                    }
                  },
                  onStepCancel: () {
                    // This is for the Stepper's "Cancel" button in default controls, or our "BACK" button
                    if (stepperIndex > 0) {
                      ws.WorkflowStep previousStepDomain = _stepForIndex(
                        stepperIndex - 1,
                      );
                      context.read<ProtocolWorkflowBloc>().add(
                        GoToStep(targetStep: previousStepDomain),
                      );
                    } else {
                      // Optionally, handle exiting the workflow if at the very first step
                      context.read<ProtocolWorkflowBloc>().add(
                        const ResetWorkflow(),
                      );
                      context.goNamed(protocolsRouteName);
                    }
                  },
                ),
              Expanded(
                child: Padding(
                  padding: const EdgeInsets.all(8.0),
                  child: widget.child,
                ),
              ),
            ],
          ),
        );
      },
    );
  }
}
