import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:pylabpraxis_flutter/src/features/run_protocol/application/protocol_start_bloc/protocol_start_bloc.dart';
import 'package:pylabpraxis_flutter/src/features/run_protocol/application/protocol_workflow_bloc/protocol_workflow_bloc.dart';

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
          state.mapOrNull(
            failure:
                (failureState) => ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(
                    content: Text(
                      'Protocol Start Failed: ${failureState.error}',
                    ),
                    backgroundColor: theme.colorScheme.error,
                    duration: const Duration(seconds: 5),
                  ),
                ),
            success: (successState) {
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(
                  content: Text(
                    'Protocol Started Successfully! Run ID: ${successState.response.runId}',
                  ),
                  backgroundColor: Colors.green,
                ),
              );
              // Notify workflow BLoC that protocol has started
              context.read<ProtocolWorkflowBloc>().add(
                ProtocolSuccessfullyStarted(response: successState.response),
              );
            },
          );
        },
        builder: (context, state) {
          return state.when(
            initial: () {
              // If BLoC is initial, workflow should have initialized it.
              // This screen expects ProtocolStartBloc to be in 'ready' state.
              final wfState = context.read<ProtocolWorkflowBloc>().state;
              if (wfState.preparedBackendConfig != null) {
                context.read<ProtocolStartBloc>().add(
                  InitializeStartScreen(
                    preparedConfig: wfState.preparedBackendConfig!,
                  ),
                );
              }
              return const Center(
                child: CircularProgressIndicator(
                  semanticsLabel: "Loading prepared configuration",
                ),
              );
            },
            ready:
                (preparedConfig) => _buildContent(
                  context,
                  preparedConfig,
                  jsonEncoder,
                  theme,
                  isLoading: false,
                ),
            startingExecution:
                (preparedConfig) => _buildContent(
                  context,
                  preparedConfig,
                  jsonEncoder,
                  theme,
                  isLoading: true,
                ),
            success:
                (response, preparedConfig) => _buildContent(
                  context,
                  preparedConfig,
                  jsonEncoder,
                  theme,
                  isLoading: false,
                  successMessage:
                      'Protocol Started: ${response.message} (Run ID: ${response.runId})',
                ),
            failure:
                (error, preparedConfig) => _buildContent(
                  context,
                  preparedConfig,
                  jsonEncoder,
                  theme,
                  isLoading: false,
                  errorMessage: error,
                ),
          );
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
                    color: theme.colorScheme.errorContainer.withOpacity(0.7),
                    elevation: 0,
                    shape: RoundedRectangleBorder(
                      side: BorderSide(
                        color: theme.colorScheme.error.withOpacity(0.5),
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
                          color: theme.colorScheme.onErrorContainer.withOpacity(
                            0.9,
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
                      color: theme.dividerColor.withOpacity(0.7),
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
            color: Colors.black.withOpacity(0.05),
            child: const Center(child: CircularProgressIndicator()),
          ),
      ],
    );
  }
}
