import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';
import 'package:pylabpraxis_flutter/src/data/models/protocol/protocol_info.dart';
import 'package:pylabpraxis_flutter/src/features/run_protocol/application/protocols_discovery_bloc/protocols_discovery_bloc.dart';
import 'package:pylabpraxis_flutter/src/features/run_protocol/application/protocol_workflow_bloc/protocol_workflow_bloc.dart';
// Import your route name constants from app_go_router.dart
import 'package:pylabpraxis_flutter/src/core/routing/app_go_router.dart';

class ProtocolsScreen extends StatefulWidget {
  const ProtocolsScreen({super.key});

  @override
  State<ProtocolsScreen> createState() => _ProtocolsScreenState();
}

class _ProtocolsScreenState extends State<ProtocolsScreen> {
  @override
  void initState() {
    super.initState();
    context.read<ProtocolsDiscoveryBloc>().add(
      const FetchDiscoveredProtocols(),
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Scaffold(
      // AppBar is now part of AppShell
      // appBar: AppBar(
      //   title: const Text('Available Protocols'),
      //   actions: [
      //     IconButton(
      //       icon: const Icon(Icons.refresh),
      //       onPressed: () {
      //         context.read<ProtocolsDiscoveryBloc>().add(
      //               const FetchDiscoveredProtocols(),
      //             );
      //       },
      //       tooltip: 'Refresh Protocols',
      //     ),
      //   ],
      // ),
      body: BlocConsumer<ProtocolsDiscoveryBloc, ProtocolsDiscoveryState>(
        listener: (context, state) {
          if (state is ProtocolsDiscoveryError) {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                content: Text('Failed to load protocols: ${state.message}'),
                backgroundColor: theme.colorScheme.error,
              ),
            );
          }
        },
        builder: (context, state) {
          return switch (state) {
            ProtocolsDiscoveryInitial() => const Center(
              child: Text("Initializing protocols..."),
            ),
            ProtocolsDiscoveryLoading() => const Center(
              child: CircularProgressIndicator(),
            ),
            ProtocolsDiscoveryLoaded(protocols: final protocols) =>
              _buildProtocolsList(context, protocols, theme),
            ProtocolsDiscoveryError(message: final errorMsg) => Center(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(
                      Icons.error_outline,
                      color: theme.colorScheme.error,
                      size: 48,
                    ),
                    const SizedBox(height: 16),
                    Text(
                      'Error loading protocols:',
                      style: theme.textTheme.titleMedium,
                      textAlign: TextAlign.center,
                    ),
                    const SizedBox(height: 8),
                    Text(
                      errorMsg,
                      textAlign: TextAlign.center,
                      style: TextStyle(color: theme.colorScheme.error),
                    ),
                    const SizedBox(height: 20),
                    ElevatedButton.icon(
                      icon: const Icon(Icons.refresh),
                      label: const Text('Retry'),
                      onPressed: () {
                        context.read<ProtocolsDiscoveryBloc>().add(
                          const FetchDiscoveredProtocols(),
                        );
                      },
                    ),
                  ],
                ),
              ),
            ),
          };
        },
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () {
          context.read<ProtocolWorkflowBloc>().add(const ResetWorkflow());
          // Navigate to the start of the Run Protocol Workflow.
          // beginProtocolWorkflowRouteName points to the first step (e.g., parameterConfigurationRouteName)
          // We pass null as 'extra' because no specific protocol is pre-selected.
          // The RunProtocolWorkflowScreen's initState or the BLoC should handle this scenario,
          // possibly by ensuring the BLoC is in a state to select a protocol or show an appropriate UI.
          // However, for a "Run New Protocol" FAB, it's typical to select the protocol *within* the workflow.
          // For now, we navigate, and the workflow screen will handle the null protocolInfo.
          // If your workflow *requires* a protocol to start, this FAB might need to navigate to a
          // dedicated protocol selection screen first, or this logic might be more complex.
          // Given our current setup, RunProtocolWorkflowScreen will receive null and should handle it.
          context.goNamed(beginProtocolWorkflowRouteName, extra: null);
        },
        label: const Text('Run New Protocol'),
        icon: const Icon(Icons.play_arrow_rounded),
        backgroundColor: theme.colorScheme.primaryContainer,
        foregroundColor: theme.colorScheme.onPrimaryContainer,
        tooltip: 'Start a new protocol run',
      ),
    );
  }

  Widget _buildProtocolsList(
    BuildContext context,
    List<ProtocolInfo> protocols,
    ThemeData theme,
  ) {
    if (protocols.isEmpty) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(
                Icons.search_off_rounded,
                size: 64,
                color: Colors.grey,
              ),
              const SizedBox(height: 16),
              Text(
                'No protocols found.',
                style: theme.textTheme.headlineSmall,
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 8),
              Text(
                'Try refreshing or check the backend server configuration.',
                style: theme.textTheme.bodyLarge,
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 20),
              ElevatedButton.icon(
                icon: const Icon(Icons.refresh),
                label: const Text('Refresh'),
                onPressed: () {
                  context.read<ProtocolsDiscoveryBloc>().add(
                    const FetchDiscoveredProtocols(),
                  );
                },
              ),
            ],
          ),
        ),
      );
    }
    return RefreshIndicator(
      onRefresh: () async {
        context.read<ProtocolsDiscoveryBloc>().add(
          const FetchDiscoveredProtocols(),
        );
      },
      child: ListView.builder(
        padding: const EdgeInsets.all(16.0),
        itemCount: protocols.length,
        itemBuilder: (context, index) {
          final protocol = protocols[index];
          return Card(
            elevation: 2,
            margin: const EdgeInsets.symmetric(vertical: 8.0),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12.0),
            ),
            child: ListTile(
              contentPadding: const EdgeInsets.symmetric(
                horizontal: 20,
                vertical: 12,
              ),
              leading: Icon(
                Icons.science_outlined,
                color: theme.colorScheme.primary,
                size: 36,
              ),
              title: Text(
                protocol.name,
                style: theme.textTheme.titleLarge?.copyWith(
                  fontWeight: FontWeight.w500,
                ),
              ),
              subtitle: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const SizedBox(height: 4),
                  Text(
                    protocol.description,
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                    style: theme.textTheme.bodyMedium?.copyWith(
                      color: theme.colorScheme.onSurfaceVariant,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Row(
                    children: [
                      Icon(
                        Icons.tag_rounded,
                        size: 16,
                        color: theme.colorScheme.secondary,
                      ),
                      const SizedBox(width: 4),
                      Text(
                        'Version: ${protocol.version}',
                        style: theme.textTheme.labelMedium,
                      ),
                      const SizedBox(width: 12),
                      Icon(
                        Icons.category_outlined,
                        size: 16,
                        color: theme.colorScheme.secondary,
                      ),
                      const SizedBox(width: 4),
                      Expanded(
                        child: Text(
                          protocol.category ?? "Uncategorized",
                          style: theme.textTheme.labelMedium,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                    ],
                  ),
                ],
              ),
              trailing: Icon(
                Icons.chevron_right_rounded,
                color: theme.colorScheme.outline,
              ),
              onTap: () {
                context.read<ProtocolWorkflowBloc>().add(
                  const ResetWorkflow(), // Reset workflow state for the new selection
                );
                // Dispatch the correct event with the selected protocol
                context.read<ProtocolWorkflowBloc>().add(
                  ProtocolSelectedInWorkflow(selectedProtocol: protocol),
                );
                // Navigate to the first step of the workflow, passing the protocol as extra.
                // The ShellRoute for the workflow will pick up this 'extra'.
                context.goNamed(
                  beginProtocolWorkflowRouteName,
                  extra: protocol,
                );
              },
            ),
          );
        },
      ),
    );
  }
}
