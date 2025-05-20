import 'dart:convert'; // For JsonEncoder
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:pylabpraxis_flutter/src/features/run_protocol/application/protocol_review_bloc/protocol_review_bloc.dart';
import 'package:pylabpraxis_flutter/src/features/run_protocol/application/protocol_workflow_bloc/protocol_workflow_bloc.dart'; // Import Workflow BLoC
import 'package:pylabpraxis_flutter/src/features/run_protocol/domain/review_data_bundle.dart';
import 'package:pylabpraxis_flutter/src/features/run_protocol/domain/workflow_step.dart'; // Import WorkflowStep

class ReviewAndPrepareScreen extends StatelessWidget {
  const ReviewAndPrepareScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Review and Prepare'),
        leading: IconButton(
          // Back button to previous step in workflow
          icon: const Icon(Icons.arrow_back_ios_new_rounded),
          onPressed: () {
            // Determine the correct previous step.
            // This might be deck config, or asset assignment if deck was skipped, etc.
            // ProtocolWorkflowBloc should handle this logic.
            // For simplicity, we assume a linear back step or let the workflow bloc decide.
            // A more robust way is for ProtocolWorkflowBloc to know the actual previous step.
            final workflowBloc = context.read<ProtocolWorkflowBloc>();
            WorkflowStep targetStep =
                WorkflowStep.deckConfiguration; // Default previous

            // Simplified logic for going back:
            if (workflowBloc.state.deckLayoutName == null &&
                workflowBloc.state.uploadedDeckFile == null) {
              // If deck was skipped or not set, try assets
              if (workflowBloc.state.assignedAssets == null &&
                  (workflowBloc
                          .state
                          .selectedProtocolDetails
                          ?.assets
                          ?.isEmpty ??
                      true)) {
                targetStep = WorkflowStep.parameterConfiguration;
              } else if (workflowBloc
                      .state
                      .selectedProtocolDetails
                      ?.assets
                      ?.isNotEmpty ??
                  false) {
                targetStep = WorkflowStep.assetAssignment;
              } else {
                // No assets, deck not set, go to params
                targetStep = WorkflowStep.parameterConfiguration;
              }
            }
            workflowBloc.add(
              GoToStep(targetStep: targetStep, fromReviewScreen: true),
            );
          },
        ),
      ),
      body: BlocConsumer<ProtocolReviewBloc, ProtocolReviewState>(
        listener: (context, state) {
          state.mapOrNull(
            preparationFailure:
                (failureState) => ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(
                    content: Text('Preparation Failed: ${failureState.error}'),
                    backgroundColor: Theme.of(context).colorScheme.error,
                    duration: const Duration(seconds: 5),
                  ),
                ),
            preparationSuccess: (successState) {
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(
                  content: const Text(
                    'Protocol Prepared Successfully! Ready to Start.',
                  ),
                  backgroundColor: Colors.green,
                ),
              );
              // ProtocolWorkflowBloc will handle navigation to StartProtocolScreen
              context.read<ProtocolWorkflowBloc>().add(
                ProtocolSuccessfullyPrepared(
                  preparedConfig: successState.preparedConfig,
                ),
              );
            },
          );
        },
        builder: (context, state) {
          return state.when(
            initial: () {
              // If initial, try to load data via workflow bloc
              // This assumes ReviewAndPrepareScreen is shown when workflow state is reviewAndPrepare
              final wfState = context.read<ProtocolWorkflowBloc>().state;
              if (wfState.currentStep == WorkflowStep.reviewAndPrepare &&
                  wfState.selectedProtocolInfo != null &&
                  wfState.configuredParameters != null &&
                  wfState.assignedAssets != null) {
                context.read<ProtocolReviewBloc>().add(
                  LoadReviewData(
                    reviewData: ReviewDataBundle(
                      selectedProtocolInfo: wfState.selectedProtocolInfo!,
                      configuredParameters: wfState.configuredParameters!,
                      assignedAssets: wfState.assignedAssets!,
                      deckLayoutName: wfState.deckLayoutName,
                      uploadedDeckFile: wfState.uploadedDeckFile,
                    ),
                  ),
                );
              }
              return const Center(
                child: CircularProgressIndicator(
                  semanticsLabel: "Loading review data",
                ),
              );
            },
            ready:
                (displayData) =>
                    _buildReviewContent(context, displayData, isLoading: false),
            preparationInProgress: () {
              // Try to get displayData from a previous 'ready' state if possible
              final lastData = context.read<ProtocolReviewBloc>().state.maybeMap(
                ready: (s) => s.displayData,
                // If preparation failed, we might still have the data that was attempted
                preparationFailure: (s) => s.displayData,
                orElse: () => null,
              );
              if (lastData != null) {
                return _buildReviewContent(context, lastData, isLoading: true);
              }
              return const Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    CircularProgressIndicator(),
                    SizedBox(height: 16),
                    Text("Preparing protocol..."),
                  ],
                ),
              );
            },
            preparationSuccess:
                (preparedConfig, reviewedData) => _buildReviewContent(
                  context,
                  reviewedData,
                  isLoading: false,
                  successMessage: "Protocol Prepared! Proceeding to Start...",
                ),
            preparationFailure: (errorMessage, displayData) {
              if (displayData != null) {
                return _buildReviewContent(
                  context,
                  displayData,
                  isLoading: false,
                  errorMessage: errorMessage,
                );
              }
              return Center(
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(
                        Icons.error_outline,
                        color: Theme.of(context).colorScheme.error,
                        size: 48,
                      ),
                      const SizedBox(height: 16),
                      Text(
                        "Preparation Failed",
                        style: Theme.of(context).textTheme.headlineSmall,
                      ),
                      const SizedBox(height: 8),
                      Text(
                        errorMessage,
                        textAlign: TextAlign.center,
                        style: TextStyle(
                          color: Theme.of(context).colorScheme.error,
                        ),
                      ),
                      const SizedBox(height: 20),
                      ElevatedButton.icon(
                        icon: const Icon(Icons.refresh),
                        label: const Text("Retry Preparation"),
                        onPressed:
                            () => context.read<ProtocolReviewBloc>().add(
                              const PrepareProtocolRequested(),
                            ),
                      ),
                    ],
                  ),
                ),
              );
            },
          );
        },
      ),
    );
  }

  Widget _buildReviewContent(
    BuildContext context,
    ReviewDataBundle displayData, {
    required bool isLoading,
    String? successMessage,
    String? errorMessage,
  }) {
    final jsonEncoder = JsonEncoder.withIndent('  ');
    final theme = Theme.of(context);
    final workflowBloc = context.read<ProtocolWorkflowBloc>();

    return Stack(
      children: [
        ListView(
          // Changed from SingleChildScrollView to ListView for multiple cards
          padding: const EdgeInsets.all(16.0),
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
                      successMessage,
                      style: TextStyle(
                        color: Colors.green.shade900,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                ),
              ),
            if (errorMessage != null &&
                !isLoading) // Don't show error if also loading (e.g. retrying)
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
                      "Error During Preparation",
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

            _buildReviewSection(
              context,
              title: 'Protocol',
              content: ListTile(
                leading: Icon(
                  Icons.biotech_outlined,
                  color: theme.colorScheme.secondary,
                  size: 28,
                ),
                title: Text(
                  displayData.selectedProtocolInfo.name,
                  style: theme.textTheme.titleMedium,
                ),
                subtitle: Text(
                  displayData.selectedProtocolInfo.description ??
                      'No description',
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                ),
              ),
              onEdit: () {
                workflowBloc.add(
                  const GoToStep(
                    targetStep: WorkflowStep.protocolSelection,
                    fromReviewScreen: true,
                  ),
                );
              },
              isEditable:
                  !isLoading &&
                  successMessage ==
                      null, // Can't edit if loading or already succeeded
            ),
            _buildReviewSection(
              context,
              title: 'Parameters',
              content:
                  displayData.configuredParameters.isEmpty
                      ? const ListTile(
                        leading: Icon(Icons.tune_outlined),
                        title: Text('No parameters configured.'),
                      )
                      : _buildScrollableJsonView(
                        context,
                        jsonEncoder.convert(displayData.configuredParameters),
                      ),
              onEdit: () {
                workflowBloc.add(
                  const GoToStep(
                    targetStep: WorkflowStep.parameterConfiguration,
                    fromReviewScreen: true,
                  ),
                );
              },
              isEditable:
                  !isLoading &&
                  successMessage == null &&
                  (workflowBloc
                          .state
                          .selectedProtocolDetails
                          ?.parameters
                          .isNotEmpty ??
                      false ||
                          workflowBloc
                              .state
                              .selectedProtocolDetails
                              ?.groupedParameters
                              ?.isNotEmpty ??
                      false),
            ),
            _buildReviewSection(
              context,
              title: 'Asset Assignments',
              content:
                  displayData.assignedAssets.isEmpty
                      ? const ListTile(
                        leading: Icon(Icons.inventory_2_outlined),
                        title: Text('No assets assigned.'),
                      )
                      : Column(
                        children:
                            displayData.assignedAssets.entries.map((entry) {
                              return ListTile(
                                leading: Icon(
                                  Icons.label_important_outline_rounded,
                                  color: theme.colorScheme.onSurfaceVariant,
                                  size: 20,
                                ),
                                title: Text(
                                  entry.key,
                                  style: theme.textTheme.bodyLarge,
                                ),
                                trailing: Text(
                                  entry.value.isNotEmpty
                                      ? entry.value
                                      : "Not set",
                                  style: theme.textTheme.bodyMedium?.copyWith(
                                    fontStyle:
                                        entry.value.isNotEmpty
                                            ? FontStyle.normal
                                            : FontStyle.italic,
                                  ),
                                ),
                              );
                            }).toList(),
                      ),
              onEdit: () {
                workflowBloc.add(
                  const GoToStep(
                    targetStep: WorkflowStep.assetAssignment,
                    fromReviewScreen: true,
                  ),
                );
              },
              isEditable:
                  !isLoading &&
                  successMessage == null &&
                  (workflowBloc
                          .state
                          .selectedProtocolDetails
                          ?.assets
                          ?.isNotEmpty ??
                      false),
            ),
            _buildReviewSection(
              context,
              title: 'Deck Layout',
              content: ListTile(
                leading: Icon(
                  Icons.deck_outlined,
                  color: theme.colorScheme.secondary,
                  size: 28,
                ),
                title: Text(
                  displayData.uploadedDeckFile?.name ??
                      displayData.deckLayoutName ??
                      'No deck layout specified.',
                  style: theme.textTheme.titleMedium,
                ),
                subtitle:
                    displayData.uploadedDeckFile != null
                        ? const Text('Uploaded File')
                        : (displayData.deckLayoutName != null
                            ? const Text('Selected Existing Layout')
                            : null),
              ),
              onEdit: () {
                workflowBloc.add(
                  const GoToStep(
                    targetStep: WorkflowStep.deckConfiguration,
                    fromReviewScreen: true,
                  ),
                );
              },
              isEditable: !isLoading && successMessage == null,
            ),
            const SizedBox(height: 80),
          ],
        ),
        if (isLoading)
          Container(
            color: Colors.black.withOpacity(0.05),
            child: const Center(child: CircularProgressIndicator()),
          ),
        Align(
          alignment: Alignment.bottomCenter,
          child: Container(
            padding: const EdgeInsets.all(16.0),
            decoration: BoxDecoration(
              color: theme.scaffoldBackgroundColor,
              boxShadow: [
                BoxShadow(
                  color: theme.shadowColor.withOpacity(0.1),
                  blurRadius: 5,
                  spreadRadius: 1,
                  offset: const Offset(0, -2),
                ),
              ],
            ),
            child: ElevatedButton.icon(
              icon: const Icon(Icons.settings_applications_rounded),
              label: const Text('PREPARE PROTOCOL'),
              onPressed:
                  isLoading || successMessage != null
                      ? null
                      : () {
                        context.read<ProtocolReviewBloc>().add(
                          const PrepareProtocolRequested(),
                        );
                      },
              style: ElevatedButton.styleFrom(
                minimumSize: const Size(double.infinity, 52), // Larger button
                textStyle: theme.textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildReviewSection(
    BuildContext context, {
    required String title,
    required Widget content,
    VoidCallback? onEdit,
    bool isEditable = true,
  }) {
    final theme = Theme.of(context);
    return Card(
      margin: const EdgeInsets.symmetric(vertical: 8.0),
      elevation: 1,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: BorderSide(color: theme.dividerColor.withOpacity(0.7)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.only(
              top: 12.0,
              left: 16.0,
              right: 8.0,
              bottom: 4.0,
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  title,
                  style: theme.textTheme.titleLarge?.copyWith(
                    fontWeight: FontWeight.w500,
                  ),
                ),
                if (onEdit != null && isEditable)
                  IconButton(
                    icon: Icon(
                      Icons.edit_outlined,
                      color: theme.colorScheme.secondary,
                      size: 22,
                    ),
                    onPressed: onEdit,
                    tooltip: 'Edit $title',
                  ),
              ],
            ),
          ),
          const Divider(height: 1, indent: 16, endIndent: 16),
          Padding(
            padding: const EdgeInsets.symmetric(vertical: 8.0, horizontal: 8.0),
            child: content,
          ),
        ],
      ),
    );
  }

  Widget _buildScrollableJsonView(BuildContext context, String jsonString) {
    final theme = Theme.of(context);
    return Padding(
      padding: const EdgeInsets.symmetric(
        horizontal: 8.0,
        vertical: 8.0,
      ), // Reduced horizontal padding
      child: Container(
        constraints: const BoxConstraints(maxHeight: 180),
        decoration: BoxDecoration(
          color: theme.colorScheme.surfaceContainerHighest.withOpacity(0.2),
          borderRadius: BorderRadius.circular(8.0),
          border: Border.all(color: theme.dividerColor.withOpacity(0.5)),
        ),
        child: Scrollbar(
          // Added Scrollbar
          thumbVisibility: true,
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(12.0),
            child: Text(
              jsonString,
              style: theme.textTheme.bodyMedium?.copyWith(
                fontFamily: 'monospace',
                letterSpacing: 0.8,
                height: 1.4,
              ),
            ),
          ),
        ),
      ),
    );
  }
}
