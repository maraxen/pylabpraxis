// pylabpraxis_flutter/lib/src/features/run_protocol/presentation/screens/start_protocol_screen.dart
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:pylabpraxis_flutter/src/features/run_protocol/application/protocol_start_bloc/protocol_start_bloc.dart';
import 'package:pylabpraxis_flutter/src/features/run_protocol/application/protocol_workflow_bloc/protocol_workflow_bloc.dart';
// Assuming ProtocolStartState structure like:
// @freezed
// sealed class ProtocolStartState with _$ProtocolStartState {
//   const factory ProtocolStartState.initial() = _Initial;
//   const factory ProtocolStartState.readyToStart({required Map<String, dynamic> backendConfig, String? protocolName}) = _ReadyToStart;
//   const factory ProtocolStartState.starting() = _Starting;
//   const factory ProtocolStartState.runInitiated({String? runId, String? message}) = _RunInitiated; // Successfully started
//   const factory ProtocolStartState.runFailed(String error) = _RunFailed; // Failed to start
// }

class StartProtocolScreen extends StatefulWidget {
  const StartProtocolScreen({super.key});

  @override
  State<StartProtocolScreen> createState() => _StartProtocolScreenState();
}

class _StartProtocolScreenState extends State<StartProtocolScreen> {
  @override
  void initState() {
    super.initState();
    final workflowState = context.read<ProtocolWorkflowBloc>().state;
    if (workflowState.preparedBackendConfig != null) {
      context.read<ProtocolStartBloc>().add(
        ProtocolStartEvent.loadConfiguration(
          backendConfig: workflowState.preparedBackendConfig!,
          protocolName:
              workflowState.selectedProtocolInfo?.name ?? 'Unknown Protocol',
        ),
      );
    } else {
      // This case should ideally not happen if workflow is correct.
      // Consider navigating back or showing an error.
      context.read<ProtocolStartBloc>().add(
        const ProtocolStartEvent.reportError(
          message: "Missing prepared backend configuration.",
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Scaffold(
      appBar: AppBar(
        title: const Text('Start Protocol Run'),
        leading: IconButton(
          // Allow going back to review if not yet started
          icon: const Icon(Icons.arrow_back),
          onPressed: () {
            final currentStartState = context.read<ProtocolStartBloc>().state;
            // Only allow going back if not in a 'starting' or 'runInitiated' state
            if (currentStartState is! ProtocolStarting &&
                currentStartState is! ProtocolRunInitiated) {
              context.read<ProtocolWorkflowBloc>().add(
                const ProtocolWorkflowEvent.goToPreviousStep(),
              );
            } else {
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(
                  content: Text(
                    'Cannot go back while protocol is starting or initiated.',
                  ),
                ),
              );
            }
          },
        ),
      ),
      body: BlocConsumer<ProtocolStartBloc, ProtocolStartState>(
        listener: (context, state) {
          if (state is ProtocolRunFailed) {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                content: Text('Failed to start protocol: ${state.error}'),
                backgroundColor: theme.colorScheme.error,
              ),
            );
          } else if (state is ProtocolRunInitiated) {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                content: Text(
                  state.message ??
                      'Protocol run successfully initiated! Run ID: ${state.runId}',
                ),
                backgroundColor: Colors.green.shade700,
              ),
            );
            // Optionally, navigate away from the workflow or to a run monitoring screen
            // context.read<ProtocolWorkflowBloc>().add(const ProtocolWorkflowEvent.resetWorkflow());
            // GoRouter.of(context).go('/home'); // Example navigation
          }
        },
        builder: (context, state) {
          return switch (state) {
            ProtocolStartInitial() => const Center(
              child: CircularProgressIndicator(),
            ),
            ProtocolStartReadyToStart(
              backendConfig: final _,
              protocolName: final protocolName,
            ) =>
              Center(
                child: Padding(
                  padding: const EdgeInsets.all(24.0),
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(
                        Icons.play_circle_outline_rounded,
                        size: 64,
                        color: theme.colorScheme.primary,
                      ),
                      const SizedBox(height: 24),
                      Text(
                        'Ready to Start',
                        style: theme.textTheme.headlineMedium,
                      ),
                      const SizedBox(height: 8),
                      Text(
                        protocolName ?? 'Selected Protocol',
                        style: theme.textTheme.titleLarge,
                        textAlign: TextAlign.center,
                      ),
                      const SizedBox(height: 32),
                      ElevatedButton.icon(
                        icon: const Icon(Icons.play_arrow_rounded),
                        label: const Text('Start Protocol Run'),
                        style: ElevatedButton.styleFrom(
                          padding: const EdgeInsets.symmetric(
                            horizontal: 32,
                            vertical: 16,
                          ),
                          textStyle: theme.textTheme.titleMedium?.copyWith(
                            color: theme.colorScheme.onPrimary,
                          ),
                          backgroundColor: theme.colorScheme.primary,
                          foregroundColor: theme.colorScheme.onPrimary,
                        ),
                        onPressed: () {
                          final wfState =
                              context.read<ProtocolWorkflowBloc>().state;
                          if (wfState.preparedBackendConfig != null) {
                            context.read<ProtocolStartBloc>().add(
                              ProtocolStartEvent.startRun(
                                backendConfig: wfState.preparedBackendConfig!,
                                protocolId:
                                    wfState
                                        .selectedProtocolInfo!
                                        .id, // Assuming ID is available
                                protocolName:
                                    wfState.selectedProtocolInfo!.name,
                              ),
                            );
                          }
                        },
                      ),
                    ],
                  ),
                ),
              ),
            ProtocolStarting() => const Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  CircularProgressIndicator(),
                  SizedBox(height: 16),
                  Text('Starting protocol run...'),
                ],
              ),
            ),
            ProtocolRunInitiated(runId: final runId, message: final message) =>
              Center(
                child: Padding(
                  padding: const EdgeInsets.all(24.0),
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(
                        Icons.check_circle_rounded,
                        size: 64,
                        color: Colors.green.shade700,
                      ),
                      const SizedBox(height: 24),
                      Text(
                        message ?? 'Protocol Run Initiated!',
                        style: theme.textTheme.headlineMedium,
                        textAlign: TextAlign.center,
                      ),
                      if (runId != null) ...[
                        const SizedBox(height: 8),
                        Text(
                          'Run ID: $runId',
                          style: theme.textTheme.titleMedium,
                        ),
                      ],
                      const SizedBox(height: 32),
                      ElevatedButton(
                        onPressed: () {
                          context.read<ProtocolWorkflowBloc>().add(
                            const ProtocolWorkflowEvent.resetWorkflow(),
                          );
                          // Potentially navigate to a dashboard or home screen
                          // Example: Navigator.of(context).popUntil((route) => route.isFirst);
                        },
                        child: const Text('Finish Workflow'),
                      ),
                    ],
                  ),
                ),
              ),
            ProtocolRunFailed(error: final error) => Center(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(
                      Icons.error_rounded,
                      color: theme.colorScheme.error,
                      size: 64,
                    ),
                    const SizedBox(height: 24),
                    Text(
                      'Failed to Start Protocol',
                      style: theme.textTheme.headlineMedium?.copyWith(
                        color: theme.colorScheme.error,
                      ),
                      textAlign: TextAlign.center,
                    ),
                    const SizedBox(height: 8),
                    Text(
                      error,
                      style: theme.textTheme.bodyLarge,
                      textAlign: TextAlign.center,
                    ),
                    const SizedBox(height: 32),
                    ElevatedButton(
                      onPressed: () {
                        // Retry logic: re-fetch config and try to load ready state
                        final wfState =
                            context.read<ProtocolWorkflowBloc>().state;
                        if (wfState.preparedBackendConfig != null) {
                          context.read<ProtocolStartBloc>().add(
                            ProtocolStartEvent.loadConfiguration(
                              backendConfig: wfState.preparedBackendConfig!,
                              protocolName:
                                  wfState.selectedProtocolInfo?.name ??
                                  'Unknown Protocol',
                            ),
                          );
                        } else {
                          context.read<ProtocolStartBloc>().add(
                            const ProtocolStartEvent.reportError(
                              message:
                                  "Missing prepared backend configuration for retry.",
                            ),
                          );
                        }
                      },
                      child: const Text('Retry'),
                    ),
                  ],
                ),
              ),
            ),
          };
        },
      ),
    );
  }
}
