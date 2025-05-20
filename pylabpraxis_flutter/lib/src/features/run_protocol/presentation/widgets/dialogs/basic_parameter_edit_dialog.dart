import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:pylabpraxis_flutter/src/data/models/protocol/parameter_config.dart';
import 'package:pylabpraxis_flutter/src/features/run_protocol/application/protocol_parameters_bloc/protocol_parameters_bloc.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

/// A full-screen dialog for editing string (non-choice) and numeric parameters.
/// Can also be used for editing values within a dictionary if [dictionaryKey] is provided.
class BasicParameterEditScreen extends StatefulWidget {
  final String parameterPath; // Path to the parameter (or parent dictionary)
  final ParameterDefinition
  parameterDefinition; // Definition of the value being edited
  final dynamic currentValue;
  final String?
  dictionaryKey; // If editing a value within a dictionary, this is the key

  const BasicParameterEditScreen({
    super.key,
    required this.parameterPath,
    required this.parameterDefinition,
    required this.currentValue,
    this.dictionaryKey, // Optional: for dictionary values
  });

  @override
  State<BasicParameterEditScreen> createState() =>
      _BasicParameterEditScreenState();
}

class _BasicParameterEditScreenState extends State<BasicParameterEditScreen> {
  late TextEditingController _textController;
  // _currentDialogValue was for dropdowns, which are now in StringParameterEditScreen
  // For numeric with slider, we use _sliderValue
  String? _validationError;
  bool _isSliderUsed = false;

  late FocusNode _numericTextFieldFocusNode;
  dynamic _sliderValue;

  @override
  void initState() {
    super.initState();
    _numericTextFieldFocusNode = FocusNode();
    // _currentDialogValue = widget.currentValue; // Not needed for dropdown here
    _textController = TextEditingController(
      text: widget.currentValue?.toString() ?? '',
    );

    final paramDef = widget.parameterDefinition;
    // Initialize slider value only if it's a numeric type with min/max constraints
    if ((paramDef.config.type == 'number' ||
            paramDef.config.type == 'integer' ||
            paramDef.config.type == 'float') &&
        paramDef.config.constraints?.minValue != null &&
        paramDef.config.constraints?.maxValue != null) {
      _sliderValue =
          num.tryParse(widget.currentValue?.toString() ?? '') ??
          paramDef.config.constraints!.minValue!;
      // Ensure sliderValue is within bounds
      if (_sliderValue < paramDef.config.constraints!.minValue!) {
        _sliderValue = paramDef.config.constraints!.minValue!;
      }
      if (_sliderValue > paramDef.config.constraints!.maxValue!) {
        _sliderValue = paramDef.config.constraints!.maxValue!;
      }
      // Sync text controller if it was initialized differently from slider value (e.g. null current value)
      if (_textController.text != _sliderValue.toString()) {
        _textController.text = _sliderValue.toString();
      }
    }
    _validateInput(_textController.text);
  }

  void _validateInput(String value) {
    final paramDef = widget.parameterDefinition;
    final constraints = paramDef.config.constraints;
    String? error;

    // Required check (applies if not a boolean, as booleans have inherent values)
    if (constraints?.required_ == true &&
        value.trim().isEmpty &&
        paramDef.config.type != 'boolean') {
      error = '${paramDef.displayName ?? paramDef.name} is required.';
    } else {
      // Type-specific validation
      switch (paramDef.config.type) {
        case 'integer':
        case 'float':
        case 'number':
          if (value.isNotEmpty) {
            // Only validate non-empty, otherwise required check handles it
            final num? parsedNum = num.tryParse(value);
            if (parsedNum == null) {
              error = 'Must be a valid number.';
            } else {
              if (constraints?.minValue != null &&
                  parsedNum < constraints.minValue!) {
                error = 'Min value: ${constraints.minValue}.';
              }
              if (constraints?.maxValue != null &&
                  parsedNum > constraints.maxValue!) {
                error = 'Max value: ${constraints.maxValue}.';
              }
              if (constraints?.step != null &&
                  constraints.step! > 0 &&
                  constraints.minValue != null) {
                // Ensure the number of decimal places in the value matches the step's decimal places
                // This is a common source of floating point precision issues with modulo.
                // A robust step validation might require converting to BigDecimal or scaled integers.
                // Simplified check:
                num step = constraints.step!;
                num valRelativeToMin = parsedNum - constraints.minValue!;
                // Check if valRelativeToMin is a multiple of step, considering precision
                if ((valRelativeToMin / step) % 1 != 0 &&
                    (valRelativeToMin / step).toStringAsFixed(8) % 1 != 0.0) {
                  // Check with some precision
                  // A more precise check:
                  // final remainder = (valRelativeToMin * 1e9).round() % (step * 1e9).round();
                  // if (remainder != 0) {
                  error =
                      'Value must align with step ${constraints.step} from min (${constraints.minValue}).';
                  // }
                }
              }
            }
          }
          break;
        case 'string': // This dialog now only handles plain strings (not choices)
          if (constraints?.minLength != null &&
              value.length < constraints.minLength!) {
            error = 'Min length: ${constraints.minLength}.';
          }
          if (constraints?.maxLength != null &&
              value.length > constraints.maxLength!) {
            error = 'Max length: ${constraints.maxLength}.';
          }
          if (constraints?.regex != null &&
              !RegExp(constraints.regex!).hasMatch(value)) {
            error =
                'Does not match pattern: ${constraints.regexDescription ?? constraints.regex}.';
          }
          break;
      }
    }

    if (mounted) {
      setState(() {
        _validationError = error;
      });
    }
  }

  void _handleSave() {
    // Use the most recent text from controller for validation, especially if slider was used then text edited.
    _validateInput(_textController.text);

    if (_validationError != null) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(_validationError!),
          backgroundColor: Theme.of(context).colorScheme.error,
        ),
      );
      return;
    }

    dynamic valueToSave;
    final paramType = widget.parameterDefinition.config.type;

    if (paramType == 'integer') {
      valueToSave = int.tryParse(_textController.text);
    } else if (paramType == 'float' || paramType == 'number') {
      valueToSave = double.tryParse(_textController.text);
    } else {
      // Plain string
      valueToSave = _textController.text;
    }

    // If field is not required and text is empty, valueToSave might be null (for numbers) or empty string.
    // The BLoC should handle what an "empty" optional value means (null vs empty string).
    if (widget.parameterDefinition.config.constraints?.required_ != true &&
        (valueToSave == null || valueToSave.toString().isEmpty)) {
      valueToSave = null; // Standardize empty optional to null for BLoC
    }

    if (widget.dictionaryKey != null) {
      // Editing a value within a dictionary
      context.read<ProtocolParametersBloc>().add(
        ProtocolParametersEvent.updateDictionaryValue(
          // Use specific event for dictionary value update
          parameterPath: widget.parameterPath, // Path to the parent dictionary
          key: widget.dictionaryKey!,
          newValue: valueToSave,
        ),
      );
    } else {
      // Editing a top-level parameter or an array item (if this dialog were used for array items)
      context.read<ProtocolParametersBloc>().add(
        ProtocolParametersEvent.parameterValueChanged(
          parameterPath: widget.parameterPath,
          value: valueToSave,
          // itemIndex: if this dialog were to support array items directly
        ),
      );
    }
    Navigator.of(context).pop();
  }

  Widget _buildNumericInputWithSlider() {
    final paramDef = widget.parameterDefinition;
    final constraints = paramDef.config.constraints!;
    final theme = Theme.of(context);

    // Ensure _sliderValue is initialized correctly and is a num
    num currentSliderNumValue =
        _sliderValue as num? ?? (constraints.minValue ?? 0.0);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.only(bottom: 8.0),
          child: Text(
            'Current Value: ${currentSliderNumValue.toStringAsFixed(paramDef.config.type == "integer" ? 0 : 2)}',
            style: theme.textTheme.titleMedium?.copyWith(
              fontWeight: FontWeight.bold,
            ),
          ),
        ),
        Slider(
          value: currentSliderNumValue.toDouble(),
          min: (constraints.minValue as num).toDouble(),
          max: (constraints.maxValue as num).toDouble(),
          divisions:
              constraints.step != null &&
                      constraints.step! > 0 &&
                      (constraints.maxValue! > constraints.minValue!)
                  ? (((constraints.maxValue! - constraints.minValue!) /
                          constraints.step!)
                      .round())
                  : null,
          label: currentSliderNumValue.toStringAsFixed(
            paramDef.config.type == "integer" ? 0 : 2,
          ),
          onChanged: (double value) {
            setState(() {
              _isSliderUsed = true;
              num newValueHolder;
              if (paramDef.config.type == "integer") {
                newValueHolder = value.round();
              } else {
                if (constraints.step != null &&
                    constraints.step.toString().contains('.')) {
                  int decimalPlaces =
                      constraints.step.toString().split('.')[1].length;
                  newValueHolder = double.parse(
                    value.toStringAsFixed(decimalPlaces),
                  );
                } else if (constraints.step != null && constraints.step! >= 1) {
                  // Integer step for float
                  newValueHolder =
                      (value / constraints.step!).round() * constraints.step!;
                } else {
                  newValueHolder =
                      value; // Potentially round to a general precision for floats
                }
              }
              // Ensure the new value from slider is within precise min/max after potential rounding
              if (newValueHolder < constraints.minValue!) {
                newValueHolder = constraints.minValue!;
              }
              if (newValueHolder > constraints.maxValue!) {
                newValueHolder = constraints.maxValue!;
              }

              _sliderValue = newValueHolder;
              _textController.text = _sliderValue.toString();
              _validateInput(_textController.text);
            });
          },
        ),
        const SizedBox(height: 16),
        TextFormField(
          controller: _textController,
          focusNode: _numericTextFieldFocusNode,
          decoration: InputDecoration(
            labelText: 'Or Enter Manually',
            hintText: 'Current: ${_sliderValue.toString()}',
            border: const OutlineInputBorder(),
            errorText: _validationError,
            suffixIcon: IconButton(
              icon: const Icon(Icons.clear),
              onPressed: () {
                _textController.clear();
                _validateInput(''); // Re-validate after clearing
                // Optionally reset slider to min or default if text is cleared
                // setState(() { _sliderValue = constraints.minValue; });
              },
            ),
          ),
          keyboardType: TextInputType.numberWithOptions(
            decimal: paramDef.config.type != 'integer',
          ),
          inputFormatters:
              (paramDef.config.type == 'integer')
                  ? <TextInputFormatter>[FilteringTextInputFormatter.digitsOnly]
                  : <TextInputFormatter>[
                    FilteringTextInputFormatter.allow(RegExp(r'^-?\d*\.?\d*')),
                  ], // Allow negative
          onChanged: (value) {
            if (!_isSliderUsed || _numericTextFieldFocusNode.hasFocus) {
              _validateInput(value);
              final num? parsed = num.tryParse(value);
              if (parsed != null && _validationError == null) {
                // Only update slider if valid number
                if (parsed >= constraints.minValue! &&
                    parsed <= constraints.maxValue!) {
                  setState(() {
                    _sliderValue = parsed;
                  });
                } else if (parsed < constraints.minValue!) {
                  // Snap to min if below
                  setState(() {
                    _sliderValue = constraints.minValue!;
                  });
                } else if (parsed > constraints.maxValue!) {
                  // Snap to max if above
                  setState(() {
                    _sliderValue = constraints.maxValue!;
                  });
                }
              }
            }
          },
          onTap: () {
            _textController.selection = TextSelection(
              baseOffset: 0,
              extentOffset: _textController.text.length,
            );
          },
          onFieldSubmitted: (_) => _handleSave(),
        ),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    final paramDef = widget.parameterDefinition;
    final constraints = paramDef.config.constraints;
    final theme = Theme.of(context);

    Widget inputWidget;

    if ((paramDef.config.type == 'number' ||
            paramDef.config.type == 'integer' ||
            paramDef.config.type == 'float') &&
        constraints?.minValue != null &&
        constraints?.maxValue != null) {
      inputWidget = _buildNumericInputWithSlider();
    } else {
      // Plain string or numeric without slider
      inputWidget = TextFormField(
        controller: _textController,
        autofocus: true,
        decoration: InputDecoration(
          labelText: 'Enter Value',
          hintText:
              paramDef.description ??
              'Enter ${paramDef.displayName ?? paramDef.name}',
          border: const OutlineInputBorder(),
          errorText: _validationError,
          suffixIcon:
              _textController.text.isNotEmpty
                  ? IconButton(
                    icon: const Icon(Icons.clear),
                    onPressed: () {
                      _textController.clear();
                      _validateInput('');
                    },
                  )
                  : null,
        ),
        keyboardType:
            (paramDef.config.type == 'integer' ||
                    paramDef.config.type == 'float' ||
                    paramDef.config.type == 'number')
                ? TextInputType.numberWithOptions(
                  decimal: paramDef.config.type != 'integer',
                )
                : TextInputType.text,
        inputFormatters:
            (paramDef.config.type == 'integer')
                ? <TextInputFormatter>[FilteringTextInputFormatter.digitsOnly]
                : (paramDef.config.type == 'float' ||
                    paramDef.config.type == 'number')
                ? <TextInputFormatter>[
                  FilteringTextInputFormatter.allow(RegExp(r'^-?\d*\.?\d*')),
                ] // Allow negative
                : null,
        onChanged: (value) {
          _isSliderUsed = false;
          _validateInput(value);
        },
        onFieldSubmitted: (_) => _handleSave(),
      );
    }

    return Scaffold(
      appBar: AppBar(
        title: Text('Edit: ${paramDef.displayName ?? paramDef.name}'),
        leading: IconButton(
          icon: const Icon(Icons.close),
          onPressed: () => Navigator.of(context).pop(),
        ),
        actions: <Widget>[
          TextButton(
            onPressed: _validationError == null ? _handleSave : null,
            child: const Text('SAVE'),
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24.0), // Increased padding
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
            inputWidget,
            if (constraints != null &&
                !((paramDef.config.type == 'number' ||
                        paramDef.config.type == 'integer' ||
                        paramDef.config.type == 'float') &&
                    constraints.minValue != null &&
                    constraints.maxValue != null)) ...[
              const SizedBox(height: 24),
              Text(
                'Constraints:',
                style: theme.textTheme.titleSmall?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 8),
              if (constraints.minValue != null)
                Text(
                  'Min value: ${constraints.minValue}',
                  style: theme.textTheme.bodyMedium,
                ),
              if (constraints.maxValue != null)
                Text(
                  'Max value: ${constraints.maxValue}',
                  style: theme.textTheme.bodyMedium,
                ),
              if (constraints.step != null)
                Text(
                  'Step: ${constraints.step}',
                  style: theme.textTheme.bodyMedium,
                ),
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
            // Validation error is now part of InputDecoration for TextFormFields,
            // or handled within _buildNumericInputWithSlider for slider errors.
          ],
        ),
      ),
    );
  }

  @override
  void dispose() {
    _textController.dispose();
    _numericTextFieldFocusNode.dispose();
    super.dispose();
  }
}

Future<void> showBasicParameterEditScreen({
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
          child: BasicParameterEditScreen(
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
