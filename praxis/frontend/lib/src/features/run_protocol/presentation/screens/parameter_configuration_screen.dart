// pylabpraxis_flutter/lib/src/features/run_protocol/presentation/screens/parameter_configuration_screen.dart
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:pylabpraxis_flutter/src/data/models/protocol/parameter_config.dart';
import 'package:pylabpraxis_flutter/src/features/run_protocol/application/protocol_parameters_bloc/protocol_parameters_bloc.dart';
import 'package:pylabpraxis_flutter/src/features/run_protocol/application/protocol_workflow_bloc/protocol_workflow_bloc.dart';
import 'package:pylabpraxis_flutter/src/features/run_protocol/presentation/widgets/dialogs/basic_parameter_edit_dialog.dart';
import 'package:pylabpraxis_flutter/src/features/run_protocol/presentation/widgets/dialogs/string_parameter_edit_screen.dart';
import 'package:pylabpraxis_flutter/src/features/run_protocol/presentation/widgets/dialogs/array_parameter_edit_dialog.dart';
import 'package:pylabpraxis_flutter/src/features/run_protocol/presentation/widgets/dialogs/dictionary_parameter_edit_screen.dart';

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
      // context.read<ProtocolParametersBloc>().add(const ProtocolParametersEvent.errorOccurred(message: "Protocol details missing for parameter configuration."));
    }
  }

  void _showEditDialog(
    BuildContext context,
    String paramNameKey,
    ParameterDefinition paramData,
    dynamic currentValue,
  ) {
    final parametersBloc = context.read<ProtocolParametersBloc>();
    Widget dialogContent;

    if (paramData.config.type == 'array') {
      dialogContent = ArrayParameterEditDialog(
        parameterPath: paramNameKey,
        parameterDefinition: paramData,
        // Assuming ArrayParameterEditDialog is updated to not require currentValue and onChanged directly,
        // and will interact with ProtocolParametersBloc for state.
      );
    } else if (paramData.config.type == 'object' ||
        paramData.config.type == 'dict' ||
        paramData.config.type == 'dictionary') {
      dialogContent = DictionaryParameterEditScreen(
        parameterPath: paramNameKey,
        parameterDefinition: paramData,
        // Assuming DictionaryParameterEditScreen is updated similarly.
      );
    } else if (paramData.config.type == 'string' &&
        (paramData.config.constraints?.array?.isEmpty ?? true)) {
      // choices -> array
      dialogContent = StringParameterEditScreen(
        parameterPath: paramNameKey,
        parameterDefinition: paramData,
        currentValue: // currentValue was not flagged as an error for StringParameterEditScreen
            currentValue as String? ?? paramData.defaultValue as String? ?? '',
        // Assuming StringParameterEditScreen is updated to not require onChanged.
      );
    } else {
      dialogContent = BasicParameterEditScreen(
        parameterPath: paramNameKey,
        parameterDefinition: paramData,
        currentValue: currentValue ?? paramData.defaultValue,
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
            );
          },
        ),
      ),
      body: BlocConsumer<ProtocolParametersBloc, ProtocolParametersState>(
        listener: (context, state) {
          // Use public factory names for type checks, as intended by Freezed
          if (state is ProtocolParametersError) {
            // Using public factory name
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                content: Text('Parameter error: ${state.message}'),
                backgroundColor: theme.colorScheme.error,
              ),
            );
          } else if (state is ProtocolParametersLoaded) {
            // Using public factory name
            context.read<ProtocolWorkflowBloc>().add(
              ProtocolWorkflowEvent.updateStepValidity(
                isValid: state.isFormValid,
              ),
            );
          }
        },
        builder: (context, state) {
          // Use public factory names for switch patterns, as intended by Freezed
          return switch (state) {
            ProtocolParametersInitial() => const Center(
              // Using public factory name
              child: Text('Initializing parameters...'),
            ),
            ProtocolParametersLoading() => const Center(
              // Using public factory name
              child: CircularProgressIndicator(),
            ),
            ProtocolParametersLoaded(
              protocolDetails: final protocolDetails,
              formState: final formState, // This is RichFormState
              isFormValid: final isFormValid,
              requiredParametersCompletionPercent: final _,
            ) =>
              () {
                final parametersMap = protocolDetails.parameters;

                // Correctly extract currentValues from formState.parameterStates
                final Map<String, dynamic> currentValues = formState
                    .parameterStates
                    .map(
                      (key, paramState) =>
                          MapEntry(key, paramState.currentValue),
                    );

                // Correctly extract validationErrors from formState.parameterStates
                final Map<String, String?> validationErrors = formState
                    .parameterStates
                    .map(
                      (key, paramState) =>
                          MapEntry(key, paramState.validationError),
                    );

                if (parametersMap.isEmpty) {
                  WidgetsBinding.instance.addPostFrameCallback((_) {
                    context.read<ProtocolWorkflowBloc>().add(
                      const ProtocolWorkflowEvent.updateStepValidity(
                        isValid: true,
                      ),
                    );
                    // Ensure parametersSubmitted receives the correct currentValues map
                    context.read<ProtocolWorkflowBloc>().add(
                      ProtocolWorkflowEvent.parametersSubmitted(
                        parameters: currentValues,
                      ), // currentValues is now correctly structured
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
                        itemCount:
                            parametersMap
                                .length, // This should be formState.parameterStates.length if grouped parameters are flattened into parameterStates
                        // Or, if parametersMap from protocolDetails is the definitive list of what *can* be configured:
                        // itemCount: parametersMap.length,
                        itemBuilder: (context, index) {
                          // Ensure we are iterating over the keys that exist in formState.parameterStates
                          // If parametersMap is the source of truth for UI listing:
                          final paramNameKeyFromDetails = parametersMap.keys
                              .elementAt(index);
                          final paramConfigData = parametersMap.values
                              .elementAt(index);

                          // Get the state for this parameter path from RichFormState
                          final formParamState =
                              formState
                                  .parameterStates[paramNameKeyFromDetails];
                          final currentValue =
                              formParamState
                                  ?.currentValue; // Use value from RichFormState
                          final errorText =
                              formParamState
                                  ?.validationError; // Use error from RichFormState

                          // Derive a parameter definition from the config
                          final parameterDefinition = ParameterDefinition(
                            name:
                                paramNameKeyFromDetails, // TODO eventually have uuid
                            displayName: paramConfigData.displayName ?? '',
                            description: paramConfigData.description ?? '',
                            defaultValue: paramConfigData.defaultValue,
                            config: paramConfigData,
                            // Map other necessary fields from paramConfigData
                          );

                          return Card(
                            margin: const EdgeInsets.symmetric(
                              horizontal: 8,
                              vertical: 4,
                            ),
                            child: ListTile(
                              title: Text(
                                paramConfigData.displayName ??
                                    '', // Or formParamState.definition.displayName
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
                                  if (errorText != null &&
                                      errorText
                                          .isNotEmpty) // errorText from validationErrors map or formParamState
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
                                    paramNameKeyFromDetails, // Use the key from parametersMap iteration
                                    parameterDefinition, // This is ParameterDefinition
                                    currentValue, // Pass the current value from RichFormState
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
                                      parameters:
                                          currentValues, // Pass the correctly mapped currentValues
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
              // Using public factory name for pattern
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
