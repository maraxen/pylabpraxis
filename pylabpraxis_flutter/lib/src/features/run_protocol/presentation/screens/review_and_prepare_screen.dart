// pylabpraxis_flutter/lib/src/features/run_protocol/presentation/screens/review_and_prepare_screen.dart
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:pylabpraxis_flutter/src/features/run_protocol/application/protocol_review_bloc/protocol_review_bloc.dart';
import 'package:pylabpraxis_flutter/src/features/run_protocol/application/protocol_workflow_bloc/protocol_workflow_bloc.dart';
import 'package:pylabpraxis_flutter/src/features/run_protocol/domain/review_data_bundle.dart'; // Assuming you have this

// Assuming ProtocolReviewState structure like:
// @freezed
// sealed class ProtocolReviewState with _$ProtocolReviewState {
//   const factory ProtocolReviewState.initial() = _Initial;
//   const factory ProtocolReviewState.loadingReviewData() = _LoadingReviewData;
//   const factory ProtocolReviewState.reviewReady(ReviewDataBundle reviewData) = _ReviewReady;
//   const factory ProtocolReviewState.preparing() = _Preparing; // Preparing for backend
//   const factory ProtocolReviewState.preparationSuccess(Map<String, dynamic> backendConfig) = _PreparationSuccess;
//   const factory ProtocolReviewState.preparationFailed(String error) = _PreparationFailed;
//   const factory ProtocolReviewState.error(String message) = _Error; // General error
// }

class ReviewAndPrepareScreen extends StatefulWidget {
  const ReviewAndPrepareScreen({super.key});

  @override
  State<ReviewAndPrepareScreen> createState() => _ReviewAndPrepareScreenState();
}

class _ReviewAndPrepareScreenState extends State<ReviewAndPrepareScreen> {
  @override
  void initState() {
    super.initState();
    final workflowState = context.read<ProtocolWorkflowBloc>().state;
    // Trigger loading of review data based on the current workflow state
    context.read<ProtocolReviewBloc>().add(
      ProtocolReviewEvent.loadReviewData(
        selectedProtocol: workflowState.selectedProtocolInfo,
        protocolDetails: workflowState.selectedProtocolDetails,
        configuredParameters: workflowState.configuredParameters,
        assignedAssets: workflowState.assignedAssets,
        deckLayoutName: workflowState.deckLayoutName,
        uploadedDeckFile: workflowState.uploadedDeckFile,
      ),
    );
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
          if (state is ProtocolReviewPreparationFailed) {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                content: Text('Preparation failed: ${state.error}'),
                backgroundColor: theme.colorScheme.error,
              ),
            );
          } else if (state is ProtocolReviewPreparationSuccess) {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                content: const Text('Protocol prepared successfully!'),
                backgroundColor: Colors.green.shade700,
              ),
            );
            // Update workflow BLoC and let it navigate
            workflowBloc.add(
              ProtocolWorkflowEvent.preparationSucceeded(state.backendConfig),
            );
          } else if (state is ProtocolReviewError) {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                content: Text('Error: ${state.message}'),
                backgroundColor: theme.colorScheme.error,
              ),
            );
          }
        },
        builder: (context, state) {
          return switch (state) {
            ProtocolReviewInitial() || ProtocolReviewLoadingReviewData() =>
              const Center(child: CircularProgressIndicator()),
            ProtocolReviewReviewReady(reviewData: final reviewData) =>
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
                              reviewData.protocolName,
                            ),
                            _buildReviewItem(
                              context,
                              'Protocol ID',
                              reviewData.protocolId,
                            ),
                            const Divider(height: 24),
                            _buildMapReviewItem(
                              context,
                              'Parameters',
                              reviewData.parameters,
                            ),
                            const Divider(height: 24),
                            _buildMapReviewItem(
                              context,
                              'Assigned Assets',
                              reviewData.assets,
                            ),
                            const Divider(height: 24),
                            _buildReviewItem(
                              context,
                              'Deck Layout',
                              reviewData.deckLayoutName ?? 'Custom',
                            ),
                            if (reviewData.deckLayoutName == null &&
                                reviewData.uploadedDeckFileName != null)
                              _buildReviewItem(
                                context,
                                'Custom Deck File',
                                reviewData.uploadedDeckFileName,
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
                        context.read<ProtocolReviewBloc>().add(
                          ProtocolReviewEvent.prepareProtocol(
                            reviewData: reviewData,
                          ), // Pass all data needed for preparation
                        );
                      },
                      child: const Text('Prepare Protocol for Run'),
                    ),
                  ],
                ),
              ),
            ProtocolReviewPreparing() => const Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  CircularProgressIndicator(),
                  SizedBox(height: 16),
                  Text('Preparing protocol...'),
                ],
              ),
            ),
            ProtocolReviewPreparationSuccess(backendConfig: final _) => Center(
              // Already handled by listener for navigation
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
            ProtocolReviewPreparationFailed(error: final error) ||
            ProtocolReviewError(message: final error) => Center(
              // Combined error display
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
                    Text('Failed: $error', textAlign: TextAlign.center),
                    const SizedBox(height: 16),
                    ElevatedButton(
                      onPressed: () {
                        final wfState =
                            context.read<ProtocolWorkflowBloc>().state;
                        context.read<ProtocolReviewBloc>().add(
                          ProtocolReviewEvent.loadReviewData(
                            selectedProtocol: wfState.selectedProtocolInfo,
                            protocolDetails: wfState.selectedProtocolDetails,
                            configuredParameters: wfState.configuredParameters,
                            assignedAssets: wfState.assignedAssets,
                            deckLayoutName: wfState.deckLayoutName,
                            uploadedDeckFile: wfState.uploadedDeckFile,
                          ),
                        );
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
