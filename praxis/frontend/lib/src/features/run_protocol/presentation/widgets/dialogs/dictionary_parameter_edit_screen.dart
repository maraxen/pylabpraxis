import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:praxis_lab_management/src/data/models/protocol/parameter_config.dart';
import 'package:praxis_lab_management/src/data/models/protocol/parameter_constraints.dart';
import 'package:praxis_lab_management/src/features/run_protocol/application/protocol_parameters_bloc/protocol_parameters_bloc.dart';
// Import other dialogs if needed for editing values
import 'basic_parameter_edit_dialog.dart';
import 'string_parameter_edit_screen.dart';
import 'array_parameter_edit_dialog.dart';

enum DictionaryEditStage { defineKeys, setValues }

class DictionaryParameterEditScreen extends StatefulWidget {
  final String parameterPath; // Path to the parent dictionary parameter
  final ParameterDefinition parameterDefinition;

  const DictionaryParameterEditScreen({
    super.key,
    required this.parameterPath,
    required this.parameterDefinition,
  });

  @override
  State<DictionaryParameterEditScreen> createState() =>
      _DictionaryParameterEditScreenState();
}

class _DictionaryParameterEditScreenState
    extends State<DictionaryParameterEditScreen> {
  DictionaryEditStage _currentStage = DictionaryEditStage.defineKeys;

  final TextEditingController _addKeyTextController = TextEditingController();
  String? _addKeyValidationError;
  final FocusNode _addKeyFocusNode = FocusNode();

  ParameterConstraints? get dictConstraints =>
      widget.parameterDefinition.config.constraints;
  ParameterConstraintsBase? get keyConstraints =>
      dictConstraints?.keyConstraints;
  // This is the general valueConstraints for the dictionary.
  // Specific keys might have overrides if the schema supports properties/patternProperties.
  ParameterConstraintsBase? get generalValueConstraints =>
      dictConstraints?.valueConstraints;

  @override
  void initState() {
    super.initState();
    bool keysArePredefinedAndNotUserModifiable =
        (keyConstraints?.array != null && keyConstraints!.array!.isNotEmpty) &&
        !(keyConstraints?.creatable ?? true) &&
        !(keyConstraints?.editable ?? true);

    if (keysArePredefinedAndNotUserModifiable) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        if (mounted) {
          final currentState = context.read<ProtocolParametersBloc>().state;
          if (currentState is ProtocolParametersLoaded) {
            final dictState =
                currentState.formState.parameterStates[widget.parameterPath];
            if (dictState?.currentValue is Map) {
              final currentMap = dictState!.currentValue as Map;
              bool allFixedKeysPresent = true;
              for (var fixedKey in keyConstraints!.array!) {
                if (!currentMap.containsKey(fixedKey.toString())) {
                  allFixedKeysPresent = false;
                  // Dispatch event to BLoC to add missing fixed keys with default values
                  // This ensures the map is populated before moving to setValues.
                  context.read<ProtocolParametersBloc>().add(
                    ProtocolParametersEvent.addDictionaryPairWithKey(
                      parameterPath: widget.parameterPath,
                      key: fixedKey.toString(),
                    ),
                  );
                }
              }
              // Check again after potential BLoC updates (might need a listener or delay)
              // For simplicity, assume BLoC updates quickly or this check is sufficient for now.
              // A more robust way would be to listen to BLoC state changes.
              final updatedState = context.read<ProtocolParametersBloc>().state;
              if (updatedState is ProtocolParametersLoaded) {
                final updatedDictState =
                    updatedState.formState.parameterStates[widget
                        .parameterPath];
                final updatedMap = updatedDictState?.currentValue as Map? ?? {};
                allFixedKeysPresent = keyConstraints!.array!.every(
                  (k) => updatedMap.containsKey(k.toString()),
                );
              }

              if (allFixedKeysPresent) {
                setState(() {
                  _currentStage = DictionaryEditStage.setValues;
                });
              }
            }
          }
        }
      });
    }
  }

  void _validateNewKeyInput(String key, List<String> existingKeys) {
    String? error;
    if (key.isEmpty) {
      error = 'Key cannot be empty.';
    } else if (existingKeys.contains(key)) {
      error = 'Key "$key" already exists.';
    }

    if (keyConstraints?.type != null && keyConstraints!.type != 'string') {
      if (keyConstraints!.type == 'integer' && int.tryParse(key) == null) {
        error = 'Key must be an integer.';
      }
    }
    if (keyConstraints?.regex != null &&
        !RegExp(keyConstraints!.regex!).hasMatch(key)) {
      error =
          'Key format is invalid: ${keyConstraints?.regexDescription ?? keyConstraints?.regex}';
    }

    if (mounted) {
      setState(() {
        _addKeyValidationError = error;
      });
    }
  }

  void _addNewKey(List<String> existingKeys) {
    final String newKey = _addKeyTextController.text.trim();
    _validateNewKeyInput(newKey, existingKeys);

    if (_addKeyValidationError == null && newKey.isNotEmpty) {
      context.read<ProtocolParametersBloc>().add(
        ProtocolParametersEvent.addDictionaryPairWithKey(
          parameterPath: widget.parameterPath,
          key: newKey,
        ),
      );
      _addKeyTextController.clear();
      _addKeyFocusNode.unfocus();
    }
  }

  void _removeKey(String keyToRemove) {
    context.read<ProtocolParametersBloc>().add(
      ProtocolParametersEvent.removeDictionaryPair(
        parameterPath: widget.parameterPath,
        keyToRemove: keyToRemove,
      ),
    );
  }

  void _confirmKeysAndProceed(Map<String, dynamic> currentMapData) {
    if (dictConstraints?.required_ == true &&
        currentMapData.isEmpty &&
        !(keyConstraints?.array?.isNotEmpty ?? false)) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text(
            'This dictionary is required and cannot be empty if keys are user-defined.',
          ),
          backgroundColor: Colors.redAccent,
        ),
      );
      return;
    }
    if (dictConstraints?.minProperties != null &&
        currentMapData.length < dictConstraints!.minProperties!) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            'Dictionary requires at least ${dictConstraints!.minProperties} entries.',
          ),
          backgroundColor: Colors.redAccent,
        ),
      );
      return;
    }

    setState(() {
      _currentStage = DictionaryEditStage.setValues;
    });
  }

  void _editValueForKey(
    BuildContext contextForDialog,
    String key,
    dynamic currentValue,
  ) {
    // Determine the specific constraints for *this value* based on the key.
    // For now, we use the general `generalValueConstraints` for all keys.
    // A more advanced schema might have `properties` or `patternProperties`
    // that define specific constraints for values of certain keys.
    ParameterConstraints? effectiveValueConstraints =
        generalValueConstraints as ParameterConstraints?;

    if (effectiveValueConstraints == null) {
      ScaffoldMessenger.of(contextForDialog).showSnackBar(
        SnackBar(content: Text('No value constraints defined for key "$key".')),
      );
      return;
    }

    // This ParameterDefinition is for the *value* associated with the key.
    final valueParamDef = ParameterDefinition(
      name: key,
      displayName: 'Value for "$key"',
      config: ParameterConfig(
        type: effectiveValueConstraints.type ?? 'string',
        constraints: effectiveValueConstraints,
        defaultValue: effectiveValueConstraints.defaultValue,
      ),
      description: "Set value for $key",
    );

    switch (effectiveValueConstraints.type) {
      case 'string':
        showStringParameterEditScreen(
          context: contextForDialog,
          parameterPath: widget.parameterPath,
          parameterDefinition: valueParamDef,
          currentValue: currentValue,
          dictionaryKey: key,
        );
        break;
      case 'integer':
      case 'float':
      case 'number':
        showBasicParameterEditScreen(
          context: contextForDialog,
          parameterPath: widget.parameterPath,
          parameterDefinition: valueParamDef,
          currentValue: currentValue,
          dictionaryKey: key,
        );
        break;
      case 'boolean':
        final bool currentBoolValue =
            currentValue as bool? ??
            effectiveValueConstraints.defaultValue as bool? ??
            false;
        context.read<ProtocolParametersBloc>().add(
          ProtocolParametersEvent.updateDictionaryValue(
            parameterPath: widget.parameterPath,
            key: key,
            newValue: !currentBoolValue,
          ),
        );
        break;
      case 'array':
        // `valueParamDef` here IS the definition for the array (type: 'array', constraints: item_constraints etc.)
        // The `parameterPath` for `ArrayParameterEditDialog` should identify this specific array value.
        // We construct a synthetic path: "parentDictPath.keyForThisArray"
        // The BLoC's array event handlers (`_onAddArrayItemWithValue`, `_onRemoveArrayItem`, etc.)
        // and `_onParameterValueChanged` (for item updates) need to parse this synthetic path
        // to target the array nested within the dictionary.
        showArrayParameterEditDialog(
          context: contextForDialog,
          parameterPath:
              '${widget.parameterPath}.$key', // Synthetic path for the array value
          parameterDefinition:
              valueParamDef, // This definition is for the array itself
        );
        break;
      case 'dict':
        ScaffoldMessenger.of(contextForDialog).showSnackBar(
          const SnackBar(
            content: Text(
              'Editing nested dictionaries is not yet fully supported here.',
            ),
          ),
        );
        // For nested dicts:
        // showDictionaryParameterEditScreen(
        //   context: contextForDialog,
        //   parameterPath: '${widget.parameterPath}.$key', // Synthetic path
        //   parameterDefinition: valueParamDef, // Definition for the nested dictionary
        // );
        break;
      default:
        ScaffoldMessenger.of(contextForDialog).showSnackBar(
          SnackBar(
            content: Text(
              'No editor for value type: ${effectiveValueConstraints.type}',
            ),
          ),
        );
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return BlocBuilder<ProtocolParametersBloc, ProtocolParametersState>(
      builder: (builderContext, state) {
        Map<String, dynamic> displayMap = {};
        String? overallDictError;
        bool isBlocLoaded = false;

        if (state is ProtocolParametersLoaded) {
          isBlocLoaded = true;
          final formParamState =
              state.formState.parameterStates[widget.parameterPath];
          if (formParamState != null) {
            displayMap = Map<String, dynamic>.from(
              formParamState.currentValue as Map? ?? {},
            );
            overallDictError = formParamState.validationError;
          }
        }

        if (!isBlocLoaded) {
          return Scaffold(
            appBar: AppBar(
              title: Text(
                widget.parameterDefinition.displayName ??
                    widget.parameterDefinition.name,
              ),
            ),
            body: const Center(
              child: CircularProgressIndicator(
                semanticsLabel: "Loading dictionary data",
              ),
            ),
          );
        }

        final currentKeysInMapFromBloc = displayMap.keys.toList();
        bool userCanCreateKeys = keyConstraints?.creatable ?? true;
        bool userCanEditKeys = keyConstraints?.editable ?? true;
        bool keysAreFixedByArray =
            keyConstraints?.array != null && keyConstraints!.array!.isNotEmpty;

        if (keysAreFixedByArray &&
            !userCanCreateKeys &&
            !userCanEditKeys &&
            _currentStage == DictionaryEditStage.defineKeys) {
          bool allFixedKeysActuallyInMap = true;
          if (keyConstraints?.array != null) {
            for (var fixedKey in keyConstraints!.array!) {
              if (!displayMap.containsKey(fixedKey.toString())) {
                allFixedKeysActuallyInMap = false;
                WidgetsBinding.instance.addPostFrameCallback((_) {
                  // Dispatch after build
                  if (mounted && !displayMap.containsKey(fixedKey.toString())) {
                    // Check again in case of rapid rebuilds
                    builderContext.read<ProtocolParametersBloc>().add(
                      ProtocolParametersEvent.addDictionaryPairWithKey(
                        parameterPath: widget.parameterPath,
                        key: fixedKey.toString(),
                      ),
                    );
                  }
                });
              }
            }
            // Re-check after potential dispatches (this is tricky due to async nature of BLoC updates)
            // A listener might be more robust for this auto-transition.
            // For now, if not all present, it will stay on key definition screen.
            final latestState =
                builderContext.read<ProtocolParametersBloc>().state;
            if (latestState is ProtocolParametersLoaded) {
              final latestMap =
                  latestState
                          .formState
                          .parameterStates[widget.parameterPath]
                          ?.currentValue
                      as Map? ??
                  {};
              allFixedKeysActuallyInMap = keyConstraints!.array!.every(
                (k) => latestMap.containsKey(k.toString()),
              );
            }
          }
          if (allFixedKeysActuallyInMap) {
            // If all fixed keys are now in the map
            WidgetsBinding.instance.addPostFrameCallback((_) {
              if (mounted && _currentStage == DictionaryEditStage.defineKeys) {
                _confirmKeysAndProceed(displayMap);
              }
            });
          }
        }

        return Scaffold(
          appBar: AppBar(
            title: Text(
              '${widget.parameterDefinition.displayName ?? widget.parameterDefinition.name} (${_currentStage == DictionaryEditStage.defineKeys ? "Define Keys" : "Set Values"})',
            ),
            leading: IconButton(
              icon: const Icon(Icons.close),
              onPressed: () => Navigator.of(context).pop(),
            ),
            actions: [
              if (_currentStage == DictionaryEditStage.defineKeys &&
                  (!keysAreFixedByArray ||
                      userCanCreateKeys ||
                      (keyConstraints?.array?.isEmpty ?? true)))
                TextButton(
                  onPressed:
                      (currentKeysInMapFromBloc.isNotEmpty ||
                              (keysAreFixedByArray &&
                                  (keyConstraints?.array?.isNotEmpty ?? false)))
                          ? () => _confirmKeysAndProceed(displayMap)
                          : null,
                  child: const Text('NEXT'),
                ),
              if (_currentStage == DictionaryEditStage.setValues)
                TextButton(
                  onPressed: () {
                    bool dictIsValid = true;
                    String? dictValidationError;
                    // Use the BLoC's own validation logic for the whole dictionary
                    final currentState =
                        builderContext.read<ProtocolParametersBloc>().state;
                    if (currentState is ProtocolParametersLoaded) {
                      final dictState =
                          currentState.formState.parameterStates[widget
                              .parameterPath];
                      if (dictState != null) {
                        dictIsValid = dictState.isValid;
                        dictValidationError = dictState.validationError;
                      }
                    }

                    if (!dictIsValid) {
                      ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(
                          content: Text(
                            dictValidationError ??
                                "Dictionary has invalid values or fails constraints.",
                          ),
                          backgroundColor: theme.colorScheme.error,
                        ),
                      );
                      return;
                    }
                    Navigator.of(context).pop();
                  },
                  child: const Text('DONE'),
                ),
            ],
          ),
          body: Column(
            children: [
              if (overallDictError != null &&
                  _currentStage == DictionaryEditStage.setValues)
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.all(12.0),
                  color: theme.colorScheme.errorContainer,
                  child: Text(
                    overallDictError,
                    style: TextStyle(color: theme.colorScheme.onErrorContainer),
                  ),
                ),
              Expanded(
                child:
                    _currentStage == DictionaryEditStage.defineKeys
                        ? _buildKeyDefinitionStage(
                          builderContext,
                          theme,
                          currentKeysInMapFromBloc,
                          userCanCreateKeys,
                          userCanEditKeys,
                          keysAreFixedByArray,
                        )
                        : _buildValueSettingStage(
                          builderContext,
                          theme,
                          displayMap,
                        ),
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildKeyDefinitionStage(
    BuildContext context,
    ThemeData theme,
    List<String> currentKeysInMap,
    bool canCreateKeys,
    bool canEditKeys,
    bool keysArePredefinedInArray,
  ) {
    List<String> keysToListInUI = List.from(currentKeysInMap);

    if (keysArePredefinedInArray) {
      Set<String> tempKeys = {}; // Start with empty set
      // Add predefined keys first to maintain their order if desired, or sort later
      tempKeys.addAll(keyConstraints!.array!.map((e) => e.toString()));
      // Then add any keys that might be in the map but not in predefined (if creatable was true)
      tempKeys.addAll(currentKeysInMap);
      keysToListInUI = tempKeys.toList()..sort(); // Sort for consistent display
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        if (widget.parameterDefinition.description != null &&
            widget.parameterDefinition.description!.isNotEmpty)
          Padding(
            padding: const EdgeInsets.fromLTRB(16.0, 16.0, 16.0, 8.0),
            child: Text(
              widget.parameterDefinition.description!,
              style: theme.textTheme.bodyMedium?.copyWith(
                color: theme.colorScheme.onSurfaceVariant,
              ),
            ),
          ),
        if (canCreateKeys &&
            (!keysArePredefinedInArray || (keyConstraints?.creatable ?? true)))
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Expanded(
                  child: TextFormField(
                    controller: _addKeyTextController,
                    focusNode: _addKeyFocusNode,
                    decoration: InputDecoration(
                      labelText: 'New Key Name',
                      hintText:
                          widget.parameterDefinition.config.examples ??
                          'e.g., sample_id',
                      border: const OutlineInputBorder(),
                      errorText: _addKeyValidationError,
                    ),
                    onChanged:
                        (value) =>
                            _validateNewKeyInput(value, currentKeysInMap),
                    onFieldSubmitted: (_) => _addNewKey(currentKeysInMap),
                  ),
                ),
                const SizedBox(width: 8),
                IconButton.filled(
                  icon: const Icon(Icons.add_circle_outline_rounded),
                  onPressed: () => _addNewKey(currentKeysInMap),
                  tooltip: 'Add Key',
                ),
              ],
            ),
          ),
        if (keysArePredefinedInArray)
          Padding(
            padding: const EdgeInsets.symmetric(
              horizontal: 16.0,
              vertical: 8.0,
            ),
            child: Text(
              (canCreateKeys && (keyConstraints?.creatable ?? false))
                  ? "Predefined/Suggested Keys (you can also add custom keys above):"
                  : ((canEditKeys && !canCreateKeys)
                      ? "Keys (can be removed if not used):"
                      : "Keys are predefined for this dictionary:"),
              style: theme.textTheme.titleSmall?.copyWith(
                color: theme.colorScheme.onSurfaceVariant,
              ),
            ),
          ),
        Expanded(
          child:
              keysToListInUI.isEmpty &&
                      !(canCreateKeys && !keysArePredefinedInArray)
                  ? Center(
                    child: Text(
                      'No keys defined for this dictionary.',
                      style: theme.textTheme.titleMedium?.copyWith(
                        color: theme.colorScheme.onSurfaceVariant,
                      ),
                    ),
                  )
                  : keysToListInUI.isEmpty &&
                      (canCreateKeys && !keysArePredefinedInArray)
                  ? Center(
                    child: Text(
                      'No keys defined yet. Add one above.',
                      style: theme.textTheme.titleMedium?.copyWith(
                        color: theme.colorScheme.onSurfaceVariant,
                      ),
                    ),
                  )
                  : ListView.builder(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 16.0,
                      vertical: 8.0,
                    ),
                    itemCount: keysToListInUI.length,
                    itemBuilder: (context, index) {
                      final key = keysToListInUI[index];
                      bool isKeyActuallyInMap = currentKeysInMap.contains(key);
                      // Deletable if: user can edit keys AND ( (it's not a predefined fixed key) OR (it is predefined but creatable is true, meaning user can remove their additions/override) ) AND it's actually in the map
                      bool canDeleteThisKey =
                          canEditKeys &&
                          (!keysArePredefinedInArray ||
                              (keyConstraints?.creatable ?? true) ||
                              !(keyConstraints!.array!
                                  .map((e) => e.toString())
                                  .contains(key))) &&
                          isKeyActuallyInMap;

                      return Card(
                        elevation: 0.5,
                        margin: const EdgeInsets.symmetric(vertical: 5.0),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(8.0),
                          side: BorderSide(
                            color: theme.dividerColor.withAlpha(120),
                          ),
                        ),
                        child: ListTile(
                          leading: Icon(
                            Icons.key_rounded,
                            color: theme.colorScheme.onSurfaceVariant.withAlpha(
                              190,
                            ),
                          ),
                          title: Text(
                            key,
                            style: theme.textTheme.bodyLarge?.copyWith(
                              fontWeight: FontWeight.w500,
                            ),
                          ),
                          trailing:
                              canDeleteThisKey
                                  ? IconButton(
                                    icon: Icon(
                                      Icons.delete_forever_rounded,
                                      color: theme.colorScheme.error,
                                    ),
                                    onPressed: () => _removeKey(key),
                                    tooltip: 'Remove Key',
                                  )
                                  : (keysArePredefinedInArray &&
                                          !isKeyActuallyInMap
                                      ? Tooltip(
                                        message:
                                            "This predefined key will be added with a default value.",
                                        child: Icon(
                                          Icons.info_outline_rounded,
                                          color: theme.disabledColor,
                                        ),
                                      )
                                      : null // No action if key is fixed and present, or not deletable
                                      ),
                        ),
                      );
                    },
                  ),
        ),
      ],
    );
  }

  Widget _buildValueSettingStage(
    BuildContext context,
    ThemeData theme,
    Map<String, dynamic> currentMapData,
  ) {
    final keysForValueSetting = currentMapData.keys.toList()..sort();

    if (keysForValueSetting.isEmpty) {
      return Center(
        /* ... (empty state as before) ... */
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(
                Icons.key_off_outlined,
                size: 60,
                color: theme.colorScheme.onSurfaceVariant,
              ),
              const SizedBox(height: 20),
              Text(
                'No keys available to set values.',
                style: theme.textTheme.headlineSmall?.copyWith(
                  color: theme.colorScheme.onSurfaceVariant,
                ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 20),
              ElevatedButton.icon(
                icon: const Icon(Icons.arrow_back_ios_new_rounded),
                label: const Text('Go Back to Define Keys'),
                onPressed:
                    () => setState(
                      () => _currentStage = DictionaryEditStage.defineKeys,
                    ),
              ),
            ],
          ),
        ),
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.all(16.0),
      itemCount: keysForValueSetting.length,
      itemBuilder: (context, index) {
        final key = keysForValueSetting[index];
        final value = currentMapData[key];
        String displayValue = value?.toString() ?? 'Not Set';
        IconData valueIcon = Icons.edit_note_outlined;
        Color valueColor =
            (value != null && value.toString().isNotEmpty)
                ? theme.colorScheme.primary
                : theme.colorScheme.onSurfaceVariant.withAlpha(190);
        bool valueIsDefaultOrNull = true;

        ParameterConstraints? specificValueConstraints =
            generalValueConstraints
                as ParameterConstraints?; // Use general by default
        // Placeholder: In a more complex schema, one might find specific constraints for this 'key'
        // e.g., from widget.parameterDefinition.config.properties[key].constraints

        if (specificValueConstraints != null) {
          if (value == specificValueConstraints.defaultValue) {
            valueIsDefaultOrNull = true; // Still using default
            valueColor = theme.colorScheme.onSurfaceVariant.withAlpha(190);
          } else if (value != null && value.toString().isNotEmpty) {
            valueIsDefaultOrNull = false; // Explicitly set to something else
            valueColor = theme.colorScheme.primary;
          } else {
            // value is null or empty string, and not the default (or no default)
            valueIsDefaultOrNull = true; // Treat as "not explicitly set"
          }

          switch (specificValueConstraints.type) {
            case 'integer':
            case 'float':
            case 'number':
              valueIcon = Icons.looks_one_rounded;
              break;
            case 'boolean':
              valueIcon =
                  (value == true)
                      ? Icons.check_box_rounded
                      : Icons.check_box_outline_blank_rounded;
              displayValue =
                  (value == true)
                      ? "True"
                      : (value == false ? "False" : "Not Set");
              break;
            case 'array':
              valueIcon = Icons.data_array_rounded;
              displayValue =
                  value is List
                      ? (value.isNotEmpty
                          ? '[${value.length} items]'
                          : '[Empty List]')
                      : 'Not Set (List)';
              break;
            case 'dict':
              valueIcon = Icons.account_tree_rounded;
              displayValue =
                  value is Map
                      ? (value.isNotEmpty
                          ? '{${value.keys.length} keys}'
                          : '{Empty Map}')
                      : 'Not Set (Map)';
              break;
            default:
              valueIcon = Icons.short_text_rounded;
              break;
          }
        }
        if (value == null || value.toString().isEmpty) {
          displayValue = "Tap to set value";
        }

        return Card(
          elevation: 1.0,
          margin: const EdgeInsets.symmetric(vertical: 6.0),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
            side: BorderSide(
              color:
                  valueIsDefaultOrNull
                      ? theme.colorScheme.outline.withAlpha(128)
                      : theme.colorScheme.primary.withAlpha(190),
              width: valueIsDefaultOrNull ? 1.0 : 1.5,
            ),
          ),
          child: ListTile(
            leading: Icon(valueIcon, color: valueColor, size: 28),
            title: Text(
              key,
              style: theme.textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.w600,
              ),
            ),
            subtitle: Text(
              displayValue,
              style: theme.textTheme.bodyMedium?.copyWith(
                color: valueColor,
                fontStyle:
                    valueIsDefaultOrNull ? FontStyle.italic : FontStyle.normal,
              ),
            ),
            trailing: Icon(
              Icons.edit_rounded,
              color: theme.colorScheme.secondary,
              size: 24,
            ), // Changed icon
            onTap: () => _editValueForKey(context, key, value),
          ),
        );
      },
    );
  }

  @override
  void dispose() {
    _addKeyTextController.dispose();
    _addKeyFocusNode.dispose();
    super.dispose();
  }
}

Future<void> showDictionaryParameterEditScreen({
  required BuildContext context,
  required String parameterPath,
  required ParameterDefinition parameterDefinition,
}) async {
  await Navigator.of(context).push(
    MaterialPageRoute<void>(
      builder: (BuildContext dialogContext) {
        return BlocProvider.value(
          value: BlocProvider.of<ProtocolParametersBloc>(context),
          child: DictionaryParameterEditScreen(
            parameterPath: parameterPath,
            parameterDefinition: parameterDefinition,
          ),
        );
      },
      fullscreenDialog: true,
    ),
  );
}
