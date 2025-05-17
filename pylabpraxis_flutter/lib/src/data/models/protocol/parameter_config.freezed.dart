// dart format width=80
// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'parameter_config.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$ConstraintConfig {

// Common constraints
 String? get description;// Description of the constraint
 bool? get editable;// Can the user edit this constrained value/structure?
 bool? get creatable;// Can the user create new items/keys? (e.g. in an array or dict)
// String constraints
@JsonKey(name: 'min_len') int? get minLen;@JsonKey(name: 'max_len') int? get maxLen; String? get regex;// Regular expression pattern
// Numeric constraints (integer, float)
@JsonKey(name: 'min_value') num? get minValue;// Using num to accommodate int and double
@JsonKey(name: 'max_value') num? get maxValue; num? get step;// Step value for numeric inputs
// Array constraints (for ParameterType.array or for choices)
// List of predefined choices. Can be simple strings or more complex objects.
 List<dynamic>? get array;// e.g. ['Choice A', 'Choice B'] or [{'value': 1, 'label': 'Option 1'}]
@JsonKey(name: 'array_len') MinMaxConstraint? get arrayLen;// Min/max number of items in an array parameter
// Reference to another parameter (for dynamic constraints)
// The value of this parameter might depend on or be filtered by another parameter's value.
 String? get param;// Name of the parameter this constraint refers to
// Dictionary constraints (for ParameterType.dictionary)
@JsonKey(name: 'key_constraints') KeyConstraint? get keyConstraints;@JsonKey(name: 'value_constraints') ValueConstraint? get valueConstraints;// For mapping types where sub-parameters are defined for each dictionary value
// e.g. mapping_example_with_subvariables
// The key is the subvariable name, value is its ParameterConfig.
 Map<String, ParameterConfig>? get subvariables;// UI hints
 String? get unit;// e.g., "mL", "°C"
 String? get placeholder;// Placeholder text for input fields
 bool? get multiline;
/// Create a copy of ConstraintConfig
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ConstraintConfigCopyWith<ConstraintConfig> get copyWith => _$ConstraintConfigCopyWithImpl<ConstraintConfig>(this as ConstraintConfig, _$identity);

  /// Serializes this ConstraintConfig to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ConstraintConfig&&(identical(other.description, description) || other.description == description)&&(identical(other.editable, editable) || other.editable == editable)&&(identical(other.creatable, creatable) || other.creatable == creatable)&&(identical(other.minLen, minLen) || other.minLen == minLen)&&(identical(other.maxLen, maxLen) || other.maxLen == maxLen)&&(identical(other.regex, regex) || other.regex == regex)&&(identical(other.minValue, minValue) || other.minValue == minValue)&&(identical(other.maxValue, maxValue) || other.maxValue == maxValue)&&(identical(other.step, step) || other.step == step)&&const DeepCollectionEquality().equals(other.array, array)&&(identical(other.arrayLen, arrayLen) || other.arrayLen == arrayLen)&&(identical(other.param, param) || other.param == param)&&(identical(other.keyConstraints, keyConstraints) || other.keyConstraints == keyConstraints)&&(identical(other.valueConstraints, valueConstraints) || other.valueConstraints == valueConstraints)&&const DeepCollectionEquality().equals(other.subvariables, subvariables)&&(identical(other.unit, unit) || other.unit == unit)&&(identical(other.placeholder, placeholder) || other.placeholder == placeholder)&&(identical(other.multiline, multiline) || other.multiline == multiline));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,description,editable,creatable,minLen,maxLen,regex,minValue,maxValue,step,const DeepCollectionEquality().hash(array),arrayLen,param,keyConstraints,valueConstraints,const DeepCollectionEquality().hash(subvariables),unit,placeholder,multiline);

@override
String toString() {
  return 'ConstraintConfig(description: $description, editable: $editable, creatable: $creatable, minLen: $minLen, maxLen: $maxLen, regex: $regex, minValue: $minValue, maxValue: $maxValue, step: $step, array: $array, arrayLen: $arrayLen, param: $param, keyConstraints: $keyConstraints, valueConstraints: $valueConstraints, subvariables: $subvariables, unit: $unit, placeholder: $placeholder, multiline: $multiline)';
}


}

/// @nodoc
abstract mixin class $ConstraintConfigCopyWith<$Res>  {
  factory $ConstraintConfigCopyWith(ConstraintConfig value, $Res Function(ConstraintConfig) _then) = _$ConstraintConfigCopyWithImpl;
@useResult
$Res call({
 String? description, bool? editable, bool? creatable,@JsonKey(name: 'min_len') int? minLen,@JsonKey(name: 'max_len') int? maxLen, String? regex,@JsonKey(name: 'min_value') num? minValue,@JsonKey(name: 'max_value') num? maxValue, num? step, List<dynamic>? array,@JsonKey(name: 'array_len') MinMaxConstraint? arrayLen, String? param,@JsonKey(name: 'key_constraints') KeyConstraint? keyConstraints,@JsonKey(name: 'value_constraints') ValueConstraint? valueConstraints, Map<String, ParameterConfig>? subvariables, String? unit, String? placeholder, bool? multiline
});


$MinMaxConstraintCopyWith<$Res>? get arrayLen;$KeyConstraintCopyWith<$Res>? get keyConstraints;$ValueConstraintCopyWith<$Res>? get valueConstraints;

}
/// @nodoc
class _$ConstraintConfigCopyWithImpl<$Res>
    implements $ConstraintConfigCopyWith<$Res> {
  _$ConstraintConfigCopyWithImpl(this._self, this._then);

  final ConstraintConfig _self;
  final $Res Function(ConstraintConfig) _then;

/// Create a copy of ConstraintConfig
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? description = freezed,Object? editable = freezed,Object? creatable = freezed,Object? minLen = freezed,Object? maxLen = freezed,Object? regex = freezed,Object? minValue = freezed,Object? maxValue = freezed,Object? step = freezed,Object? array = freezed,Object? arrayLen = freezed,Object? param = freezed,Object? keyConstraints = freezed,Object? valueConstraints = freezed,Object? subvariables = freezed,Object? unit = freezed,Object? placeholder = freezed,Object? multiline = freezed,}) {
  return _then(_self.copyWith(
description: freezed == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as String?,editable: freezed == editable ? _self.editable : editable // ignore: cast_nullable_to_non_nullable
as bool?,creatable: freezed == creatable ? _self.creatable : creatable // ignore: cast_nullable_to_non_nullable
as bool?,minLen: freezed == minLen ? _self.minLen : minLen // ignore: cast_nullable_to_non_nullable
as int?,maxLen: freezed == maxLen ? _self.maxLen : maxLen // ignore: cast_nullable_to_non_nullable
as int?,regex: freezed == regex ? _self.regex : regex // ignore: cast_nullable_to_non_nullable
as String?,minValue: freezed == minValue ? _self.minValue : minValue // ignore: cast_nullable_to_non_nullable
as num?,maxValue: freezed == maxValue ? _self.maxValue : maxValue // ignore: cast_nullable_to_non_nullable
as num?,step: freezed == step ? _self.step : step // ignore: cast_nullable_to_non_nullable
as num?,array: freezed == array ? _self.array : array // ignore: cast_nullable_to_non_nullable
as List<dynamic>?,arrayLen: freezed == arrayLen ? _self.arrayLen : arrayLen // ignore: cast_nullable_to_non_nullable
as MinMaxConstraint?,param: freezed == param ? _self.param : param // ignore: cast_nullable_to_non_nullable
as String?,keyConstraints: freezed == keyConstraints ? _self.keyConstraints : keyConstraints // ignore: cast_nullable_to_non_nullable
as KeyConstraint?,valueConstraints: freezed == valueConstraints ? _self.valueConstraints : valueConstraints // ignore: cast_nullable_to_non_nullable
as ValueConstraint?,subvariables: freezed == subvariables ? _self.subvariables : subvariables // ignore: cast_nullable_to_non_nullable
as Map<String, ParameterConfig>?,unit: freezed == unit ? _self.unit : unit // ignore: cast_nullable_to_non_nullable
as String?,placeholder: freezed == placeholder ? _self.placeholder : placeholder // ignore: cast_nullable_to_non_nullable
as String?,multiline: freezed == multiline ? _self.multiline : multiline // ignore: cast_nullable_to_non_nullable
as bool?,
  ));
}
/// Create a copy of ConstraintConfig
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$MinMaxConstraintCopyWith<$Res>? get arrayLen {
    if (_self.arrayLen == null) {
    return null;
  }

  return $MinMaxConstraintCopyWith<$Res>(_self.arrayLen!, (value) {
    return _then(_self.copyWith(arrayLen: value));
  });
}/// Create a copy of ConstraintConfig
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$KeyConstraintCopyWith<$Res>? get keyConstraints {
    if (_self.keyConstraints == null) {
    return null;
  }

  return $KeyConstraintCopyWith<$Res>(_self.keyConstraints!, (value) {
    return _then(_self.copyWith(keyConstraints: value));
  });
}/// Create a copy of ConstraintConfig
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$ValueConstraintCopyWith<$Res>? get valueConstraints {
    if (_self.valueConstraints == null) {
    return null;
  }

  return $ValueConstraintCopyWith<$Res>(_self.valueConstraints!, (value) {
    return _then(_self.copyWith(valueConstraints: value));
  });
}
}


/// @nodoc
@JsonSerializable()

class _ConstraintConfig implements ConstraintConfig {
  const _ConstraintConfig({this.description, this.editable, this.creatable, @JsonKey(name: 'min_len') this.minLen, @JsonKey(name: 'max_len') this.maxLen, this.regex, @JsonKey(name: 'min_value') this.minValue, @JsonKey(name: 'max_value') this.maxValue, this.step, final  List<dynamic>? array, @JsonKey(name: 'array_len') this.arrayLen, this.param, @JsonKey(name: 'key_constraints') this.keyConstraints, @JsonKey(name: 'value_constraints') this.valueConstraints, final  Map<String, ParameterConfig>? subvariables, this.unit, this.placeholder, this.multiline = false}): _array = array,_subvariables = subvariables;
  factory _ConstraintConfig.fromJson(Map<String, dynamic> json) => _$ConstraintConfigFromJson(json);

// Common constraints
@override final  String? description;
// Description of the constraint
@override final  bool? editable;
// Can the user edit this constrained value/structure?
@override final  bool? creatable;
// Can the user create new items/keys? (e.g. in an array or dict)
// String constraints
@override@JsonKey(name: 'min_len') final  int? minLen;
@override@JsonKey(name: 'max_len') final  int? maxLen;
@override final  String? regex;
// Regular expression pattern
// Numeric constraints (integer, float)
@override@JsonKey(name: 'min_value') final  num? minValue;
// Using num to accommodate int and double
@override@JsonKey(name: 'max_value') final  num? maxValue;
@override final  num? step;
// Step value for numeric inputs
// Array constraints (for ParameterType.array or for choices)
// List of predefined choices. Can be simple strings or more complex objects.
 final  List<dynamic>? _array;
// Step value for numeric inputs
// Array constraints (for ParameterType.array or for choices)
// List of predefined choices. Can be simple strings or more complex objects.
@override List<dynamic>? get array {
  final value = _array;
  if (value == null) return null;
  if (_array is EqualUnmodifiableListView) return _array;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(value);
}

// e.g. ['Choice A', 'Choice B'] or [{'value': 1, 'label': 'Option 1'}]
@override@JsonKey(name: 'array_len') final  MinMaxConstraint? arrayLen;
// Min/max number of items in an array parameter
// Reference to another parameter (for dynamic constraints)
// The value of this parameter might depend on or be filtered by another parameter's value.
@override final  String? param;
// Name of the parameter this constraint refers to
// Dictionary constraints (for ParameterType.dictionary)
@override@JsonKey(name: 'key_constraints') final  KeyConstraint? keyConstraints;
@override@JsonKey(name: 'value_constraints') final  ValueConstraint? valueConstraints;
// For mapping types where sub-parameters are defined for each dictionary value
// e.g. mapping_example_with_subvariables
// The key is the subvariable name, value is its ParameterConfig.
 final  Map<String, ParameterConfig>? _subvariables;
// For mapping types where sub-parameters are defined for each dictionary value
// e.g. mapping_example_with_subvariables
// The key is the subvariable name, value is its ParameterConfig.
@override Map<String, ParameterConfig>? get subvariables {
  final value = _subvariables;
  if (value == null) return null;
  if (_subvariables is EqualUnmodifiableMapView) return _subvariables;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(value);
}

// UI hints
@override final  String? unit;
// e.g., "mL", "°C"
@override final  String? placeholder;
// Placeholder text for input fields
@override@JsonKey() final  bool? multiline;

/// Create a copy of ConstraintConfig
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ConstraintConfigCopyWith<_ConstraintConfig> get copyWith => __$ConstraintConfigCopyWithImpl<_ConstraintConfig>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ConstraintConfigToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _ConstraintConfig&&(identical(other.description, description) || other.description == description)&&(identical(other.editable, editable) || other.editable == editable)&&(identical(other.creatable, creatable) || other.creatable == creatable)&&(identical(other.minLen, minLen) || other.minLen == minLen)&&(identical(other.maxLen, maxLen) || other.maxLen == maxLen)&&(identical(other.regex, regex) || other.regex == regex)&&(identical(other.minValue, minValue) || other.minValue == minValue)&&(identical(other.maxValue, maxValue) || other.maxValue == maxValue)&&(identical(other.step, step) || other.step == step)&&const DeepCollectionEquality().equals(other._array, _array)&&(identical(other.arrayLen, arrayLen) || other.arrayLen == arrayLen)&&(identical(other.param, param) || other.param == param)&&(identical(other.keyConstraints, keyConstraints) || other.keyConstraints == keyConstraints)&&(identical(other.valueConstraints, valueConstraints) || other.valueConstraints == valueConstraints)&&const DeepCollectionEquality().equals(other._subvariables, _subvariables)&&(identical(other.unit, unit) || other.unit == unit)&&(identical(other.placeholder, placeholder) || other.placeholder == placeholder)&&(identical(other.multiline, multiline) || other.multiline == multiline));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,description,editable,creatable,minLen,maxLen,regex,minValue,maxValue,step,const DeepCollectionEquality().hash(_array),arrayLen,param,keyConstraints,valueConstraints,const DeepCollectionEquality().hash(_subvariables),unit,placeholder,multiline);

@override
String toString() {
  return 'ConstraintConfig(description: $description, editable: $editable, creatable: $creatable, minLen: $minLen, maxLen: $maxLen, regex: $regex, minValue: $minValue, maxValue: $maxValue, step: $step, array: $array, arrayLen: $arrayLen, param: $param, keyConstraints: $keyConstraints, valueConstraints: $valueConstraints, subvariables: $subvariables, unit: $unit, placeholder: $placeholder, multiline: $multiline)';
}


}

/// @nodoc
abstract mixin class _$ConstraintConfigCopyWith<$Res> implements $ConstraintConfigCopyWith<$Res> {
  factory _$ConstraintConfigCopyWith(_ConstraintConfig value, $Res Function(_ConstraintConfig) _then) = __$ConstraintConfigCopyWithImpl;
@override @useResult
$Res call({
 String? description, bool? editable, bool? creatable,@JsonKey(name: 'min_len') int? minLen,@JsonKey(name: 'max_len') int? maxLen, String? regex,@JsonKey(name: 'min_value') num? minValue,@JsonKey(name: 'max_value') num? maxValue, num? step, List<dynamic>? array,@JsonKey(name: 'array_len') MinMaxConstraint? arrayLen, String? param,@JsonKey(name: 'key_constraints') KeyConstraint? keyConstraints,@JsonKey(name: 'value_constraints') ValueConstraint? valueConstraints, Map<String, ParameterConfig>? subvariables, String? unit, String? placeholder, bool? multiline
});


@override $MinMaxConstraintCopyWith<$Res>? get arrayLen;@override $KeyConstraintCopyWith<$Res>? get keyConstraints;@override $ValueConstraintCopyWith<$Res>? get valueConstraints;

}
/// @nodoc
class __$ConstraintConfigCopyWithImpl<$Res>
    implements _$ConstraintConfigCopyWith<$Res> {
  __$ConstraintConfigCopyWithImpl(this._self, this._then);

  final _ConstraintConfig _self;
  final $Res Function(_ConstraintConfig) _then;

/// Create a copy of ConstraintConfig
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? description = freezed,Object? editable = freezed,Object? creatable = freezed,Object? minLen = freezed,Object? maxLen = freezed,Object? regex = freezed,Object? minValue = freezed,Object? maxValue = freezed,Object? step = freezed,Object? array = freezed,Object? arrayLen = freezed,Object? param = freezed,Object? keyConstraints = freezed,Object? valueConstraints = freezed,Object? subvariables = freezed,Object? unit = freezed,Object? placeholder = freezed,Object? multiline = freezed,}) {
  return _then(_ConstraintConfig(
description: freezed == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as String?,editable: freezed == editable ? _self.editable : editable // ignore: cast_nullable_to_non_nullable
as bool?,creatable: freezed == creatable ? _self.creatable : creatable // ignore: cast_nullable_to_non_nullable
as bool?,minLen: freezed == minLen ? _self.minLen : minLen // ignore: cast_nullable_to_non_nullable
as int?,maxLen: freezed == maxLen ? _self.maxLen : maxLen // ignore: cast_nullable_to_non_nullable
as int?,regex: freezed == regex ? _self.regex : regex // ignore: cast_nullable_to_non_nullable
as String?,minValue: freezed == minValue ? _self.minValue : minValue // ignore: cast_nullable_to_non_nullable
as num?,maxValue: freezed == maxValue ? _self.maxValue : maxValue // ignore: cast_nullable_to_non_nullable
as num?,step: freezed == step ? _self.step : step // ignore: cast_nullable_to_non_nullable
as num?,array: freezed == array ? _self._array : array // ignore: cast_nullable_to_non_nullable
as List<dynamic>?,arrayLen: freezed == arrayLen ? _self.arrayLen : arrayLen // ignore: cast_nullable_to_non_nullable
as MinMaxConstraint?,param: freezed == param ? _self.param : param // ignore: cast_nullable_to_non_nullable
as String?,keyConstraints: freezed == keyConstraints ? _self.keyConstraints : keyConstraints // ignore: cast_nullable_to_non_nullable
as KeyConstraint?,valueConstraints: freezed == valueConstraints ? _self.valueConstraints : valueConstraints // ignore: cast_nullable_to_non_nullable
as ValueConstraint?,subvariables: freezed == subvariables ? _self._subvariables : subvariables // ignore: cast_nullable_to_non_nullable
as Map<String, ParameterConfig>?,unit: freezed == unit ? _self.unit : unit // ignore: cast_nullable_to_non_nullable
as String?,placeholder: freezed == placeholder ? _self.placeholder : placeholder // ignore: cast_nullable_to_non_nullable
as String?,multiline: freezed == multiline ? _self.multiline : multiline // ignore: cast_nullable_to_non_nullable
as bool?,
  ));
}

/// Create a copy of ConstraintConfig
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$MinMaxConstraintCopyWith<$Res>? get arrayLen {
    if (_self.arrayLen == null) {
    return null;
  }

  return $MinMaxConstraintCopyWith<$Res>(_self.arrayLen!, (value) {
    return _then(_self.copyWith(arrayLen: value));
  });
}/// Create a copy of ConstraintConfig
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$KeyConstraintCopyWith<$Res>? get keyConstraints {
    if (_self.keyConstraints == null) {
    return null;
  }

  return $KeyConstraintCopyWith<$Res>(_self.keyConstraints!, (value) {
    return _then(_self.copyWith(keyConstraints: value));
  });
}/// Create a copy of ConstraintConfig
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$ValueConstraintCopyWith<$Res>? get valueConstraints {
    if (_self.valueConstraints == null) {
    return null;
  }

  return $ValueConstraintCopyWith<$Res>(_self.valueConstraints!, (value) {
    return _then(_self.copyWith(valueConstraints: value));
  });
}
}


/// @nodoc
mixin _$MinMaxConstraint {

 int get min; int get max;
/// Create a copy of MinMaxConstraint
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$MinMaxConstraintCopyWith<MinMaxConstraint> get copyWith => _$MinMaxConstraintCopyWithImpl<MinMaxConstraint>(this as MinMaxConstraint, _$identity);

  /// Serializes this MinMaxConstraint to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is MinMaxConstraint&&(identical(other.min, min) || other.min == min)&&(identical(other.max, max) || other.max == max));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,min,max);

@override
String toString() {
  return 'MinMaxConstraint(min: $min, max: $max)';
}


}

/// @nodoc
abstract mixin class $MinMaxConstraintCopyWith<$Res>  {
  factory $MinMaxConstraintCopyWith(MinMaxConstraint value, $Res Function(MinMaxConstraint) _then) = _$MinMaxConstraintCopyWithImpl;
@useResult
$Res call({
 int min, int max
});




}
/// @nodoc
class _$MinMaxConstraintCopyWithImpl<$Res>
    implements $MinMaxConstraintCopyWith<$Res> {
  _$MinMaxConstraintCopyWithImpl(this._self, this._then);

  final MinMaxConstraint _self;
  final $Res Function(MinMaxConstraint) _then;

/// Create a copy of MinMaxConstraint
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? min = null,Object? max = null,}) {
  return _then(_self.copyWith(
min: null == min ? _self.min : min // ignore: cast_nullable_to_non_nullable
as int,max: null == max ? _self.max : max // ignore: cast_nullable_to_non_nullable
as int,
  ));
}

}


/// @nodoc
@JsonSerializable()

class _MinMaxConstraint implements MinMaxConstraint {
  const _MinMaxConstraint({required this.min, required this.max});
  factory _MinMaxConstraint.fromJson(Map<String, dynamic> json) => _$MinMaxConstraintFromJson(json);

@override final  int min;
@override final  int max;

/// Create a copy of MinMaxConstraint
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$MinMaxConstraintCopyWith<_MinMaxConstraint> get copyWith => __$MinMaxConstraintCopyWithImpl<_MinMaxConstraint>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$MinMaxConstraintToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _MinMaxConstraint&&(identical(other.min, min) || other.min == min)&&(identical(other.max, max) || other.max == max));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,min,max);

@override
String toString() {
  return 'MinMaxConstraint(min: $min, max: $max)';
}


}

/// @nodoc
abstract mixin class _$MinMaxConstraintCopyWith<$Res> implements $MinMaxConstraintCopyWith<$Res> {
  factory _$MinMaxConstraintCopyWith(_MinMaxConstraint value, $Res Function(_MinMaxConstraint) _then) = __$MinMaxConstraintCopyWithImpl;
@override @useResult
$Res call({
 int min, int max
});




}
/// @nodoc
class __$MinMaxConstraintCopyWithImpl<$Res>
    implements _$MinMaxConstraintCopyWith<$Res> {
  __$MinMaxConstraintCopyWithImpl(this._self, this._then);

  final _MinMaxConstraint _self;
  final $Res Function(_MinMaxConstraint) _then;

/// Create a copy of MinMaxConstraint
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? min = null,Object? max = null,}) {
  return _then(_MinMaxConstraint(
min: null == min ? _self.min : min // ignore: cast_nullable_to_non_nullable
as int,max: null == max ? _self.max : max // ignore: cast_nullable_to_non_nullable
as int,
  ));
}


}


/// @nodoc
mixin _$KeyConstraint {

// Type of the key (e.g., string, integer). Typically string for JSON keys.
// For simplicity, assuming keys are strings unless specified otherwise.
// If keys can be other types, this might need a ParameterType enum.
 ParameterType get type;// Defaulting to string for keys
 String? get description;// List of predefined choices for keys.
 List<String>? get array;// If keys must be chosen from a list
// Regex for key validation if keys are strings and creatable.
 String? get regex;// Can the user create new keys?
 bool get creatable;// Can the user edit existing keys?
 bool get editable;// Reference to another parameter (e.g. keys should be chosen from values of another param)
 String? get param;
/// Create a copy of KeyConstraint
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$KeyConstraintCopyWith<KeyConstraint> get copyWith => _$KeyConstraintCopyWithImpl<KeyConstraint>(this as KeyConstraint, _$identity);

  /// Serializes this KeyConstraint to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is KeyConstraint&&(identical(other.type, type) || other.type == type)&&(identical(other.description, description) || other.description == description)&&const DeepCollectionEquality().equals(other.array, array)&&(identical(other.regex, regex) || other.regex == regex)&&(identical(other.creatable, creatable) || other.creatable == creatable)&&(identical(other.editable, editable) || other.editable == editable)&&(identical(other.param, param) || other.param == param));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,type,description,const DeepCollectionEquality().hash(array),regex,creatable,editable,param);

@override
String toString() {
  return 'KeyConstraint(type: $type, description: $description, array: $array, regex: $regex, creatable: $creatable, editable: $editable, param: $param)';
}


}

/// @nodoc
abstract mixin class $KeyConstraintCopyWith<$Res>  {
  factory $KeyConstraintCopyWith(KeyConstraint value, $Res Function(KeyConstraint) _then) = _$KeyConstraintCopyWithImpl;
@useResult
$Res call({
 ParameterType type, String? description, List<String>? array, String? regex, bool creatable, bool editable, String? param
});




}
/// @nodoc
class _$KeyConstraintCopyWithImpl<$Res>
    implements $KeyConstraintCopyWith<$Res> {
  _$KeyConstraintCopyWithImpl(this._self, this._then);

  final KeyConstraint _self;
  final $Res Function(KeyConstraint) _then;

/// Create a copy of KeyConstraint
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? type = null,Object? description = freezed,Object? array = freezed,Object? regex = freezed,Object? creatable = null,Object? editable = null,Object? param = freezed,}) {
  return _then(_self.copyWith(
type: null == type ? _self.type : type // ignore: cast_nullable_to_non_nullable
as ParameterType,description: freezed == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as String?,array: freezed == array ? _self.array : array // ignore: cast_nullable_to_non_nullable
as List<String>?,regex: freezed == regex ? _self.regex : regex // ignore: cast_nullable_to_non_nullable
as String?,creatable: null == creatable ? _self.creatable : creatable // ignore: cast_nullable_to_non_nullable
as bool,editable: null == editable ? _self.editable : editable // ignore: cast_nullable_to_non_nullable
as bool,param: freezed == param ? _self.param : param // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

}


/// @nodoc
@JsonSerializable()

class _KeyConstraint implements KeyConstraint {
  const _KeyConstraint({this.type = ParameterType.string, this.description, final  List<String>? array, this.regex, this.creatable = true, this.editable = true, this.param}): _array = array;
  factory _KeyConstraint.fromJson(Map<String, dynamic> json) => _$KeyConstraintFromJson(json);

// Type of the key (e.g., string, integer). Typically string for JSON keys.
// For simplicity, assuming keys are strings unless specified otherwise.
// If keys can be other types, this might need a ParameterType enum.
@override@JsonKey() final  ParameterType type;
// Defaulting to string for keys
@override final  String? description;
// List of predefined choices for keys.
 final  List<String>? _array;
// List of predefined choices for keys.
@override List<String>? get array {
  final value = _array;
  if (value == null) return null;
  if (_array is EqualUnmodifiableListView) return _array;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(value);
}

// If keys must be chosen from a list
// Regex for key validation if keys are strings and creatable.
@override final  String? regex;
// Can the user create new keys?
@override@JsonKey() final  bool creatable;
// Can the user edit existing keys?
@override@JsonKey() final  bool editable;
// Reference to another parameter (e.g. keys should be chosen from values of another param)
@override final  String? param;

/// Create a copy of KeyConstraint
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$KeyConstraintCopyWith<_KeyConstraint> get copyWith => __$KeyConstraintCopyWithImpl<_KeyConstraint>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$KeyConstraintToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _KeyConstraint&&(identical(other.type, type) || other.type == type)&&(identical(other.description, description) || other.description == description)&&const DeepCollectionEquality().equals(other._array, _array)&&(identical(other.regex, regex) || other.regex == regex)&&(identical(other.creatable, creatable) || other.creatable == creatable)&&(identical(other.editable, editable) || other.editable == editable)&&(identical(other.param, param) || other.param == param));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,type,description,const DeepCollectionEquality().hash(_array),regex,creatable,editable,param);

@override
String toString() {
  return 'KeyConstraint(type: $type, description: $description, array: $array, regex: $regex, creatable: $creatable, editable: $editable, param: $param)';
}


}

/// @nodoc
abstract mixin class _$KeyConstraintCopyWith<$Res> implements $KeyConstraintCopyWith<$Res> {
  factory _$KeyConstraintCopyWith(_KeyConstraint value, $Res Function(_KeyConstraint) _then) = __$KeyConstraintCopyWithImpl;
@override @useResult
$Res call({
 ParameterType type, String? description, List<String>? array, String? regex, bool creatable, bool editable, String? param
});




}
/// @nodoc
class __$KeyConstraintCopyWithImpl<$Res>
    implements _$KeyConstraintCopyWith<$Res> {
  __$KeyConstraintCopyWithImpl(this._self, this._then);

  final _KeyConstraint _self;
  final $Res Function(_KeyConstraint) _then;

/// Create a copy of KeyConstraint
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? type = null,Object? description = freezed,Object? array = freezed,Object? regex = freezed,Object? creatable = null,Object? editable = null,Object? param = freezed,}) {
  return _then(_KeyConstraint(
type: null == type ? _self.type : type // ignore: cast_nullable_to_non_nullable
as ParameterType,description: freezed == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as String?,array: freezed == array ? _self._array : array // ignore: cast_nullable_to_non_nullable
as List<String>?,regex: freezed == regex ? _self.regex : regex // ignore: cast_nullable_to_non_nullable
as String?,creatable: null == creatable ? _self.creatable : creatable // ignore: cast_nullable_to_non_nullable
as bool,editable: null == editable ? _self.editable : editable // ignore: cast_nullable_to_non_nullable
as bool,param: freezed == param ? _self.param : param // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}


}


/// @nodoc
mixin _$ValueConstraint {

// Type of the value.
 ParameterType get type; String? get description;// General constraints applicable to the value based on its type.
// This reuses the main ConstraintConfig for nested constraints.
 ConstraintConfig? get constraints;// Can the user edit existing values?
 bool get editable;// If values are themselves dictionaries with a defined structure
// This is similar to ConstraintConfig.subvariables but directly on ValueConstraint
// This allows for defining a schema for the dictionary's values.
 Map<String, ParameterConfig>? get subvariables;// Reference to another parameter (e.g. values should be chosen from values of another param)
 String? get param;
/// Create a copy of ValueConstraint
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ValueConstraintCopyWith<ValueConstraint> get copyWith => _$ValueConstraintCopyWithImpl<ValueConstraint>(this as ValueConstraint, _$identity);

  /// Serializes this ValueConstraint to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ValueConstraint&&(identical(other.type, type) || other.type == type)&&(identical(other.description, description) || other.description == description)&&(identical(other.constraints, constraints) || other.constraints == constraints)&&(identical(other.editable, editable) || other.editable == editable)&&const DeepCollectionEquality().equals(other.subvariables, subvariables)&&(identical(other.param, param) || other.param == param));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,type,description,constraints,editable,const DeepCollectionEquality().hash(subvariables),param);

@override
String toString() {
  return 'ValueConstraint(type: $type, description: $description, constraints: $constraints, editable: $editable, subvariables: $subvariables, param: $param)';
}


}

/// @nodoc
abstract mixin class $ValueConstraintCopyWith<$Res>  {
  factory $ValueConstraintCopyWith(ValueConstraint value, $Res Function(ValueConstraint) _then) = _$ValueConstraintCopyWithImpl;
@useResult
$Res call({
 ParameterType type, String? description, ConstraintConfig? constraints, bool editable, Map<String, ParameterConfig>? subvariables, String? param
});


$ConstraintConfigCopyWith<$Res>? get constraints;

}
/// @nodoc
class _$ValueConstraintCopyWithImpl<$Res>
    implements $ValueConstraintCopyWith<$Res> {
  _$ValueConstraintCopyWithImpl(this._self, this._then);

  final ValueConstraint _self;
  final $Res Function(ValueConstraint) _then;

/// Create a copy of ValueConstraint
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? type = null,Object? description = freezed,Object? constraints = freezed,Object? editable = null,Object? subvariables = freezed,Object? param = freezed,}) {
  return _then(_self.copyWith(
type: null == type ? _self.type : type // ignore: cast_nullable_to_non_nullable
as ParameterType,description: freezed == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as String?,constraints: freezed == constraints ? _self.constraints : constraints // ignore: cast_nullable_to_non_nullable
as ConstraintConfig?,editable: null == editable ? _self.editable : editable // ignore: cast_nullable_to_non_nullable
as bool,subvariables: freezed == subvariables ? _self.subvariables : subvariables // ignore: cast_nullable_to_non_nullable
as Map<String, ParameterConfig>?,param: freezed == param ? _self.param : param // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}
/// Create a copy of ValueConstraint
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$ConstraintConfigCopyWith<$Res>? get constraints {
    if (_self.constraints == null) {
    return null;
  }

  return $ConstraintConfigCopyWith<$Res>(_self.constraints!, (value) {
    return _then(_self.copyWith(constraints: value));
  });
}
}


/// @nodoc
@JsonSerializable()

class _ValueConstraint implements ValueConstraint {
  const _ValueConstraint({required this.type, this.description, this.constraints, this.editable = true, final  Map<String, ParameterConfig>? subvariables, this.param}): _subvariables = subvariables;
  factory _ValueConstraint.fromJson(Map<String, dynamic> json) => _$ValueConstraintFromJson(json);

// Type of the value.
@override final  ParameterType type;
@override final  String? description;
// General constraints applicable to the value based on its type.
// This reuses the main ConstraintConfig for nested constraints.
@override final  ConstraintConfig? constraints;
// Can the user edit existing values?
@override@JsonKey() final  bool editable;
// If values are themselves dictionaries with a defined structure
// This is similar to ConstraintConfig.subvariables but directly on ValueConstraint
// This allows for defining a schema for the dictionary's values.
 final  Map<String, ParameterConfig>? _subvariables;
// If values are themselves dictionaries with a defined structure
// This is similar to ConstraintConfig.subvariables but directly on ValueConstraint
// This allows for defining a schema for the dictionary's values.
@override Map<String, ParameterConfig>? get subvariables {
  final value = _subvariables;
  if (value == null) return null;
  if (_subvariables is EqualUnmodifiableMapView) return _subvariables;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(value);
}

// Reference to another parameter (e.g. values should be chosen from values of another param)
@override final  String? param;

/// Create a copy of ValueConstraint
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ValueConstraintCopyWith<_ValueConstraint> get copyWith => __$ValueConstraintCopyWithImpl<_ValueConstraint>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ValueConstraintToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _ValueConstraint&&(identical(other.type, type) || other.type == type)&&(identical(other.description, description) || other.description == description)&&(identical(other.constraints, constraints) || other.constraints == constraints)&&(identical(other.editable, editable) || other.editable == editable)&&const DeepCollectionEquality().equals(other._subvariables, _subvariables)&&(identical(other.param, param) || other.param == param));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,type,description,constraints,editable,const DeepCollectionEquality().hash(_subvariables),param);

@override
String toString() {
  return 'ValueConstraint(type: $type, description: $description, constraints: $constraints, editable: $editable, subvariables: $subvariables, param: $param)';
}


}

/// @nodoc
abstract mixin class _$ValueConstraintCopyWith<$Res> implements $ValueConstraintCopyWith<$Res> {
  factory _$ValueConstraintCopyWith(_ValueConstraint value, $Res Function(_ValueConstraint) _then) = __$ValueConstraintCopyWithImpl;
@override @useResult
$Res call({
 ParameterType type, String? description, ConstraintConfig? constraints, bool editable, Map<String, ParameterConfig>? subvariables, String? param
});


@override $ConstraintConfigCopyWith<$Res>? get constraints;

}
/// @nodoc
class __$ValueConstraintCopyWithImpl<$Res>
    implements _$ValueConstraintCopyWith<$Res> {
  __$ValueConstraintCopyWithImpl(this._self, this._then);

  final _ValueConstraint _self;
  final $Res Function(_ValueConstraint) _then;

/// Create a copy of ValueConstraint
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? type = null,Object? description = freezed,Object? constraints = freezed,Object? editable = null,Object? subvariables = freezed,Object? param = freezed,}) {
  return _then(_ValueConstraint(
type: null == type ? _self.type : type // ignore: cast_nullable_to_non_nullable
as ParameterType,description: freezed == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as String?,constraints: freezed == constraints ? _self.constraints : constraints // ignore: cast_nullable_to_non_nullable
as ConstraintConfig?,editable: null == editable ? _self.editable : editable // ignore: cast_nullable_to_non_nullable
as bool,subvariables: freezed == subvariables ? _self._subvariables : subvariables // ignore: cast_nullable_to_non_nullable
as Map<String, ParameterConfig>?,param: freezed == param ? _self.param : param // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

/// Create a copy of ValueConstraint
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$ConstraintConfigCopyWith<$Res>? get constraints {
    if (_self.constraints == null) {
    return null;
  }

  return $ConstraintConfigCopyWith<$Res>(_self.constraints!, (value) {
    return _then(_self.copyWith(constraints: value));
  });
}
}


/// @nodoc
mixin _$ParameterConfig {

// Unique identifier for the parameter (within the protocol).
 String get name;// Data type of the parameter.
 ParameterType get type;// Human-readable label for the UI.
 String? get label;// Detailed description of the parameter.
 String? get description;// Default value for the parameter.
@JsonKey(name: 'default_value') dynamic get defaultValue;// Whether the parameter is required.
 bool get required;// Grouping hint for UI organization.
 String? get group;// Order of display within a group or globally.
 int? get order;// Specific constraints for this parameter.
 ConstraintConfig? get constraints;// UI hints for rendering (e.g., 'slider', 'color-picker').
// Could be a string or a map for more complex hints.
 Map<String, dynamic>? get ui;// Is this parameter considered advanced? (for UI filtering)
 bool get advanced;// Is this parameter currently hidden in the UI?
 bool get hidden;// Conditional visibility based on other parameters.
// e.g. { "param": "otherParamName", "value": "specificValue" }
// meaning this parameter is visible only if "otherParamName" has "specificValue".
 Map<String, dynamic>? get visibleIf;
/// Create a copy of ParameterConfig
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ParameterConfigCopyWith<ParameterConfig> get copyWith => _$ParameterConfigCopyWithImpl<ParameterConfig>(this as ParameterConfig, _$identity);

  /// Serializes this ParameterConfig to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ParameterConfig&&(identical(other.name, name) || other.name == name)&&(identical(other.type, type) || other.type == type)&&(identical(other.label, label) || other.label == label)&&(identical(other.description, description) || other.description == description)&&const DeepCollectionEquality().equals(other.defaultValue, defaultValue)&&(identical(other.required, required) || other.required == required)&&(identical(other.group, group) || other.group == group)&&(identical(other.order, order) || other.order == order)&&(identical(other.constraints, constraints) || other.constraints == constraints)&&const DeepCollectionEquality().equals(other.ui, ui)&&(identical(other.advanced, advanced) || other.advanced == advanced)&&(identical(other.hidden, hidden) || other.hidden == hidden)&&const DeepCollectionEquality().equals(other.visibleIf, visibleIf));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,name,type,label,description,const DeepCollectionEquality().hash(defaultValue),required,group,order,constraints,const DeepCollectionEquality().hash(ui),advanced,hidden,const DeepCollectionEquality().hash(visibleIf));

@override
String toString() {
  return 'ParameterConfig(name: $name, type: $type, label: $label, description: $description, defaultValue: $defaultValue, required: $required, group: $group, order: $order, constraints: $constraints, ui: $ui, advanced: $advanced, hidden: $hidden, visibleIf: $visibleIf)';
}


}

/// @nodoc
abstract mixin class $ParameterConfigCopyWith<$Res>  {
  factory $ParameterConfigCopyWith(ParameterConfig value, $Res Function(ParameterConfig) _then) = _$ParameterConfigCopyWithImpl;
@useResult
$Res call({
 String name, ParameterType type, String? label, String? description,@JsonKey(name: 'default_value') dynamic defaultValue, bool required, String? group, int? order, ConstraintConfig? constraints, Map<String, dynamic>? ui, bool advanced, bool hidden, Map<String, dynamic>? visibleIf
});


$ConstraintConfigCopyWith<$Res>? get constraints;

}
/// @nodoc
class _$ParameterConfigCopyWithImpl<$Res>
    implements $ParameterConfigCopyWith<$Res> {
  _$ParameterConfigCopyWithImpl(this._self, this._then);

  final ParameterConfig _self;
  final $Res Function(ParameterConfig) _then;

/// Create a copy of ParameterConfig
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? name = null,Object? type = null,Object? label = freezed,Object? description = freezed,Object? defaultValue = freezed,Object? required = null,Object? group = freezed,Object? order = freezed,Object? constraints = freezed,Object? ui = freezed,Object? advanced = null,Object? hidden = null,Object? visibleIf = freezed,}) {
  return _then(_self.copyWith(
name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String,type: null == type ? _self.type : type // ignore: cast_nullable_to_non_nullable
as ParameterType,label: freezed == label ? _self.label : label // ignore: cast_nullable_to_non_nullable
as String?,description: freezed == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as String?,defaultValue: freezed == defaultValue ? _self.defaultValue : defaultValue // ignore: cast_nullable_to_non_nullable
as dynamic,required: null == required ? _self.required : required // ignore: cast_nullable_to_non_nullable
as bool,group: freezed == group ? _self.group : group // ignore: cast_nullable_to_non_nullable
as String?,order: freezed == order ? _self.order : order // ignore: cast_nullable_to_non_nullable
as int?,constraints: freezed == constraints ? _self.constraints : constraints // ignore: cast_nullable_to_non_nullable
as ConstraintConfig?,ui: freezed == ui ? _self.ui : ui // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>?,advanced: null == advanced ? _self.advanced : advanced // ignore: cast_nullable_to_non_nullable
as bool,hidden: null == hidden ? _self.hidden : hidden // ignore: cast_nullable_to_non_nullable
as bool,visibleIf: freezed == visibleIf ? _self.visibleIf : visibleIf // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>?,
  ));
}
/// Create a copy of ParameterConfig
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$ConstraintConfigCopyWith<$Res>? get constraints {
    if (_self.constraints == null) {
    return null;
  }

  return $ConstraintConfigCopyWith<$Res>(_self.constraints!, (value) {
    return _then(_self.copyWith(constraints: value));
  });
}
}


/// @nodoc
@JsonSerializable()

class _ParameterConfig implements ParameterConfig {
  const _ParameterConfig({required this.name, required this.type, this.label, this.description, @JsonKey(name: 'default_value') this.defaultValue, this.required = false, this.group, this.order, this.constraints, final  Map<String, dynamic>? ui, this.advanced = false, this.hidden = false, final  Map<String, dynamic>? visibleIf}): _ui = ui,_visibleIf = visibleIf;
  factory _ParameterConfig.fromJson(Map<String, dynamic> json) => _$ParameterConfigFromJson(json);

// Unique identifier for the parameter (within the protocol).
@override final  String name;
// Data type of the parameter.
@override final  ParameterType type;
// Human-readable label for the UI.
@override final  String? label;
// Detailed description of the parameter.
@override final  String? description;
// Default value for the parameter.
@override@JsonKey(name: 'default_value') final  dynamic defaultValue;
// Whether the parameter is required.
@override@JsonKey() final  bool required;
// Grouping hint for UI organization.
@override final  String? group;
// Order of display within a group or globally.
@override final  int? order;
// Specific constraints for this parameter.
@override final  ConstraintConfig? constraints;
// UI hints for rendering (e.g., 'slider', 'color-picker').
// Could be a string or a map for more complex hints.
 final  Map<String, dynamic>? _ui;
// UI hints for rendering (e.g., 'slider', 'color-picker').
// Could be a string or a map for more complex hints.
@override Map<String, dynamic>? get ui {
  final value = _ui;
  if (value == null) return null;
  if (_ui is EqualUnmodifiableMapView) return _ui;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(value);
}

// Is this parameter considered advanced? (for UI filtering)
@override@JsonKey() final  bool advanced;
// Is this parameter currently hidden in the UI?
@override@JsonKey() final  bool hidden;
// Conditional visibility based on other parameters.
// e.g. { "param": "otherParamName", "value": "specificValue" }
// meaning this parameter is visible only if "otherParamName" has "specificValue".
 final  Map<String, dynamic>? _visibleIf;
// Conditional visibility based on other parameters.
// e.g. { "param": "otherParamName", "value": "specificValue" }
// meaning this parameter is visible only if "otherParamName" has "specificValue".
@override Map<String, dynamic>? get visibleIf {
  final value = _visibleIf;
  if (value == null) return null;
  if (_visibleIf is EqualUnmodifiableMapView) return _visibleIf;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(value);
}


/// Create a copy of ParameterConfig
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ParameterConfigCopyWith<_ParameterConfig> get copyWith => __$ParameterConfigCopyWithImpl<_ParameterConfig>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ParameterConfigToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _ParameterConfig&&(identical(other.name, name) || other.name == name)&&(identical(other.type, type) || other.type == type)&&(identical(other.label, label) || other.label == label)&&(identical(other.description, description) || other.description == description)&&const DeepCollectionEquality().equals(other.defaultValue, defaultValue)&&(identical(other.required, required) || other.required == required)&&(identical(other.group, group) || other.group == group)&&(identical(other.order, order) || other.order == order)&&(identical(other.constraints, constraints) || other.constraints == constraints)&&const DeepCollectionEquality().equals(other._ui, _ui)&&(identical(other.advanced, advanced) || other.advanced == advanced)&&(identical(other.hidden, hidden) || other.hidden == hidden)&&const DeepCollectionEquality().equals(other._visibleIf, _visibleIf));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,name,type,label,description,const DeepCollectionEquality().hash(defaultValue),required,group,order,constraints,const DeepCollectionEquality().hash(_ui),advanced,hidden,const DeepCollectionEquality().hash(_visibleIf));

@override
String toString() {
  return 'ParameterConfig(name: $name, type: $type, label: $label, description: $description, defaultValue: $defaultValue, required: $required, group: $group, order: $order, constraints: $constraints, ui: $ui, advanced: $advanced, hidden: $hidden, visibleIf: $visibleIf)';
}


}

/// @nodoc
abstract mixin class _$ParameterConfigCopyWith<$Res> implements $ParameterConfigCopyWith<$Res> {
  factory _$ParameterConfigCopyWith(_ParameterConfig value, $Res Function(_ParameterConfig) _then) = __$ParameterConfigCopyWithImpl;
@override @useResult
$Res call({
 String name, ParameterType type, String? label, String? description,@JsonKey(name: 'default_value') dynamic defaultValue, bool required, String? group, int? order, ConstraintConfig? constraints, Map<String, dynamic>? ui, bool advanced, bool hidden, Map<String, dynamic>? visibleIf
});


@override $ConstraintConfigCopyWith<$Res>? get constraints;

}
/// @nodoc
class __$ParameterConfigCopyWithImpl<$Res>
    implements _$ParameterConfigCopyWith<$Res> {
  __$ParameterConfigCopyWithImpl(this._self, this._then);

  final _ParameterConfig _self;
  final $Res Function(_ParameterConfig) _then;

/// Create a copy of ParameterConfig
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? name = null,Object? type = null,Object? label = freezed,Object? description = freezed,Object? defaultValue = freezed,Object? required = null,Object? group = freezed,Object? order = freezed,Object? constraints = freezed,Object? ui = freezed,Object? advanced = null,Object? hidden = null,Object? visibleIf = freezed,}) {
  return _then(_ParameterConfig(
name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String,type: null == type ? _self.type : type // ignore: cast_nullable_to_non_nullable
as ParameterType,label: freezed == label ? _self.label : label // ignore: cast_nullable_to_non_nullable
as String?,description: freezed == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as String?,defaultValue: freezed == defaultValue ? _self.defaultValue : defaultValue // ignore: cast_nullable_to_non_nullable
as dynamic,required: null == required ? _self.required : required // ignore: cast_nullable_to_non_nullable
as bool,group: freezed == group ? _self.group : group // ignore: cast_nullable_to_non_nullable
as String?,order: freezed == order ? _self.order : order // ignore: cast_nullable_to_non_nullable
as int?,constraints: freezed == constraints ? _self.constraints : constraints // ignore: cast_nullable_to_non_nullable
as ConstraintConfig?,ui: freezed == ui ? _self._ui : ui // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>?,advanced: null == advanced ? _self.advanced : advanced // ignore: cast_nullable_to_non_nullable
as bool,hidden: null == hidden ? _self.hidden : hidden // ignore: cast_nullable_to_non_nullable
as bool,visibleIf: freezed == visibleIf ? _self._visibleIf : visibleIf // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>?,
  ));
}

/// Create a copy of ParameterConfig
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$ConstraintConfigCopyWith<$Res>? get constraints {
    if (_self.constraints == null) {
    return null;
  }

  return $ConstraintConfigCopyWith<$Res>(_self.constraints!, (value) {
    return _then(_self.copyWith(constraints: value));
  });
}
}

// dart format on
