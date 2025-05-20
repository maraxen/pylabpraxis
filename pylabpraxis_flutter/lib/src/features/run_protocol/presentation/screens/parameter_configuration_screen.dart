// pylabpraxis_flutter/lib/src/features/run_protocol/presentation/screens/parameter_configuration_screen.dart
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:pylabpraxis_flutter/src/data/models/protocol/parameter_config.dart';
import 'package:pylabpraxis_flutter/src/features/run_protocol/application/protocol_parameters_bloc/protocol_parameters_bloc.dart';
import 'package:pylabpraxis_flutter/src/features/run_protocol/application/protocol_workflow_bloc/protocol_workflow_bloc.dart';
import 'package:pylabpraxis_flutter/src/features/run_protocol/presentation/widgets/dialogs/basic_parameter_edit_dialog.dart'; // Updated to BasicParameterEditScreen
import 'package:pylabpraxis_flutter/src/features/run_protocol/presentation/widgets/dialogs/string_parameter_edit_screen.dart';
import 'package:pylabpraxis_flutter/src/features/run_protocol/presentation/widgets/dialogs/array_parameter_edit_dialog.dart';
import 'package:pylabpraxis_flutter/src/features/run_protocol/presentation/widgets/dialogs/dictionary_parameter_edit_screen.dart';
import 'package:pylabpraxis_flutter/src/data/models/protocol/protocol_details.dart';
// Assuming ParameterDefinition is no longer a separate class for this screen,
// and dialogs will take parameterPath and ParameterConfig.

class ParameterConfigurationScreen extends StatefulWidget {
  const ParameterConfigurationScreen({super.key});

  @override
  State<ParameterConfigurationScreen> createState() =>
      _ParameterConfigurationScreenState();
}

class _ParameterConfigurationScreenState
    extends State<ParameterConfigurationScreen> {
  @override
  void initState() {
    super.initState();
    final workflowState = context.read<ProtocolWorkflowBloc>().state;
    final protocolDetails = workflowState.selectedProtocolDetails;

    if (protocolDetails != null) {
      context.read<ProtocolParametersBloc>().add(
        ProtocolParametersEvent.loadProtocolParameters(
          protocolDetails: protocolDetails,
          existingConfiguredParameters: workflowState.configuredParameters,
        ),
      );
    } else {
      // Handle error: protocol details not available.
      // This might involve showing an error in this screen or relying on the BLoC to emit an error state.
      // For example, dispatch an event to ProtocolParametersBloc to report the issue.
      // context.read<ProtocolParametersBloc>().add(const ProtocolParametersEvent.errorOccurred(message: "Protocol details missing for parameter configuration."));
    }
  }

  // paramData is ParameterConfig from backend model
  void _showEditDialog(
    BuildContext context,
    String paramNameKey,
    ParameterDefinition paramData,
    dynamic currentValue,
  ) {
    final parametersBloc = context.read<ProtocolParametersBloc>();

    Widget dialogContent;

    // Ensure your ParameterConfig model has a 'type' field and 'constraints.choices'
    if (paramData.config.type == 'array') {
      dialogContent = ArrayParameterEditDialog(
        parameterPath: paramNameKey,
        parameterDefinition:
            paramData, // Pass ParameterConfig as parameterDefinition or similar
        currentValue:
            currentValue as List<dynamic>? ??
            paramData.defaultValue as List<dynamic>? ??
            [],
        onChanged: (newValue) {
          parametersBloc.add(
            ProtocolParametersEvent.parameterValueChanged(
              parameterPath: paramNameKey,
              value: newValue,
            ),
          );
        },
      );
    } else if (paramData.config.type == 'object' ||
        paramData.config.type == 'dict' ||
        paramData.config.type == 'dictionary') {
      dialogContent = DictionaryParameterEditScreen(
        parameterPath: paramNameKey,
        parameterDefinition: paramData,
        currentValue:
            currentValue as Map<String, dynamic>? ??
            paramData.defaultValue as Map<String, dynamic>? ??
            {},
        onChanged: (newValue) {
          parametersBloc.add(
            ProtocolParametersEvent.parameterValueChanged(
              parameterPath: paramNameKey,
              value: newValue,
            ),
          );
        },
      );
    } else if (paramData.config.type == 'string' &&
        (paramData.config.constraints?.choices?.isEmpty ?? true)) {
      dialogContent = StringParameterEditScreen(
        parameterPath: paramNameKey,
        parameterDefinition: paramData,
        currentValue:
            currentValue as String? ?? paramData.defaultValue as String? ?? '',
        onChanged: (newValue) {
          parametersBloc.add(
            ProtocolParametersEvent.parameterValueChanged(
              parameterPath: paramNameKey,
              value: newValue,
            ),
          );
        },
      );
    } else {
      // Basic types (integer, number, boolean, string with choices)
      // Using BasicParameterEditScreen as per user's provided code
      // It expects `parameterDefinition` which should be compatible with `ParameterConfig`
      // and `parameterPath`.
      // The BasicParameterEditScreen itself will need to use `widget.parameterConfig.displayName` etc.
      // instead of `widget.parameterDefinition.name` if `ParameterConfig` doesn't have `name`.
      // For now, assuming BasicParameterEditScreen is adapted or ParameterConfig is sufficient.
      // The key is that `paramNameKey` is the path/name.

      // Let's assume BasicParameterEditScreen is updated to take parameterConfig
      // and parameterPath, and internally uses parameterPath for the name.
      // If BasicParameterEditScreen strictly needs a 'ParameterDefinition' object with 'name' field,
      // you'd construct it here.
      // For now, we pass `paramData` as `parameterDefinition` and `paramNameKey` as `parameterPath`.
      // The internal implementation of BasicParameterEditScreen must align.
      // The user provided BasicParameterEditScreen takes `parameterDefinition` and `parameterPath`.
      // `parameterDefinition` in that context seems to be the `ParameterConfig` object itself,
      // and it uses `widget.parameterDefinition.displayName`, `widget.parameterDefinition.config.type`.
      // This implies `ParameterConfig` has `displayName` and a nested `config` object.
      // This contradicts `protocolDetails.parameters` being `Map<String, ParameterConfig>`.

      // Re-evaluating based on user's BasicParameterEditScreen:
      // It takes `ParameterDefinition parameterDefinition` and `String parameterPath`.
      // Inside it uses `widget.parameterDefinition.config.type`, `.displayName`, `.name`.
      // This means the `ParameterDefinition` class used by the dialog has `name`, `displayName`, and `config` fields.
      // `protocolDetails.parameters` is `Map<String, ParameterConfig>`, where `ParameterConfig` is the `config` part.

      // We need to construct the `ParameterDefinition` object for the dialog.
      // Assuming `ParameterConfig` (i.e., `paramData`) has `displayName`, `description`, `type`, `constraints`.
      // The `name` is `paramNameKey`.

      // This requires a `ParameterDefinition` class that matches the dialog's expectation.
      // For now, I will assume the dialogs are flexible or will be adapted.
      // The most straightforward is if dialogs take `parameterPath` and `parameterConfig`.
      // If BasicParameterEditScreen strictly takes `ParameterDefinition parameterDefinition`,
      // and that class has `name`, `displayName`, `config` (where config is `ParameterConfig`),
      // then you'd do:
      // final uiDefinition = ParameterDefinition(name: paramNameKey, displayName: paramData.displayName, config: paramData);
      // dialogContent = BasicParameterEditScreen(parameterPath: paramNameKey, parameterDefinition: uiDefinition, ...);
      // For simplicity, I'll assume dialogs can work with path and config directly.
      // The user's BasicParameterEditScreen takes `parameterPath` and `parameterDefinition`.
      // Let's assume `paramData` IS the `parameterDefinition` and `paramNameKey` is `parameterPath`.
      // The dialog then needs to use `widget.parameterPath` for name, and `widget.parameterDefinition` for other props.

      dialogContent = BasicParameterEditScreen(
        // User provided this screen
        parameterPath: paramNameKey, // This is the name/key
        parameterDefinition:
            paramData, // This is ParameterConfig, which BasicParameterEditScreen uses
        currentValue: currentValue ?? paramData.defaultValue,
        // onChanged is handled internally by BasicParameterEditScreen by dispatching events
      );
    }

    showDialog(
      context: context,
      builder: (BuildContext dialogContext) {
        return BlocProvider.value(value: parametersBloc, child: dialogContent);
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Scaffold(
      appBar: AppBar(
        title: const Text('Configure Parameters'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () {
            context.read<ProtocolWorkflowBloc>().add(
              const ProtocolWorkflowEvent.goToPreviousStep(),
            ); // Corrected
          },
        ),
      ),
      body: BlocConsumer<ProtocolParametersBloc, ProtocolParametersState>(
        listener: (context, state) {
          if (state is ProtocolParametersError) {
            // Use public factory name
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                content: Text('Parameter error: ${state.message}'),
                backgroundColor: theme.colorScheme.error,
              ),
            );
          } else if (state is ProtocolParametersLoaded) {
            // Use public factory name
            context.read<ProtocolWorkflowBloc>().add(
              ProtocolWorkflowEvent.updateStepValidity(
                isValid: state.isFormValid,
              ),
            );
          }
        },
        builder: (context, state) {
          return switch (state) {
            ProtocolParametersInitial() => const Center(
              child: Text('Initializing parameters...'),
            ), // Use public factory name
            ProtocolParametersLoading() => const Center(
              child: CircularProgressIndicator(),
            ), // Use public factory name
            ProtocolParametersLoaded(
              // Use public factory name and destructure
              protocolDetails: final protocolDetails,
              formState: final formState,
              isFormValid: final isFormValid,
              // requiredParametersCompletionPercent is available if needed
            ) =>
              () {
                // Parameters are a map where key is name, value is ParameterConfig
                final parametersMap = protocolDetails.parameters;
                final currentValues = formState.values;
                final validationErrors = formState.errors;

                if (parametersMap.isEmpty) {
                  WidgetsBinding.instance.addPostFrameCallback((_) {
                    context.read<ProtocolWorkflowBloc>().add(
                      const ProtocolWorkflowEvent.updateStepValidity(
                        isValid: true,
                      ),
                    );
                    context.read<ProtocolWorkflowBloc>().add(
                      ProtocolWorkflowEvent.parametersSubmitted(
                        parameters: const {},
                      ), // Corrected
                    );
                  });
                  return Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        const Icon(
                          Icons.settings_applications_outlined,
                          size: 48,
                          color: Colors.grey,
                        ),
                        const SizedBox(height: 16),
                        const Text(
                          'No parameters to configure for this protocol.',
                        ),
                      ],
                    ),
                  );
                }
                return Column(
                  children: [
                    Expanded(
                      child: ListView.builder(
                        padding: const EdgeInsets.all(8.0),
                        itemCount: parametersMap.length,
                        itemBuilder: (context, index) {
                          final paramNameKey = parametersMap.keys.elementAt(
                            index,
                          );
                          final paramConfigData = parametersMap.values
                              .elementAt(index); // This is ParameterConfig

                          final currentValue = currentValues[paramNameKey];
                          final errorText = validationErrors[paramNameKey];

                          return Card(
                            margin: const EdgeInsets.symmetric(
                              horizontal: 8,
                              vertical: 4,
                            ),
                            child: ListTile(
                              title: Text(
                                paramConfigData.displayName,
                                style: theme.textTheme.titleMedium,
                              ),
                              subtitle: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(
                                    'Current: ${currentValue ?? "Not set"} ${paramConfigData.units ?? ""}',
                                    style: theme.textTheme.bodySmall,
                                  ),
                                  if (paramConfigData.description != null &&
                                      paramConfigData.description!.isNotEmpty)
                                    Padding(
                                      padding: const EdgeInsets.only(top: 4.0),
                                      child: Text(
                                        paramConfigData.description!,
                                        style: theme.textTheme.labelSmall,
                                        maxLines: 2,
                                        overflow: TextOverflow.ellipsis,
                                      ),
                                    ),
                                  if (errorText != null && errorText.isNotEmpty)
                                    Padding(
                                      padding: const EdgeInsets.only(top: 4.0),
                                      child: Text(
                                        errorText,
                                        style: TextStyle(
                                          color: theme.colorScheme.error,
                                          fontSize: 12,
                                        ),
                                      ),
                                    ),
                                ],
                              ),
                              trailing: Icon(
                                Icons.edit_outlined,
                                color: theme.colorScheme.primary,
                              ),
                              onTap:
                                  () => _showEditDialog(
                                    context,
                                    paramNameKey,
                                    paramConfigData,
                                    currentValue,
                                  ),
                            ),
                          );
                        },
                      ),
                    ),
                    Padding(
                      padding: const EdgeInsets.all(16.0),
                      child: ElevatedButton(
                        style: ElevatedButton.styleFrom(
                          minimumSize: const Size(double.infinity, 48),
                        ),
                        onPressed:
                            isFormValid
                                ? () {
                                  context.read<ProtocolWorkflowBloc>().add(
                                    ProtocolWorkflowEvent.parametersSubmitted(
                                      // Corrected
                                      parameters: currentValues,
                                    ),
                                  );
                                }
                                : null,
                        child: const Text('Confirm Parameters & Next'),
                      ),
                    ),
                  ],
                );
              }(),
            ProtocolParametersError(message: final message) => Center(
              // Use public factory name
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
                      'Error configuring parameters: $message',
                      textAlign: TextAlign.center,
                    ),
                    const SizedBox(height: 16),
                    ElevatedButton(
                      onPressed: () {
                        final wfState =
                            context.read<ProtocolWorkflowBloc>().state;
                        final details = wfState.selectedProtocolDetails;
                        if (details != null) {
                          context.read<ProtocolParametersBloc>().add(
                            ProtocolParametersEvent.loadProtocolParameters(
                              // Corrected
                              protocolDetails: details,
                              existingConfiguredParameters:
                                  wfState.configuredParameters,
                            ),
                          );
                        }
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
