import 'package:pylabpraxis_flutter/src/data/models/protocol/parameter_config.dart';
import 'package:pylabpraxis_flutter/src/data/models/protocol/parameter_constraints.dart';

class ValidationResult {
  final bool isValid;
  final String? validationError;

  const ValidationResult({required this.isValid, this.validationError});
}

class ParameterValidationService {
  /// Converts a constraint map to a structured ParameterConstraints object
  static ParameterConstraints getConstraints(dynamic constraints) {
    if (constraints == null) return const ParameterConstraints();
    if (constraints is ParameterConstraints) return constraints;
    if (constraints is Map<String, dynamic>) {
      return ParameterConstraints.fromMap(constraints);
    }
    return const ParameterConstraints();
  }

  /// Validates a parameter value based on the parameter definition and constraints
  static ValidationResult validateParameterValue(
    ParameterDefinition paramDef,
    dynamic value, {
    List<dynamic>? arrayItems,
    Map<String, dynamic>? mapItems,
    String? dictItemKey,
    dynamic dictItemValue,
  }) {
    final rawConstraints = paramDef.config.constraints;
    final constraints = getConstraints(rawConstraints);

    // Get item specific constraints for dictionary items
    final itemSpecificConstraints =
        dictItemKey != null && rawConstraints != null
            ? getConstraints(rawConstraints.valueConstraints)
            : constraints;

    // If no constraints and not a dictionary item, it's valid
    if (itemSpecificConstraints == const ParameterConstraints() &&
        dictItemKey == null) {
      return const ValidationResult(isValid: true);
    }

    dynamic valueToValidate = dictItemKey != null ? dictItemValue : value;
    String displayName =
        dictItemKey != null
            ? 'Value for "$dictItemKey"'
            : (paramDef.displayName ?? paramDef.name);
    String paramType =
        dictItemKey != null
            ? (itemSpecificConstraints.type ?? 'unknown')
            : paramDef.config.type;

    // Check if required but empty
    if (itemSpecificConstraints.required_ == true) {
      bool isEmpty = false;
      if (valueToValidate == null) {
        isEmpty = true;
      } else if (valueToValidate is String && valueToValidate.trim().isEmpty) {
        isEmpty = true;
      } else if (valueToValidate is List && valueToValidate.isEmpty) {
        isEmpty = true; // For required arrays, empty means not set
      } else if (valueToValidate is Map && valueToValidate.isEmpty) {
        isEmpty = true; // For required dicts, empty means not set
      }

      if (isEmpty) {
        return ValidationResult(
          isValid: false,
          validationError: '$displayName is required.',
        );
      }
    }

    // Number validation
    if ((paramType == 'number' ||
            paramType == 'integer' ||
            paramType == 'float') &&
        valueToValidate != null) {
      // Convert string to num if needed
      num? numValue;
      if (valueToValidate is String) {
        try {
          if (paramType == 'integer') {
            numValue = int.parse(valueToValidate);
          } else {
            numValue = double.parse(valueToValidate);
          }
        } catch (e) {
          return ValidationResult(
            isValid: false,
            validationError: '$displayName must be a valid number.',
          );
        }
      } else if (valueToValidate is num) {
        numValue = valueToValidate;
      } else {
        return ValidationResult(
          isValid: false,
          validationError: '$displayName must be a number.',
        );
      }

      // Min/Max validation
      if (itemSpecificConstraints.minValue != null &&
          numValue < itemSpecificConstraints.minValue!) {
        return ValidationResult(
          isValid: false,
          validationError:
              '$displayName must be at least ${itemSpecificConstraints.minValue}.',
        );
      }

      if (itemSpecificConstraints.maxValue != null &&
          numValue > itemSpecificConstraints.maxValue!) {
        return ValidationResult(
          isValid: false,
          validationError:
              '$displayName must be at most ${itemSpecificConstraints.maxValue}.',
        );
      }

      // Integer type check
      if (paramType == 'integer' && numValue != numValue.toInt()) {
        return ValidationResult(
          isValid: false,
          validationError: '$displayName must be an integer.',
        );
      }
    }

    // String validation
    if (paramType == 'string' && valueToValidate != null) {
      final strValue = valueToValidate.toString();

      // Length validation
      if (itemSpecificConstraints.minLength != null &&
          strValue.length < itemSpecificConstraints.minLength!) {
        return ValidationResult(
          isValid: false,
          validationError:
              '$displayName must be at least ${itemSpecificConstraints.minLength} characters.',
        );
      }

      if (itemSpecificConstraints.maxLength != null &&
          strValue.length > itemSpecificConstraints.maxLength!) {
        return ValidationResult(
          isValid: false,
          validationError:
              '$displayName must be at most ${itemSpecificConstraints.maxLength} characters.',
        );
      }

      // Regex validation
      if (itemSpecificConstraints.regex != null) {
        final RegExp regex = RegExp(itemSpecificConstraints.regex!);
        if (!regex.hasMatch(strValue)) {
          return ValidationResult(
            isValid: false,
            validationError:
                itemSpecificConstraints.regexDescription ??
                '$displayName does not match required format.',
          );
        }
      }
    }

    // Array validation
    if (paramType == 'array' && arrayItems != null) {
      // Items count validation
      if (itemSpecificConstraints.minItems != null &&
          arrayItems.length < itemSpecificConstraints.minItems!) {
        return ValidationResult(
          isValid: false,
          validationError:
              '$displayName must have at least ${itemSpecificConstraints.minItems} items.',
        );
      }

      if (itemSpecificConstraints.maxItems != null &&
          arrayItems.length > itemSpecificConstraints.maxItems!) {
        return ValidationResult(
          isValid: false,
          validationError:
              '$displayName must have at most ${itemSpecificConstraints.maxItems} items.',
        );
      }

      // TODO: Validate individual array items based on itemSpecificConstraints.items
    }

    // Dictionary validation
    if (paramType == 'dict' && mapItems != null) {
      // Properties count validation
      if (itemSpecificConstraints.minProperties != null &&
          mapItems.length < itemSpecificConstraints.minProperties!) {
        return ValidationResult(
          isValid: false,
          validationError:
              '$displayName must have at least ${itemSpecificConstraints.minProperties} properties.',
        );
      }

      if (itemSpecificConstraints.maxProperties != null &&
          mapItems.length > itemSpecificConstraints.maxProperties!) {
        return ValidationResult(
          isValid: false,
          validationError:
              '$displayName must have at most ${itemSpecificConstraints.maxProperties} properties.',
        );
      }

      // Key validation for specific dictionary item
      if (dictItemKey != null && dictItemValue != null) {
        // Already handled by recursive validation
      }
    }

    return const ValidationResult(isValid: true);
  }
}
