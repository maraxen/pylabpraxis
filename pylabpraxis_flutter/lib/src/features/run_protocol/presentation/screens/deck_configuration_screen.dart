import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:file_picker/file_picker.dart';
import 'package:pylabpraxis_flutter/src/features/run_protocol/application/deck_configuration_bloc/deck_configuration_bloc.dart';
import 'package:pylabpraxis_flutter/src/features/run_protocol/application/protocol_workflow_bloc/protocol_workflow_bloc.dart';

class DeckConfigurationScreen extends StatefulWidget {
  const DeckConfigurationScreen({super.key});

  @override
  State<DeckConfigurationScreen> createState() =>
      _DeckConfigurationScreenState();
}

class _DeckConfigurationScreenState extends State<DeckConfigurationScreen> {
  @override
  void initState() {
    super.initState();
    final deckBloc = context.read<DeckConfigurationBloc>();
    // Fetch available layouts if not already loaded or initialized by workflow.
    // Workflow BLoC's GoToStep for deck config should handle InitializeDeckConfiguration.
    if (deckBloc.state is DeckConfigurationInitial) {
      deckBloc.add(const FetchAvailableDeckLayouts());
    }
  }

  Future<void> _pickDeckFile(BuildContext blocContext) async {
    // Pass BLoC context
    try {
      FilePickerResult? result = await FilePicker.platform.pickFiles(
        type: FileType.custom,
        allowedExtensions: ['json'],
      );

      if (result != null && result.files.single.path != null) {
        PlatformFile file = result.files.first;
        blocContext.read<DeckConfigurationBloc>().add(
          DeckFilePicked(file: file),
        );
      }
    } catch (e) {
      if (mounted) {
        // Check if widget is still in the tree
        ScaffoldMessenger.of(blocContext).showSnackBar(
          // Use BLoC context for ScaffoldMessenger
          SnackBar(content: Text('Error picking file: ${e.toString()}')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Scaffold(
      // AppBar is part of parent workflow screen
      body: BlocConsumer<DeckConfigurationBloc, DeckConfigurationState>(
        listener: (context, state) {
          state.mapOrNull(
            error:
                (errorState) => ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(
                    content: Text('Error: ${errorState.message}'),
                    backgroundColor: theme.colorScheme.error,
                  ),
                ),
            loaded: (loadedState) {
              context.read<ProtocolWorkflowBloc>().add(
                UpdateStepValidity(isValid: loadedState.isSelectionValid),
              );
            },
          );
        },
        builder: (context, state) {
          // Renamed context to builderContext to avoid conflict
          return Column(
            children: [
              Expanded(
                child: SingleChildScrollView(
                  padding: const EdgeInsets.all(24.0), // Increased padding
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: <Widget>[
                      Text(
                        'Choose an existing deck layout or upload a new one.',
                        style: theme.textTheme.titleLarge?.copyWith(
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        'The deck layout defines the positions and types of labware on the robot deck.',
                        style: theme.textTheme.bodyMedium?.copyWith(
                          color: theme.colorScheme.onSurfaceVariant,
                        ),
                      ),
                      const SizedBox(height: 32),
                      if (state is DeckConfigurationLoading)
                        const Center(
                          child: Padding(
                            padding: EdgeInsets.all(16.0),
                            child: CircularProgressIndicator(),
                          ),
                        ),
                      if (state is DeckConfigurationError)
                        Center(
                          child: Column(
                            children: [
                              Icon(
                                Icons.error_outline_rounded,
                                color: theme.colorScheme.error,
                                size: 32,
                              ),
                              const SizedBox(height: 8),
                              Text(
                                state.message,
                                style: TextStyle(
                                  color: theme.colorScheme.error,
                                ),
                              ),
                              const SizedBox(height: 12),
                              ElevatedButton.icon(
                                icon: const Icon(Icons.refresh_rounded),
                                label: const Text('Retry Fetch'),
                                onPressed:
                                    () => context
                                        .read<DeckConfigurationBloc>()
                                        .add(const FetchAvailableDeckLayouts()),
                              ),
                            ],
                          ),
                        ),
                      if (state is DeckConfigurationLoaded) ...[
                        _buildDropdown(context, state),
                        const SizedBox(height: 24),
                        Row(
                          children: [
                            const Expanded(child: Divider()),
                            Padding(
                              padding: const EdgeInsets.symmetric(
                                horizontal: 16.0,
                              ),
                              child: Text(
                                "OR",
                                style: theme.textTheme.labelLarge?.copyWith(
                                  color: theme.colorScheme.outline,
                                ),
                              ),
                            ),
                            const Expanded(child: Divider()),
                          ],
                        ),
                        const SizedBox(height: 24),
                        _buildFileUploadSection(
                          context,
                          state,
                        ), // Pass builderContext
                        if (state.selectedLayoutName != null ||
                            state.pickedFile != null) ...[
                          const SizedBox(height: 32),
                          Center(
                            child: _buildClearSelectionButton(context),
                          ), // Pass builderContext
                        ],
                      ],
                      if (state is DeckConfigurationInitial)
                        const Center(
                          child: Padding(
                            padding: EdgeInsets.all(16.0),
                            child: Text("Initializing deck configuration..."),
                          ),
                        ),
                    ],
                  ),
                ),
              ),
              // "Next" button is part of the global RunProtocolWorkflowScreen
            ],
          );
        },
      ),
    );
  }

  Widget _buildDropdown(
    BuildContext blocContext,
    DeckConfigurationLoaded state,
  ) {
    // Use blocContext
    final theme = Theme.of(blocContext);
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Select Existing Layout:',
          style: theme.textTheme.titleSmall?.copyWith(
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 12),
        DropdownButtonFormField<String>(
          decoration: InputDecoration(
            border: const OutlineInputBorder(),
            hintText:
                state.availableLayouts.isEmpty
                    ? 'No layouts available'
                    : 'Choose a layout',
            prefixIcon: const Icon(Icons.inventory_2_outlined),
          ),
          value: state.selectedLayoutName,
          items:
              state.availableLayouts
                  .map(
                    (layout) =>
                        DropdownMenuItem(value: layout, child: Text(layout)),
                  )
                  .toList(),
          onChanged:
              (state.pickedFile != null || state.availableLayouts.isEmpty)
                  ? null
                  : (String? newValue) {
                    blocContext.read<DeckConfigurationBloc>().add(
                      DeckLayoutSelected(layoutName: newValue),
                    );
                  },
          isExpanded: true,
        ),
      ],
    );
  }

  Widget _buildFileUploadSection(
    BuildContext blocContext,
    DeckConfigurationLoaded state,
  ) {
    // Use blocContext
    final theme = Theme.of(blocContext);
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Text(
          'Upload New Layout (.json):',
          style: theme.textTheme.titleSmall?.copyWith(
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 12),
        ElevatedButton.icon(
          icon: const Icon(Icons.upload_file_rounded),
          label: const Text('Select .json File from Device'),
          onPressed:
              state.selectedLayoutName != null
                  ? null
                  : () => _pickDeckFile(blocContext), // Pass blocContext
          style: ElevatedButton.styleFrom(
            padding: const EdgeInsets.symmetric(vertical: 16), // Larger button
            textStyle: theme.textTheme.labelLarge,
          ),
        ),
        if (state.pickedFile != null) ...[
          const SizedBox(height: 16),
          Card(
            elevation: 0,
            shape: RoundedRectangleBorder(
              side: BorderSide(color: theme.colorScheme.primary),
              borderRadius: BorderRadius.circular(8),
            ),
            color: theme.colorScheme.primaryContainer.withOpacity(0.3),
            child: ListTile(
              leading: Icon(
                Icons.check_circle_outline_rounded,
                color: theme.colorScheme.primary,
              ),
              title: Text(
                state.pickedFile!.name,
                style: TextStyle(
                  fontWeight: FontWeight.bold,
                  color: theme.colorScheme.onPrimaryContainer,
                ),
              ),
              subtitle: Text(
                '${(state.pickedFile!.size / 1024).toStringAsFixed(2)} KB',
                style: TextStyle(
                  color: theme.colorScheme.onPrimaryContainer.withOpacity(0.8),
                ),
              ),
              trailing: IconButton(
                icon: Icon(
                  Icons.close_rounded,
                  color: theme.colorScheme.onPrimaryContainer.withOpacity(0.7),
                ),
                onPressed:
                    () => blocContext.read<DeckConfigurationBloc>().add(
                      const ClearDeckSelection(),
                    ),
                tooltip: "Clear Uploaded File",
              ),
            ),
          ),
        ],
      ],
    );
  }

  Widget _buildClearSelectionButton(BuildContext blocContext) {
    // Use blocContext
    return OutlinedButton.icon(
      icon: const Icon(Icons.clear_all_rounded, size: 20),
      label: const Text('Clear Current Selection'),
      onPressed: () {
        blocContext.read<DeckConfigurationBloc>().add(
          const ClearDeckSelection(),
        );
      },
      style: OutlinedButton.styleFrom(
        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 10),
        foregroundColor: Theme.of(blocContext).colorScheme.secondary,
        side: BorderSide(
          color: Theme.of(blocContext).colorScheme.secondary.withOpacity(0.5),
        ),
      ),
    );
  }
}
