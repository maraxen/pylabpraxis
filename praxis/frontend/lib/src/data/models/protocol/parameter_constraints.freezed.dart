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
mixin _$ParameterConstraintsBase {

@JsonKey(name: '_required') bool? get required_; String? get type; num? get minValue; num? get maxValue; num? get step; int? get minLength; int? get maxLength; String? get regex; String? get regexDescription; int? get minItems; int? get maxItems; int? get minProperties; int? get maxProperties; List<String>? get array; Map<String, dynamic>? get items; bool? get uniqueItems; bool? get creatable; bool? get editable; dynamic get defaultValue;
/// Create a copy of ParameterConstraintsBase
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ParameterConstraintsBaseCopyWith<ParameterConstraintsBase> get copyWith => _$ParameterConstraintsBaseCopyWithImpl<ParameterConstraintsBase>(this as ParameterConstraintsBase, _$identity);

  /// Serializes this ParameterConstraintsBase to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ParameterConstraintsBase&&(identical(other.required_, required_) || other.required_ == required_)&&(identical(other.type, type) || other.type == type)&&(identical(other.minValue, minValue) || other.minValue == minValue)&&(identical(other.maxValue, maxValue) || other.maxValue == maxValue)&&(identical(other.step, step) || other.step == step)&&(identical(other.minLength, minLength) || other.minLength == minLength)&&(identical(other.maxLength, maxLength) || other.maxLength == maxLength)&&(identical(other.regex, regex) || other.regex == regex)&&(identical(other.regexDescription, regexDescription) || other.regexDescription == regexDescription)&&(identical(other.minItems, minItems) || other.minItems == minItems)&&(identical(other.maxItems, maxItems) || other.maxItems == maxItems)&&(identical(other.minProperties, minProperties) || other.minProperties == minProperties)&&(identical(other.maxProperties, maxProperties) || other.maxProperties == maxProperties)&&const DeepCollectionEquality().equals(other.array, array)&&const DeepCollectionEquality().equals(other.items, items)&&(identical(other.uniqueItems, uniqueItems) || other.uniqueItems == uniqueItems)&&(identical(other.creatable, creatable) || other.creatable == creatable)&&(identical(other.editable, editable) || other.editable == editable)&&const DeepCollectionEquality().equals(other.defaultValue, defaultValue));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hashAll([runtimeType,required_,type,minValue,maxValue,step,minLength,maxLength,regex,regexDescription,minItems,maxItems,minProperties,maxProperties,const DeepCollectionEquality().hash(array),const DeepCollectionEquality().hash(items),uniqueItems,creatable,editable,const DeepCollectionEquality().hash(defaultValue)]);

@override
String toString() {
  return 'ParameterConstraintsBase(required_: $required_, type: $type, minValue: $minValue, maxValue: $maxValue, step: $step, minLength: $minLength, maxLength: $maxLength, regex: $regex, regexDescription: $regexDescription, minItems: $minItems, maxItems: $maxItems, minProperties: $minProperties, maxProperties: $maxProperties, array: $array, items: $items, uniqueItems: $uniqueItems, creatable: $creatable, editable: $editable, defaultValue: $defaultValue)';
}


}

/// @nodoc
abstract mixin class $ParameterConstraintsBaseCopyWith<$Res>  {
  factory $ParameterConstraintsBaseCopyWith(ParameterConstraintsBase value, $Res Function(ParameterConstraintsBase) _then) = _$ParameterConstraintsBaseCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: '_required') bool? required_, String? type, num? minValue, num? maxValue, num? step, int? minLength, int? maxLength, String? regex, String? regexDescription, int? minItems, int? maxItems, int? minProperties, int? maxProperties, List<String>? array, Map<String, dynamic>? items, bool? uniqueItems, bool? creatable, bool? editable, dynamic defaultValue
});




}
/// @nodoc
class _$ParameterConstraintsBaseCopyWithImpl<$Res>
    implements $ParameterConstraintsBaseCopyWith<$Res> {
  _$ParameterConstraintsBaseCopyWithImpl(this._self, this._then);

  final ParameterConstraintsBase _self;
  final $Res Function(ParameterConstraintsBase) _then;

/// Create a copy of ParameterConstraintsBase
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? required_ = freezed,Object? type = freezed,Object? minValue = freezed,Object? maxValue = freezed,Object? step = freezed,Object? minLength = freezed,Object? maxLength = freezed,Object? regex = freezed,Object? regexDescription = freezed,Object? minItems = freezed,Object? maxItems = freezed,Object? minProperties = freezed,Object? maxProperties = freezed,Object? array = freezed,Object? items = freezed,Object? uniqueItems = freezed,Object? creatable = freezed,Object? editable = freezed,Object? defaultValue = freezed,}) {
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
as Map<String, dynamic>?,uniqueItems: freezed == uniqueItems ? _self.uniqueItems : uniqueItems // ignore: cast_nullable_to_non_nullable
as bool?,creatable: freezed == creatable ? _self.creatable : creatable // ignore: cast_nullable_to_non_nullable
as bool?,editable: freezed == editable ? _self.editable : editable // ignore: cast_nullable_to_non_nullable
as bool?,defaultValue: freezed == defaultValue ? _self.defaultValue : defaultValue // ignore: cast_nullable_to_non_nullable
as dynamic,
  ));
}

}


/// @nodoc
@JsonSerializable()

class _ParameterConstraintsBase implements ParameterConstraintsBase {
  const _ParameterConstraintsBase({@JsonKey(name: '_required') this.required_, this.type, this.minValue, this.maxValue, this.step, this.minLength, this.maxLength, this.regex, this.regexDescription, this.minItems, this.maxItems, this.minProperties, this.maxProperties, final  List<String>? array, final  Map<String, dynamic>? items, this.uniqueItems, this.creatable, this.editable, this.defaultValue}): _array = array,_items = items;
  factory _ParameterConstraintsBase.fromJson(Map<String, dynamic> json) => _$ParameterConstraintsBaseFromJson(json);

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

@override final  bool? uniqueItems;
@override final  bool? creatable;
@override final  bool? editable;
@override final  dynamic defaultValue;

/// Create a copy of ParameterConstraintsBase
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ParameterConstraintsBaseCopyWith<_ParameterConstraintsBase> get copyWith => __$ParameterConstraintsBaseCopyWithImpl<_ParameterConstraintsBase>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ParameterConstraintsBaseToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _ParameterConstraintsBase&&(identical(other.required_, required_) || other.required_ == required_)&&(identical(other.type, type) || other.type == type)&&(identical(other.minValue, minValue) || other.minValue == minValue)&&(identical(other.maxValue, maxValue) || other.maxValue == maxValue)&&(identical(other.step, step) || other.step == step)&&(identical(other.minLength, minLength) || other.minLength == minLength)&&(identical(other.maxLength, maxLength) || other.maxLength == maxLength)&&(identical(other.regex, regex) || other.regex == regex)&&(identical(other.regexDescription, regexDescription) || other.regexDescription == regexDescription)&&(identical(other.minItems, minItems) || other.minItems == minItems)&&(identical(other.maxItems, maxItems) || other.maxItems == maxItems)&&(identical(other.minProperties, minProperties) || other.minProperties == minProperties)&&(identical(other.maxProperties, maxProperties) || other.maxProperties == maxProperties)&&const DeepCollectionEquality().equals(other._array, _array)&&const DeepCollectionEquality().equals(other._items, _items)&&(identical(other.uniqueItems, uniqueItems) || other.uniqueItems == uniqueItems)&&(identical(other.creatable, creatable) || other.creatable == creatable)&&(identical(other.editable, editable) || other.editable == editable)&&const DeepCollectionEquality().equals(other.defaultValue, defaultValue));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hashAll([runtimeType,required_,type,minValue,maxValue,step,minLength,maxLength,regex,regexDescription,minItems,maxItems,minProperties,maxProperties,const DeepCollectionEquality().hash(_array),const DeepCollectionEquality().hash(_items),uniqueItems,creatable,editable,const DeepCollectionEquality().hash(defaultValue)]);

@override
String toString() {
  return 'ParameterConstraintsBase(required_: $required_, type: $type, minValue: $minValue, maxValue: $maxValue, step: $step, minLength: $minLength, maxLength: $maxLength, regex: $regex, regexDescription: $regexDescription, minItems: $minItems, maxItems: $maxItems, minProperties: $minProperties, maxProperties: $maxProperties, array: $array, items: $items, uniqueItems: $uniqueItems, creatable: $creatable, editable: $editable, defaultValue: $defaultValue)';
}


}

/// @nodoc
abstract mixin class _$ParameterConstraintsBaseCopyWith<$Res> implements $ParameterConstraintsBaseCopyWith<$Res> {
  factory _$ParameterConstraintsBaseCopyWith(_ParameterConstraintsBase value, $Res Function(_ParameterConstraintsBase) _then) = __$ParameterConstraintsBaseCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: '_required') bool? required_, String? type, num? minValue, num? maxValue, num? step, int? minLength, int? maxLength, String? regex, String? regexDescription, int? minItems, int? maxItems, int? minProperties, int? maxProperties, List<String>? array, Map<String, dynamic>? items, bool? uniqueItems, bool? creatable, bool? editable, dynamic defaultValue
});




}
/// @nodoc
class __$ParameterConstraintsBaseCopyWithImpl<$Res>
    implements _$ParameterConstraintsBaseCopyWith<$Res> {
  __$ParameterConstraintsBaseCopyWithImpl(this._self, this._then);

  final _ParameterConstraintsBase _self;
  final $Res Function(_ParameterConstraintsBase) _then;

/// Create a copy of ParameterConstraintsBase
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? required_ = freezed,Object? type = freezed,Object? minValue = freezed,Object? maxValue = freezed,Object? step = freezed,Object? minLength = freezed,Object? maxLength = freezed,Object? regex = freezed,Object? regexDescription = freezed,Object? minItems = freezed,Object? maxItems = freezed,Object? minProperties = freezed,Object? maxProperties = freezed,Object? array = freezed,Object? items = freezed,Object? uniqueItems = freezed,Object? creatable = freezed,Object? editable = freezed,Object? defaultValue = freezed,}) {
  return _then(_ParameterConstraintsBase(
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
as Map<String, dynamic>?,uniqueItems: freezed == uniqueItems ? _self.uniqueItems : uniqueItems // ignore: cast_nullable_to_non_nullable
as bool?,creatable: freezed == creatable ? _self.creatable : creatable // ignore: cast_nullable_to_non_nullable
as bool?,editable: freezed == editable ? _self.editable : editable // ignore: cast_nullable_to_non_nullable
as bool?,defaultValue: freezed == defaultValue ? _self.defaultValue : defaultValue // ignore: cast_nullable_to_non_nullable
as dynamic,
  ));
}


}


/// @nodoc
mixin _$ParameterConstraints {

@JsonKey(name: '_required') bool? get required_; String? get type; num? get minValue; num? get maxValue; num? get step; int? get minLength; int? get maxLength; String? get regex; String? get regexDescription; int? get minItems; int? get maxItems; int? get minProperties; int? get maxProperties; List<String>? get array; Map<String, dynamic>? get items;@JsonKey(name: 'creatable') bool? get creatable;@JsonKey(name: 'editable') bool? get editable; bool? get uniqueItems; ParameterConstraintsBase? get valueConstraints; ParameterConstraintsBase? get keyConstraints; dynamic get defaultValue;
/// Create a copy of ParameterConstraints
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ParameterConstraintsCopyWith<ParameterConstraints> get copyWith => _$ParameterConstraintsCopyWithImpl<ParameterConstraints>(this as ParameterConstraints, _$identity);

  /// Serializes this ParameterConstraints to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ParameterConstraints&&(identical(other.required_, required_) || other.required_ == required_)&&(identical(other.type, type) || other.type == type)&&(identical(other.minValue, minValue) || other.minValue == minValue)&&(identical(other.maxValue, maxValue) || other.maxValue == maxValue)&&(identical(other.step, step) || other.step == step)&&(identical(other.minLength, minLength) || other.minLength == minLength)&&(identical(other.maxLength, maxLength) || other.maxLength == maxLength)&&(identical(other.regex, regex) || other.regex == regex)&&(identical(other.regexDescription, regexDescription) || other.regexDescription == regexDescription)&&(identical(other.minItems, minItems) || other.minItems == minItems)&&(identical(other.maxItems, maxItems) || other.maxItems == maxItems)&&(identical(other.minProperties, minProperties) || other.minProperties == minProperties)&&(identical(other.maxProperties, maxProperties) || other.maxProperties == maxProperties)&&const DeepCollectionEquality().equals(other.array, array)&&const DeepCollectionEquality().equals(other.items, items)&&(identical(other.creatable, creatable) || other.creatable == creatable)&&(identical(other.editable, editable) || other.editable == editable)&&(identical(other.uniqueItems, uniqueItems) || other.uniqueItems == uniqueItems)&&(identical(other.valueConstraints, valueConstraints) || other.valueConstraints == valueConstraints)&&(identical(other.keyConstraints, keyConstraints) || other.keyConstraints == keyConstraints)&&const DeepCollectionEquality().equals(other.defaultValue, defaultValue));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hashAll([runtimeType,required_,type,minValue,maxValue,step,minLength,maxLength,regex,regexDescription,minItems,maxItems,minProperties,maxProperties,const DeepCollectionEquality().hash(array),const DeepCollectionEquality().hash(items),creatable,editable,uniqueItems,valueConstraints,keyConstraints,const DeepCollectionEquality().hash(defaultValue)]);

@override
String toString() {
  return 'ParameterConstraints(required_: $required_, type: $type, minValue: $minValue, maxValue: $maxValue, step: $step, minLength: $minLength, maxLength: $maxLength, regex: $regex, regexDescription: $regexDescription, minItems: $minItems, maxItems: $maxItems, minProperties: $minProperties, maxProperties: $maxProperties, array: $array, items: $items, creatable: $creatable, editable: $editable, uniqueItems: $uniqueItems, valueConstraints: $valueConstraints, keyConstraints: $keyConstraints, defaultValue: $defaultValue)';
}


}

/// @nodoc
abstract mixin class $ParameterConstraintsCopyWith<$Res>  {
  factory $ParameterConstraintsCopyWith(ParameterConstraints value, $Res Function(ParameterConstraints) _then) = _$ParameterConstraintsCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: '_required') bool? required_, String? type, num? minValue, num? maxValue, num? step, int? minLength, int? maxLength, String? regex, String? regexDescription, int? minItems, int? maxItems, int? minProperties, int? maxProperties, List<String>? array, Map<String, dynamic>? items,@JsonKey(name: 'creatable') bool? creatable,@JsonKey(name: 'editable') bool? editable, bool? uniqueItems, ParameterConstraintsBase? valueConstraints, ParameterConstraintsBase? keyConstraints, dynamic defaultValue
});


$ParameterConstraintsBaseCopyWith<$Res>? get valueConstraints;$ParameterConstraintsBaseCopyWith<$Res>? get keyConstraints;

}
/// @nodoc
class _$ParameterConstraintsCopyWithImpl<$Res>
    implements $ParameterConstraintsCopyWith<$Res> {
  _$ParameterConstraintsCopyWithImpl(this._self, this._then);

  final ParameterConstraints _self;
  final $Res Function(ParameterConstraints) _then;

/// Create a copy of ParameterConstraints
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? required_ = freezed,Object? type = freezed,Object? minValue = freezed,Object? maxValue = freezed,Object? step = freezed,Object? minLength = freezed,Object? maxLength = freezed,Object? regex = freezed,Object? regexDescription = freezed,Object? minItems = freezed,Object? maxItems = freezed,Object? minProperties = freezed,Object? maxProperties = freezed,Object? array = freezed,Object? items = freezed,Object? creatable = freezed,Object? editable = freezed,Object? uniqueItems = freezed,Object? valueConstraints = freezed,Object? keyConstraints = freezed,Object? defaultValue = freezed,}) {
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
as Map<String, dynamic>?,creatable: freezed == creatable ? _self.creatable : creatable // ignore: cast_nullable_to_non_nullable
as bool?,editable: freezed == editable ? _self.editable : editable // ignore: cast_nullable_to_non_nullable
as bool?,uniqueItems: freezed == uniqueItems ? _self.uniqueItems : uniqueItems // ignore: cast_nullable_to_non_nullable
as bool?,valueConstraints: freezed == valueConstraints ? _self.valueConstraints : valueConstraints // ignore: cast_nullable_to_non_nullable
as ParameterConstraintsBase?,keyConstraints: freezed == keyConstraints ? _self.keyConstraints : keyConstraints // ignore: cast_nullable_to_non_nullable
as ParameterConstraintsBase?,defaultValue: freezed == defaultValue ? _self.defaultValue : defaultValue // ignore: cast_nullable_to_non_nullable
as dynamic,
  ));
}
/// Create a copy of ParameterConstraints
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$ParameterConstraintsBaseCopyWith<$Res>? get valueConstraints {
    if (_self.valueConstraints == null) {
    return null;
  }

  return $ParameterConstraintsBaseCopyWith<$Res>(_self.valueConstraints!, (value) {
    return _then(_self.copyWith(valueConstraints: value));
  });
}/// Create a copy of ParameterConstraints
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$ParameterConstraintsBaseCopyWith<$Res>? get keyConstraints {
    if (_self.keyConstraints == null) {
    return null;
  }

  return $ParameterConstraintsBaseCopyWith<$Res>(_self.keyConstraints!, (value) {
    return _then(_self.copyWith(keyConstraints: value));
  });
}
}


/// @nodoc
@JsonSerializable()

class _ParameterConstraints implements ParameterConstraints {
  const _ParameterConstraints({@JsonKey(name: '_required') this.required_, this.type, this.minValue, this.maxValue, this.step, this.minLength, this.maxLength, this.regex, this.regexDescription, this.minItems, this.maxItems, this.minProperties, this.maxProperties, final  List<String>? array, final  Map<String, dynamic>? items, @JsonKey(name: 'creatable') this.creatable, @JsonKey(name: 'editable') this.editable, this.uniqueItems, this.valueConstraints, this.keyConstraints, this.defaultValue}): _array = array,_items = items;
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

@override@JsonKey(name: 'creatable') final  bool? creatable;
@override@JsonKey(name: 'editable') final  bool? editable;
@override final  bool? uniqueItems;
@override final  ParameterConstraintsBase? valueConstraints;
@override final  ParameterConstraintsBase? keyConstraints;
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
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _ParameterConstraints&&(identical(other.required_, required_) || other.required_ == required_)&&(identical(other.type, type) || other.type == type)&&(identical(other.minValue, minValue) || other.minValue == minValue)&&(identical(other.maxValue, maxValue) || other.maxValue == maxValue)&&(identical(other.step, step) || other.step == step)&&(identical(other.minLength, minLength) || other.minLength == minLength)&&(identical(other.maxLength, maxLength) || other.maxLength == maxLength)&&(identical(other.regex, regex) || other.regex == regex)&&(identical(other.regexDescription, regexDescription) || other.regexDescription == regexDescription)&&(identical(other.minItems, minItems) || other.minItems == minItems)&&(identical(other.maxItems, maxItems) || other.maxItems == maxItems)&&(identical(other.minProperties, minProperties) || other.minProperties == minProperties)&&(identical(other.maxProperties, maxProperties) || other.maxProperties == maxProperties)&&const DeepCollectionEquality().equals(other._array, _array)&&const DeepCollectionEquality().equals(other._items, _items)&&(identical(other.creatable, creatable) || other.creatable == creatable)&&(identical(other.editable, editable) || other.editable == editable)&&(identical(other.uniqueItems, uniqueItems) || other.uniqueItems == uniqueItems)&&(identical(other.valueConstraints, valueConstraints) || other.valueConstraints == valueConstraints)&&(identical(other.keyConstraints, keyConstraints) || other.keyConstraints == keyConstraints)&&const DeepCollectionEquality().equals(other.defaultValue, defaultValue));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hashAll([runtimeType,required_,type,minValue,maxValue,step,minLength,maxLength,regex,regexDescription,minItems,maxItems,minProperties,maxProperties,const DeepCollectionEquality().hash(_array),const DeepCollectionEquality().hash(_items),creatable,editable,uniqueItems,valueConstraints,keyConstraints,const DeepCollectionEquality().hash(defaultValue)]);

@override
String toString() {
  return 'ParameterConstraints(required_: $required_, type: $type, minValue: $minValue, maxValue: $maxValue, step: $step, minLength: $minLength, maxLength: $maxLength, regex: $regex, regexDescription: $regexDescription, minItems: $minItems, maxItems: $maxItems, minProperties: $minProperties, maxProperties: $maxProperties, array: $array, items: $items, creatable: $creatable, editable: $editable, uniqueItems: $uniqueItems, valueConstraints: $valueConstraints, keyConstraints: $keyConstraints, defaultValue: $defaultValue)';
}


}

/// @nodoc
abstract mixin class _$ParameterConstraintsCopyWith<$Res> implements $ParameterConstraintsCopyWith<$Res> {
  factory _$ParameterConstraintsCopyWith(_ParameterConstraints value, $Res Function(_ParameterConstraints) _then) = __$ParameterConstraintsCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: '_required') bool? required_, String? type, num? minValue, num? maxValue, num? step, int? minLength, int? maxLength, String? regex, String? regexDescription, int? minItems, int? maxItems, int? minProperties, int? maxProperties, List<String>? array, Map<String, dynamic>? items,@JsonKey(name: 'creatable') bool? creatable,@JsonKey(name: 'editable') bool? editable, bool? uniqueItems, ParameterConstraintsBase? valueConstraints, ParameterConstraintsBase? keyConstraints, dynamic defaultValue
});


@override $ParameterConstraintsBaseCopyWith<$Res>? get valueConstraints;@override $ParameterConstraintsBaseCopyWith<$Res>? get keyConstraints;

}
/// @nodoc
class __$ParameterConstraintsCopyWithImpl<$Res>
    implements _$ParameterConstraintsCopyWith<$Res> {
  __$ParameterConstraintsCopyWithImpl(this._self, this._then);

  final _ParameterConstraints _self;
  final $Res Function(_ParameterConstraints) _then;

/// Create a copy of ParameterConstraints
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? required_ = freezed,Object? type = freezed,Object? minValue = freezed,Object? maxValue = freezed,Object? step = freezed,Object? minLength = freezed,Object? maxLength = freezed,Object? regex = freezed,Object? regexDescription = freezed,Object? minItems = freezed,Object? maxItems = freezed,Object? minProperties = freezed,Object? maxProperties = freezed,Object? array = freezed,Object? items = freezed,Object? creatable = freezed,Object? editable = freezed,Object? uniqueItems = freezed,Object? valueConstraints = freezed,Object? keyConstraints = freezed,Object? defaultValue = freezed,}) {
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
as Map<String, dynamic>?,creatable: freezed == creatable ? _self.creatable : creatable // ignore: cast_nullable_to_non_nullable
as bool?,editable: freezed == editable ? _self.editable : editable // ignore: cast_nullable_to_non_nullable
as bool?,uniqueItems: freezed == uniqueItems ? _self.uniqueItems : uniqueItems // ignore: cast_nullable_to_non_nullable
as bool?,valueConstraints: freezed == valueConstraints ? _self.valueConstraints : valueConstraints // ignore: cast_nullable_to_non_nullable
as ParameterConstraintsBase?,keyConstraints: freezed == keyConstraints ? _self.keyConstraints : keyConstraints // ignore: cast_nullable_to_non_nullable
as ParameterConstraintsBase?,defaultValue: freezed == defaultValue ? _self.defaultValue : defaultValue // ignore: cast_nullable_to_non_nullable
as dynamic,
  ));
}

/// Create a copy of ParameterConstraints
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$ParameterConstraintsBaseCopyWith<$Res>? get valueConstraints {
    if (_self.valueConstraints == null) {
    return null;
  }

  return $ParameterConstraintsBaseCopyWith<$Res>(_self.valueConstraints!, (value) {
    return _then(_self.copyWith(valueConstraints: value));
  });
}/// Create a copy of ParameterConstraints
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$ParameterConstraintsBaseCopyWith<$Res>? get keyConstraints {
    if (_self.keyConstraints == null) {
    return null;
  }

  return $ParameterConstraintsBaseCopyWith<$Res>(_self.keyConstraints!, (value) {
    return _then(_self.copyWith(keyConstraints: value));
  });
}
}

// dart format on
