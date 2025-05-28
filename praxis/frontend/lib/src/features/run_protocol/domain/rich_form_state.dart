import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:flutter/foundation.dart';
import 'package:praxis_lab_management/src/data/models/protocol/protocol_details.dart';
import 'package:praxis_lab_management/src/data/models/protocol/parameter_config.dart';
import 'package:praxis_lab_management/src/features/run_protocol/domain/parameter_validation_service.dart';

part 'rich_form_state.freezed.dart';

@freezed
abstract class ParameterUIHints with _$ParameterUIHints {
  const factory ParameterUIHints.none() = _NoneHints;
  const factory ParameterUIHints.dropdown({required List<String> choices}) =
      _DropdownHints;
  const factory ParameterUIHints.slider({
    required num minValue,
    required num maxValue,
    num? divisions,
  }) = _SliderHints;
}

@freezed
abstract class FormParameterState with _$FormParameterState {
  const FormParameterState._();

  const factory FormParameterState({
    required String parameterName,
    dynamic currentValue,
    @Default(true) bool isValid,
    String? validationError,
    ParameterUIHints? uiHints,
    ParameterDefinition? definition,
  }) = _FormParameterState;

  bool get isRequired => definition?.config.constraints?.required_ == true;
  bool get hasDefaultValue => definition?.defaultValue != null;

  bool get isSetAndNotDefault {
    if (!isRequired) return true;
    if (currentValue == null) return false;
    if (currentValue is String && currentValue.isEmpty) return false;
    if (currentValue is List && currentValue.isEmpty) {
      if (hasDefaultValue && defaultValueAsListIsEmpty) {
        return false;
      } else if (!hasDefaultValue) {
        return false;
      }
    }
    if (currentValue is Map && currentValue.isEmpty) {
      if (hasDefaultValue && defaultValueAsMapIsEmpty) {
        return false;
      } else if (!hasDefaultValue) {
        return false;
      }
    }
    if (hasDefaultValue) {
      if (currentValue is List && definition!.defaultValue is List) {
        return !listEquals(
          currentValue as List<dynamic>,
          definition!.defaultValue as List<dynamic>,
        );
      }
      if (currentValue is Map && definition!.defaultValue is Map) {
        return !mapEquals(
          currentValue as Map<dynamic, dynamic>,
          definition!.defaultValue as Map<dynamic, dynamic>,
        );
      }
      return currentValue != definition!.defaultValue;
    }
    return true;
  }

  dynamic get defaultValue => definition?.defaultValue;
  bool get defaultValueAsListIsEmpty =>
      defaultValue is List && (defaultValue as List).isEmpty;
  bool get defaultValueAsMapIsEmpty =>
      defaultValue is Map && (defaultValue as Map).isEmpty;
}

@freezed
abstract class RichFormState with _$RichFormState {
  const RichFormState._();

  const factory RichFormState({
    required Map<String, FormParameterState> parameterStates,
    @Default(false) bool isFormValid,
  }) = _RichFormState;

  factory RichFormState.fromProtocolDetails(
    ProtocolDetails details, {
    Map<String, dynamic>? existingConfiguredParameters,
  }) {
    final Map<String, FormParameterState> initialStates = {};

    // Helper to get existing value for a path if available
    dynamic getExistingValue(String path) {
      if (existingConfiguredParameters == null) return null;
      return existingConfiguredParameters.containsKey(path)
          ? existingConfiguredParameters[path]
          : null;
    }

    void processParameterList(
      List<ParameterDefinition> params,
      String groupPath,
    ) {
      for (final paramDef in params) {
        final paramPath =
            groupPath.isEmpty ? paramDef.name : '$groupPath.${paramDef.name}';

        dynamic initialValue = getExistingValue(paramPath);
        bool hasExistingValue = initialValue != null;

        if (!hasExistingValue) {
          // Only use default if no existing value is provided
          initialValue = paramDef.defaultValue;
          if (paramDef.config.type == 'array' && initialValue == null) {
            initialValue = [];
          } else if (paramDef.config.type == 'dict' && initialValue == null) {
            initialValue = {};
          }
        }

        ParameterUIHints uiHints = const ParameterUIHints.none();
        if (paramDef.config.constraints?.array != null &&
            paramDef.config.constraints!.array!.isNotEmpty) {
          uiHints = ParameterUIHints.dropdown(
            choices:
                paramDef.config.constraints!.array!
                    .map((e) => e.toString())
                    .toList(),
          );
        } else if (paramDef.config.constraints?.minValue != null &&
            paramDef.config.constraints?.maxValue != null) {
          uiHints = ParameterUIHints.slider(
            minValue: paramDef.config.constraints!.minValue!,
            maxValue: paramDef.config.constraints!.maxValue!,
          );
        }

        // Initial validation using the shared validation service
        final validationResult =
            ParameterValidationService.validateParameterValue(
              paramDef,
              initialValue,
              arrayItems:
                  paramDef.config.type == 'array'
                      ? (initialValue as List<dynamic>?)
                      : null,
              mapItems:
                  paramDef.config.type == 'dict'
                      ? (initialValue as Map<String, dynamic>?)
                      : null,
            );

        initialStates[paramPath] = FormParameterState(
          parameterName: paramDef.name,
          currentValue: initialValue,
          isValid: validationResult.isValid,
          validationError: validationResult.validationError,
          uiHints: uiHints,
          definition: paramDef,
        );
      }
    }

    // Process main parameters
    // Convert parameters map to a list of ParameterDefinition objects
    final parametersList = details.parameterDefinitions.values.toList();
    processParameterList(parametersList, '');

    final List<ParameterGroup> parameterGroups = details.derivedParameterGroups;
    for (final group in parameterGroups) {
      if (group != 'default') {
        processParameterList(group.parameters ?? [], group.name);
      }
    }

    final bool overallFormValidity = initialStates.values.every(
      (ps) => ps.isValid,
    );

    return RichFormState(
      parameterStates: initialStates,
      isFormValid: overallFormValidity,
    );
  }

  FormParameterState? operator [](String parameterPath) =>
      parameterStates[parameterPath];

  RichFormState updateParameterState(
    String parameterPath,
    FormParameterState newState,
  ) {
    final newStates = Map<String, FormParameterState>.from(parameterStates);
    newStates[parameterPath] = newState;
    final bool newFormValidity = newStates.values.every(
      (state) => state.isValid,
    );
    return copyWith(parameterStates: newStates, isFormValid: newFormValidity);
  }

  int get totalRequiredParameters {
    return parameterStates.values.where((ps) => ps.isRequired).length;
  }

  int get setRequiredParametersNotDefault {
    return parameterStates.values
        .where((ps) => ps.isRequired && ps.isSetAndNotDefault && ps.isValid)
        .length;
  }

  double get requiredParametersCompletionPercent {
    final total = totalRequiredParameters;
    if (total == 0) return 1.0;
    return (setRequiredParametersNotDefault / total).clamp(0.0, 1.0);
  }

  bool get isAnyParameterInvalid {
    return parameterStates.values.any((state) => !state.isValid);
  }

  // Keep the existing getter to avoid breaking code
  bool get getFormValid => isFormValid;
}
