import 'package:freezed_annotation/freezed_annotation.dart';

part 'parameter_constraints.freezed.dart';
part 'parameter_constraints.g.dart';

/// Model for parameter constraints that provides type-safe access to constraints
/// This should be generated with `flutter pub run build_runner build`
@freezed
sealed class ParameterConstraints with _$ParameterConstraints {
  const factory ParameterConstraints({
    @JsonKey(name: '_required') bool? required_,
    String? type,
    num? minValue,
    num? maxValue,
    num? step,
    int? minLength,
    int? maxLength,
    String? regex,
    String? regexDescription,
    int? minItems,
    int? maxItems,
    int? minProperties,
    int? maxProperties,
    List<String>? array,
    Map<String, dynamic>? items,
    Map<String, dynamic>? valueConstraints,
    dynamic defaultValue,
  }) = _ParameterConstraints;

  factory ParameterConstraints.fromJson(Map<String, dynamic> json) =>
      _$ParameterConstraintsFromJson(json);

  /// A temporary factory to create from raw maps (can be used until code generation is run)
  factory ParameterConstraints.fromMap(Map<String, dynamic> map) {
    return ParameterConstraints(
      required_: map['_required'] as bool?,
      type: map['type'] as String?,
      minValue: map['minValue'] as num?,
      maxValue: map['maxValue'] as num?,
      step: map['step'] as num?,
      minLength: map['minLength'] as int?,
      maxLength: map['maxLength'] as int?,
      regex: map['regex'] as String?,
      regexDescription: map['regexDescription'] as String?,
      minItems: map['minItems'] as int?,
      maxItems: map['maxItems'] as int?,
      minProperties: map['minProperties'] as int?,
      maxProperties: map['maxProperties'] as int?,
      array:
          map['array'] != null
              ? (map['array'] as List<dynamic>)
                  .map((e) => e.toString())
                  .toList()
              : null,
      items: map['items'] as Map<String, dynamic>?,
      valueConstraints: map['valueConstraints'] as Map<String, dynamic>?,
      defaultValue: map['defaultValue'],
    );
  }
}

/// Extension to safely access constraint properties from a Map
extension ConstraintsMapExtension on Map<String, dynamic>? {
  bool? get required_ => this?['_required'] as bool?;
  num? get minValue => this?['minValue'] as num?;
  num? get maxValue => this?['maxValue'] as num?;
  num? get step => this?['step'] as num?;
  int? get minLength => this?['minLength'] as int?;
  int? get maxLength => this?['maxLength'] as int?;
  String? get regex => this?['regex'] as String?;
  String? get regexDescription => this?['regexDescription'] as String?;
  List<String>? get array =>
      this?['array'] != null
          ? (this!['array'] as List<dynamic>).map((e) => e.toString()).toList()
          : null;
  Map<String, dynamic>? get items => this?['items'] as Map<String, dynamic>?;
  Map<String, dynamic>? get valueConstraints =>
      this?['valueConstraints'] as Map<String, dynamic>?;
}
