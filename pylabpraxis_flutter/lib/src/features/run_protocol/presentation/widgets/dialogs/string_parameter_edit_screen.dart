import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:pylabpraxis_flutter/src/data/models/protocol/parameter_config.dart';
import 'package:pylabpraxis_flutter/src/features/run_protocol/application/protocol_parameters_bloc/protocol_parameters_bloc.dart';

class StringParameterEditScreen extends StatefulWidget {
  final String parameterPath; // Path to the parameter (or parent dictionary)
  final ParameterDefinition parameterDefinition;
  final dynamic currentValue;
  final String? dictionaryKey; // If editing a value within a dictionary

  const StringParameterEditScreen({
    super.key,
    required this.parameterPath,
    required this.parameterDefinition,
    required this.currentValue,
    this.dictionaryKey, // Optional
  });

  @override
  State<StringParameterEditScreen> createState() =>
      _StringParameterEditScreenState();
}

class _StringParameterEditScreenState extends State<StringParameterEditScreen> {
  late TextEditingController _textController;
  String? _selectedChipValue;
  bool _showOtherTextField = false;
  String? _validationError;

  static const String _otherChipValueKey = '__OTHER__';

  @override
  void initState() {
    super.initState();
    _textController = TextEditingController();
    _initializeState();
  }

  void _initializeState() {
    final constraints = widget.parameterDefinition.config.constraints;
    final currentStringValue = widget.currentValue?.toString();

    if (constraints?.array != null && constraints!.array!.isNotEmpty) {
      if (currentStringValue != null &&
          constraints.array!
              .map((e) => e.toString())
              .contains(currentStringValue)) {
        _selectedChipValue = currentStringValue;
        _showOtherTextField = false;
      } else if (currentStringValue != null && currentStringValue.isNotEmpty) {
        _selectedChipValue = _otherChipValueKey;
        _textController.text = currentStringValue;
        _showOtherTextField = true;
      } else {
        _selectedChipValue = null;
        _showOtherTextField = false;
      }
    } else {
      _textController.text = currentStringValue ?? '';
      _showOtherTextField = true;
    }
    // Initial validation based on current/derived state
    if (_selectedChipValue == _otherChipValueKey ||
        !(constraints?.array?.isNotEmpty ?? false)) {
      _validateInput(_textController.text);
    } else if (_selectedChipValue != null) {
      _validateInput(_selectedChipValue!);
    } else {
      _validateInput(''); // For required check if nothing is selected
    }
  }

  void _validateInput(String value) {
    final paramDef = widget.parameterDefinition;
    final constraints = paramDef.config.constraints;
    String? error;

    String valueToValidate = value;
    // Determine the actual value to validate based on chip selection or text field
    if (constraints?.array != null && constraints!.array!.isNotEmpty) {
      // Chip mode
      if (_selectedChipValue == _otherChipValueKey) {
        valueToValidate = _textController.text;
      } else if (_selectedChipValue != null) {
        valueToValidate = _selectedChipValue!;
      } else {
        // Nothing selected
        valueToValidate = ""; // Treat as empty for required check
      }
    } else {
      // Simple text field mode
      valueToValidate = _textController.text;
    }

    if (constraints?.required_ == true) {
      if (valueToValidate.trim().isEmpty) {
        error = '${paramDef.displayName ?? paramDef.name} is required.';
      }
    }

    // Apply other string constraints only if a value is present (or if required and empty, error already set)
    if (error == null && valueToValidate.isNotEmpty) {
      if (constraints?.minLength != null &&
          valueToValidate.length < constraints!.minLength!) {
        error = 'Min length: ${constraints.minLength}.';
      }
      if (constraints?.maxLength != null &&
          valueToValidate.length > constraints!.maxLength!) {
        error = 'Max length: ${constraints!.maxLength}.';
      }
      if (constraints?.regex != null &&
          !RegExp(constraints!.regex!).hasMatch(valueToValidate)) {
        error =
            'Does not match pattern: ${constraints.regexDescription ?? constraints.regex}.';
      }
    }

    if (mounted) {
      setState(() {
        _validationError = error;
      });
    }
  }

  void _handleChipSelected(String value) {
    setState(() {
      if (_selectedChipValue == value && value != _otherChipValueKey) {
        _selectedChipValue = null;
        _showOtherTextField = false;
        _validateInput('');
      } else {
        _selectedChipValue = value;
        if (value == _otherChipValueKey) {
          _showOtherTextField = true;
          _validateInput(_textController.text);
        } else {
          _showOtherTextField = false;
          _textController.clear();
          _validateInput(value);
        }
      }
    });
  }

  void _handleSave() {
    String finalValueToSave;
    final bool hasChoices =
        widget.parameterDefinition.config.constraints?.array != null &&
        widget.parameterDefinition.config.constraints!.array!.isNotEmpty;

    if (hasChoices) {
      if (_selectedChipValue == _otherChipValueKey) {
        finalValueToSave = _textController.text.trim();
        _validateInput(finalValueToSave);
      } else if (_selectedChipValue != null) {
        finalValueToSave = _selectedChipValue!;
        _validateInput(finalValueToSave);
      } else {
        // Nothing selected
        finalValueToSave = '';
        _validateInput(
          finalValueToSave,
        ); // This will trigger 'required' error if applicable
      }
    } else {
      // Simple text field
      finalValueToSave = _textController.text.trim();
      _validateInput(finalValueToSave);
    }

    if (_validationError != null) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(_validationError!),
          backgroundColor: Theme.of(context).colorScheme.error,
        ),
      );
      return;
    }

    dynamic valueForBloc = finalValueToSave;
    if (widget.parameterDefinition.config.constraints?.required_ != true &&
        finalValueToSave.isEmpty &&
        _selectedChipValue == null) {
      valueForBloc = null;
    }

    if (widget.dictionaryKey != null) {
      context.read<ProtocolParametersBloc>().add(
        ProtocolParametersEvent.updateDictionaryValue(
          parameterPath: widget.parameterPath,
          key: widget.dictionaryKey!,
          newValue: valueForBloc,
        ),
      );
    } else {
      context.read<ProtocolParametersBloc>().add(
        ProtocolParametersEvent.parameterValueChanged(
          parameterPath: widget.parameterPath,
          value: valueForBloc,
        ),
      );
    }
    Navigator.of(context).pop();
  }

  @override
  Widget build(BuildContext context) {
    final paramDef = widget.parameterDefinition;
    final constraints = paramDef.config.constraints;
    final theme = Theme.of(context);
    final bool hasChoices =
        constraints?.array != null && constraints!.array!.isNotEmpty;

    return Scaffold(
      appBar: AppBar(
        title: Text('Edit: ${paramDef.displayName ?? paramDef.name}'),
        leading: IconButton(
          icon: const Icon(Icons.close),
          onPressed: () => Navigator.of(context).pop(),
        ),
        actions: <Widget>[
          TextButton(onPressed: _handleSave, child: const Text('SAVE')),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (paramDef.description != null &&
                paramDef.description!.isNotEmpty)
              Padding(
                padding: const EdgeInsets.only(bottom: 20.0),
                child: Text(
                  paramDef.description!,
                  style: theme.textTheme.titleMedium?.copyWith(
                    color: theme.colorScheme.onSurfaceVariant,
                  ),
                ),
              ),
            if (hasChoices) ...[
              Text(
                'Choose an option:',
                style: theme.textTheme.titleSmall?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 12.0),
              Wrap(
                spacing: 8.0,
                runSpacing: 8.0,
                children: [
                  ...constraints.array!.map((choice) {
                    final choiceString = choice.toString();
                    return FilterChip(
                      label: Text(choiceString),
                      selected: _selectedChipValue == choiceString,
                      onSelected: (selected) {
                        _handleChipSelected(choiceString);
                      },
                      selectedColor: theme.colorScheme.primaryContainer,
                      checkmarkColor: theme.colorScheme.onPrimaryContainer,
                      labelStyle:
                          _selectedChipValue == choiceString
                              ? TextStyle(
                                color: theme.colorScheme.onPrimaryContainer,
                              )
                              : null,
                    );
                  }).toList(),
                  FilterChip(
                    label: const Text('Other...'),
                    selected: _selectedChipValue == _otherChipValueKey,
                    onSelected: (selected) {
                      _handleChipSelected(_otherChipValueKey);
                    },
                    selectedColor: theme.colorScheme.secondaryContainer,
                    checkmarkColor: theme.colorScheme.onSecondaryContainer,
                    labelStyle:
                        _selectedChipValue == _otherChipValueKey
                            ? TextStyle(
                              color: theme.colorScheme.onSecondaryContainer,
                            )
                            : null,
                  ),
                ],
              ),
              const SizedBox(height: 20.0),
            ],
            if (_showOtherTextField || !hasChoices)
              TextFormField(
                controller: _textController,
                autofocus:
                    _showOtherTextField, // Autofocus if "Other" is selected or it's the only input
                decoration: InputDecoration(
                  labelText:
                      hasChoices ? 'Specify "Other" Value' : 'Enter Value',
                  border: const OutlineInputBorder(),
                  errorText: _validationError,
                  suffixIcon:
                      _textController.text.isNotEmpty
                          ? IconButton(
                            icon: const Icon(Icons.clear),
                            onPressed: () {
                              _textController.clear();
                              if (_selectedChipValue == _otherChipValueKey ||
                                  !hasChoices) {
                                _validateInput('');
                              }
                            },
                          )
                          : null,
                ),
                onChanged: (value) {
                  if (_selectedChipValue == _otherChipValueKey || !hasChoices) {
                    _validateInput(value);
                  }
                },
                onFieldSubmitted: (_) => _handleSave(),
              ),

            if (constraints != null && !hasChoices) ...[
              const SizedBox(height: 24),
              Text(
                'Constraints:',
                style: theme.textTheme.titleSmall?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 8),
              if (constraints.minLength != null)
                Text(
                  'Min length: ${constraints.minLength}',
                  style: theme.textTheme.bodyMedium,
                ),
              if (constraints.maxLength != null)
                Text(
                  'Max length: ${constraints.maxLength}',
                  style: theme.textTheme.bodyMedium,
                ),
              if (constraints.regex != null) ...[
                Text(
                  'Pattern: ${constraints.regexDescription ?? constraints.regex}',
                  style: theme.textTheme.bodyMedium,
                ),
              ],
            ],
            if (_validationError != null &&
                hasChoices &&
                !(_showOtherTextField &&
                    _selectedChipValue == _otherChipValueKey))
              Padding(
                // Show error for chip selection if text field is hidden
                padding: const EdgeInsets.only(top: 12.0),
                child: Text(
                  _validationError!,
                  style: TextStyle(
                    color: theme.colorScheme.error,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }

  @override
  void dispose() {
    _textController.dispose();
    super.dispose();
  }
}

Future<void> showStringParameterEditScreen({
  required BuildContext context,
  required String parameterPath,
  required ParameterDefinition parameterDefinition,
  required dynamic currentValue,
  String? dictionaryKey, // Added to pass through
}) async {
  await Navigator.of(context).push(
    MaterialPageRoute<void>(
      builder: (BuildContext dialogContext) {
        return BlocProvider.value(
          value: BlocProvider.of<ProtocolParametersBloc>(context),
          child: StringParameterEditScreen(
            parameterPath: parameterPath,
            parameterDefinition: parameterDefinition,
            currentValue: currentValue,
            dictionaryKey: dictionaryKey, // Pass it here
          ),
        );
      },
      fullscreenDialog: true,
    ),
  );
}
