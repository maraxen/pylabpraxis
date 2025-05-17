// FILE: lib/src/data/models/protocol/parameter_config.dart
// Purpose: Defines the configuration for a single protocol parameter, including its type and constraints.
// Corresponds to: ParameterConfig, Constraint, KeyConstraint, ValueConstraint, SubvariableConfig in protocol.models.ts

import 'package:freezed_annotation/freezed_annotation.dart';

part 'parameter_config.freezed.dart';
part 'parameter_config.g.dart';

// Enum for the type of parameter.
// Corresponds to: ParameterConfig['type']
enum ParameterType {
  string,
  integer,
  float, // 'number' in TypeScript can map to float/double in Dart
  boolean,
  array, // Represents a list of items
  dictionary, // Represents a map or key-value pairs
  // Add other types if they exist in your backend, e.g., 'file', 'date'
}

// Enum for the type of constraint, if you have specific constraint types
// that are not directly tied to ParameterType.
// For now, constraints are embedded, but this could be used if 'Constraint' had a 'type' field.
// enum ConstraintType {
//   min_value,
//   max_value,
//   // ... etc.
// }

// Base class for constraints. Due to the varied nature of constraints,
// we'll define specific constraint classes or embed them directly.
// The TypeScript 'Constraint' interface is a union of different possible constraint fields.
// In Freezed, we can model this with optional fields in a single class,
// or by using a union if the structures are very different.
// For now, let's use a single class with optional fields.

@freezed
abstract class ConstraintConfig with _$ConstraintConfig {
  const factory ConstraintConfig({
    // Common constraints
    String? description, // Description of the constraint
    bool? editable, // Can the user edit this constrained value/structure?
    bool?
    creatable, // Can the user create new items/keys? (e.g. in an array or dict)
    // String constraints
    @JsonKey(name: 'min_len') int? minLen,
    @JsonKey(name: 'max_len') int? maxLen,
    String? regex, // Regular expression pattern
    // Numeric constraints (integer, float)
    @JsonKey(name: 'min_value')
    num? minValue, // Using num to accommodate int and double
    @JsonKey(name: 'max_value') num? maxValue,
    num? step, // Step value for numeric inputs
    // Array constraints (for ParameterType.array or for choices)
    // List of predefined choices. Can be simple strings or more complex objects.
    List<dynamic>?
    array, // e.g. ['Choice A', 'Choice B'] or [{'value': 1, 'label': 'Option 1'}]
    @JsonKey(name: 'array_len')
    MinMaxConstraint? arrayLen, // Min/max number of items in an array parameter
    // Reference to another parameter (for dynamic constraints)
    // The value of this parameter might depend on or be filtered by another parameter's value.
    String? param, // Name of the parameter this constraint refers to
    // Dictionary constraints (for ParameterType.dictionary)
    @JsonKey(name: 'key_constraints') KeyConstraint? keyConstraints,
    @JsonKey(name: 'value_constraints') ValueConstraint? valueConstraints,

    // For mapping types where sub-parameters are defined for each dictionary value
    // e.g. mapping_example_with_subvariables
    // The key is the subvariable name, value is its ParameterConfig.
    Map<String, ParameterConfig>? subvariables,

    // UI hints
    String? unit, // e.g., "mL", "°C"
    String? placeholder, // Placeholder text for input fields
    @Default(false)
    bool? multiline, // For string inputs, should it be a multiline text field?
  }) = _ConstraintConfig;

  factory ConstraintConfig.fromJson(Map<String, dynamic> json) =>
      _$ConstraintConfigFromJson(json);
}

@freezed
abstract class MinMaxConstraint with _$MinMaxConstraint {
  const factory MinMaxConstraint({required int min, required int max}) =
      _MinMaxConstraint;

  factory MinMaxConstraint.fromJson(Map<String, dynamic> json) =>
      _$MinMaxConstraintFromJson(json);
}

// Constraints for keys in a dictionary parameter.
// Corresponds to: KeyConstraint in protocol.models.ts
@freezed
abstract class KeyConstraint with _$KeyConstraint {
  const factory KeyConstraint({
    // Type of the key (e.g., string, integer). Typically string for JSON keys.
    // For simplicity, assuming keys are strings unless specified otherwise.
    // If keys can be other types, this might need a ParameterType enum.
    @Default(ParameterType.string)
    ParameterType type, // Defaulting to string for keys
    String? description,
    // List of predefined choices for keys.
    List<String>? array, // If keys must be chosen from a list
    // Regex for key validation if keys are strings and creatable.
    String? regex,
    // Can the user create new keys?
    @Default(true) bool creatable,
    // Can the user edit existing keys?
    @Default(true) bool editable,
    // Reference to another parameter (e.g. keys should be chosen from values of another param)
    String? param,
  }) = _KeyConstraint;

  factory KeyConstraint.fromJson(Map<String, dynamic> json) =>
      _$KeyConstraintFromJson(json);
}

// Constraints for values in a dictionary parameter.
// Corresponds to: ValueConstraint in protocol.models.ts
@freezed
abstract class ValueConstraint with _$ValueConstraint {
  const factory ValueConstraint({
    // Type of the value.
    required ParameterType type,
    String? description,
    // General constraints applicable to the value based on its type.
    // This reuses the main ConstraintConfig for nested constraints.
    ConstraintConfig? constraints,
    // Can the user edit existing values?
    @Default(true) bool editable,
    // If values are themselves dictionaries with a defined structure
    // This is similar to ConstraintConfig.subvariables but directly on ValueConstraint
    // This allows for defining a schema for the dictionary's values.
    Map<String, ParameterConfig>? subvariables,
    // Reference to another parameter (e.g. values should be chosen from values of another param)
    String? param,
  }) = _ValueConstraint;

  factory ValueConstraint.fromJson(Map<String, dynamic> json) =>
      _$ValueConstraintFromJson(json);
}

// Main ParameterConfig class
// Corresponds to: ParameterConfig in protocol.models.ts
@freezed
abstract class ParameterConfig with _$ParameterConfig {
  const factory ParameterConfig({
    // Unique identifier for the parameter (within the protocol).
    required String name,
    // Data type of the parameter.
    required ParameterType type,
    // Human-readable label for the UI.
    String? label,
    // Detailed description of the parameter.
    String? description,
    // Default value for the parameter.
    @JsonKey(name: 'default_value') dynamic defaultValue,
    // Whether the parameter is required.
    @Default(false) bool required,
    // Grouping hint for UI organization.
    String? group,
    // Order of display within a group or globally.
    int? order,
    // Specific constraints for this parameter.
    ConstraintConfig? constraints,
    // UI hints for rendering (e.g., 'slider', 'color-picker').
    // Could be a string or a map for more complex hints.
    Map<String, dynamic>? ui,
    // Is this parameter considered advanced? (for UI filtering)
    @Default(false) bool advanced,
    // Is this parameter currently hidden in the UI?
    @Default(false) bool hidden,
    // Conditional visibility based on other parameters.
    // e.g. { "param": "otherParamName", "value": "specificValue" }
    // meaning this parameter is visible only if "otherParamName" has "specificValue".
    Map<String, dynamic>? visibleIf,
  }) = _ParameterConfig;

  factory ParameterConfig.fromJson(Map<String, dynamic> json) =>
      _$ParameterConfigFromJson(json);
}

// Note: The `SubvariableConfig` from TypeScript seems to be largely covered by
// `ParameterConfig` itself, especially when used within `ConstraintConfig.subvariables`
// or `ValueConstraint.subvariables`. If `SubvariableConfig` had distinct properties
// not present in `ParameterConfig`, we would create a separate class for it.
// For now, we assume subvariables are defined using instances of `ParameterConfig`.
