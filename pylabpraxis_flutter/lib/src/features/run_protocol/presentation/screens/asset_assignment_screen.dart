import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:pylabpraxis_flutter/src/data/models/protocol/protocol_asset.dart';
import 'package:pylabpraxis_flutter/src/features/run_protocol/application/protocol_assets_bloc/protocol_assets_bloc.dart';
import 'package:pylabpraxis_flutter/src/features/run_protocol/application/protocol_workflow_bloc/protocol_workflow_bloc.dart'; // For submitting

class AssetAssignmentScreen extends StatefulWidget {
  const AssetAssignmentScreen({super.key});

  @override
  State<AssetAssignmentScreen> createState() => _AssetAssignmentScreenState();
}

class _AssetAssignmentScreenState extends State<AssetAssignmentScreen> {
  // Use a map of TextEditingControllers to manage each TextFormField's state
  // and preserve input during rebuilds if not relying solely on BLoC state for initialValue.
  final Map<String, TextEditingController> _controllers = {};

  @override
  void initState() {
    super.initState();
    // Initialize controllers when BLoC loads assets
    // This is better done by listening to the BLoC state in BlocConsumer/BlocListener
    // For now, we assume BLoC is loaded by workflow before this screen is shown.
    final assetsBloc = context.read<ProtocolAssetsBloc>();
    if (assetsBloc.state is ProtocolAssetsLoaded) {
      _initializeControllers(
        (assetsBloc.state as ProtocolAssetsLoaded).currentAssignments,
      );
    }
  }

  void _initializeControllers(Map<String, String> assignments) {
    assignments.forEach((assetName, assignedValue) {
      _controllers[assetName] = TextEditingController(text: assignedValue);
    });
  }

  @override
  void dispose() {
    for (var controller in _controllers.values) {
      controller.dispose();
    }
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    // Fix the mapOrNull and when usage in UI components
    return Scaffold(
      body: BlocConsumer<ProtocolAssetsBloc, ProtocolAssetsState>(
        listener: (context, state) {
          if (state is _ProtocolAssetsError) {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                content: Text('Error: ${state.message}'),
                backgroundColor: theme.colorScheme.error,
              ),
            );
          } else if (state is _ProtocolAssetsLoaded) {
            // Initialize controllers when assets are loaded
            // This ensures if we navigate back and data is reloaded, controllers update.
            state.currentAssignments.forEach((assetName, assignedValue) {
              if (_controllers.containsKey(assetName)) {
                // Only update if text differs to avoid losing cursor position
                if (_controllers[assetName]!.text != assignedValue) {
                  _controllers[assetName]!.text = assignedValue;
                }
              } else {
                _controllers[assetName] = TextEditingController(
                  text: assignedValue,
                );
              }
            });
            // Inform workflow BLoC about validity
            context.read<ProtocolWorkflowBloc>().add(
              UpdateStepValidity(isValid: state.isValid),
            );
          }
        },
        builder: (context, state) {
          if (state is _ProtocolAssetsInitial) {
            return const Center(child: Text('Loading asset requirements...'));
          } else if (state is _ProtocolAssetsError) {
            return Center(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Text(
                  'Error: ${state.message}',
                  textAlign: TextAlign.center,
                ),
              ),
            );
          } else if (state is _ProtocolAssetsLoaded) {
            final requiredAssets = state.requiredAssets;
            final currentAssignments = state.currentAssignments;
            final isValid = state.isValid;

            if (requiredAssets.isEmpty) {
              // If no assets, this step is valid and should allow proceeding.
              // This should be handled by ProtocolWorkflowBloc: if no assets, skip this step.
              // For now, show a message and allow "Next" via workflow.
              WidgetsBinding.instance.addPostFrameCallback((_) {
                // Ensure build is complete
                context.read<ProtocolWorkflowBloc>().add(
                  const UpdateStepValidity(isValid: true),
                );
              });
              return Center(
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(
                        Icons.check_circle_outline_rounded,
                        size: 48,
                        color: theme.colorScheme.primary,
                      ),
                      const SizedBox(height: 16),
                      Text(
                        'No assets required for this protocol.',
                        style: theme.textTheme.titleMedium,
                      ),
                      const SizedBox(height: 8),
                      Text(
                        'You can proceed to the next step.',
                        style: theme.textTheme.bodyMedium,
                      ),
                    ],
                  ),
                ),
              );
            }
            return Column(
              children: [
                Expanded(
                  child: ListView.builder(
                    padding: const EdgeInsets.all(16.0),
                    itemCount: requiredAssets.length,
                    itemBuilder: (context, index) {
                      final asset = requiredAssets[index];
                      // Ensure controller exists for this asset
                      if (!_controllers.containsKey(asset.name)) {
                        _controllers[asset.name] = TextEditingController(
                          text: currentAssignments[asset.name] ?? '',
                        );
                      }
                      final controller = _controllers[asset.name]!;

                      bool isRequiredAndEmpty =
                          asset.required == true &&
                          controller.text.trim().isEmpty;

                      return Card(
                        elevation: 1,
                        margin: const EdgeInsets.symmetric(vertical: 8.0),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12),
                          side: BorderSide(
                            color:
                                isRequiredAndEmpty
                                    ? theme.colorScheme.error
                                    : theme.dividerColor.withAlpha(
                                      (0.7 * 255).toInt(),
                                    ),
                            width: isRequiredAndEmpty ? 1.5 : 1,
                          ),
                        ),
                        child: Padding(
                          padding: const EdgeInsets.all(16.0),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                asset.displayName ?? asset.name,
                                style: theme.textTheme.titleLarge?.copyWith(
                                  fontWeight: FontWeight.w500,
                                ),
                              ),
                              if (asset.description != null &&
                                  asset.description!.isNotEmpty)
                                Padding(
                                  padding: const EdgeInsets.only(
                                    top: 4.0,
                                    bottom: 8.0,
                                  ),
                                  child: Text(
                                    asset.description!,
                                    style: theme.textTheme.bodySmall?.copyWith(
                                      color: theme.colorScheme.onSurfaceVariant,
                                    ),
                                  ),
                                ),
                              Row(
                                children: [
                                  Chip(
                                    avatar: Icon(
                                      Icons.category_outlined,
                                      size: 16,
                                      color:
                                          theme
                                              .colorScheme
                                              .onSecondaryContainer,
                                    ),
                                    label: Text(
                                      asset.type,
                                      style: theme.textTheme.labelSmall,
                                    ),
                                    backgroundColor: theme
                                        .colorScheme
                                        .secondaryContainer
                                        .withAlpha((0.7 * 255).toInt()),
                                    padding: const EdgeInsets.symmetric(
                                      horizontal: 8,
                                      vertical: 2,
                                    ),
                                  ),
                                  const SizedBox(width: 8),
                                  if (asset.required == true)
                                    Chip(
                                      avatar: Icon(
                                        Icons.star_rounded,
                                        size: 16,
                                        color:
                                            theme.colorScheme.onErrorContainer,
                                      ),
                                      label: Text(
                                        'Required',
                                        style: theme.textTheme.labelSmall,
                                      ),
                                      backgroundColor: theme
                                          .colorScheme
                                          .errorContainer
                                          .withAlpha((0.7 * 255).toInt()),
                                      padding: const EdgeInsets.symmetric(
                                        horizontal: 8,
                                        vertical: 2,
                                      ),
                                    ),
                                ],
                              ),
                              const SizedBox(height: 16),
                              TextFormField(
                                controller: controller,
                                decoration: InputDecoration(
                                  labelText:
                                      'Assign ID/Name for "${asset.name}"',
                                  border: const OutlineInputBorder(),
                                  errorText:
                                      isRequiredAndEmpty
                                          ? 'This asset is required.'
                                          : null,
                                ),
                                onChanged: (value) {
                                  context.read<ProtocolAssetsBloc>().add(
                                    AssetAssignmentChanged(
                                      assetName: asset.name,
                                      assignedValue: value,
                                    ),
                                  );
                                },
                                // BLoC handles overall form validity, TextFormField validator can provide immediate field feedback
                                // validator: (value) {
                                //   if (asset.required == true && (value == null || value.trim().isEmpty)) {
                                //     return 'This asset is required.';
                                //   }
                                //   return null;
                                // },
                                // autovalidateMode: AutovalidateMode.onUserInteraction,
                              ),
                            ],
                          ),
                        ),
                      );
                    },
                  ),
                ),
                // "Next" button is part of the global RunProtocolWorkflowScreen
              ],
            );
          }

          // Default loading state
          return const Center(child: CircularProgressIndicator());
        },
      ),
    );
  }
}
