import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:praxis_lab_management/src/features/run_protocol/application/protocol_start_bloc/protocol_start_bloc.dart';
import 'package:praxis_lab_management/src/features/run_protocol/application/protocol_workflow_bloc/protocol_workflow_bloc.dart';

class StartProtocolScreen extends StatelessWidget {
  const StartProtocolScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final jsonEncoder = JsonEncoder.withIndent('  ');
    final theme = Theme.of(context);

    return Scaffold(
      // AppBar is part of parent workflow screen
      body: BlocConsumer<ProtocolStartBloc, ProtocolStartState>(
        listener: (context, state) {
          // Replace mapOrNull with if-else if pattern matching
          if (state is ProtocolStartFailure) {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                content: Text('Protocol Start Failed: ${state.error}'),
                backgroundColor: theme.colorScheme.error,
                duration: const Duration(seconds: 5),
              ),
            );
          } else if (state is ProtocolStartSuccess) {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                content: Text(
                  'Protocol Started Successfully! Run ID: ${state.response.runId}',
                ),
                backgroundColor: Colors.green,
              ),
            );
            // Notify workflow BLoC that protocol has started
            context.read<ProtocolWorkflowBloc>().add(
              ProtocolSuccessfullyStarted(response: state.response),
            );
          }
        },
        builder: (context, state) {
          // Replace when with switch pattern matching
          // Ensure that ProtocolStartState is a sealed class or that all subtypes are handled.
          // The class definitions for ProtocolStartInitial, ProtocolStartReady etc.
          // must be available in this scope.
          // If they are part of the protocol_start_state.dart which is imported by protocol_start_bloc.dart,
          // you might need to import protocol_start_state.dart directly here as well,
          // or ensure protocol_start_bloc.dart exports them.
          switch (state) {
            case ProtocolStartInitial():
              // If BLoC is initial, workflow should have initialized it.
              // This screen expects ProtocolStartBloc to be in 'ready' state.
              final wfState = context.read<ProtocolWorkflowBloc>().state;
              // Ensure wfState.preparedBackendConfig is not null before accessing it
              final preparedConfig = wfState.preparedBackendConfig;
              if (preparedConfig != null) {
                context.read<ProtocolStartBloc>().add(
                  InitializeStartScreen(preparedConfig: preparedConfig),
                );
              }
              return const Center(
                child: CircularProgressIndicator(
                  semanticsLabel: "Loading prepared configuration",
                ),
              );
            case ProtocolStartReady(preparedConfig: final config):
              return _buildContent(
                context,
                config,
                jsonEncoder,
                theme,
                isLoading: false,
              );
            case ProtocolStartingExecution(preparedConfig: final config):
              return _buildContent(
                context,
                config,
                jsonEncoder,
                theme,
                isLoading: true,
              );
            case ProtocolStartSuccess(
              response: final response,
              preparedConfig: final config,
            ):
              return _buildContent(
                context,
                config,
                jsonEncoder,
                theme,
                isLoading: false,
                successMessage:
                    'Protocol Started: ${response.message} (Run ID: ${response.runId})',
              );
            case ProtocolStartFailure(
              error: final errorMsg,
              preparedConfig: final config,
            ):
              // If preparedConfig can be null in ProtocolStartFailure, handle it:
              final currentConfig = config;
              return _buildContent(
                context,
                currentConfig, // Use a fallback if config is null
                jsonEncoder,
                theme,
                isLoading: false,
                errorMessage: errorMsg,
              );
            // It's good practice to have a default case if not all states are explicitly handled
            // or if ProtocolStartState is not a sealed class.
            // However, if ProtocolStartState is sealed and all cases are covered,
            // the analyzer might tell you a default case is not needed.
            default:
              // This case should ideally not be reached if all states are handled.
              // You might want to log an error or show a generic error UI.
              return const Center(child: Text("Unhandled state"));
          }
        },
      ),
    );
  }

  Widget _buildContent(
    BuildContext context,
    Map<String, dynamic> preparedConfig,
    JsonEncoder jsonEncoder,
    ThemeData theme, {
    required bool isLoading,
    String? successMessage,
    String? errorMessage,
  }) {
    return Stack(
      children: [
        Padding(
          padding: const EdgeInsets.all(24.0), // Increased padding
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: <Widget>[
              if (successMessage != null)
                Padding(
                  padding: const EdgeInsets.only(bottom: 16.0),
                  child: Card(
                    color: Colors.green.shade50,
                    elevation: 0,
                    shape: RoundedRectangleBorder(
                      side: BorderSide(color: Colors.green.shade200),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: ListTile(
                      leading: Icon(
                        Icons.check_circle_outline_rounded,
                        color: Colors.green.shade700,
                        size: 28,
                      ),
                      title: Text(
                        "Success!",
                        style: theme.textTheme.titleMedium?.copyWith(
                          color: Colors.green.shade900,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      subtitle: Text(
                        successMessage,
                        style: TextStyle(color: Colors.green.shade800),
                      ),
                    ),
                  ),
                ),
              if (errorMessage != null)
                Padding(
                  padding: const EdgeInsets.only(bottom: 16.0),
                  child: Card(
                    color: theme.colorScheme.errorContainer.withAlpha(190),
                    elevation: 0,
                    shape: RoundedRectangleBorder(
                      side: BorderSide(
                        color: theme.colorScheme.error.withAlpha(120),
                      ),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: ListTile(
                      leading: Icon(
                        Icons.error_outline_rounded,
                        color: theme.colorScheme.onErrorContainer,
                        size: 28,
                      ),
                      title: Text(
                        "Error Starting Protocol",
                        style: TextStyle(
                          color: theme.colorScheme.onErrorContainer,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      subtitle: Text(
                        errorMessage,
                        style: TextStyle(
                          color: theme.colorScheme.onErrorContainer.withAlpha(
                            230,
                          ),
                        ),
                      ),
                    ),
                  ),
                ),
              Text(
                'Prepared Configuration:',
                style: theme.textTheme.titleLarge?.copyWith(
                  fontWeight: FontWeight.w500,
                ),
              ),
              const SizedBox(height: 12),
              Expanded(
                child: Container(
                  decoration: BoxDecoration(
                    color:
                        theme
                            .colorScheme
                            .surfaceContainerLowest, // M3 surface color
                    borderRadius: BorderRadius.circular(12.0),
                    border: Border.all(
                      color: theme.dividerColor.withAlpha(190),
                    ),
                  ),
                  child: Scrollbar(
                    thumbVisibility: true,
                    child: SingleChildScrollView(
                      padding: const EdgeInsets.all(16.0),
                      child: Text(
                        jsonEncoder.convert(preparedConfig),
                        style: theme.textTheme.bodyMedium?.copyWith(
                          fontFamily: 'monospace',
                          letterSpacing: 0.5,
                          height: 1.5,
                        ),
                      ),
                    ),
                  ),
                ),
              ),
              const SizedBox(height: 24),
              ElevatedButton.icon(
                icon:
                    isLoading
                        ? Container(
                          width: 20,
                          height: 20,
                          padding: const EdgeInsets.all(2.0),
                          child: CircularProgressIndicator(
                            strokeWidth: 2.5,
                            color: theme.colorScheme.onPrimary,
                          ),
                        )
                        : const Icon(Icons.play_circle_fill_rounded, size: 22),
                label: Text(
                  isLoading ? 'STARTING...' : 'START PROTOCOL EXECUTION',
                ),
                onPressed:
                    isLoading || successMessage != null
                        ? null
                        : () {
                          context.read<ProtocolStartBloc>().add(
                            const ExecuteStartProtocol(),
                          );
                        },
                style: ElevatedButton.styleFrom(
                  minimumSize: const Size(double.infinity, 52),
                  textStyle: theme.textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                  backgroundColor:
                      Colors.green.shade600, // Distinct start button color
                  foregroundColor: Colors.white,
                ),
              ),
            ],
          ),
        ),
        if (isLoading &&
            successMessage == null) // Show overlay only if not already success
          Container(
            color: Colors.black.withAlpha(12),
            child: const Center(child: CircularProgressIndicator()),
          ),
      ],
    );
  }
}
