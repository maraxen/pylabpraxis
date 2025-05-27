// pylabpraxis_flutter/lib/src/features/run_protocol/presentation/widgets/dialogs/basic_parameter_edit_dialog.dart
// Renamed from BasicParameterEditDialog to BasicParameterEditScreen as per user's file
// This is the user's provided code for BasicParameterEditScreen, with minimal adjustments for clarity if needed.
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:pylabpraxis_flutter/src/data/models/protocol/parameter_config.dart'; // Assuming ParameterConfig is the type for parameterDefinition.config
import 'package:pylabpraxis_flutter/src/features/run_protocol/application/protocol_parameters_bloc/protocol_parameters_bloc.dart';
import 'package:pylabpraxis_flutter/src/data/models/protocol/parameter_constraints.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

class BasicParameterEditScreen extends StatefulWidget {
  final String parameterPath; // Path to the parameter (or parent dictionary)
  final ParameterDefinition
  parameterDefinition; // Definition of the value being edited (this is the ParameterConfig from backend)
  final dynamic currentValue;
  final String?
  dictionaryKey; // If editing a value within a dictionary, this is the key

  const BasicParameterEditScreen({
    super.key,
    required this.parameterPath,
    required this.parameterDefinition,
    required this.currentValue,
    this.dictionaryKey,
  });

  @override
  State<BasicParameterEditScreen> createState() =>
      _BasicParameterEditScreenState();
}

class _BasicParameterEditScreenState extends State<BasicParameterEditScreen> {
  late TextEditingController _textController;
  String? _validationError;
  bool _isSliderUsed = false;

  late FocusNode _numericTextFieldFocusNode;
  dynamic _sliderValue;

  // Helper to access properties, assuming parameterConfig is ParameterConfig
  String get _paramName =>
      widget.parameterPath; // Use parameterPath for the name
  String get _displayName =>
      widget.parameterDefinition.displayName ?? _paramName;
  String? get _description => widget.parameterDefinition.description;
  String get _paramType => widget.parameterDefinition.config.type;
  ParameterConstraints? get _constraints =>
      widget.parameterDefinition.config.constraints;

  @override
  void initState() {
    super.initState();
    _numericTextFieldFocusNode = FocusNode();
    _textController = TextEditingController(
      text: widget.currentValue?.toString() ?? '',
    );

    // Initialize slider value only if it's a numeric type with min/max constraints
    if ((_paramType == 'number' ||
            _paramType == 'integer' ||
            _paramType == 'float') &&
        _constraints?.minValue != null &&
        _constraints?.maxValue != null) {
      _sliderValue =
          num.tryParse(widget.currentValue?.toString() ?? '') ??
          _constraints!.minValue!;
      // Ensure sliderValue is within bounds
      if (_sliderValue < _constraints!.minValue!) {
        _sliderValue = _constraints!.minValue!;
      }
      if (_sliderValue > _constraints!.maxValue!) {
        _sliderValue = _constraints!.maxValue!;
      }
      if (_textController.text != _sliderValue.toString()) {
        _textController.text = _sliderValue.toString();
      }
    }
    _validateInput(_textController.text);
  }

  void _validateInput(String value) {
    final constraints = _constraints;
    String? error;

    if (constraints?.required_ == true &&
        value.trim().isEmpty &&
        _paramType != 'boolean') {
      error = '$_displayName is required.';
    } else {
      switch (_paramType) {
        case 'integer':
        case 'float':
        case 'number':
          if (value.isNotEmpty) {
            final num? parsedNum = num.tryParse(value);
            if (parsedNum == null) {
              error = 'Must be a valid number.';
            } else {
              if (constraints?.minValue != null &&
                  parsedNum < constraints!.minValue!) {
                error = 'Min value: ${constraints.minValue}.';
              }
              if (constraints?.maxValue != null &&
                  parsedNum > constraints!.maxValue!) {
                error = 'Max value: ${constraints.maxValue}.';
              }
              if (constraints?.step != null &&
                  constraints!.step! > 0 &&
                  constraints.minValue != null) {
                num step = constraints.step!;
                num valRelativeToMin = parsedNum - constraints.minValue!;
                // A more robust check for step alignment, especially for floating point numbers
                if (step != 0) {
                  // Using a small epsilon for float comparison
                  final double epsilon =
                      1e-9; // Adjust epsilon based on required precision
                  final double remainder = (valRelativeToMin / step) % 1.0;
                  if (!(remainder.abs() < epsilon ||
                      (1.0 - remainder).abs() < epsilon)) {
                    error =
                        'Value must align with step ${constraints.step} from min (${constraints.minValue}). Current: $parsedNum';
                  }
                }
              }
            }
          }
          break;
        case 'string':
          if (constraints?.minLength != null &&
              value.length < constraints!.minLength!) {
            error = 'Min length: ${constraints.minLength}.';
          }
          if (constraints?.maxLength != null &&
              value.length > constraints!.maxLength!) {
            error = 'Max length: ${constraints.maxLength}.';
          }
          if (constraints?.regex != null &&
              !RegExp(constraints!.regex!).hasMatch(value)) {
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

    if (_paramType == 'integer') {
      valueToSave = int.tryParse(_textController.text);
    } else if (_paramType == 'float' || _paramType == 'number') {
      valueToSave = double.tryParse(_textController.text);
    } else {
      valueToSave = _textController.text;
    }

    if (_constraints?.required_ != true && (_textController.text.isEmpty)) {
      // Check original text for emptiness
      valueToSave = null;
    }

    if (widget.dictionaryKey != null) {
      context.read<ProtocolParametersBloc>().add(
        ProtocolParametersEvent.updateDictionaryValue(
          parameterPath: widget.parameterPath,
          key: widget.dictionaryKey!,
          newValue: valueToSave,
        ),
      );
    } else {
      context.read<ProtocolParametersBloc>().add(
        ProtocolParametersEvent.parameterValueChanged(
          parameterPath: widget.parameterPath, // This is the name/key
          value: valueToSave,
        ),
      );
    }
    if (mounted) {
      Navigator.of(context).pop();
    }
  }

  Widget _buildNumericInputWithSlider() {
    final constraints = _constraints!;
    final theme = Theme.of(context);

    num currentSliderNumValue =
        _sliderValue as num? ?? (constraints.minValue ?? 0.0);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.only(bottom: 8.0),
          child: Text(
            'Current Value: ${currentSliderNumValue.toStringAsFixed(_paramType == "integer" ? 0 : 2)}', // Ensure currentSliderNumValue is not null
            style: theme.textTheme.titleMedium?.copyWith(
              fontWeight: FontWeight.bold,
            ),
          ),
        ),
        Slider(
          value: currentSliderNumValue.toDouble(),
          min: (constraints.minValue!).toDouble(), // Ensure not null
          max: (constraints.maxValue!).toDouble(), // Ensure not null
          divisions:
              constraints.step != null &&
                      constraints.step! > 0 &&
                      (constraints.maxValue! > constraints.minValue!)
                  ? (((constraints.maxValue! - constraints.minValue!) /
                          constraints.step!)
                      .round())
                  : null,
          label: currentSliderNumValue.toStringAsFixed(
            // Ensure not null
            _paramType == "integer" ? 0 : 2,
          ),
          onChanged: (double value) {
            setState(() {
              _isSliderUsed = true;
              num newValueHolder;
              if (_paramType == "integer") {
                newValueHolder = value.round();
              } else {
                // Handle float steps more carefully
                if (constraints.step != null && constraints.step! > 0) {
                  // Snap to the nearest step
                  newValueHolder =
                      (value / constraints.step!).round() * constraints.step!;
                  // Ensure precision matches step if step has decimals
                  if (constraints.step.toString().contains('.')) {
                    int decimalPlaces =
                        constraints.step.toString().split('.')[1].length;
                    newValueHolder = double.parse(
                      newValueHolder.toStringAsFixed(decimalPlaces),
                    );
                  }
                } else {
                  newValueHolder = value; // No step, or step is 0
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
            hintText:
                'Current: ${_sliderValue?.toString() ?? ""}', // Handle null _sliderValue
            border: const OutlineInputBorder(),
            errorText: _validationError,
            suffixIcon: IconButton(
              icon: const Icon(Icons.clear),
              onPressed: () {
                _textController.clear();
                _validateInput('');
                // Optionally reset slider
                if (mounted) {
                  setState(() {
                    _sliderValue = constraints.minValue; // Reset slider to min
                    _validateInput(
                      _sliderValue?.toString() ?? '',
                    ); // Re-validate if slider value is used
                  });
                }
              },
            ),
          ),
          keyboardType: TextInputType.numberWithOptions(
            decimal: _paramType != 'integer',
          ),
          inputFormatters:
              (_paramType == 'integer')
                  ? <TextInputFormatter>[FilteringTextInputFormatter.digitsOnly]
                  : <TextInputFormatter>[
                    FilteringTextInputFormatter.allow(RegExp(r'^-?\d*\.?\d*')),
                  ],
          onChanged: (value) {
            if (!_isSliderUsed || _numericTextFieldFocusNode.hasFocus) {
              _validateInput(value);
              final num? parsed = num.tryParse(value);
              if (parsed != null && _validationError == null) {
                if (parsed >= constraints.minValue! &&
                    parsed <= constraints.maxValue!) {
                  if (mounted) {
                    setState(() {
                      _sliderValue = parsed;
                    });
                  }
                } else if (parsed < constraints.minValue!) {
                  if (mounted) {
                    setState(() {
                      _sliderValue = constraints.minValue!;
                    });
                  }
                } else if (parsed > constraints.maxValue!) {
                  if (mounted) {
                    setState(() {
                      _sliderValue = constraints.maxValue!;
                    });
                  }
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
    final constraints = _constraints;
    final theme = Theme.of(context);

    Widget inputWidget;

    if ((_paramType == 'number' ||
            _paramType == 'integer' ||
            _paramType == 'float') &&
        constraints?.minValue != null &&
        constraints?.maxValue != null) {
      inputWidget = _buildNumericInputWithSlider();
    } else {
      inputWidget = TextFormField(
        controller: _textController,
        autofocus: true,
        decoration: InputDecoration(
          labelText: 'Enter Value',
          hintText: _description ?? 'Enter $_displayName',
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
            (_paramType == 'integer' ||
                    _paramType == 'float' ||
                    _paramType == 'number')
                ? TextInputType.numberWithOptions(
                  decimal: _paramType != 'integer',
                )
                : TextInputType.text,
        inputFormatters:
            (_paramType == 'integer')
                ? <TextInputFormatter>[FilteringTextInputFormatter.digitsOnly]
                : (_paramType == 'float' || _paramType == 'number')
                ? <TextInputFormatter>[
                  FilteringTextInputFormatter.allow(RegExp(r'^-?\d*\.?\d*')),
                ]
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
        title: Text('Edit: $_displayName'),
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
        padding: const EdgeInsets.all(24.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (_description != null && _description!.isNotEmpty)
              Padding(
                padding: const EdgeInsets.only(bottom: 20.0),
                child: Text(
                  _description!,
                  style: theme.textTheme.titleMedium?.copyWith(
                    color: theme.colorScheme.onSurfaceVariant,
                  ),
                ),
              ),
            inputWidget,
            if (constraints != null &&
                !((_paramType == 'number' ||
                        _paramType == 'integer' ||
                        _paramType == 'float') &&
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

// The showBasicParameterEditScreen function needs to be updated to pass ParameterConfig as parameterDefinition
Future<void> showBasicParameterEditScreen({
  required BuildContext context,
  required String parameterPath,
  required ParameterDefinition parameterDefinition,
  required dynamic currentValue,
  String? dictionaryKey,
}) async {
  await Navigator.of(context).push(
    MaterialPageRoute<void>(
      builder: (BuildContext dialogContext) {
        // If ProtocolParametersBloc is not directly available via BlocProvider.of<...>(context)
        // from the calling context (e.g., if this function is called from a utility),
        // you might need to ensure it's provided higher up or pass it explicitly.
        // For now, assuming it's available from the original context.
        return BlocProvider.value(
          value: BlocProvider.of<ProtocolParametersBloc>(
            context,
          ), // context is from the caller
          child: BasicParameterEditScreen(
            parameterPath: parameterPath,
            parameterDefinition: parameterDefinition,
            currentValue: currentValue,
            dictionaryKey: dictionaryKey,
          ),
        );
      },
      fullscreenDialog: true,
    ),
  );
}
