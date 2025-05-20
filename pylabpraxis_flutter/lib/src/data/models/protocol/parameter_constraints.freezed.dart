// dart format width=80
// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'parameter_constraints.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$ParameterConstraints {

@JsonKey(name: '_required') bool? get required_; String? get type; num? get minValue; num? get maxValue; num? get step; int? get minLength; int? get maxLength; String? get regex; String? get regexDescription; int? get minItems; int? get maxItems; int? get minProperties; int? get maxProperties; List<String>? get array; Map<String, dynamic>? get items; Map<String, dynamic>? get valueConstraints; dynamic get defaultValue;
/// Create a copy of ParameterConstraints
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ParameterConstraintsCopyWith<ParameterConstraints> get copyWith => _$ParameterConstraintsCopyWithImpl<ParameterConstraints>(this as ParameterConstraints, _$identity);

  /// Serializes this ParameterConstraints to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ParameterConstraints&&(identical(other.required_, required_) || other.required_ == required_)&&(identical(other.type, type) || other.type == type)&&(identical(other.minValue, minValue) || other.minValue == minValue)&&(identical(other.maxValue, maxValue) || other.maxValue == maxValue)&&(identical(other.step, step) || other.step == step)&&(identical(other.minLength, minLength) || other.minLength == minLength)&&(identical(other.maxLength, maxLength) || other.maxLength == maxLength)&&(identical(other.regex, regex) || other.regex == regex)&&(identical(other.regexDescription, regexDescription) || other.regexDescription == regexDescription)&&(identical(other.minItems, minItems) || other.minItems == minItems)&&(identical(other.maxItems, maxItems) || other.maxItems == maxItems)&&(identical(other.minProperties, minProperties) || other.minProperties == minProperties)&&(identical(other.maxProperties, maxProperties) || other.maxProperties == maxProperties)&&const DeepCollectionEquality().equals(other.array, array)&&const DeepCollectionEquality().equals(other.items, items)&&const DeepCollectionEquality().equals(other.valueConstraints, valueConstraints)&&const DeepCollectionEquality().equals(other.defaultValue, defaultValue));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,required_,type,minValue,maxValue,step,minLength,maxLength,regex,regexDescription,minItems,maxItems,minProperties,maxProperties,const DeepCollectionEquality().hash(array),const DeepCollectionEquality().hash(items),const DeepCollectionEquality().hash(valueConstraints),const DeepCollectionEquality().hash(defaultValue));

@override
String toString() {
  return 'ParameterConstraints(required_: $required_, type: $type, minValue: $minValue, maxValue: $maxValue, step: $step, minLength: $minLength, maxLength: $maxLength, regex: $regex, regexDescription: $regexDescription, minItems: $minItems, maxItems: $maxItems, minProperties: $minProperties, maxProperties: $maxProperties, array: $array, items: $items, valueConstraints: $valueConstraints, defaultValue: $defaultValue)';
}


}

/// @nodoc
abstract mixin class $ParameterConstraintsCopyWith<$Res>  {
  factory $ParameterConstraintsCopyWith(ParameterConstraints value, $Res Function(ParameterConstraints) _then) = _$ParameterConstraintsCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: '_required') bool? required_, String? type, num? minValue, num? maxValue, num? step, int? minLength, int? maxLength, String? regex, String? regexDescription, int? minItems, int? maxItems, int? minProperties, int? maxProperties, List<String>? array, Map<String, dynamic>? items, Map<String, dynamic>? valueConstraints, dynamic defaultValue
});




}
/// @nodoc
class _$ParameterConstraintsCopyWithImpl<$Res>
    implements $ParameterConstraintsCopyWith<$Res> {
  _$ParameterConstraintsCopyWithImpl(this._self, this._then);

  final ParameterConstraints _self;
  final $Res Function(ParameterConstraints) _then;

/// Create a copy of ParameterConstraints
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? required_ = freezed,Object? type = freezed,Object? minValue = freezed,Object? maxValue = freezed,Object? step = freezed,Object? minLength = freezed,Object? maxLength = freezed,Object? regex = freezed,Object? regexDescription = freezed,Object? minItems = freezed,Object? maxItems = freezed,Object? minProperties = freezed,Object? maxProperties = freezed,Object? array = freezed,Object? items = freezed,Object? valueConstraints = freezed,Object? defaultValue = freezed,}) {
  return _then(_self.copyWith(
required_: freezed == required_ ? _self.required_ : required_ // ignore: cast_nullable_to_non_nullable
as bool?,type: freezed == type ? _self.type : type // ignore: cast_nullable_to_non_nullable
as String?,minValue: freezed == minValue ? _self.minValue : minValue // ignore: cast_nullable_to_non_nullable
as num?,maxValue: freezed == maxValue ? _self.maxValue : maxValue // ignore: cast_nullable_to_non_nullable
as num?,step: freezed == step ? _self.step : step // ignore: cast_nullable_to_non_nullable
as num?,minLength: freezed == minLength ? _self.minLength : minLength // ignore: cast_nullable_to_non_nullable
as int?,maxLength: freezed == maxLength ? _self.maxLength : maxLength // ignore: cast_nullable_to_non_nullable
as int?,regex: freezed == regex ? _self.regex : regex // ignore: cast_nullable_to_non_nullable
as String?,regexDescription: freezed == regexDescription ? _self.regexDescription : regexDescription // ignore: cast_nullable_to_non_nullable
as String?,minItems: freezed == minItems ? _self.minItems : minItems // ignore: cast_nullable_to_non_nullable
as int?,maxItems: freezed == maxItems ? _self.maxItems : maxItems // ignore: cast_nullable_to_non_nullable
as int?,minProperties: freezed == minProperties ? _self.minProperties : minProperties // ignore: cast_nullable_to_non_nullable
as int?,maxProperties: freezed == maxProperties ? _self.maxProperties : maxProperties // ignore: cast_nullable_to_non_nullable
as int?,array: freezed == array ? _self.array : array // ignore: cast_nullable_to_non_nullable
as List<String>?,items: freezed == items ? _self.items : items // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>?,valueConstraints: freezed == valueConstraints ? _self.valueConstraints : valueConstraints // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>?,defaultValue: freezed == defaultValue ? _self.defaultValue : defaultValue // ignore: cast_nullable_to_non_nullable
as dynamic,
  ));
}

}


/// @nodoc
@JsonSerializable()

class _ParameterConstraints implements ParameterConstraints {
  const _ParameterConstraints({@JsonKey(name: '_required') this.required_, this.type, this.minValue, this.maxValue, this.step, this.minLength, this.maxLength, this.regex, this.regexDescription, this.minItems, this.maxItems, this.minProperties, this.maxProperties, final  List<String>? array, final  Map<String, dynamic>? items, final  Map<String, dynamic>? valueConstraints, this.defaultValue}): _array = array,_items = items,_valueConstraints = valueConstraints;
  factory _ParameterConstraints.fromJson(Map<String, dynamic> json) => _$ParameterConstraintsFromJson(json);

@override@JsonKey(name: '_required') final  bool? required_;
@override final  String? type;
@override final  num? minValue;
@override final  num? maxValue;
@override final  num? step;
@override final  int? minLength;
@override final  int? maxLength;
@override final  String? regex;
@override final  String? regexDescription;
@override final  int? minItems;
@override final  int? maxItems;
@override final  int? minProperties;
@override final  int? maxProperties;
 final  List<String>? _array;
@override List<String>? get array {
  final value = _array;
  if (value == null) return null;
  if (_array is EqualUnmodifiableListView) return _array;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(value);
}

 final  Map<String, dynamic>? _items;
@override Map<String, dynamic>? get items {
  final value = _items;
  if (value == null) return null;
  if (_items is EqualUnmodifiableMapView) return _items;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(value);
}

 final  Map<String, dynamic>? _valueConstraints;
@override Map<String, dynamic>? get valueConstraints {
  final value = _valueConstraints;
  if (value == null) return null;
  if (_valueConstraints is EqualUnmodifiableMapView) return _valueConstraints;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(value);
}

@override final  dynamic defaultValue;

/// Create a copy of ParameterConstraints
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ParameterConstraintsCopyWith<_ParameterConstraints> get copyWith => __$ParameterConstraintsCopyWithImpl<_ParameterConstraints>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ParameterConstraintsToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _ParameterConstraints&&(identical(other.required_, required_) || other.required_ == required_)&&(identical(other.type, type) || other.type == type)&&(identical(other.minValue, minValue) || other.minValue == minValue)&&(identical(other.maxValue, maxValue) || other.maxValue == maxValue)&&(identical(other.step, step) || other.step == step)&&(identical(other.minLength, minLength) || other.minLength == minLength)&&(identical(other.maxLength, maxLength) || other.maxLength == maxLength)&&(identical(other.regex, regex) || other.regex == regex)&&(identical(other.regexDescription, regexDescription) || other.regexDescription == regexDescription)&&(identical(other.minItems, minItems) || other.minItems == minItems)&&(identical(other.maxItems, maxItems) || other.maxItems == maxItems)&&(identical(other.minProperties, minProperties) || other.minProperties == minProperties)&&(identical(other.maxProperties, maxProperties) || other.maxProperties == maxProperties)&&const DeepCollectionEquality().equals(other._array, _array)&&const DeepCollectionEquality().equals(other._items, _items)&&const DeepCollectionEquality().equals(other._valueConstraints, _valueConstraints)&&const DeepCollectionEquality().equals(other.defaultValue, defaultValue));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,required_,type,minValue,maxValue,step,minLength,maxLength,regex,regexDescription,minItems,maxItems,minProperties,maxProperties,const DeepCollectionEquality().hash(_array),const DeepCollectionEquality().hash(_items),const DeepCollectionEquality().hash(_valueConstraints),const DeepCollectionEquality().hash(defaultValue));

@override
String toString() {
  return 'ParameterConstraints(required_: $required_, type: $type, minValue: $minValue, maxValue: $maxValue, step: $step, minLength: $minLength, maxLength: $maxLength, regex: $regex, regexDescription: $regexDescription, minItems: $minItems, maxItems: $maxItems, minProperties: $minProperties, maxProperties: $maxProperties, array: $array, items: $items, valueConstraints: $valueConstraints, defaultValue: $defaultValue)';
}


}

/// @nodoc
abstract mixin class _$ParameterConstraintsCopyWith<$Res> implements $ParameterConstraintsCopyWith<$Res> {
  factory _$ParameterConstraintsCopyWith(_ParameterConstraints value, $Res Function(_ParameterConstraints) _then) = __$ParameterConstraintsCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: '_required') bool? required_, String? type, num? minValue, num? maxValue, num? step, int? minLength, int? maxLength, String? regex, String? regexDescription, int? minItems, int? maxItems, int? minProperties, int? maxProperties, List<String>? array, Map<String, dynamic>? items, Map<String, dynamic>? valueConstraints, dynamic defaultValue
});




}
/// @nodoc
class __$ParameterConstraintsCopyWithImpl<$Res>
    implements _$ParameterConstraintsCopyWith<$Res> {
  __$ParameterConstraintsCopyWithImpl(this._self, this._then);

  final _ParameterConstraints _self;
  final $Res Function(_ParameterConstraints) _then;

/// Create a copy of ParameterConstraints
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? required_ = freezed,Object? type = freezed,Object? minValue = freezed,Object? maxValue = freezed,Object? step = freezed,Object? minLength = freezed,Object? maxLength = freezed,Object? regex = freezed,Object? regexDescription = freezed,Object? minItems = freezed,Object? maxItems = freezed,Object? minProperties = freezed,Object? maxProperties = freezed,Object? array = freezed,Object? items = freezed,Object? valueConstraints = freezed,Object? defaultValue = freezed,}) {
  return _then(_ParameterConstraints(
required_: freezed == required_ ? _self.required_ : required_ // ignore: cast_nullable_to_non_nullable
as bool?,type: freezed == type ? _self.type : type // ignore: cast_nullable_to_non_nullable
as String?,minValue: freezed == minValue ? _self.minValue : minValue // ignore: cast_nullable_to_non_nullable
as num?,maxValue: freezed == maxValue ? _self.maxValue : maxValue // ignore: cast_nullable_to_non_nullable
as num?,step: freezed == step ? _self.step : step // ignore: cast_nullable_to_non_nullable
as num?,minLength: freezed == minLength ? _self.minLength : minLength // ignore: cast_nullable_to_non_nullable
as int?,maxLength: freezed == maxLength ? _self.maxLength : maxLength // ignore: cast_nullable_to_non_nullable
as int?,regex: freezed == regex ? _self.regex : regex // ignore: cast_nullable_to_non_nullable
as String?,regexDescription: freezed == regexDescription ? _self.regexDescription : regexDescription // ignore: cast_nullable_to_non_nullable
as String?,minItems: freezed == minItems ? _self.minItems : minItems // ignore: cast_nullable_to_non_nullable
as int?,maxItems: freezed == maxItems ? _self.maxItems : maxItems // ignore: cast_nullable_to_non_nullable
as int?,minProperties: freezed == minProperties ? _self.minProperties : minProperties // ignore: cast_nullable_to_non_nullable
as int?,maxProperties: freezed == maxProperties ? _self.maxProperties : maxProperties // ignore: cast_nullable_to_non_nullable
as int?,array: freezed == array ? _self._array : array // ignore: cast_nullable_to_non_nullable
as List<String>?,items: freezed == items ? _self._items : items // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>?,valueConstraints: freezed == valueConstraints ? _self._valueConstraints : valueConstraints // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>?,defaultValue: freezed == defaultValue ? _self.defaultValue : defaultValue // ignore: cast_nullable_to_non_nullable
as dynamic,
  ));
}


}

// dart format on
