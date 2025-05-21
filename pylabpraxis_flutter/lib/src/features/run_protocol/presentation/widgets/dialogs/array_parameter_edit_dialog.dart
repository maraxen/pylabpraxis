import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:pylabpraxis_flutter/src/data/models/protocol/parameter_config.dart';
import 'package:pylabpraxis_flutter/src/features/run_protocol/application/protocol_parameters_bloc/protocol_parameters_bloc.dart';
import 'package:pylabpraxis_flutter/src/data/models/protocol/parameter_constraints.dart';
// Import item editing dialogs if needed for complex item types
import 'basic_parameter_edit_dialog.dart';
import 'string_parameter_edit_screen.dart';

/// A full-screen dialog for editing array parameters using InputChips.
class ArrayParameterEditDialog extends StatefulWidget {
  final String parameterPath;
  final ParameterDefinition parameterDefinition;
  // currentItems is not passed directly; BLoC state is the source of truth
  // final List<dynamic> currentItems;

  const ArrayParameterEditDialog({
    super.key,
    required this.parameterPath,
    required this.parameterDefinition,
    // required this.currentItems,
  });

  @override
  State<ArrayParameterEditDialog> createState() =>
      _ArrayParameterEditDialogState();
}

class _ArrayParameterEditDialogState extends State<ArrayParameterEditDialog> {
  final TextEditingController _addItemTextController = TextEditingController();
  String? _addItemValidationError;
  final FocusNode _addItemFocusNode = FocusNode();

  int? _editingChipIndex;
  String _editingChipOriginalValue = "";

  ParameterConstraints? get arrayConstraints =>
      widget.parameterDefinition.config.constraints;
  Map<String, dynamic>? get arrayConstraintsMap =>
      widget.parameterDefinition.config.constraints?.valueConstraints;
  ParameterConstraints? get itemConstraints =>
      ParameterConstraints.fromMap(arrayConstraintsMap!);

  void _validateAddItemInput(String value, List<dynamic> currentItems) {
    String? error;
    if (value.trim().isEmpty) {
      // Basic check for empty input before type validation
      // error = "Item value cannot be empty."; // Only if items themselves are required to be non-empty
    } else if (itemConstraints != null) {
      final tempItemDef = ParameterDefinition(
        name: "item_validator",
        config: ParameterConfig(
          type: itemConstraints!.type ?? "string",
          constraints: itemConstraints,
        ),
      );
      // Use the BLoC's validation logic if possible, or replicate parts of it.
      // For simplicity, basic type checks here.
      // This validation should ideally be more robust and align with _validateParameterValue in BLoC
      switch (itemConstraints!.type) {
        case 'integer':
          if (int.tryParse(value) == null) error = 'Must be a valid integer.';
          break;
        case 'number':
        case 'float':
          if (double.tryParse(value) == null) error = 'Must be a valid number.';
          break;
        // Add more type checks as needed (string regex, length, etc.)
      }
      // Check for uniqueness if uniqueItems constraint is true
      if (arrayConstraints?.uniqueItems == true &&
          currentItems.map((e) => e.toString()).contains(value.trim())) {
        if (!(_editingChipIndex != null &&
            value.trim() == _editingChipOriginalValue)) {
          // Allow saving if current value is same as original during edit
          error = 'Items in this list must be unique. "$value" already exists.';
        }
      }
    }
    if (mounted) {
      setState(() {
        _addItemValidationError = error;
      });
    }
  }

  void _addItemToList(List<dynamic> currentItems) {
    final String valueString = _addItemTextController.text.trim();
    _validateAddItemInput(valueString, currentItems);

    if (_addItemValidationError == null && valueString.isNotEmpty) {
      dynamic valueToAdd = valueString;
      if (itemConstraints != null) {
        if (itemConstraints!.type == 'integer') {
          valueToAdd = int.tryParse(valueString) ?? valueString;
        } else if (itemConstraints!.type == 'float' ||
            itemConstraints!.type == 'number') {
          valueToAdd = double.tryParse(valueString) ?? valueString;
        } else if (itemConstraints!.type == 'boolean') {
          if (valueString.toLowerCase() == 'true') {
            valueToAdd = true;
          } else if (valueString.toLowerCase() == 'false')
            valueToAdd = false;
          else {
            /* Invalid boolean string, validation should catch */
          }
        }
      }

      if (_editingChipIndex != null) {
        context.read<ProtocolParametersBloc>().add(
          ProtocolParametersEvent.parameterValueChanged(
            parameterPath: widget.parameterPath,
            value: valueToAdd,
            itemIndex: _editingChipIndex!,
          ),
        );
        setState(() {
          _editingChipIndex = null;
          _editingChipOriginalValue = "";
        });
      } else {
        if (arrayConstraints?.maxItems != null &&
            currentItems.length >= arrayConstraints!.maxItems!) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(
                'Cannot add more than ${arrayConstraints!.maxItems} items.',
              ),
              backgroundColor: Theme.of(context).colorScheme.error,
            ),
          );
          return;
        }
        context.read<ProtocolParametersBloc>().add(
          ProtocolParametersEvent.addArrayItemWithValue(
            parameterPath: widget.parameterPath,
            value: valueToAdd,
          ),
        );
      }
      _addItemTextController.clear();
      _addItemFocusNode.unfocus();
      _addItemValidationError =
          null; // Clear validation error after successful add/update
    } else if (valueString.isEmpty && _editingChipIndex == null) {
      setState(() {
        _addItemValidationError = "Cannot add an empty item.";
      });
    }
  }

  void _removeItem(BuildContext context, int index) {
    context.read<ProtocolParametersBloc>().add(
      ProtocolParametersEvent.removeArrayItem(
        parameterPath: widget.parameterPath,
        index: index,
      ),
    );
    if (_editingChipIndex == index) {
      _cancelEditChip();
    }
  }

  void _startEditChip(int index, dynamic currentValue) {
    // For simple types (string, number, boolean), edit inline using the top text field.
    // For complex types (nested array/dict as items), a new dialog would be needed.
    if (itemConstraints != null &&
        (itemConstraints!.type == 'string' ||
            itemConstraints!.type == 'integer' ||
            itemConstraints!.type == 'float' ||
            itemConstraints!.type == 'number' ||
            itemConstraints!.type == 'boolean')) {
      setState(() {
        _editingChipIndex = index;
        _editingChipOriginalValue = currentValue?.toString() ?? "";
        _addItemTextController.text = _editingChipOriginalValue;
        _addItemValidationError = null;
        _addItemFocusNode.requestFocus();
      });
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            'Editing complex array items (like nested lists/maps) directly is not yet supported here. Remove and re-add if needed.',
          ),
        ),
      );
    }
  }

  void _cancelEditChip() {
    if (mounted) {
      setState(() {
        _editingChipIndex = null;
        _editingChipOriginalValue = "";
        _addItemTextController.clear();
        _addItemValidationError = null;
        _addItemFocusNode.unfocus();
      });
    }
  }

  void _reorderItem(BuildContext context, int oldIndex, int targetIndex) {
    context.read<ProtocolParametersBloc>().add(
      ProtocolParametersEvent.reorderArrayItem(
        parameterPath: widget.parameterPath,
        oldIndex: oldIndex,
        targetIndex: targetIndex,
      ),
    );
    if (_editingChipIndex == oldIndex) {
      _cancelEditChip();
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return BlocBuilder<ProtocolParametersBloc, ProtocolParametersState>(
      builder: (context, state) {
        List<dynamic> displayItems = [];
        String? overallArrayError;
        bool isLoaded = false;

        if (state is ProtocolParametersLoaded) {
          isLoaded = true;
          final formParamState =
              state.formState.parameterStates[widget.parameterPath];
          if (formParamState != null) {
            displayItems = List.from(
              formParamState.currentValue as List? ?? [],
            );
            overallArrayError = formParamState.validationError;
          }
        }

        if (!isLoaded) {
          return Scaffold(
            appBar: AppBar(
              title: Text(
                'Edit List: ${widget.parameterDefinition.displayName ?? widget.parameterDefinition.name}',
              ),
            ),
            body: const Center(child: CircularProgressIndicator()),
          );
        }

        String itemTypeName = itemConstraints?.type ?? "item";
        TextInputType keyboardType = TextInputType.text;
        if (itemTypeName == 'integer') {
          keyboardType = TextInputType.number;
        } else if (itemTypeName == 'number' || itemTypeName == 'float') {
          keyboardType = const TextInputType.numberWithOptions(decimal: true);
        }

        bool canAddMoreItems =
            arrayConstraints?.maxItems == null ||
            displayItems.length < arrayConstraints!.maxItems!;

        return Scaffold(
          appBar: AppBar(
            title: Text(
              'Edit List: ${widget.parameterDefinition.displayName ?? widget.parameterDefinition.name}',
            ),
            leading: IconButton(
              icon: const Icon(Icons.close),
              onPressed: () => Navigator.of(context).pop(),
            ),
            actions: [
              TextButton(
                onPressed: () {
                  // Final validation of array (minItems, maxItems) is handled by BLoC.
                  // If there's an active edit, try to save it.
                  if (_editingChipIndex != null &&
                      _addItemTextController.text.isNotEmpty) {
                    _addItemToList(
                      displayItems,
                    ); // This will update the item then BLoC state
                  }
                  Navigator.of(context).pop();
                },
                child: const Text(
                  'DONE',
                  style: TextStyle(fontWeight: FontWeight.bold),
                ),
              ),
            ],
          ),
          body: Column(
            children: [
              Padding(
                padding: const EdgeInsets.fromLTRB(16.0, 16.0, 16.0, 8.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    if (widget.parameterDefinition.description != null &&
                        widget.parameterDefinition.description!.isNotEmpty)
                      Padding(
                        padding: const EdgeInsets.only(bottom: 12.0),
                        child: Text(
                          widget.parameterDefinition.description!,
                          style: theme.textTheme.titleSmall?.copyWith(
                            color: theme.colorScheme.onSurfaceVariant,
                          ),
                        ),
                      ),
                    Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Expanded(
                          child: TextFormField(
                            controller: _addItemTextController,
                            focusNode: _addItemFocusNode,
                            decoration: InputDecoration(
                              labelText:
                                  _editingChipIndex != null
                                      ? 'Edit "$_editingChipOriginalValue"'
                                      : (canAddMoreItems
                                          ? 'New $itemTypeName value'
                                          : 'Max items reached'),
                              hintText: canAddMoreItems ? 'Enter value' : '',
                              border: const OutlineInputBorder(),
                              errorText: _addItemValidationError,
                            ),
                            keyboardType: keyboardType,
                            inputFormatters:
                                itemTypeName == 'integer'
                                    ? [FilteringTextInputFormatter.digitsOnly]
                                    : (itemTypeName == 'number' ||
                                            itemTypeName == 'float'
                                        ? [
                                          FilteringTextInputFormatter.allow(
                                            RegExp(r'^-?\d*\.?\d*'),
                                          ),
                                        ]
                                        : null),
                            onChanged:
                                (value) =>
                                    _validateAddItemInput(value, displayItems),
                            onFieldSubmitted:
                                canAddMoreItems || _editingChipIndex != null
                                    ? (_) => _addItemToList(displayItems)
                                    : null,
                            enabled:
                                canAddMoreItems || _editingChipIndex != null,
                          ),
                        ),
                        const SizedBox(width: 8),
                        IconButton.filled(
                          icon: Icon(
                            _editingChipIndex != null
                                ? Icons.check_circle_outline
                                : Icons.add_circle_outline,
                          ),
                          onPressed:
                              (canAddMoreItems || _editingChipIndex != null)
                                  ? () => _addItemToList(displayItems)
                                  : null,
                          tooltip:
                              _editingChipIndex != null
                                  ? 'Update Item'
                                  : (canAddMoreItems
                                      ? 'Add Item'
                                      : 'Max items reached'),
                          style: IconButton.styleFrom(
                            backgroundColor:
                                (canAddMoreItems || _editingChipIndex != null)
                                    ? (_editingChipIndex != null
                                        ? theme.colorScheme.secondaryContainer
                                        : theme.colorScheme.primaryContainer)
                                    : theme.disabledColor.withAlpha(30),
                            foregroundColor:
                                (canAddMoreItems || _editingChipIndex != null)
                                    ? (_editingChipIndex != null
                                        ? theme.colorScheme.onSecondaryContainer
                                        : theme.colorScheme.onPrimaryContainer)
                                    : theme.disabledColor,
                          ),
                        ),
                        if (_editingChipIndex != null) ...[
                          const SizedBox(width: 4),
                          IconButton(
                            icon: Icon(
                              Icons.cancel_outlined,
                              color: theme.colorScheme.onSurfaceVariant,
                            ),
                            onPressed: _cancelEditChip,
                            tooltip: 'Cancel Edit',
                          ),
                        ],
                      ],
                    ),
                  ],
                ),
              ),
              if (overallArrayError != null)
                Padding(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 16.0,
                    vertical: 4.0,
                  ),
                  child: Text(
                    overallArrayError,
                    style: TextStyle(
                      color: theme.colorScheme.error,
                      fontSize: 12,
                    ),
                  ),
                ),
              Expanded(
                child:
                    displayItems.isEmpty
                        ? Center(
                          child: Padding(
                            padding: const EdgeInsets.all(24.0),
                            child: Text(
                              'No items in this list yet.',
                              style: theme.textTheme.titleMedium?.copyWith(
                                color: theme.colorScheme.onSurfaceVariant,
                              ),
                              textAlign: TextAlign.center,
                            ),
                          ),
                        )
                        : ReorderableListView.builder(
                          padding: const EdgeInsets.symmetric(
                            horizontal: 16.0,
                            vertical: 8.0,
                          ),
                          itemCount: displayItems.length,
                          itemBuilder: (context, index) {
                            final item = displayItems[index];
                            return Card(
                              // Using Card for better visual grouping and tap target for reorder
                              key: ValueKey(
                                '${widget.parameterPath}_item_card_$index}_${item.hashCode}',
                              ),
                              elevation: 0.5,
                              margin: const EdgeInsets.symmetric(vertical: 5.0),
                              shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(8.0),
                                side: BorderSide(
                                  color:
                                      _editingChipIndex == index
                                          ? theme.colorScheme.primary
                                          : theme.dividerColor.withAlpha(128),
                                ),
                              ),
                              child: Row(
                                children: [
                                  // ReorderableDragStartListener makes only the handle draggable
                                  ReorderableDragStartListener(
                                    index: index,
                                    child: Padding(
                                      padding: const EdgeInsets.symmetric(
                                        horizontal: 12.0,
                                      ),
                                      child: Icon(
                                        Icons.drag_indicator_outlined,
                                        color:
                                            theme.colorScheme.onSurfaceVariant,
                                      ),
                                    ),
                                  ),
                                  Expanded(
                                    child: InputChip(
                                      label: Text(
                                        item?.toString() ?? 'N/A',
                                        style: TextStyle(
                                          color:
                                              _editingChipIndex == index
                                                  ? theme.colorScheme.onPrimary
                                                  : null,
                                        ),
                                      ),
                                      selected: _editingChipIndex == index,
                                      showCheckmark: false,
                                      backgroundColor:
                                          _editingChipIndex == index
                                              ? theme.colorScheme.primary
                                                  .withAlpha(51)
                                              : null,
                                      selectedColor:
                                          theme
                                              .colorScheme
                                              .primary, // Text color when selected
                                      labelStyle: TextStyle(
                                        fontWeight:
                                            _editingChipIndex == index
                                                ? FontWeight.bold
                                                : FontWeight.normal,
                                      ),
                                      onSelected: (bool selected) {
                                        if (_editingChipIndex == index) {
                                          // Tapped chip being edited
                                          _cancelEditChip();
                                        } else {
                                          _startEditChip(index, item);
                                        }
                                      },
                                      onDeleted:
                                          () => _removeItem(context, index),
                                      deleteIconColor: theme.colorScheme.error
                                          .withAlpha(210),
                                      materialTapTargetSize:
                                          MaterialTapTargetSize.shrinkWrap,
                                      padding: const EdgeInsets.symmetric(
                                        horizontal: 12.0,
                                        vertical: 10.0,
                                      ),
                                    ),
                                  ),
                                ],
                              ),
                            );
                          },
                          onReorder: (oldIndex, newIndex) {
                            // ReorderableListView's newIndex is the final position after drop.
                            // If item is moved down, newIndex will be > oldIndex.
                            // If item is moved up, newIndex will be < oldIndex.
                            // The BLoC needs the old index and the target index *before* removal from old position.
                            // If newIndex > oldIndex, it means the item was dragged past (newIndex-1) items.
                            // So, the target index for insertion becomes newIndex-1.
                            int targetIndex = newIndex;
                            if (oldIndex < newIndex) {
                              targetIndex = newIndex - 1;
                            }
                            _reorderItem(context, oldIndex, targetIndex);
                          },
                        ),
              ),
            ],
          ),
        );
      },
    );
  }

  @override
  void dispose() {
    _addItemTextController.dispose();
    _addItemFocusNode.dispose();
    super.dispose();
  }
}

extension on ParameterConstraints? {
  get uniqueItems => this?.uniqueItems ?? false;
}

Future<void> showArrayParameterEditDialog({
  required BuildContext context,
  required String parameterPath,
  required ParameterDefinition parameterDefinition,
  // currentItems is no longer passed, dialog fetches from BLoC
  // required List<dynamic> currentItems,
}) async {
  await Navigator.of(context).push(
    MaterialPageRoute<void>(
      builder: (BuildContext dialogContext) {
        // Ensure the dialog has access to the same ProtocolParametersBloc instance
        return BlocProvider.value(
          value: BlocProvider.of<ProtocolParametersBloc>(context),
          child: ArrayParameterEditDialog(
            parameterPath: parameterPath,
            parameterDefinition: parameterDefinition,
            // currentItems: currentItems, // Fetched from BLoC via BlocBuilder
          ),
        );
      },
      fullscreenDialog: true,
    ),
  );
}
