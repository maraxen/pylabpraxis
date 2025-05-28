// praxis_lab_management/lib/src/features/run_protocol/presentation/screens/review_and_prepare_screen.dart
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:praxis_lab_management/src/features/run_protocol/application/protocol_review_bloc/protocol_review_bloc.dart';
import 'package:praxis_lab_management/src/features/run_protocol/application/protocol_workflow_bloc/protocol_workflow_bloc.dart';
import 'package:praxis_lab_management/src/features/run_protocol/domain/review_data_bundle.dart';
// For ProtocolInfo
// For PlatformFile if used in ProtocolWorkflowState and ReviewDataBundle

class ReviewAndPrepareScreen extends StatefulWidget {
  const ReviewAndPrepareScreen({super.key});

  @override
  State<ReviewAndPrepareScreen> createState() => _ReviewAndPrepareScreenState();
}

class _ReviewAndPrepareScreenState extends State<ReviewAndPrepareScreen> {
  // Helper method to create ReviewDataBundle safely
  ReviewDataBundle? _createReviewDataBundle(
    ProtocolWorkflowState workflowState,
  ) {
    final protocolInfo = workflowState.selectedProtocolInfo;
    final configuredParams = workflowState.configuredParameters;
    final assignedAssets = workflowState.assignedAssets;

    // It's crucial that these are non-null by this point in the workflow.
    // If they can be null, the workflow or this screen needs to handle that explicitly.
    if (protocolInfo == null) {
      debugPrint(
        'ReviewAndPrepareScreen: selectedProtocolInfo is null in workflowState.',
      );
      return null;
    }
    if (configuredParams == null) {
      debugPrint(
        'ReviewAndPrepareScreen: configuredParameters is null in workflowState.',
      );
      return null;
    }
    if (assignedAssets == null) {
      debugPrint(
        'ReviewAndPrepareScreen: assignedAssets is null in workflowState.',
      );
      return null;
    }

    return ReviewDataBundle(
      selectedProtocolInfo: protocolInfo,
      configuredParameters: configuredParams,
      assignedAssets: assignedAssets,
      deckLayoutName: workflowState.deckLayoutName,
      uploadedDeckFile: workflowState.uploadedDeckFile,
    );
  }

  @override
  void initState() {
    super.initState();
    final workflowState = context.read<ProtocolWorkflowBloc>().state;
    final reviewData = _createReviewDataBundle(workflowState);

    if (reviewData != null) {
      context.read<ProtocolReviewBloc>().add(
        ProtocolReviewEvent.loadReviewData(reviewData: reviewData),
      );
    } else {
      // Dispatch an error or handle UI for missing critical data
      // For example, you could add an error state to ProtocolReviewBloc
      // or show a SnackBar here and pop the screen.
      // For now, assuming ReviewBloc will handle it or stay in initial.
      WidgetsBinding.instance.addPostFrameCallback((_) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text(
                'Critical data for review is missing. Please go back and complete previous steps.',
              ),
              backgroundColor: Colors.red,
            ),
          );
          // Optionally navigate back if appropriate
          // Navigator.of(context).pop();
        }
      });
    }
  }

  Widget _buildReviewItem(
    BuildContext context,
    String title,
    String? value, {
    bool isFile = false,
  }) {
    final theme = Theme.of(context);
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: theme.textTheme.titleSmall?.copyWith(
              color: theme.colorScheme.onSurfaceVariant,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            value == null || value.isEmpty
                ? (isFile ? 'No file uploaded' : 'Not set')
                : value,
            style: theme.textTheme.bodyLarge,
          ),
        ],
      ),
    );
  }

  Widget _buildMapReviewItem(
    BuildContext context,
    String title,
    Map<String, dynamic>? dataMap,
  ) {
    final theme = Theme.of(context);
    if (dataMap == null || dataMap.isEmpty) {
      return _buildReviewItem(context, title, 'None');
    }
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: theme.textTheme.titleSmall?.copyWith(
              color: theme.colorScheme.onSurfaceVariant,
            ),
          ),
          const SizedBox(height: 4),
          Card(
            elevation: 0,
            shape: RoundedRectangleBorder(
              side: BorderSide(color: theme.dividerColor),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Padding(
              padding: const EdgeInsets.all(8.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children:
                    dataMap.entries.map((entry) {
                      return Padding(
                        padding: const EdgeInsets.symmetric(vertical: 2.0),
                        child: Row(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Expanded(
                              flex: 2,
                              child: Text(
                                '${entry.key}:',
                                style: theme.textTheme.bodyMedium?.copyWith(
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                            ),
                            Expanded(
                              flex: 3,
                              child: Text(
                                entry.value.toString(),
                                style: theme.textTheme.bodyMedium,
                              ),
                            ),
                          ],
                        ),
                      );
                    }).toList(),
              ),
            ),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final workflowBloc = context.read<ProtocolWorkflowBloc>();

    return Scaffold(
      appBar: AppBar(
        title: const Text('Review and Prepare'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () {
            workflowBloc.add(const ProtocolWorkflowEvent.goToPreviousStep());
          },
        ),
      ),
      body: BlocConsumer<ProtocolReviewBloc, ProtocolReviewState>(
        listener: (context, state) {
          if (state is ProtocolPreparationFailure) {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                content: Text('Preparation failed: ${state.error}'),
                backgroundColor: theme.colorScheme.error,
              ),
            );
          } else if (state is ProtocolPreparationSuccess) {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                content: const Text('Protocol prepared successfully!'),
                backgroundColor: Colors.green.shade700,
              ),
            );
            workflowBloc.add(
              ProtocolWorkflowEvent.protocolPrepared(
                preparedConfig:
                    state.preparedConfig, // Access correct field name
              ),
            );
          }
        },
        builder: (context, state) {
          return switch (state) {
            ProtocolReviewInitial() => const Center(
              child: Text(
                "Loading review data... If this persists, critical data might be missing.",
              ), // More informative
            ),
            // Correct destructuring based on ProtocolReviewState.ready field name
            ProtocolReviewReady(displayData: final reviewData) =>
              SingleChildScrollView(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Please review your protocol configuration:',
                      style: theme.textTheme.headlineSmall,
                    ),
                    const SizedBox(height: 16),
                    Card(
                      child: Padding(
                        padding: const EdgeInsets.all(16.0),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            _buildReviewItem(
                              context,
                              'Protocol Name',
                              reviewData
                                  .selectedProtocolInfo
                                  .name, // Corrected: use destructured reviewData
                            ),
                            _buildReviewItem(
                              context,
                              'Protocol ID',
                              reviewData
                                  .selectedProtocolInfo
                                  .name, // TODO: include ID
                            ),
                            const Divider(height: 24),
                            _buildMapReviewItem(
                              context,
                              'Parameters',
                              reviewData.configuredParameters,
                            ),
                            const Divider(height: 24),
                            _buildMapReviewItem(
                              context,
                              'Assigned Assets',
                              reviewData.assignedAssets,
                            ),
                            const Divider(height: 24),
                            _buildReviewItem(
                              context,
                              'Deck Layout',
                              reviewData.deckLayoutName ?? 'Custom',
                            ),
                            if (reviewData.deckLayoutName == null &&
                                reviewData.uploadedDeckFile != null)
                              _buildReviewItem(
                                context,
                                'Custom Deck File',
                                reviewData.uploadedDeckFile?.name,
                                isFile: true,
                              ),
                          ],
                        ),
                      ),
                    ),
                    const SizedBox(height: 24),
                    ElevatedButton(
                      style: ElevatedButton.styleFrom(
                        minimumSize: const Size(double.infinity, 48),
                      ),
                      onPressed: () {
                        // Ensure prepareProtocol event exists and is used correctly
                        context.read<ProtocolReviewBloc>().add(
                          ProtocolReviewEvent.prepareProtocolRequested(),
                        );
                      },
                      child: const Text('Prepare Protocol for Run'),
                    ),
                  ],
                ),
              ),
            // Correct destructuring if `reviewData` is a field of this state
            ProtocolPreparationInProgress(
              reviewData: final currentReviewData,
            ) =>
              Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    CircularProgressIndicator(),
                    SizedBox(height: 16),
                    Text(
                      'Preparing protocol for "${currentReviewData.selectedProtocolInfo.name}"...',
                    ),
                  ],
                ),
              ),
            // Correct destructuring based on ProtocolReviewState.preparationSuccess field names
            ProtocolPreparationSuccess(
              preparedConfig: final _,
              reviewedData: final __,
            ) =>
              Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(
                      Icons.check_circle,
                      color: Colors.green.shade700,
                      size: 48,
                    ),
                    const SizedBox(height: 16),
                    const Text('Protocol Prepared Successfully!'),
                    const SizedBox(height: 8),
                    const Text('Proceeding to start...'),
                  ],
                ),
              ),
            // Correct destructuring based on ProtocolReviewState.preparationFailure field names
            ProtocolPreparationFailure(
              error: final error,
              displayData: final reviewDataForRetry,
            ) =>
              Center(
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
                        'Failed to prepare protocol: $error',
                        textAlign: TextAlign.center,
                      ),
                      const SizedBox(height: 16),
                      ElevatedButton(
                        onPressed: () {
                          final wfState =
                              context.read<ProtocolWorkflowBloc>().state;
                          // Use the helper to reconstruct the bundle for retry
                          final retryBundle = _createReviewDataBundle(wfState);
                          if (retryBundle != null) {
                            context.read<ProtocolReviewBloc>().add(
                              ProtocolReviewEvent.loadReviewData(
                                reviewData: retryBundle,
                              ),
                            );
                          } else if (reviewDataForRetry != null) {
                            // Fallback to using displayData from the failure state if available
                            context.read<ProtocolReviewBloc>().add(
                              ProtocolReviewEvent.loadReviewData(
                                reviewData: reviewDataForRetry,
                              ),
                            );
                          } else {
                            ScaffoldMessenger.of(context).showSnackBar(
                              SnackBar(
                                content: Text(
                                  'Cannot retry: essential data for review is missing.',
                                ),
                                backgroundColor: theme.colorScheme.error,
                              ),
                            );
                          }
                        },
                        child: const Text('Retry Loading Review Data'),
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
