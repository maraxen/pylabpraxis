// ignore_for_file: curly_braces_in_flow_control_structures

import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:pylabpraxis_flutter/src/data/models/protocol/protocol_details.dart';
import 'package:pylabpraxis_flutter/src/data/models/protocol/parameter_config.dart'; // For ParameterDefinition
import 'package:pylabpraxis_flutter/src/features/run_protocol/domain/rich_form_state.dart';
import 'package:pylabpraxis_flutter/src/features/run_protocol/domain/parameter_validation_service.dart';

part 'protocol_parameters_event.dart';
part 'protocol_parameters_state.dart';
part 'protocol_parameters_bloc.freezed.dart';

class ProtocolParametersBloc
    extends Bloc<ProtocolParametersEvent, ProtocolParametersState> {
  ProtocolParametersBloc() : super(const ProtocolParametersState.initial()) {
    on<LoadProtocolParameters>(_onLoadProtocolParameters);
    on<ParameterValueChanged>(_onParameterValueChanged);
    on<AddArrayItem>(_onAddArrayItem);
    on<AddArrayItemWithValue>(_onAddArrayItemWithValue);
    on<RemoveArrayItem>(_onRemoveArrayItem);
    on<ReorderArrayItem>(_onReorderArrayItem);
    on<AddDictionaryPair>(_onAddDictionaryPair);
    on<AddDictionaryPairWithKey>(_onAddDictionaryPairWithKey);
    on<RemoveDictionaryPair>(_onRemoveDictionaryPair);
    on<UpdateDictionaryKey>(_onUpdateDictionaryKey);
    on<UpdateDictionaryValue>(_onUpdateDictionaryValue);
    on<AssignValueToDictionaryKey>(_onAssignValueToDictionaryKey);
    on<ValidateParameterValue>(_onValidateParameterValue);
  }

  // Replace the previous _validateParameterValue with this simplified version
  ValidationResult validateParameterValue(
    ParameterDefinition paramDef,
    dynamic value, {
    List<dynamic>? arrayItems,
    Map<String, dynamic>? mapItems,
    String? dictItemKey,
    dynamic dictItemValue,
  }) {
    return ParameterValidationService.validateParameterValue(
      paramDef,
      value,
      arrayItems: arrayItems,
      mapItems: mapItems,
      dictItemKey: dictItemKey,
      dictItemValue: dictItemValue,
    );
  }

  // Public getter to directly access the current state
  ProtocolParametersState get currentState => state;

  // Helper getter to check if the current state is loaded
  bool get isStateLoaded => state is ProtocolParametersLoaded;

  // Helper getter to get completion percent
  double get completionPercent =>
      state is ProtocolParametersLoaded
          ? (state as ProtocolParametersLoaded)
              .requiredParametersCompletionPercent
          : 0.0;

  // Helper getter to get form validity
  bool get isFormValid =>
      state is ProtocolParametersLoaded
          ? (state as ProtocolParametersLoaded).isFormValid
          : false;

  Future<void> _onLoadProtocolParameters(
    LoadProtocolParameters event,
    Emitter<ProtocolParametersState> emit,
  ) async {
    emit(const ProtocolParametersState.loading());
    try {
      final richFormState = RichFormState.fromProtocolDetails(
        event.protocolDetails,
        existingConfiguredParameters: event.existingConfiguredParameters,
      );
      emit(
        ProtocolParametersState.loaded(
          protocolDetails: event.protocolDetails,
          formState: richFormState,
          isFormValid: richFormState.isFormValid,
          requiredParametersCompletionPercent:
              richFormState.requiredParametersCompletionPercent,
        ),
      );
    } catch (e) {
      emit(
        ProtocolParametersState.error(
          message: 'Failed to initialize parameters: ${e.toString()}',
        ),
      );
    }
  }

  Future<void> _onValidateParameterValue(
    ValidateParameterValue event,
    Emitter<ProtocolParametersState> emit,
  ) async {
    if (state is! ProtocolParametersLoaded) return;

    final loadedState = state as ProtocolParametersLoaded;
    final currentFormState = loadedState.formState;
    final parameterPath = event.parameterPath;

    FormParameterState? paramState = currentFormState[parameterPath];
    if (paramState == null || paramState.definition == null) return;

    final validationResult = validateParameterValue(
      paramState.definition!, // Added null assertion
      event.value,
    );

    final updatedParamState = paramState.copyWith(
      isValid: validationResult.isValid,
      validationError: validationResult.validationError,
    );

    final newRichFormState = currentFormState.updateParameterState(
      parameterPath,
      updatedParamState,
    );

    emit(
      loadedState.copyWith(
        formState: newRichFormState,
        isFormValid: newRichFormState.isFormValid,
        requiredParametersCompletionPercent:
            newRichFormState.requiredParametersCompletionPercent,
      ),
    );
  }

  Future<void> _onParameterValueChanged(
    ParameterValueChanged event,
    Emitter<ProtocolParametersState> emit,
  ) async {
    if (state is! ProtocolParametersLoaded) return;

    final loadedState = state as ProtocolParametersLoaded;
    final currentFormState = loadedState.formState;
    final parameterPath = event.parameterPath;

    FormParameterState? paramStateToUpdate = currentFormState[parameterPath];
    if (paramStateToUpdate == null || paramStateToUpdate.definition == null) {
      emit(
        ProtocolParametersState.error(
          message: 'Parameter $parameterPath not found or definition missing.',
        ),
      );
      return;
    }

    final paramDef = paramStateToUpdate.definition!;
    dynamic newValueForParam = paramStateToUpdate.currentValue;
    ValidationResult validationResult;

    if (paramDef.config.type == 'array' && event.itemIndex != null) {
      List<dynamic> currentArray = List.from(
        paramStateToUpdate.currentValue as List? ?? [],
      );
      if (event.itemIndex! >= 0 && event.itemIndex! < currentArray.length) {
        currentArray[event.itemIndex!] = event.value;
        newValueForParam = currentArray;
        validationResult = validateParameterValue(
          paramDef,
          newValueForParam,
          arrayItems: currentArray,
        );
      } else {
        return;
      }
    } else if (paramDef.config.type == 'dict' &&
        event.subKeyOrDictItemKey != null) {
      Map<String, dynamic> currentMap = Map<String, dynamic>.from(
        paramStateToUpdate.currentValue as Map? ?? {},
      );
      currentMap[event.subKeyOrDictItemKey!] = event.value;
      newValueForParam = currentMap;
      validationResult = validateParameterValue(
        paramDef,
        newValueForParam,
        mapItems: currentMap,
        dictItemKey: event.subKeyOrDictItemKey,
        dictItemValue: event.value,
      );
    } else {
      newValueForParam = event.value;
      validationResult = validateParameterValue(
        paramDef,
        newValueForParam,
        arrayItems:
            paramDef.config.type == 'array'
                ? (newValueForParam as List<dynamic>?)
                : null,
        mapItems:
            paramDef.config.type == 'dict'
                ? (newValueForParam as Map<String, dynamic>?)
                : null,
      );
    }

    final updatedParamState = paramStateToUpdate.copyWith(
      currentValue: newValueForParam,
      isValid: validationResult.isValid,
      validationError: validationResult.validationError,
    );

    final newRichFormState = currentFormState.updateParameterState(
      parameterPath,
      updatedParamState,
    );

    emit(
      loadedState.copyWith(
        formState: newRichFormState,
        isFormValid: newRichFormState.isFormValid,
        requiredParametersCompletionPercent:
            newRichFormState.requiredParametersCompletionPercent,
      ),
    );
  }

  Future<void> _onAddArrayItem(
    AddArrayItem event,
    Emitter<ProtocolParametersState> emit,
  ) async {
    if (state is! ProtocolParametersLoaded) return;
    final loadedState = state as ProtocolParametersLoaded;
    final currentFormState = loadedState.formState;
    final parameterPath = event.parameterPath;
    FormParameterState? arrayParamState = currentFormState[parameterPath];
    if (arrayParamState == null ||
        arrayParamState.definition == null ||
        arrayParamState.definition?.config.type != 'array') {
      return;
    }
    List<dynamic> currentArray = List.from(
      arrayParamState.currentValue as List? ?? [],
    );

    dynamic newItemDefaultValue;
    final itemConstraints = arrayParamState.definition?.config.constraints;
    if (itemConstraints != null) {
      newItemDefaultValue = itemConstraints.defaultValue;
      if (newItemDefaultValue == null) {
        switch (itemConstraints.type) {
          case 'string':
            newItemDefaultValue = '';
            break;
          case 'number':
          case 'integer':
          case 'float':
            newItemDefaultValue = null;
            break;
          case 'boolean':
            newItemDefaultValue = false;
            break;
          case 'array':
            newItemDefaultValue = [];
            break;
          case 'dict':
            newItemDefaultValue = {};
            break;
          default:
            newItemDefaultValue = null;
        }
      }
    } else {
      newItemDefaultValue = null;
    }
    currentArray.add(newItemDefaultValue);
    final validationResult = validateParameterValue(
      arrayParamState.definition!,
      currentArray,
      arrayItems: currentArray,
    );
    final updatedParamState = arrayParamState.copyWith(
      currentValue: currentArray,
      isValid: validationResult.isValid,
      validationError: validationResult.validationError,
    );
    final newRichFormState = currentFormState.updateParameterState(
      parameterPath,
      updatedParamState,
    );
    emit(
      loadedState.copyWith(
        formState: newRichFormState,
        isFormValid: newRichFormState.isFormValid,
        requiredParametersCompletionPercent:
            newRichFormState.requiredParametersCompletionPercent,
      ),
    );
  }

  Future<void> _onAddArrayItemWithValue(
    AddArrayItemWithValue event,
    Emitter<ProtocolParametersState> emit,
  ) async {
    if (state is! ProtocolParametersLoaded) return;
    final loadedState = state as ProtocolParametersLoaded;
    final currentFormState = loadedState.formState;
    final parameterPath = event.parameterPath;
    FormParameterState? arrayParamState = currentFormState[parameterPath];
    if (arrayParamState == null ||
        arrayParamState.definition == null ||
        arrayParamState.definition?.config.type != 'array') {
      return;
    }

    List<dynamic> currentArray = List.from(
      arrayParamState.currentValue as List? ?? [],
    );
    currentArray.add(event.value);
    final validationResult = validateParameterValue(
      arrayParamState.definition!,
      currentArray,
      arrayItems: currentArray,
    );
    final updatedParamState = arrayParamState.copyWith(
      currentValue: currentArray,
      isValid: validationResult.isValid,
      validationError: validationResult.validationError,
    );
    final newRichFormState = currentFormState.updateParameterState(
      parameterPath,
      updatedParamState,
    );
    emit(
      loadedState.copyWith(
        formState: newRichFormState,
        isFormValid: newRichFormState.isFormValid,
        requiredParametersCompletionPercent:
            newRichFormState.requiredParametersCompletionPercent,
      ),
    );
  }

  Future<void> _onRemoveArrayItem(
    RemoveArrayItem event,
    Emitter<ProtocolParametersState> emit,
  ) async {
    if (state is! ProtocolParametersLoaded) return;
    final loadedState = state as ProtocolParametersLoaded;
    final currentFormState = loadedState.formState;
    final parameterPath = event.parameterPath;
    FormParameterState? arrayParamState = currentFormState[parameterPath];
    if (arrayParamState == null ||
        arrayParamState.definition == null ||
        arrayParamState.definition?.config.type != 'array') {
      return;
    }

    List<dynamic> currentArray = List.from(
      arrayParamState.currentValue as List? ?? [],
    );
    if (event.index >= 0 && event.index < currentArray.length) {
      currentArray.removeAt(event.index);
    } else {
      return;
    }
    final validationResult = validateParameterValue(
      arrayParamState.definition!,
      currentArray,
      arrayItems: currentArray,
    );
    final updatedParamState = arrayParamState.copyWith(
      currentValue: currentArray,
      isValid: validationResult.isValid,
      validationError: validationResult.validationError,
    );
    final newRichFormState = currentFormState.updateParameterState(
      parameterPath,
      updatedParamState,
    );
    emit(
      loadedState.copyWith(
        formState: newRichFormState,
        isFormValid: newRichFormState.isFormValid,
        requiredParametersCompletionPercent:
            newRichFormState.requiredParametersCompletionPercent,
      ),
    );
  }

  Future<void> _onReorderArrayItem(
    ReorderArrayItem event,
    Emitter<ProtocolParametersState> emit,
  ) async {
    if (state is! ProtocolParametersLoaded) return;
    final loadedState = state as ProtocolParametersLoaded;
    final currentFormState = loadedState.formState;
    final parameterPath = event.parameterPath;
    FormParameterState? arrayParamState = currentFormState[parameterPath];
    if (arrayParamState == null ||
        arrayParamState.definition == null ||
        arrayParamState.definition?.config.type != 'array') {
      return;
    }

    List<dynamic> currentArray = List.from(
      arrayParamState.currentValue as List? ?? [],
    );
    if (event.oldIndex >= 0 &&
        event.oldIndex < currentArray.length &&
        event.newIndex >= 0 &&
        event.newIndex < currentArray.length) {
      final item = currentArray.removeAt(event.oldIndex);
      currentArray.insert(event.newIndex, item);
    } else {
      return;
    }
    final validationResult = validateParameterValue(
      arrayParamState.definition!,
      currentArray,
      arrayItems: currentArray,
    );
    final updatedParamState = arrayParamState.copyWith(
      currentValue: currentArray,
      isValid: validationResult.isValid,
      validationError: validationResult.validationError,
    );
    final newRichFormState = currentFormState.updateParameterState(
      parameterPath,
      updatedParamState,
    );
    emit(
      loadedState.copyWith(
        formState: newRichFormState,
        isFormValid: newRichFormState.isFormValid,
        requiredParametersCompletionPercent:
            newRichFormState.requiredParametersCompletionPercent,
      ),
    );
  }

  Future<void> _onAddDictionaryPair(
    AddDictionaryPair event,
    Emitter<ProtocolParametersState> emit,
  ) async {
    if (state is! ProtocolParametersLoaded) return;
    final loadedState = state as ProtocolParametersLoaded;
    final currentFormState = loadedState.formState;
    final paramPath = event.parameterPath;
    FormParameterState? dictParamState = currentFormState[paramPath];
    if (dictParamState == null ||
        dictParamState.definition == null ||
        dictParamState.definition?.config.type != 'dict') {
      return;
    }

    Map<String, dynamic> currentMap = Map<String, dynamic>.from(
      dictParamState.currentValue as Map? ?? {},
    );
    // ... (logic for newKey and newValue)
    String newKey = "new_key_${currentMap.length + 1}";
    int i = 1;
    while (currentMap.containsKey(newKey)) {
      newKey = "new_key_${currentMap.length + 1 + i}";
      i++;
    }
    dynamic newValue;
    final valueConstraints =
        dictParamState.definition?.config.constraints?.valueConstraints;
    if (valueConstraints != null) {
      newValue = valueConstraints.defaultValue;
      if (newValue == null) {
        switch (valueConstraints.type) {
          case 'string':
            newValue = '';
            break;
          case 'number':
          case 'integer':
          case 'float':
            newValue = null;
            break;
          case 'boolean':
            newValue = false;
            break;
          case 'array':
            newValue = [];
            break;
          case 'dict':
            newValue = {};
            break;
          default:
            newValue = null;
        }
      }
    } else {
      newValue = null;
    }
    currentMap[newKey] = newValue;
    final validationResult = validateParameterValue(
      dictParamState.definition!,
      currentMap,
      mapItems: currentMap,
    );
    final updatedParamState = dictParamState.copyWith(
      currentValue: currentMap,
      isValid: validationResult.isValid,
      validationError: validationResult.validationError,
    );
    final newRichFormState = currentFormState.updateParameterState(
      paramPath,
      updatedParamState,
    );
    emit(
      loadedState.copyWith(
        formState: newRichFormState,
        isFormValid: newRichFormState.isFormValid,
        requiredParametersCompletionPercent:
            newRichFormState.requiredParametersCompletionPercent,
      ),
    );
  }

  Future<void> _onAddDictionaryPairWithKey(
    AddDictionaryPairWithKey event,
    Emitter<ProtocolParametersState> emit,
  ) async {
    if (state is! ProtocolParametersLoaded) return;
    final loadedState = state as ProtocolParametersLoaded;
    final currentFormState = loadedState.formState;
    final paramPath = event.parameterPath;
    FormParameterState? dictParamState = currentFormState[paramPath];
    if (dictParamState == null ||
        dictParamState.definition == null ||
        dictParamState.definition?.config.type != 'dict') {
      return;
    }

    Map<String, dynamic> currentMap = Map<String, dynamic>.from(
      dictParamState.currentValue as Map? ?? {},
    );
    if (currentMap.containsKey(event.key)) {
      /* ... */
      return;
    }
    // ... (logic for defaultValue)
    dynamic defaultValue;
    final valueConstraints =
        dictParamState.definition?.config.constraints?.valueConstraints;
    if (valueConstraints != null) {
      defaultValue = valueConstraints.defaultValue;
      if (defaultValue == null) {
        switch (valueConstraints.type) {
          case 'string':
            defaultValue = '';
            break;
          case 'number':
          case 'integer':
          case 'float':
            defaultValue = null;
            break;
          case 'boolean':
            defaultValue = false;
            break;
          case 'array':
            defaultValue = [];
            break;
          case 'dict':
            defaultValue = {};
            break;
          default:
            defaultValue = null;
        }
      }
    } else {
      defaultValue = null;
    }
    currentMap[event.key] = defaultValue;
    final validationResult = validateParameterValue(
      dictParamState.definition!,
      currentMap,
      mapItems: currentMap,
    );
    final updatedParamState = dictParamState.copyWith(
      currentValue: currentMap,
      isValid: validationResult.isValid,
      validationError: validationResult.validationError,
    );
    final newRichFormState = currentFormState.updateParameterState(
      paramPath,
      updatedParamState,
    );
    emit(
      loadedState.copyWith(
        formState: newRichFormState,
        isFormValid: newRichFormState.isFormValid,
        requiredParametersCompletionPercent:
            newRichFormState.requiredParametersCompletionPercent,
      ),
    );
  }

  Future<void> _onRemoveDictionaryPair(
    RemoveDictionaryPair event,
    Emitter<ProtocolParametersState> emit,
  ) async {
    if (state is! ProtocolParametersLoaded) return;
    final loadedState = state as ProtocolParametersLoaded;
    final currentFormState = loadedState.formState;
    final paramPath = event.parameterPath;
    FormParameterState? dictParamState = currentFormState[paramPath];
    if (dictParamState == null ||
        dictParamState.definition == null ||
        dictParamState.definition?.config.type != 'dict') {
      return;
    }

    Map<String, dynamic> currentMap = Map<String, dynamic>.from(
      dictParamState.currentValue as Map? ?? {},
    );
    currentMap.remove(event.keyToRemove);
    final validationResult = validateParameterValue(
      dictParamState.definition!,
      currentMap,
      mapItems: currentMap,
    );
    final updatedParamState = dictParamState.copyWith(
      currentValue: currentMap,
      isValid: validationResult.isValid,
      validationError: validationResult.validationError,
    );
    final newRichFormState = currentFormState.updateParameterState(
      paramPath,
      updatedParamState,
    );
    emit(
      loadedState.copyWith(
        formState: newRichFormState,
        isFormValid: newRichFormState.isFormValid,
        requiredParametersCompletionPercent:
            newRichFormState.requiredParametersCompletionPercent,
      ),
    );
  }

  Future<void> _onUpdateDictionaryKey(
    UpdateDictionaryKey event,
    Emitter<ProtocolParametersState> emit,
  ) async {
    if (state is! ProtocolParametersLoaded) return;
    final loadedState = state as ProtocolParametersLoaded;
    final currentFormState = loadedState.formState;
    final paramPath = event.parameterPath;
    FormParameterState? dictParamState = currentFormState[paramPath];
    if (dictParamState == null ||
        dictParamState.definition == null ||
        dictParamState.definition?.config.type != 'dict') {
      return;
    }

    Map<String, dynamic> currentMap = Map<String, dynamic>.from(
      dictParamState.currentValue as Map? ?? {},
    );
    if (currentMap.containsKey(event.oldKey)) {
      /* ... */
    } else {
      /* ... */
      return;
    }
    if (event.oldKey == event.newKey) return;
    if (currentMap.containsKey(event.newKey)) {
      /* emit error */
      return;
    }
    final value = currentMap.remove(event.oldKey);
    currentMap[event.newKey] = value;
    final validationResult = validateParameterValue(
      dictParamState.definition!,
      currentMap,
      mapItems: currentMap,
    );
    final updatedParamState = dictParamState.copyWith(
      currentValue: currentMap,
      isValid: validationResult.isValid,
      validationError: validationResult.validationError,
    );
    final newRichFormState = currentFormState.updateParameterState(
      paramPath,
      updatedParamState,
    );
    emit(
      loadedState.copyWith(
        formState: newRichFormState,
        isFormValid: newRichFormState.isFormValid,
        requiredParametersCompletionPercent:
            newRichFormState.requiredParametersCompletionPercent,
      ),
    );
  }

  Future<void> _onUpdateDictionaryValue(
    UpdateDictionaryValue event,
    Emitter<ProtocolParametersState> emit,
  ) async {
    if (state is! ProtocolParametersLoaded) return;
    final loadedState = state as ProtocolParametersLoaded;
    final currentFormState = loadedState.formState;
    final paramPath = event.parameterPath;
    FormParameterState? dictParamState = currentFormState[paramPath];
    if (dictParamState == null ||
        dictParamState.definition == null ||
        dictParamState.definition?.config.type != 'dict') {
      return;
    }

    Map<String, dynamic> currentMap = Map<String, dynamic>.from(
      dictParamState.currentValue as Map? ?? {},
    );
    if (currentMap.containsKey(event.key)) {
      currentMap[event.key] = event.newValue;
      final validationResult = validateParameterValue(
        dictParamState.definition!,
        currentMap,
        mapItems: currentMap,
        dictItemKey: event.key,
        dictItemValue: event.newValue,
      );
      final updatedParamState = dictParamState.copyWith(
        currentValue: currentMap,
        isValid: validationResult.isValid,
        validationError: validationResult.validationError,
      );
      final newRichFormState = currentFormState.updateParameterState(
        paramPath,
        updatedParamState,
      );
      emit(
        loadedState.copyWith(
          formState: newRichFormState,
          isFormValid: newRichFormState.isFormValid,
          requiredParametersCompletionPercent:
              newRichFormState.requiredParametersCompletionPercent,
        ),
      );
    } else {
      /* ... */
    }
  }

  Future<void> _onAssignValueToDictionaryKey(
    AssignValueToDictionaryKey event,
    Emitter<ProtocolParametersState> emit,
  ) async {
    if (state is! ProtocolParametersLoaded) return;
    final loadedState = state as ProtocolParametersLoaded;
    final currentFormState = loadedState.formState;
    final dictParameterPath = event.dictParameterPath;
    FormParameterState? dictParamState = currentFormState[dictParameterPath];
    if (dictParamState == null ||
        dictParamState.definition == null ||
        dictParamState.definition?.config.type != 'dict') {
      return;
    }

    Map<String, dynamic> currentMap = Map<String, dynamic>.from(
      dictParamState.currentValue as Map? ?? {},
    );
    currentMap[event.targetKey] = event.draggableValue;
    final validationResult = validateParameterValue(
      dictParamState.definition!,
      currentMap,
      mapItems: currentMap,
      dictItemKey: event.targetKey,
      dictItemValue: event.draggableValue,
    );
    final updatedParamState = dictParamState.copyWith(
      currentValue: currentMap,
      isValid: validationResult.isValid,
      validationError: validationResult.validationError,
    );
    final newRichFormState = currentFormState.updateParameterState(
      dictParameterPath,
      updatedParamState,
    );
    emit(
      loadedState.copyWith(
        formState: newRichFormState,
        isFormValid: newRichFormState.isFormValid,
        requiredParametersCompletionPercent:
            newRichFormState.requiredParametersCompletionPercent,
      ),
    );
  }
}
