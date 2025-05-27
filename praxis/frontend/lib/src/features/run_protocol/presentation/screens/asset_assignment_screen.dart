// pylabpraxis_flutter/lib/src/features/run_protocol/presentation/screens/asset_assignment_screen.dart
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:pylabpraxis_flutter/src/features/run_protocol/application/protocol_assets_bloc/protocol_assets_bloc.dart';
import 'package:pylabpraxis_flutter/src/features/run_protocol/application/protocol_workflow_bloc/protocol_workflow_bloc.dart'; // For submitting and UpdateStepValidity

class AssetAssignmentScreen extends StatefulWidget {
  const AssetAssignmentScreen({super.key});

  @override
  State<AssetAssignmentScreen> createState() => _AssetAssignmentScreenState();
}

class _AssetAssignmentScreenState extends State<AssetAssignmentScreen> {
  final Map<String, TextEditingController> _controllers = {};

  @override
  void initState() {
    super.initState();
    final assetsBloc = context.read<ProtocolAssetsBloc>();
    // Initialize controllers based on the current state if it's already loaded.
    // This handles cases where the BLoC might have loaded data before this widget's initState.
    final currentState = assetsBloc.state;
    if (currentState is ProtocolAssetsLoaded) {
      _initializeControllers(currentState.currentAssignments);
    }
  }

  void _initializeControllers(Map<String, String> assignments) {
    assignments.forEach((assetName, assignedValue) {
      if (_controllers.containsKey(assetName)) {
        _controllers[assetName]!.text = assignedValue;
      } else {
        _controllers[assetName] = TextEditingController(text: assignedValue);
      }
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

    return Scaffold(
      body: BlocConsumer<ProtocolAssetsBloc, ProtocolAssetsState>(
        listener: (context, state) {
          // Using Dart's pattern matching (if-case or switch) for listener logic
          if (state is ProtocolAssetsLoaded) {
            final loadedState = state; // Already typed
            // Initialize or update controllers when assets are loaded
            loadedState.currentAssignments.forEach((assetName, assignedValue) {
              if (_controllers.containsKey(assetName)) {
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
              ProtocolWorkflowEvent.updateStepValidity(
                isValid: loadedState.isValid,
              ),
            );
          } else if (state is ProtocolAssetsError) {
            final errorState = state; // Already typed
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                content: Text('Error: ${errorState.message}'),
                backgroundColor: theme.colorScheme.error,
              ),
            );
          }
          // No action needed for ProtocolAssetsInitial in the listener for this example
        },
        builder: (context, state) {
          // Using Dart's switch expression for pattern matching in the builder
          return switch (state) {
            ProtocolAssetsInitial() => const Center(
              child: Text('Loading asset requirements...'),
            ),
            ProtocolAssetsLoaded(
              requiredAssets: final requiredAssets,
              currentAssignments: final currentAssignments,
            ) =>
              () {
                if (requiredAssets.isEmpty) {
                  WidgetsBinding.instance.addPostFrameCallback((_) {
                    context.read<ProtocolWorkflowBloc>().add(
                      const ProtocolWorkflowEvent.updateStepValidity(
                        isValid: true,
                      ),
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
                          if (!_controllers.containsKey(asset.name)) {
                            _controllers[asset.name] = TextEditingController(
                              text: currentAssignments[asset.name] ?? '',
                            );
                          }
                          final controller = _controllers[asset.name]!;
                          final bool isActuallyRequired = asset.required;
                          bool isRequiredAndEmpty =
                              isActuallyRequired &&
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
                                          (0.7 * 255).round(),
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
                                        style: theme.textTheme.bodySmall
                                            ?.copyWith(
                                              color:
                                                  theme
                                                      .colorScheme
                                                      .onSurfaceVariant,
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
                                            .withAlpha((0.7 * 255).round()),
                                        padding: const EdgeInsets.symmetric(
                                          horizontal: 8,
                                          vertical: 2,
                                        ),
                                      ),
                                      const SizedBox(width: 8),
                                      if (isActuallyRequired)
                                        Chip(
                                          avatar: Icon(
                                            Icons.star_rounded,
                                            size: 16,
                                            color:
                                                theme
                                                    .colorScheme
                                                    .onErrorContainer,
                                          ),
                                          label: Text(
                                            'Required',
                                            style: theme.textTheme.labelSmall,
                                          ),
                                          backgroundColor: theme
                                              .colorScheme
                                              .errorContainer
                                              .withAlpha((0.7 * 255).round()),
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
                                        ProtocolAssetsEvent.assetAssignmentChanged(
                                          assetName: asset.name,
                                          assignedValue: value,
                                        ),
                                      );
                                    },
                                  ),
                                ],
                              ),
                            ),
                          );
                        },
                      ),
                    ),
                  ],
                );
              }(), // Immediately invoke the returned function from the loaded case
            ProtocolAssetsError(message: final message) => Center(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Text(
                      'Error loading assets: $message',
                      textAlign: TextAlign.center,
                      style: TextStyle(color: theme.colorScheme.error),
                    ),
                    const SizedBox(height: 16),
                    ElevatedButton(
                      onPressed: () {
                        context.read<ProtocolAssetsBloc>().add(
                          const ProtocolAssetsEvent.loadRequested(),
                        );
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
