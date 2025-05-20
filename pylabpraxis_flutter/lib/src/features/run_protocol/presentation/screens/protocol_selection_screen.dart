import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:pylabpraxis_flutter/src/data/models/protocol/protocol_info.dart';
import 'package:pylabpraxis_flutter/src/features/run_protocol/application/protocols_discovery_bloc/protocols_discovery_bloc.dart';
import 'package:pylabpraxis_flutter/src/features/run_protocol/application/protocol_workflow_bloc/protocol_workflow_bloc.dart'; // For dispatching to workflow

class ProtocolSelectionScreen extends StatefulWidget {
  const ProtocolSelectionScreen({super.key});

  @override
  State<ProtocolSelectionScreen> createState() =>
      _ProtocolSelectionScreenState();
}

class _ProtocolSelectionScreenState extends State<ProtocolSelectionScreen> {
  ProtocolInfo?
  _selectedProtocolForUI; // Local UI state for highlighting selection

  @override
  void initState() {
    super.initState();
    // Fetch protocols if not already loaded or if explicitly desired on screen init
    // This might be redundant if RunProtocolWorkflowScreen already triggers this.
    // Consider if this BLoC should be auto-fetching on creation or via an explicit init event.
    final discoveryBloc = context.read<ProtocolsDiscoveryBloc>();
    if (discoveryBloc.state is ProtocolsDiscoveryInitial ||
        discoveryBloc.state is ProtocolsDiscoveryError) {
      discoveryBloc.add(const FetchDiscoveredProtocols());
    }

    // Initialize _selectedProtocolForUI from workflow state if available (e.g., navigating back)
    final workflowState = context.read<ProtocolWorkflowBloc>().state;
    if (workflowState.selectedProtocolInfo != null) {
      _selectedProtocolForUI = workflowState.selectedProtocolInfo;
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    // The "Next" button's enabled state is now controlled by ProtocolWorkflowBloc.isCurrentStepDataValid
    // This screen's responsibility is to dispatch ProtocolSelectedInWorkflow.
    // The ProtocolWorkflowBloc then sets its own isCurrentStepDataValid to true for this step.

    return Scaffold(
      // AppBar is typically part of the parent workflow screen
      // appBar: AppBar(
      //   title: const Text('Select Protocol'),
      // ),
      body: Column(
        children: [
          Expanded(
            child: BlocConsumer<
              ProtocolsDiscoveryBloc,
              ProtocolsDiscoveryState
            >(
              listener: (context, state) {
                state.mapOrNull(
                  error:
                      (errorState) =>
                          ScaffoldMessenger.of(context).showSnackBar(
                            SnackBar(
                              content: Text('Error: ${errorState.message}'),
                              backgroundColor: theme.colorScheme.error,
                            ),
                          ),
                );
              },
              builder: (context, state) {
                return state.when(
                  initial:
                      () => const Center(
                        child: Text('Initializing protocols...'),
                      ),
                  loading:
                      () => const Center(child: CircularProgressIndicator()),
                  loaded: (protocols) {
                    if (protocols.isEmpty) {
                      return Center(
                        child: Padding(
                          padding: const EdgeInsets.all(16.0),
                          child: Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Icon(
                                Icons.search_off_rounded,
                                size: 48,
                                color: theme.colorScheme.onSurfaceVariant,
                              ),
                              const SizedBox(height: 16),
                              Text(
                                'No protocols found.',
                                style: theme.textTheme.titleMedium,
                              ),
                              const SizedBox(height: 16),
                              ElevatedButton.icon(
                                icon: const Icon(Icons.refresh_rounded),
                                label: const Text('Retry Fetch'),
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
                    return ListView.builder(
                      padding: const EdgeInsets.symmetric(vertical: 8.0),
                      itemCount: protocols.length,
                      itemBuilder: (context, index) {
                        final protocol = protocols[index];
                        final bool isSelected =
                            _selectedProtocolForUI?.id == protocol.id;
                        return Card(
                          elevation: isSelected ? 3 : 1,
                          margin: const EdgeInsets.symmetric(
                            horizontal: 16,
                            vertical: 6,
                          ),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(12),
                            side: BorderSide(
                              color:
                                  isSelected
                                      ? theme.colorScheme.primary
                                      : theme.dividerColor.withOpacity(0.5),
                              width: isSelected ? 1.5 : 1,
                            ),
                          ),
                          child: ListTile(
                            leading: Icon(
                              isSelected
                                  ? Icons.check_circle_rounded
                                  : Icons.biotech_outlined,
                              color:
                                  isSelected
                                      ? theme.colorScheme.primary
                                      : theme.colorScheme.secondary,
                            ),
                            title: Text(
                              protocol.name,
                              style: theme.textTheme.titleMedium?.copyWith(
                                fontWeight:
                                    isSelected
                                        ? FontWeight.bold
                                        : FontWeight.normal,
                              ),
                            ),
                            subtitle: Text(
                              protocol.description ??
                                  'No description available',
                              maxLines: 2,
                              overflow: TextOverflow.ellipsis,
                            ),
                            selected: isSelected,
                            selectedTileColor: theme
                                .colorScheme
                                .primaryContainer
                                .withOpacity(0.3),
                            onTap: () {
                              setState(() {
                                _selectedProtocolForUI = protocol;
                              });
                              // Dispatch to workflow BLoC
                              context.read<ProtocolWorkflowBloc>().add(
                                ProtocolSelectedInWorkflow(
                                  selectedProtocol: protocol,
                                ),
                              );
                            },
                          ),
                        );
                      },
                    );
                  },
                  error:
                      (message) => Center(
                        child: Padding(
                          padding: const EdgeInsets.all(16.0),
                          child: Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Icon(
                                Icons.error_outline_rounded,
                                size: 48,
                                color: theme.colorScheme.error,
                              ),
                              const SizedBox(height: 16),
                              Text(
                                'Error loading protocols: $message',
                                textAlign: TextAlign.center,
                                style: theme.textTheme.titleMedium?.copyWith(
                                  color: theme.colorScheme.error,
                                ),
                              ),
                              const SizedBox(height: 16),
                              ElevatedButton.icon(
                                icon: const Icon(Icons.refresh_rounded),
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
                );
              },
            ),
          ),
          // "Next" button is now part of the global RunProtocolWorkflowScreen's bottom navigation bar
        ],
      ),
    );
  }
}
