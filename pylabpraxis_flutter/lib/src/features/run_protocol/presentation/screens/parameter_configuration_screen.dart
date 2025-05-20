import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:pylabpraxis_flutter/src/data/models/protocol/protocol_details.dart';
import 'package:pylabpraxis_flutter/src/data/models/protocol/parameter_config.dart';
import 'package:pylabpraxis_flutter/src/features/run_protocol/application/protocol_parameters_bloc/protocol_parameters_bloc.dart';
import 'package:pylabpraxis_flutter/src/features/run_protocol/domain/rich_form_state.dart';
import 'package:pylabpraxis_flutter/src/features/run_protocol/presentation/widgets/dialogs/basic_parameter_edit_dialog.dart';
import 'package:pylabpraxis_flutter/src/features/run_protocol/presentation/widgets/dialogs/string_parameter_edit_screen.dart';
import 'package:pylabpraxis_flutter/src/features/run_protocol/presentation/widgets/dialogs/array_parameter_edit_dialog.dart';
import 'package:pylabpraxis_flutter/src/features/run_protocol/presentation/widgets/dialogs/dictionary_parameter_edit_screen.dart';

class ParameterConfigurationScreen extends StatelessWidget {
  const ParameterConfigurationScreen({super.key});

  Map<String, List<MapEntry<String, FormParameterState>>>
  _groupParametersByType(RichFormState formState, ProtocolDetails details) {
    final Map<String, List<MapEntry<String, FormParameterState>>> grouped = {};
    formState.parameterStates.forEach((path, paramState) {
      if (paramState.definition == null) return;
      final type = paramState.definition!.config.type;
      if (!grouped.containsKey(type)) {
        grouped[type] = [];
      }
      grouped[type]!.add(MapEntry(path, paramState));
    });
    return grouped;
  }

  String _getParameterTypeDisplayName(String typeKey) {
    switch (typeKey) {
      case 'string':
        return 'Text & Choices';
      case 'boolean':
        return 'Switches (On/Off)';
      case 'integer':
      case 'float':
      case 'number':
        return 'Numbers & Sliders';
      case 'array':
        return 'Lists / Arrays';
      case 'dict':
        return 'Mappings / Dictionaries';
      default:
        return typeKey.toUpperCase();
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Scaffold(
      body: BlocConsumer<ProtocolParametersBloc, ProtocolParametersState>(
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
              // The ProtocolWorkflowBloc will typically listen to this BLoC's state
              // or receive an event when the form's overall validity changes.
              // For now, the validity is checked when "Next" is pressed in the workflow.
            },
          );
        },
        builder: (context, state) {
          return state.when(
            initial:
                () => const Center(child: Text('Initializing parameters...')),
            loading: () => const Center(child: CircularProgressIndicator()),
            error:
                (message) => Center(
                  child: Padding(
                    padding: const EdgeInsets.all(16.0),
                    child: Text(
                      'Error loading parameters: $message',
                      textAlign: TextAlign.center,
                    ),
                  ),
                ),
            loaded: (protocolDetails, formState, isFormValid) {
              final groupedParams = _groupParametersByType(
                formState,
                protocolDetails,
              );

              final preferredOrder = [
                'string',
                'number',
                'integer',
                'float',
                'boolean',
                'array',
                'dict',
              ];
              final sortedGroupKeys =
                  groupedParams.keys.toList()..sort((a, b) {
                    int indexA = preferredOrder.indexOf(a);
                    int indexB = preferredOrder.indexOf(b);
                    if (indexA == -1) indexA = preferredOrder.length;
                    if (indexB == -1) indexB = preferredOrder.length;
                    return indexA.compareTo(indexB);
                  });

              if (formState.parameterStates.isEmpty) {
                return const Center(
                  child: Text('No parameters to configure for this protocol.'),
                );
              }

              bool hasUnsetRequired = formState.parameterStates.values.any(
                (ps) =>
                    ps.definition?.config.constraints?.required_ == true &&
                    (ps.currentValue == null ||
                        ps.currentValue.toString().isEmpty ||
                        ps.currentValue == ps.definition?.defaultValue),
              );

              return Column(
                children: [
                  if (hasUnsetRequired)
                    Container(
                      width: double.infinity,
                      padding: const EdgeInsets.symmetric(
                        horizontal: 16.0,
                        vertical: 10.0,
                      ),
                      color: theme.colorScheme.tertiaryContainer.withOpacity(
                        0.8,
                      ),
                      child: Row(
                        children: [
                          Icon(
                            Icons.error_outline_rounded,
                            color: theme.colorScheme.onTertiaryContainer,
                            size: 20,
                          ),
                          const SizedBox(width: 10),
                          Expanded(
                            child: Text(
                              'Some required parameters need attention or are using default values.',
                              style: theme.textTheme.labelLarge?.copyWith(
                                color: theme.colorScheme.onTertiaryContainer,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  Expanded(
                    child: ListView.builder(
                      padding: const EdgeInsets.only(
                        top: 8.0,
                        bottom: 16.0,
                      ), // Add padding for carousels
                      itemCount: sortedGroupKeys.length,
                      itemBuilder: (context, index) {
                        final typeKey = sortedGroupKeys[index];
                        if (!groupedParams.containsKey(typeKey)) {
                          return const SizedBox.shrink();
                        }
                        final paramsOfType = groupedParams[typeKey]!;

                        if (paramsOfType.isEmpty) {
                          return const SizedBox.shrink();
                        }

                        return Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Padding(
                              padding: const EdgeInsets.fromLTRB(
                                16.0,
                                16.0,
                                16.0,
                                8.0,
                              ), // Adjusted padding
                              child: Text(
                                _getParameterTypeDisplayName(typeKey),
                                style: theme.textTheme.headlineSmall?.copyWith(
                                  fontWeight: FontWeight.w500,
                                ),
                              ),
                            ),
                            SizedBox(
                              height:
                                  typeKey == 'boolean'
                                      ? 70
                                      : 210, // Adjusted height
                              child: ListView.builder(
                                scrollDirection: Axis.horizontal,
                                itemCount: paramsOfType.length,
                                padding: const EdgeInsets.symmetric(
                                  horizontal: 12.0,
                                ), // Padding for first/last card
                                itemBuilder: (context, paramIndex) {
                                  final entry = paramsOfType[paramIndex];
                                  return _buildParameterDisplayItem(
                                    context,
                                    entry.key,
                                    entry.value.definition!,
                                    entry.value,
                                  );
                                },
                              ),
                            ),
                            if (index < sortedGroupKeys.length - 1)
                              const Divider(
                                height: 24,
                                thickness: 0.5,
                                indent: 16,
                                endIndent: 16,
                              ),
                          ],
                        );
                      },
                    ),
                  ),
                ],
              );
            },
          );
        },
      ),
    );
  }

  Widget _buildParameterDisplayItem(
    BuildContext context,
    String parameterPath,
    ParameterDefinition paramDef,
    FormParameterState paramState,
  ) {
    final parametersBloc = context.read<ProtocolParametersBloc>();
    final theme = Theme.of(context);

    if (paramDef.config.type == 'boolean') {
      bool currentValue =
          paramState.currentValue as bool? ??
          paramDef.defaultValue as bool? ??
          false;
      return Padding(
        padding: const EdgeInsets.symmetric(horizontal: 6.0, vertical: 8.0),
        child: ActionChip(
          avatar: Icon(
            currentValue
                ? Icons.check_circle
                : Icons.radio_button_unchecked_outlined, // Changed icon
            color:
                currentValue
                    ? theme.colorScheme.onPrimary
                    : theme.colorScheme.onSurfaceVariant,
            size: 20,
          ),
          label: Text(
            paramDef.displayName ?? paramDef.name,
            style: TextStyle(
              color:
                  currentValue
                      ? theme.colorScheme.onPrimary
                      : theme.colorScheme.onSurfaceVariant,
              fontWeight: FontWeight.w500,
            ),
          ),
          backgroundColor:
              currentValue
                  ? theme.colorScheme.primary
                  : theme.colorScheme.secondaryContainer.withOpacity(0.7),
          onPressed: () {
            parametersBloc.add(
              ProtocolParametersEvent.parameterValueChanged(
                parameterPath: parameterPath,
                value: !currentValue,
              ),
            );
          },
          tooltip: paramDef.description,
          elevation: currentValue ? 2 : 1,
          pressElevation: 3,
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(20.0),
            side: BorderSide(
              color:
                  paramState.validationError != null
                      ? theme.colorScheme.error
                      : (currentValue
                          ? theme.colorScheme.primary.withOpacity(0.5)
                          : theme.colorScheme.outline.withOpacity(0.5)),
              width: paramState.validationError != null ? 1.5 : 1.0,
            ),
          ),
        ),
      );
    }

    bool isRequired = paramDef.config.constraints?.required_ == true;
    bool hasDefault = paramDef.defaultValue != null;
    bool currentValueIsDefault =
        hasDefault && paramState.currentValue == paramDef.defaultValue;
    bool isSetAndNotDefault =
        paramState.currentValue != null &&
        paramState.currentValue.toString().isNotEmpty &&
        (!hasDefault || paramState.currentValue != paramDef.defaultValue);
    bool needsAttention =
        isRequired &&
        (paramState.currentValue == null ||
            paramState.currentValue.toString().isEmpty ||
            (hasDefault && paramState.currentValue == paramDef.defaultValue));

    // For partial fill display (numeric types with min/max)
    double? fillPercentage;
    bool isNumericWithRange = false;
    if ((paramDef.config.type == 'number' ||
            paramDef.config.type == 'integer' ||
            paramDef.config.type == 'float') &&
        paramDef.config.constraints?.minValue != null &&
        paramDef.config.constraints?.maxValue != null) {
      isNumericWithRange = true;
      final num? currentNum = num.tryParse(
        paramState.currentValue?.toString() ?? '',
      );
      final num minVal = paramDef.config.constraints!.minValue!;
      final num maxVal = paramDef.config.constraints!.maxValue!;
      if (currentNum != null && maxVal > minVal) {
        fillPercentage = ((currentNum - minVal) / (maxVal - minVal)).clamp(
          0.0,
          1.0,
        );
      } else if (currentNum == null && hasDefault) {
        // Show default fill if not set
        final num? defaultNum = num.tryParse(
          paramDef.defaultValue?.toString() ?? '',
        );
        if (defaultNum != null && maxVal > minVal) {
          fillPercentage = ((defaultNum - minVal) / (maxVal - minVal)).clamp(
            0.0,
            1.0,
          );
        }
      }
    }

    return Card(
      margin: const EdgeInsets.symmetric(
        horizontal: 6.0,
        vertical: 8.0,
      ), // Adjusted margin
      elevation: 1.5,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16.0),
        side: BorderSide(
          color:
              paramState.validationError != null
                  ? theme.colorScheme.error
                  : (needsAttention
                      ? theme.colorScheme.tertiary
                      : theme.colorScheme.outlineVariant.withOpacity(0.7)),
          width:
              paramState.validationError != null || needsAttention ? 1.8 : 1.2,
        ),
      ),
      clipBehavior: Clip.antiAlias, // Important for Stack and Positioned
      child: InkWell(
        onTap: () {
          _showEditDialogForParameter(
            context,
            parameterPath,
            paramDef,
            paramState.currentValue,
          );
        },
        borderRadius: BorderRadius.circular(16.0),
        child: SizedBox(
          // Use SizedBox for consistent card height if needed, or rely on content
          width: 230, // Slightly wider cards
          child: Stack(
            children: [
              if (isNumericWithRange && fillPercentage != null)
                Positioned.fill(
                  child: Align(
                    alignment: Alignment.bottomCenter,
                    child: FractionallySizedBox(
                      heightFactor: fillPercentage,
                      widthFactor: 1.0,
                      child: Container(
                        decoration: BoxDecoration(
                          gradient: LinearGradient(
                            colors: [
                              theme.colorScheme.primaryContainer.withOpacity(
                                0.1,
                              ),
                              theme.colorScheme.primaryContainer.withOpacity(
                                0.4,
                              ),
                            ],
                            begin: Alignment.bottomCenter,
                            end: Alignment.topCenter,
                          ),
                          // borderRadius: const BorderRadius.only(bottomLeft: Radius.circular(15), bottomRight: Radius.circular(15)), // Match card radius
                        ),
                      ),
                    ),
                  ),
                ),
              Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          paramDef.displayName ?? paramDef.name,
                          style: theme.textTheme.titleMedium?.copyWith(
                            fontWeight: FontWeight.w600,
                          ),
                          maxLines: 2,
                          overflow: TextOverflow.ellipsis,
                        ),
                        if (isRequired)
                          Padding(
                            padding: const EdgeInsets.only(top: 2.0),
                            child: Text(
                              'Required',
                              style: theme.textTheme.labelSmall?.copyWith(
                                color:
                                    needsAttention
                                        ? theme.colorScheme.tertiary
                                        : theme.colorScheme.onSurfaceVariant,
                                fontStyle: FontStyle.italic,
                              ),
                            ),
                          ),
                        if (paramDef.description != null &&
                            paramDef.description!.isNotEmpty)
                          Padding(
                            padding: const EdgeInsets.only(top: 6.0),
                            child: Text(
                              paramDef.description!,
                              style: theme.textTheme.bodySmall?.copyWith(
                                color: theme.colorScheme.onSurfaceVariant
                                    .withOpacity(0.8),
                              ),
                              maxLines: 2,
                              overflow: TextOverflow.ellipsis,
                            ),
                          ),
                      ],
                    ),

                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        if (isNumericWithRange &&
                            paramDef.config.constraints?.minValue != null &&
                            paramDef.config.constraints?.maxValue != null)
                          Padding(
                            padding: const EdgeInsets.only(bottom: 4.0),
                            child: Text(
                              'Range: ${paramDef.config.constraints!.minValue} - ${paramDef.config.constraints!.maxValue}',
                              style: theme.textTheme.labelSmall?.copyWith(
                                color: theme.colorScheme.onSurfaceVariant,
                              ),
                            ),
                          ),
                        Text(
                          paramState.currentValue?.toString() ??
                              (hasDefault
                                  ? '(Default: ${paramDef.defaultValue})'
                                  : 'Not Set'),
                          style: theme.textTheme.bodyLarge?.copyWith(
                            fontWeight:
                                isSetAndNotDefault
                                    ? FontWeight.w600
                                    : FontWeight.normal,
                            color:
                                isSetAndNotDefault
                                    ? theme.colorScheme.primary
                                    : (needsAttention
                                        ? theme.colorScheme.tertiary
                                        : theme.textTheme.bodyLarge?.color
                                            ?.withOpacity(0.8)),
                          ),
                          maxLines: 2,
                          overflow: TextOverflow.ellipsis,
                        ),
                        if (hasDefault &&
                            !currentValueIsDefault &&
                            paramState.currentValue != null &&
                            paramState.currentValue.toString().isNotEmpty)
                          Padding(
                            padding: const EdgeInsets.only(top: 2.0),
                            child: Text(
                              'Default: ${paramDef.defaultValue}',
                              style: theme.textTheme.labelSmall?.copyWith(
                                fontStyle: FontStyle.italic,
                                color: theme.colorScheme.onSurfaceVariant
                                    .withOpacity(0.7),
                              ),
                            ),
                          ),
                      ],
                    ),

                    if (paramState.validationError != null)
                      Padding(
                        padding: const EdgeInsets.only(top: 4.0),
                        child: Text(
                          paramState.validationError!,
                          style: theme.textTheme.labelMedium?.copyWith(
                            color: theme.colorScheme.error,
                            fontWeight: FontWeight.w500,
                          ),
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  void _showEditDialogForParameter(
    BuildContext context,
    String parameterPath,
    ParameterDefinition paramDef,
    dynamic currentValue,
  ) {
    switch (paramDef.config.type) {
      case 'string':
        showStringParameterEditScreen(
          context: context,
          parameterPath: parameterPath,
          parameterDefinition: paramDef,
          currentValue: currentValue,
          // dictionaryKey is not passed here as this is for top-level params or array items
        );
        break;
      case 'integer':
      case 'float':
      case 'number':
        showBasicParameterEditScreen(
          context: context,
          parameterPath: parameterPath,
          parameterDefinition: paramDef,
          currentValue: currentValue,
          // dictionaryKey is not passed here
        );
        break;
      case 'array':
        final items =
            (currentValue is List<dynamic>) ? currentValue : <dynamic>[];
        showArrayParameterEditDialog(
          context: context,
          parameterPath:
              parameterPath, // This is the path to the array parameter itself
          parameterDefinition: paramDef,
          currentItems: items,
        );
        break;
      case 'dict':
        final mapValue =
            (currentValue is Map<String, dynamic>)
                ? currentValue
                : <String, dynamic>{};
        showDictionaryParameterEditScreen(
          context: context,
          parameterPath: parameterPath, // Path to the dictionary parameter
          parameterDefinition: paramDef,
          // currentValue: mapValue, // Dictionary dialog now fetches from BLoC
        );
        break;
      case 'boolean':
        // Handled by ActionChip directly.
        break;
      default:
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              'No editor available for type: ${paramDef.config.type}',
            ),
          ),
        );
    }
  }
}

extension CustomColorScheme on ColorScheme {
  Color get warningContainer =>
      brightness == Brightness.light
          ? Colors.orange.shade100
          : Colors.orange.shade900;
  Color get onWarningContainer =>
      brightness == Brightness.light
          ? Colors.orange.shade900
          : Colors.orange.shade100;
}
