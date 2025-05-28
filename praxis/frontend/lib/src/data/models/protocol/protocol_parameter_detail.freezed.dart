// dart format width=80
// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'protocol_parameter_detail.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$ProtocolParameterDetail {

 String get paramType; bool get isRequired;@JsonKey(name: 'default') dynamic get defaultValue; String? get description; Map<String, dynamic>? get constraints; String? get displayName; String? get unit;
/// Create a copy of ProtocolParameterDetail
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ProtocolParameterDetailCopyWith<ProtocolParameterDetail> get copyWith => _$ProtocolParameterDetailCopyWithImpl<ProtocolParameterDetail>(this as ProtocolParameterDetail, _$identity);

  /// Serializes this ProtocolParameterDetail to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ProtocolParameterDetail&&(identical(other.paramType, paramType) || other.paramType == paramType)&&(identical(other.isRequired, isRequired) || other.isRequired == isRequired)&&const DeepCollectionEquality().equals(other.defaultValue, defaultValue)&&(identical(other.description, description) || other.description == description)&&const DeepCollectionEquality().equals(other.constraints, constraints)&&(identical(other.displayName, displayName) || other.displayName == displayName)&&(identical(other.unit, unit) || other.unit == unit));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,paramType,isRequired,const DeepCollectionEquality().hash(defaultValue),description,const DeepCollectionEquality().hash(constraints),displayName,unit);

@override
String toString() {
  return 'ProtocolParameterDetail(paramType: $paramType, isRequired: $isRequired, defaultValue: $defaultValue, description: $description, constraints: $constraints, displayName: $displayName, unit: $unit)';
}


}

/// @nodoc
abstract mixin class $ProtocolParameterDetailCopyWith<$Res>  {
  factory $ProtocolParameterDetailCopyWith(ProtocolParameterDetail value, $Res Function(ProtocolParameterDetail) _then) = _$ProtocolParameterDetailCopyWithImpl;
@useResult
$Res call({
 String paramType, bool isRequired,@JsonKey(name: 'default') dynamic defaultValue, String? description, Map<String, dynamic>? constraints, String? displayName, String? unit
});




}
/// @nodoc
class _$ProtocolParameterDetailCopyWithImpl<$Res>
    implements $ProtocolParameterDetailCopyWith<$Res> {
  _$ProtocolParameterDetailCopyWithImpl(this._self, this._then);

  final ProtocolParameterDetail _self;
  final $Res Function(ProtocolParameterDetail) _then;

/// Create a copy of ProtocolParameterDetail
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? paramType = null,Object? isRequired = null,Object? defaultValue = freezed,Object? description = freezed,Object? constraints = freezed,Object? displayName = freezed,Object? unit = freezed,}) {
  return _then(_self.copyWith(
paramType: null == paramType ? _self.paramType : paramType // ignore: cast_nullable_to_non_nullable
as String,isRequired: null == isRequired ? _self.isRequired : isRequired // ignore: cast_nullable_to_non_nullable
as bool,defaultValue: freezed == defaultValue ? _self.defaultValue : defaultValue // ignore: cast_nullable_to_non_nullable
as dynamic,description: freezed == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as String?,constraints: freezed == constraints ? _self.constraints : constraints // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>?,displayName: freezed == displayName ? _self.displayName : displayName // ignore: cast_nullable_to_non_nullable
as String?,unit: freezed == unit ? _self.unit : unit // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

}


/// @nodoc
@JsonSerializable()

class _ProtocolParameterDetail implements ProtocolParameterDetail {
  const _ProtocolParameterDetail({required this.paramType, required this.isRequired, @JsonKey(name: 'default') this.defaultValue, this.description, final  Map<String, dynamic>? constraints, this.displayName, this.unit}): _constraints = constraints;
  factory _ProtocolParameterDetail.fromJson(Map<String, dynamic> json) => _$ProtocolParameterDetailFromJson(json);

@override final  String paramType;
@override final  bool isRequired;
@override@JsonKey(name: 'default') final  dynamic defaultValue;
@override final  String? description;
 final  Map<String, dynamic>? _constraints;
@override Map<String, dynamic>? get constraints {
  final value = _constraints;
  if (value == null) return null;
  if (_constraints is EqualUnmodifiableMapView) return _constraints;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(value);
}

@override final  String? displayName;
@override final  String? unit;

/// Create a copy of ProtocolParameterDetail
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ProtocolParameterDetailCopyWith<_ProtocolParameterDetail> get copyWith => __$ProtocolParameterDetailCopyWithImpl<_ProtocolParameterDetail>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ProtocolParameterDetailToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _ProtocolParameterDetail&&(identical(other.paramType, paramType) || other.paramType == paramType)&&(identical(other.isRequired, isRequired) || other.isRequired == isRequired)&&const DeepCollectionEquality().equals(other.defaultValue, defaultValue)&&(identical(other.description, description) || other.description == description)&&const DeepCollectionEquality().equals(other._constraints, _constraints)&&(identical(other.displayName, displayName) || other.displayName == displayName)&&(identical(other.unit, unit) || other.unit == unit));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,paramType,isRequired,const DeepCollectionEquality().hash(defaultValue),description,const DeepCollectionEquality().hash(_constraints),displayName,unit);

@override
String toString() {
  return 'ProtocolParameterDetail(paramType: $paramType, isRequired: $isRequired, defaultValue: $defaultValue, description: $description, constraints: $constraints, displayName: $displayName, unit: $unit)';
}


}

/// @nodoc
abstract mixin class _$ProtocolParameterDetailCopyWith<$Res> implements $ProtocolParameterDetailCopyWith<$Res> {
  factory _$ProtocolParameterDetailCopyWith(_ProtocolParameterDetail value, $Res Function(_ProtocolParameterDetail) _then) = __$ProtocolParameterDetailCopyWithImpl;
@override @useResult
$Res call({
 String paramType, bool isRequired,@JsonKey(name: 'default') dynamic defaultValue, String? description, Map<String, dynamic>? constraints, String? displayName, String? unit
});




}
/// @nodoc
class __$ProtocolParameterDetailCopyWithImpl<$Res>
    implements _$ProtocolParameterDetailCopyWith<$Res> {
  __$ProtocolParameterDetailCopyWithImpl(this._self, this._then);

  final _ProtocolParameterDetail _self;
  final $Res Function(_ProtocolParameterDetail) _then;

/// Create a copy of ProtocolParameterDetail
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? paramType = null,Object? isRequired = null,Object? defaultValue = freezed,Object? description = freezed,Object? constraints = freezed,Object? displayName = freezed,Object? unit = freezed,}) {
  return _then(_ProtocolParameterDetail(
paramType: null == paramType ? _self.paramType : paramType // ignore: cast_nullable_to_non_nullable
as String,isRequired: null == isRequired ? _self.isRequired : isRequired // ignore: cast_nullable_to_non_nullable
as bool,defaultValue: freezed == defaultValue ? _self.defaultValue : defaultValue // ignore: cast_nullable_to_non_nullable
as dynamic,description: freezed == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as String?,constraints: freezed == constraints ? _self._constraints : constraints // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>?,displayName: freezed == displayName ? _self.displayName : displayName // ignore: cast_nullable_to_non_nullable
as String?,unit: freezed == unit ? _self.unit : unit // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}


}

// dart format on
