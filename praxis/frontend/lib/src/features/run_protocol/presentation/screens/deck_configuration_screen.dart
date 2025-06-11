// praxis_lab_management/lib/src/features/run_protocol/presentation/screens/deck_instance_screen.dart
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:file_picker/file_picker.dart';
import 'package:praxis_lab_management/src/features/run_protocol/application/deck_instance_bloc/deck_instance_bloc.dart';
import 'package:praxis_lab_management/src/features/run_protocol/application/protocol_workflow_bloc/protocol_workflow_bloc.dart';

class DeckInstanceScreen extends StatefulWidget {
  const DeckInstanceScreen({super.key});

  @override
  State<DeckInstanceScreen> createState() => _DeckInstanceScreenState();
}

class _DeckInstanceScreenState extends State<DeckInstanceScreen> {
  @override
  void initState() {
    super.initState();
    final workflowState = context.read<ProtocolWorkflowBloc>().state;
    context.read<DeckInstanceBloc>().add(
      DeckInstanceEvent.initializeDeckInstance(
        // Corrected event name
        initialSelectedLayoutName: workflowState.deckLayoutName,
        initialPickedFile: workflowState.uploadedDeckFile,
        // availableLayouts: workflowState.availableLayouts, // This should be fetched by the BLoC itself
      ),
    );
    context.read<DeckInstanceBloc>().add(
      const DeckInstanceEvent.fetchAvailableDeckLayouts(),
    ); // Corrected event name
  }

  Future<void> _pickFile() async {
    // Removed context from parameters
    final result = await FilePicker.platform.pickFiles(
      type: FileType.custom,
      allowedExtensions: ['json'],
    );

    if (result != null && result.files.single.path != null) {
      if (!mounted) return; // Check mounted after await
      context.read<DeckInstanceBloc>().add(
        DeckInstanceEvent.deckFilePicked(file: result.files.single),
      ); // Corrected event name
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Scaffold(
      appBar: AppBar(
        title: const Text('Configure Deck Layout'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () {
            context.read<ProtocolWorkflowBloc>().add(
              const ProtocolWorkflowEvent.goToPreviousStep(),
            );
          },
        ),
      ),
      body: BlocConsumer<DeckInstanceBloc, DeckInstanceState>(
        listener: (context, state) {
          if (state is DeckInstanceError) {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                content: Text('Deck config error: ${state.message}'),
                backgroundColor: theme.colorScheme.error,
              ),
            );
          } else if (state is DeckInstanceLoaded) {
            context.read<ProtocolWorkflowBloc>().add(
              ProtocolWorkflowEvent.updateStepValidity(
                isValid: state.isSelectionValid,
              ), // Corrected property name
            );
          }
        },
        builder: (context, state) {
          return switch (state) {
            DeckInstanceInitial() => const Center(
              child: Text('Initializing deck instanceuration...'),
            ),
            DeckInstanceLoading(
              // Access properties if needed, e.g., to show stale data while loading
              // availableLayouts: final availableLayouts,
              // selectedLayoutName: final selectedLayoutName,
              // pickedFile: final pickedFile,
            ) =>
              const Center(child: CircularProgressIndicator()),
            DeckInstanceLoaded(
              availableLayouts: final availableLayouts, // Corrected property name
              selectedLayoutName: final selectedLayoutName,
              pickedFile: final pickedFile, // Corrected property name
              isSelectionValid: final isSelectionValid, // Corrected property name
            ) =>
              Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Select a Predefined Layout:',
                      style: theme.textTheme.titleMedium,
                    ),
                    const SizedBox(height: 8),
                    if (availableLayouts.isEmpty) // Corrected property name
                      const Text('No predefined layouts available. Fetching...')
                    else
                      DropdownButtonFormField<String>(
                        decoration: const InputDecoration(
                          border: OutlineInputBorder(),
                          hintText: 'Choose a layout',
                        ),
                        value: selectedLayoutName,
                        items:
                            availableLayouts // Corrected property name
                                .map(
                                  (name) => DropdownMenuItem(
                                    value: name,
                                    child: Text(name),
                                  ),
                                )
                                .toList(),
                        onChanged: (value) {
                          if (value != null) {
                            context.read<DeckInstanceBloc>().add(
                              DeckInstanceEvent.deckLayoutSelected(
                                layoutName: value,
                              ),
                            ); // Corrected event name
                          }
                        },
                      ),
                    const SizedBox(height: 24),
                    Text(
                      'Or Upload a Custom Layout:',
                      style: theme.textTheme.titleMedium,
                    ),
                    const SizedBox(height: 8),
                    ElevatedButton.icon(
                      icon: const Icon(Icons.upload_file),
                      label: const Text('Pick .json File'),
                      onPressed: _pickFile, // Call method without context
                    ),
                    if (pickedFile != null) ...[
                      // Corrected property name
                      const SizedBox(height: 8),
                      Text(
                        'Uploaded: ${pickedFile.name}',
                        style: theme.textTheme.bodySmall,
                      ), // Corrected property name
                      TextButton(
                        onPressed: () {
                          context.read<DeckInstanceBloc>().add(
                            const DeckInstanceEvent.clearDeckSelection(),
                          ); // Corrected event name
                        },
                        child: const Text('Clear Uploaded File'),
                      ),
                    ],
                    const Spacer(),
                    ElevatedButton(
                      style: ElevatedButton.styleFrom(
                        minimumSize: const Size(double.infinity, 48),
                      ),
                      onPressed:
                          isSelectionValid // Corrected property name
                              ? () {
                                context.read<ProtocolWorkflowBloc>().add(
                                  ProtocolWorkflowEvent.deckConfigSubmitted(
                                    // Assuming this event exists
                                    layoutName: selectedLayoutName,
                                    uploadedFile:
                                        pickedFile, // Corrected property name
                                  ),
                                );
                              }
                              : null,
                      child: const Text('Confirm Deck Layout & Next'),
                    ),
                  ],
                ),
              ),
            DeckInstanceError(message: final message) => Center(
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
                      'Error with deck instanceuration: $message',
                      textAlign: TextAlign.center,
                    ),
                    const SizedBox(height: 16),
                    ElevatedButton(
                      onPressed: () {
                        final wfState =
                            context.read<ProtocolWorkflowBloc>().state;
                        context.read<DeckInstanceBloc>().add(
                          DeckInstanceEvent.initializeDeckInstance(
                            // Corrected event name
                            initialSelectedLayoutName: wfState.deckLayoutName,
                            initialPickedFile: wfState.uploadedDeckFile,
                          ),
                        );
                        context.read<DeckInstanceBloc>().add(
                          const DeckInstanceEvent.fetchAvailableDeckLayouts(),
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
