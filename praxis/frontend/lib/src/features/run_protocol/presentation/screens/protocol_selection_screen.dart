// praxis_lab_management/lib/src/features/run_protocol/presentation/screens/protocol_selection_screen.dart
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
// Keep this if ProtocolInfo is used (it is for `protocols` list)
import 'package:praxis_lab_management/src/features/run_protocol/application/protocols_discovery_bloc/protocols_discovery_bloc.dart';
import 'package:praxis_lab_management/src/features/run_protocol/application/protocol_workflow_bloc/protocol_workflow_bloc.dart';

class ProtocolSelectionScreen extends StatefulWidget {
  const ProtocolSelectionScreen({super.key});

  @override
  State<ProtocolSelectionScreen> createState() =>
      _ProtocolSelectionScreenState();
}

class _ProtocolSelectionScreenState extends State<ProtocolSelectionScreen> {
  @override
  void initState() {
    super.initState();
    final protocolsBloc = context.read<ProtocolsDiscoveryBloc>();
    // Only add event if not already loading or loaded to prevent multiple fetches on quick rebuilds
    // Check against the public type names
    final currentState = protocolsBloc.state;
    if (currentState is! ProtocolsDiscoveryLoading &&
        currentState is! ProtocolsDiscoveryLoaded) {
      protocolsBloc.add(
        const ProtocolsDiscoveryEvent.fetchDiscoveredProtocols(),
      ); // Corrected event name
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Scaffold(
      appBar: AppBar(title: const Text('Select a Protocol')),
      body: BlocConsumer<ProtocolsDiscoveryBloc, ProtocolsDiscoveryState>(
        listener: (context, state) {
          // Use public type name for checking
          if (state is ProtocolsDiscoveryError) {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                content: Text('Error loading protocols: ${state.message}'),
                backgroundColor: theme.colorScheme.error,
              ),
            );
          }
        },
        builder: (context, state) {
          // Use public type names for switch cases
          return switch (state) {
            ProtocolsDiscoveryInitial() => const Center(
              child: Text('Initializing protocol list...'),
            ),
            ProtocolsDiscoveryLoading() => const Center(
              child: CircularProgressIndicator(),
            ),
            ProtocolsDiscoveryLoaded(protocols: final protocols) => () {
              if (protocols.isEmpty) {
                return Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      const Icon(
                        Icons.search_off_rounded,
                        size: 48,
                        color: Colors.grey,
                      ),
                      const SizedBox(height: 16),
                      const Text('No protocols found.'),
                      const SizedBox(height: 8),
                      ElevatedButton(
                        onPressed: () {
                          context.read<ProtocolsDiscoveryBloc>().add(
                            const ProtocolsDiscoveryEvent.fetchDiscoveredProtocols(),
                          ); // Corrected event name
                        },
                        child: const Text('Retry'),
                      ),
                    ],
                  ),
                );
              }
              return ListView.builder(
                padding: const EdgeInsets.all(8.0),
                itemCount: protocols.length,
                itemBuilder: (context, index) {
                  final protocol =
                      protocols[index]; // protocol is of type ProtocolInfo
                  return Card(
                    margin: const EdgeInsets.symmetric(
                      horizontal: 8,
                      vertical: 4,
                    ),
                    child: ListTile(
                      title: Text(
                        protocol.name,
                        style: theme.textTheme.titleMedium,
                      ),
                      subtitle: Text(
                        protocol.description ?? 'No description available.',
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis,
                        style: theme.textTheme.bodySmall,
                      ),
                      trailing: Icon(
                        Icons.arrow_forward_ios,
                        size: 16,
                        color: theme.colorScheme.primary,
                      ),
                      onTap: () {
                        context.read<ProtocolWorkflowBloc>().add(
                          ProtocolWorkflowEvent.protocolSelected(
                            // Ensure this event exists
                            selectedProtocol: protocol,
                          ), // Pass the selected protocol (type ProtocolInfo)
                        );
                      },
                    ),
                  );
                },
              );
            }(),
            ProtocolsDiscoveryError(message: final message) => Center(
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
                      'Failed to load protocols: $message',
                      textAlign: TextAlign.center,
                    ),
                    const SizedBox(height: 16),
                    ElevatedButton(
                      onPressed: () {
                        context.read<ProtocolsDiscoveryBloc>().add(
                          const ProtocolsDiscoveryEvent.fetchDiscoveredProtocols(),
                        ); // Corrected event name
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
